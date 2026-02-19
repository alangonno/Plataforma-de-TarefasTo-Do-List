document.addEventListener('DOMContentLoaded', () => {
    const taskListContainer = document.getElementById('task-list-container');
    const createTaskForm = document.getElementById('create-task-form');
    const filterButtons = document.querySelectorAll('.filter-btn');

    // Obtém a URL base para a lista de tarefas do atributo 'data-task-list-url' do contêiner.
    const taskListUrl = taskListContainer.dataset.taskListUrl;

    // Função auxiliar para extrair o token CSRF de um cookie.
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Verifica se o cookie começa com o nome desejado.
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    const csrftoken = getCookie('csrftoken');

    function clearFormErrors(formElement) {
        formElement.querySelectorAll('.alert.alert-error').forEach(errorDiv => {
            errorDiv.remove();
        });
        formElement.querySelectorAll('.is-invalid').forEach(input => {
            input.classList.remove('is-invalid');
        });
    }

    // Função para exibir uma mensagem de erro genérica na parte superior do contêiner da lista de tarefas.
    function displayGlobalError(message) {
        clearGlobalErrors();
        const errorDiv = document.createElement('div');
        errorDiv.classList.add('alert', 'alert-error', 'global');
        errorDiv.setAttribute('role', 'alert');
        errorDiv.innerHTML = `<p>${DOMPurify.sanitize(message)}</p>`; // Sanitização
        taskListContainer.prepend(errorDiv);
    }

    // Função auxiliar para limpar mensagens de erro globais.
    function clearGlobalErrors() {
        taskListContainer.querySelectorAll('.alert.alert-error.global').forEach(errorDiv => errorDiv.remove());
    }

    // Exibe mensagens de erro de validação de um formulário recebidas de uma resposta AJAX.
    function displayFormErrors(formElement, errors) {
        clearFormErrors(formElement);

        // Lida com erros que não estão associados a um campo específico do formulário.
        if (errors.__all__) {
            const nonFieldErrorsDiv = document.createElement('div');
            nonFieldErrorsDiv.classList.add('alert', 'alert-error');
            nonFieldErrorsDiv.setAttribute('role', 'alert');
            (Array.isArray(errors.__all__) ? errors.__all__ : [errors.__all__]).forEach(error => {
                nonFieldErrorsDiv.innerHTML += `<p>${DOMPurify.sanitize(error)}</p>`; 
            });
            formElement.prepend(nonFieldErrorsDiv);
        }

        // Lida com erros associados a campos específicos do formulário.
        for (const fieldName in errors) {
            if (fieldName !== '__all__') {
                const fieldInput = formElement.querySelector(`[name="${fieldName}"]`);
                if (fieldInput) {
                    fieldInput.classList.add('is-invalid');
                    const errorDiv = document.createElement('div');
                    errorDiv.classList.add('alert', 'alert-error');
                    (Array.isArray(errors[fieldName]) ? errors[fieldName] : [errors[fieldName]]).forEach(error => {
                        errorDiv.innerHTML += `<p>${DOMPurify.sanitize(error)}</p>`; 
                    });
                    // Insere a div de erro imediatamente após o campo de entrada.
                    fieldInput.parentNode.insertBefore(errorDiv, fieldInput.nextSibling);
                }
            }
        }
    }

    // --- Funcionalidade de Filtragem de Tarefas ---
    filterButtons.forEach(button => {
        button.addEventListener('click', () => {
            clearGlobalErrors(); // Limpa erros globais antes de tentar filtrar.
            
            filterButtons.forEach(btn => btn.classList.remove('filter-btn-active'));
            button.classList.add('filter-btn-active');

            const filter = button.dataset.filter;
            let url = taskListUrl;
            
            if (filter !== 'all') {
                url += `?completed=${filter}`;
            }

            // Faz uma requisição AJAX para obter a lista de tarefas filtrada.
            fetch(url, {
                headers: {
                    // Sinaliza para o servidor que esta é uma requisição AJAX.
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.text()) // Espera texto HTML como resposta.
            .then(html => {
                taskListContainer.innerHTML = html; // Atualiza o conteúdo do contêiner da lista de tarefas.
                addEventListenersToTasks(); // Re-adiciona os event listeners para as novas tarefas carregadas.
            })
            .catch(error => {
                // Erros de rede ou do servidor são capturados aqui. Exibe mensagem genérica.
                displayGlobalError('Ocorreu um erro ao carregar as tarefas. Tente novamente.');
            });
        });
    });

    // --- Funcionalidade de Criação de Tarefas ---
    if (createTaskForm) {
        createTaskForm.addEventListener('submit', (e) => {
            e.preventDefault(); // Impede o envio padrão do formulário, que recarregaria a página.
            clearGlobalErrors(); // Limpa erros globais antes de tentar criar uma tarefa.

            const formData = new FormData(createTaskForm);

            // Envia os dados do formulário via AJAX para criar uma nova tarefa.
            fetch(createTaskForm.action, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest', // Sinaliza requisição AJAX.
                    'X-CSRFToken': csrftoken // Inclui o token CSRF para segurança.
                },
                body: formData // Envia os dados do formulário.
            })
            .then(response => {
                // Verifica se a resposta HTTP indica um erro (status 4xx ou 5xx).
                if (!response.ok) {
                    // Se houver erro, tenta parsear a resposta como JSON para obter detalhes do erro.
                    return response.json().then(err => Promise.reject(err));
                }
                return response.json(); // Se a resposta for bem-sucedida, parseia como JSON.
            })
            .then(data => {
                if (data.success) {
                    clearFormErrors(createTaskForm);
                    createTaskForm.reset();

                    // Constrói o HTML dinamicamente.
                    const sanitizedId = DOMPurify.sanitize(data.task.id);
                    const sanitizedTitle = DOMPurify.sanitize(data.task.title);
                    const sanitizedDescription = DOMPurify.sanitize(data.task.description || '');
                    const sanitizedDueDate = data.task.due_date ? DOMPurify.sanitize(data.task.due_date) : '';

                    const newTaskHtml = `
                        <li class="task-item" id="task-item-${sanitizedId}">
                            <div class="task-view" id="task-view-${sanitizedId}">
                                <div class="task-main">
                                    <div class="task-checkbox-wrapper">
                                        <input
                                            type="checkbox"
                                            ${data.task.completed ? 'checked' : ''}
                                            data-task-id="${sanitizedId}"
                                            class="task-checkbox task-completed-toggle"
                                            id="checkbox-${sanitizedId}"
                                        >
                                        <label for="checkbox-${sanitizedId}" class="checkbox-custom"></label>
                                    </div>

                                    <div class="task-content">
                                        <span class="task-title ${data.task.completed ? 'task-completed' : ''}">${sanitizedTitle}</span>
                                        ${sanitizedDueDate ? `<span class="task-due-date">Prazo: ${sanitizedDueDate}</span>` : ''}
                                        <p class="task-description">${sanitizedDescription || 'Sem descrição.'}</p>
                                    </div>
                                </div>

                                <div class="task-actions">
                                    <button data-task-id="${sanitizedId}" class="btn btn-edit edit-task-button">Editar</button>
                                    <form action="/tasks/${sanitizedId}/delete/" method="post" class="delete-task-form" style="display:inline;">
                                        <input type="hidden" name="csrfmiddlewaretoken" value="${csrftoken}">
                                        <button type="submit" data-task-id="${sanitizedId}" class="btn btn-delete">Excluir</button>
                                    </form>
                                </div>
                            </div>

                            <div id="edit-form-${sanitizedId}" class="task-edit-form" style="display:none;">
                                <form class="edit-task-form-actual" data-task-id="${sanitizedId}" action="/tasks/${sanitizedId}/update/" method="post">
                                    <input type="hidden" name="csrfmiddlewaretoken" value="${csrftoken}">
                                    <div class="form-group">
                                        <label for="id_title_${sanitizedId}" class="form-label">Título</label>
                                        <input type="text" id="id_title_${sanitizedId}" name="title" value="${sanitizedTitle}" required class="form-input">
                                    </div>
                                    <div class="form-group">
                                        <label for="id_description_${sanitizedId}" class="form-label">Descrição</label>
                                        <textarea id="id_description_${sanitizedId}" name="description" class="form-textarea">${sanitizedDescription}</textarea>
                                    </div>
                                    <div class="form-row form-row-split">
                                        <div class="form-group">
                                            <label for="id_due_date_${sanitizedId}" class="form-label">Data de Vencimento</label>
                                            <input type="date" id="id_due_date_${sanitizedId}" name="due_date" value="${sanitizedDueDate}" class="form-input">
                                        </div>
                                        <div class="form-group form-group-checkbox">
                                            <div class="checkbox-wrapper">
                                                <input type="checkbox" id="id_completed_${sanitizedId}" name="completed" ${data.task.completed ? 'checked' : ''} class="task-checkbox">
                                                <label for="id_completed_${sanitizedId}" class="checkbox-label">Concluída</label>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="edit-actions">
                                        <button type="submit" class="btn btn-primary">Salvar</button>
                                        <button type="button" class="btn btn-secondary cancel-edit-button" data-task-id="${sanitizedId}">Cancelar</button>
                                    </div>
                                </form>
                            </div>
                        </li>
                    `;
                    const ul = taskListContainer.querySelector('ul');
                    // Verifica se a lista está vazia com a mensagem "Nenhuma tarefa encontrada." para substituir.
                    if (ul.querySelector('li') && ul.querySelector('li').textContent.includes('Nenhuma tarefa encontrada.')) {
                        ul.innerHTML = newTaskHtml;
                    } else {
                        // Adiciona a nova tarefa ao final da lista.
                        ul.insertAdjacentHTML('beforeend', newTaskHtml);
                    }
                    addEventListenersToTasks(); // Re-adiciona os event listeners para a nova tarefa.
                }
            })
            .catch(error => {
                // Se o erro vier do servidor com validações, exibe-as no formulário.
                // Caso contrário (ex: erro de rede), exibe uma mensagem global genérica.
                if (error && error.errors) {
                    displayFormErrors(createTaskForm, error.errors);
                } else {
                    displayGlobalError('Ocorreu um erro ao criar a tarefa. Tente novamente.');
                }
            });
        });
    }

    // --- Gerenciamento de Event Listeners para Tarefas (existentes e novas)
    function addEventListenersToTasks() {
        document.querySelectorAll('.task-completed-toggle').forEach(checkbox => {
            checkbox.onchange = (e) => {
                const taskId = e.target.dataset.taskId;
                const completed = e.target.checked;
                clearGlobalErrors(); // Limpa erros globais antes de tentar atualizar.
                
                const currentTaskItem = document.getElementById(`task-item-${taskId}`);
                const title = currentTaskItem.querySelector('.task-title').textContent;
                const description = currentTaskItem.querySelector('.task-description').textContent;
                const dueDateSpan = currentTaskItem.querySelector('.task-due-date');
                // Prazo: DD-MM-YYYY" (ajustar conforme formato real)
                const due_date_text = dueDateSpan ? dueDateSpan.textContent.replace('Prazo: ', '') : '';
                
                let due_date = '';
                // Garante que a data esteja no formato correto (YYYY-MM-DD) para envio ao backend.
                // Adapte o `split` e a ordem dos `parts` se o formato na tela for diferente.
                if (due_date_text) {
                    const parts = due_date_text.split('-'); // Supondo o formato DD-MM-YYYY
                    if (parts.length === 3) {
                        due_date = `${parts[2]}-${parts[1]}-${parts[0]}`; // Converte para YYYY-MM-DD
                    }
                }

                const formData = new FormData();
                formData.append('title', title);
                formData.append('description', description === 'Sem descrição.' ? '' : description);
                formData.append('due_date', due_date);
                formData.append('completed', completed);
                formData.append('csrfmiddlewaretoken', csrftoken);

                // Envia a requisição AJAX para atualizar o status da tarefa.
                fetch(`/tasks/${taskId}/update/`, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': csrftoken
                    },
                    body: formData
                })
                .then(response => {
                    if (!response.ok) {
                        return response.json().then(err => Promise.reject(err));
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.success) {
                        
                        document.querySelector(`#task-item-${taskId} .task-title`).classList.toggle('task-completed', data.task.completed);
                    } else {
                        // Se o erro vier do servidor com validações, exibe-as como erro global.
                        displayGlobalError(data.errors && data.errors.__all__ ? data.errors.__all__[0] : 'Ocorreu um erro ao atualizar o status da tarefa. Tente novamente.');
                        e.target.checked = !completed; // Reverte o estado do checkbox em caso de erro.
                    }
                })
                .catch(error => {
                    // Erros de rede ou do servidor são capturados aqui. Exibe mensagem genérica.
                    displayGlobalError('Ocorreu um erro ao atualizar o status da tarefa. Tente novamente.');
                    e.target.checked = !completed; // Reverte o estado do checkbox em caso de erro de rede.
                });
            };
        });

        // Lida com a exclusão de tarefas via envio de formulário AJAX.
        document.querySelectorAll('.delete-task-form').forEach(form => {
            form.onsubmit = (e) => {
                e.preventDefault();
                const taskId = e.target.querySelector('button').dataset.taskId;
                clearGlobalErrors(); // Limpa erros globais antes de tentar excluir.

                fetch(form.action, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': csrftoken
                    },
                    body: new FormData(form)
                })
                .then(response => {
                    if (!response.ok) { // Check response.ok for network errors before parsing JSON
                        return response.json().then(err => Promise.reject(err));
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.success) {
                        document.getElementById(`task-item-${taskId}`).remove(); // Remove o item da tarefa do DOM.
                        const ul = taskListContainer.querySelector('ul');
                        // Se não houver mais tarefas, exibe a mensagem de "Nenhuma tarefa encontrada.".
                        if (!ul.querySelector('li')) {
                            ul.innerHTML = '<li class="task-empty"><p class="empty-message">Nenhuma tarefa encontrada.</p></li>';
                        }
                    } else {
                        // Se o erro vier do servidor com validações, exibe-as como erro global.
                        displayGlobalError(data.errors && data.errors.__all__ ? data.errors.__all__[0] : 'Ocorreu um erro ao excluir a tarefa. Tente novamente.');
                    }
                })
                .catch(error => {
                    displayGlobalError('Ocorreu um erro ao excluir a tarefa. Tente novamente.');
                });
            };
        });

        // Alterna a visibilidade do formulário de edição da tarefa.
        document.querySelectorAll('.edit-task-button').forEach(button => {
            button.onclick = (e) => {
                const taskId = e.target.dataset.taskId;
                document.getElementById(`edit-form-${taskId}`).style.display = 'block'; // Mostra o formulário de edição.
                e.target.style.display = 'none'; // Esconde o botão "Editar".
            };
        });

        // Cancela a edição, escondendo o formulário e mostrando o botão "Editar".
        document.querySelectorAll('.cancel-edit-button').forEach(button => {
            button.onclick = (e) => {
                const taskId = e.target.dataset.taskId;
                document.getElementById(`edit-form-${taskId}`).style.display = 'none'; // Esconde o formulário de edição.
                document.querySelector(`#task-item-${taskId} .edit-task-button`).style.display = 'inline'; // Mostra o botão "Editar".
            };
        });

        // Lida com o envio do formulário de atualização de tarefa via AJAX.
        document.querySelectorAll('.edit-task-form-actual').forEach(form => {
            form.onsubmit = (e) => {
                e.preventDefault();
                const taskId = e.target.dataset.taskId;
                const formData = new FormData(form);

                fetch(form.action, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': csrftoken
                    },
                    body: formData
                })
                .then(response => {
                    if (!response.ok) {
                        return response.json().then(err => Promise.reject(err));
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.success) {
                        const taskItem = document.getElementById(`task-item-${taskId}`);
                        const task = data.task;
                        // Atualiza dinamicamente os detalhes da tarefa no DOM com os novos dados.
                        taskItem.querySelector('.task-title').textContent = task.title;
                        taskItem.querySelector('.task-title').classList.toggle('task-completed', task.completed);
                        taskItem.querySelector('.task-completed-toggle').checked = task.completed;
                        taskItem.querySelector('.task-description').textContent = task.description || 'Sem descrição.';
                        const dueDateSpan = taskItem.querySelector('.task-due-date');
                        if (task.due_date) {
                            if (dueDateSpan) {
                                // Se o span de data de vencimento já existe, atualiza seu conteúdo.
                                dueDateSpan.textContent = `Prazo: ${DOMPurify.sanitize(task.due_date)}`;
                            } else {
                                // Se não existe, cria um novo span e o insere após o título.
                                const titleSpan = taskItem.querySelector('.task-title');
                                titleSpan.insertAdjacentHTML('afterend', `<span class="task-due-date">Prazo: ${DOMPurify.sanitize(task.due_date)}</span>`);
                            }
                        } else {
                            if (dueDateSpan) dueDateSpan.remove(); // Remove o span se a data de vencimento for removida.
                        }

                        document.getElementById(`edit-form-${taskId}`).style.display = 'none';
                        document.querySelector(`#task-item-${taskId} .edit-task-button`).style.display = 'inline';
                    } else {
                        // Em um ambiente de produção, erros de validação seriam exibidos ao usuário na UI, não no console.
                        displayFormErrors(form, data.errors);
                    }
                })
                .catch(error => {
                    displayFormErrors(form, { '__all__': ['Ocorreu um erro ao atualizar a tarefa.'] });
                });
            };
        });
    }

    addEventListenersToTasks(); // Inicializa os event listeners para as tarefas carregadas inicialmente.
});
