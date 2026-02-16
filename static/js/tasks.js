document.addEventListener('DOMContentLoaded', () => {
    const taskListContainer = document.getElementById('task-list-container');
    const createTaskForm = document.getElementById('create-task-form');
    const filterButtons = document.querySelectorAll('.filter-btn');

    const taskListUrl = taskListContainer.dataset.taskListUrl;

    // Function to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    const csrftoken = getCookie('csrftoken');

    // Function to clear existing form errors
    function clearFormErrors(formElement) {
        formElement.querySelectorAll('.alert.alert-error').forEach(errorDiv => {
            errorDiv.remove();
        });
        formElement.querySelectorAll('.is-invalid').forEach(input => {
            input.classList.remove('is-invalid');
        });
    }

    // Function to display form errors from an AJAX response
    function displayFormErrors(formElement, errors) {
        clearFormErrors(formElement); // Clear existing errors first

        // Handle non-field errors (e.g., __all__ errors)
        if (errors.__all__) {
            const nonFieldErrorsDiv = document.createElement('div');
            nonFieldErrorsDiv.classList.add('alert', 'alert-error');
            nonFieldErrorsDiv.setAttribute('role', 'alert');
            (Array.isArray(errors.__all__) ? errors.__all__ : [errors.__all__]).forEach(error => {
                nonFieldErrorsDiv.innerHTML += `<p>${error}</p>`;
            });
            formElement.prepend(nonFieldErrorsDiv); // Add to the top of the form
        }

        // Handle field-specific errors
        for (const fieldName in errors) {
            if (fieldName !== '__all__') {
                const fieldInput = formElement.querySelector(`[name="${fieldName}"]`);
                if (fieldInput) {
                    fieldInput.classList.add('is-invalid'); // Add is-invalid class to the input
                    const formGroup = fieldInput.closest('.form-group');
                    if (formGroup) {
                        const errorDiv = document.createElement('div');
                        errorDiv.classList.add('alert', 'alert-error');
                        (Array.isArray(errors[fieldName]) ? errors[fieldName] : [errors[fieldName]]).forEach(error => {
                            errorDiv.innerHTML += `<p>${error}</p>`;
                        });
                        formGroup.appendChild(errorDiv); // Add after the input within the form-group
                    }
                }
            }
        }
    }

    // --- Task Filtering ---
    filterButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Update class names for active state
            filterButtons.forEach(btn => btn.classList.remove('filter-btn-active')); // Changed from active
            button.classList.add('filter-btn-active'); // Changed from active
            const filter = button.dataset.filter;
            let url = taskListUrl; // Use the URL from the data attribute
            if (filter !== 'all') {
                url += `?completed=${filter}`;
            }
            fetch(url, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.text())
            .then(html => {
                taskListContainer.innerHTML = html;
                addEventListenersToTasks(); // Re-add event listeners for new tasks
            })
            .catch(error => console.error('Error fetching filtered tasks:', error));
        });
    });

    // --- Task Creation ---
    if (createTaskForm) {
        createTaskForm.addEventListener('submit', (e) => {
            e.preventDefault();

            const formData = new FormData(createTaskForm);

            fetch(createTaskForm.action, {
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
                    clearFormErrors(createTaskForm); // Clear any existing errors
                    createTaskForm.reset();
                    // Dynamically add the new task to the list
                    const newTaskHtml = `
                        <li class="task-item" id="task-item-${data.task.id}">
                            <div class="task-view" id="task-view-${data.task.id}">
                                <div class="task-main">
                                    <div class="task-checkbox-wrapper">
                                        <input
                                            type="checkbox"
                                            ${data.task.completed ? 'checked' : ''}
                                            data-task-id="${data.task.id}"
                                            class="task-checkbox task-completed-toggle"
                                            id="checkbox-${data.task.id}"
                                        >
                                        <label for="checkbox-${data.task.id}" class="checkbox-custom"></label>
                                    </div>

                                    <div class="task-content">
                                        <span class="task-title ${data.task.completed ? 'task-completed' : ''}">${data.task.title}</span>
                                        ${data.task.due_date ? `<span class="task-due-date">Prazo: ${data.task.due_date}</span>` : ''}
                                        <p class="task-description">${data.task.description || 'Sem descrição.'}</p>
                                    </div>
                                </div>

                                <div class="task-actions">
                                    <button data-task-id="${data.task.id}" class="btn btn-edit edit-task-button">Editar</button>
                                    <form action="/tasks/${data.task.id}/delete/" method="post" class="delete-task-form" style="display:inline;">
                                        <input type="hidden" name="csrfmiddlewaretoken" value="${csrftoken}">
                                        <button type="submit" data-task-id="${data.task.id}" class="btn btn-delete">Excluir</button>
                                    </form>
                                </div>
                            </div>

                            <div id="edit-form-${data.task.id}" class="task-edit-form" style="display:none;">
                                <form class="edit-task-form-actual" data-task-id="${data.task.id}" action="/tasks/${data.task.id}/update/" method="post">
                                    <input type="hidden" name="csrfmiddlewaretoken" value="${csrftoken}">
                                    <div class="form-group">
                                        <label for="id_title_${data.task.id}" class="form-label">Título</label>
                                        <input type="text" id="id_title_${data.task.id}" name="title" value="${data.task.title}" required class="form-input">
                                    </div>
                                    <div class="form-group">
                                        <label for="id_description_${data.task.id}" class="form-label">Descrição</label>
                                        <textarea id="id_description_${data.task.id}" name="description" class="form-textarea">${data.task.description || ''}</textarea>
                                    </div>
                                    <div class="form-row form-row-split">
                                        <div class="form-group">
                                            <label for="id_due_date_${data.task.id}" class="form-label">Data de Vencimento</label>
                                            <input type="date" id="id_due_date_${data.task.id}" name="due_date" value="${data.task.due_date || ''}" class="form-input">
                                        </div>
                                        <div class="form-group form-group-checkbox">
                                            <div class="checkbox-wrapper">
                                                <input type="checkbox" id="id_completed_${data.task.id}" name="completed" ${data.task.completed ? 'checked' : ''} class="task-checkbox">
                                                <label for="id_completed_${data.task.id}" class="checkbox-label">Concluída</label>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="edit-actions">
                                        <button type="submit" class="btn btn-primary">Salvar</button>
                                        <button type="button" class="btn btn-secondary cancel-edit-button" data-task-id="${data.task.id}">Cancelar</button>
                                    </div>
                                </form>
                            </div>
                        </li>
                    `;
                    const ul = taskListContainer.querySelector('ul');
                    if (ul.querySelector('li') && ul.querySelector('li').textContent.includes('Nenhuma tarefa encontrada.')) { // Check for "Nenhuma tarefa encontrada." more robustly
                        ul.innerHTML = newTaskHtml; // Replace "No tasks found" message
                    } else {
                        ul.insertAdjacentHTML('beforeend', newTaskHtml);
                    }
                    addEventListenersToTasks(); // Re-add event listeners for the new task
                }
            })
            .catch(error => {
                // Assuming error.errors contains the Django form errors
                displayFormErrors(createTaskForm, error.errors);
            });
        });
    }

    // --- Event Listeners for existing and new tasks ---
    function addEventListenersToTasks() {
        // Toggle completed status
        document.querySelectorAll('.task-completed-toggle').forEach(checkbox => {
            checkbox.onchange = (e) => {
                const taskId = e.target.dataset.taskId;
                const completed = e.target.checked;
                
                const currentTaskItem = document.getElementById(`task-item-${taskId}`);
                const title = currentTaskItem.querySelector('.task-title').textContent;
                const description = currentTaskItem.querySelector('.task-description').textContent;
                const dueDateSpan = currentTaskItem.querySelector('.task-due-date');
                const due_date_text = dueDateSpan ? dueDateSpan.textContent.replace('Prazo: ', '') : ''; // Adjusted from (Prazo: )
                
                // due_date para DD--MM-YYYY
                let due_date = '';
                if (due_date_text) {
                    const parts = due_date_text.split('/');
                    if (parts.length === 3) {
                        due_date = `${parts[0]}-${parts[1]}-${parts[2]}`;
                    }
                }

                const formData = new FormData();
                formData.append('title', title); // Send existing title
                formData.append('description', description === 'Sem descrição.' ? '' : description); // Send existing description
                formData.append('due_date', due_date); // Send existing due_date
                formData.append('completed', completed);
                formData.append('csrfmiddlewaretoken', csrftoken);

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
                        // Update class name for completed status
                        const taskTitleSpan = document.querySelector(`#task-item-${taskId} .task-title`);
                        if (data.task.completed) {
                            taskTitleSpan.classList.add('task-completed'); // Changed from completed
                        } else {
                            taskTitleSpan.classList.remove('task-completed'); // Changed from completed
                        }
                    } else {
                        console.error('Error updating task status:', data.errors);
                        e.target.checked = !completed; // Revert checkbox state
                    }
                })
                .catch(error => {
                    console.error('Network error updating task status:', error);
                    e.target.checked = !completed; // Revert checkbox state
                });
            };
        });

        // Delete Task
        document.querySelectorAll('.delete-task-form').forEach(form => {
            form.onsubmit = (e) => {
                e.preventDefault();
                const taskId = e.target.querySelector('button').dataset.taskId;

                fetch(form.action, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': csrftoken
                    },
                    body: new FormData(form)
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        document.getElementById(`task-item-${taskId}`).remove();
                        // If no tasks left, show "Nenhuma tarefa encontrada."
                        const ul = taskListContainer.querySelector('ul');
                        if (!ul.querySelector('li')) {
                            ul.innerHTML = '<li class="task-empty"><p class="empty-message">Nenhuma tarefa encontrada.</p></li>'; // Updated empty message HTML
                        }
                    } else {
                        console.error('Error deleting task:', data.errors);
                    }
                })
                .catch(error => console.error('Network error deleting task:', error));
            };
        });

        // Edit Task Toggle
        document.querySelectorAll('.edit-task-button').forEach(button => {
            button.onclick = (e) => {
                const taskId = e.target.dataset.taskId;
                document.getElementById(`edit-form-${taskId}`).style.display = 'block';
                e.target.style.display = 'none'; // Hide edit button
            };
        });

        // Cancel Edit
        document.querySelectorAll('.cancel-edit-button').forEach(button => {
            button.onclick = (e) => {
                const taskId = e.target.dataset.taskId;
                document.getElementById(`edit-form-${taskId}`).style.display = 'none';
                document.querySelector(`#task-item-${taskId} .edit-task-button`).style.display = 'inline'; // Show edit button
            };
        });

        // Actual Task Update Submission
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
                        taskItem.querySelector('.task-title').textContent = task.title;
                        taskItem.querySelector('.task-title').classList.toggle('task-completed', task.completed); // Changed from completed
                        taskItem.querySelector('.task-completed-toggle').checked = task.completed;
                        taskItem.querySelector('.task-description').textContent = task.description || 'Sem descrição.';
                        const dueDateSpan = taskItem.querySelector('.task-due-date');
                        if (task.due_date) {
                            if (dueDateSpan) {
                                dueDateSpan.textContent = `Prazo: ${task.due_date}`; // Adjusted from (Prazo: )
                            } else {
                                // If no due_date span existed, create one
                                const titleSpan = taskItem.querySelector('.task-title');
                                titleSpan.insertAdjacentHTML('afterend', `<span class="task-due-date">Prazo: ${task.due_date}</span>`); // Adjusted from (Prazo: )
                            }
                        } else {
                            if (dueDateSpan) dueDateSpan.remove(); // Remove if no due date
                        }

                        // Hide edit form and show edit button
                        document.getElementById(`edit-form-${taskId}`).style.display = 'none';
                        document.querySelector(`#task-item-${taskId} .edit-task-button`).style.display = 'inline';
                    } else {
                        console.error('Error updating task:', data.errors);
                        displayFormErrors(form, data.errors);
                    }
                })
                .catch(error => {
                    console.error('Network error updating task:', error);
                    displayFormErrors(form, { '__all__': ['Ocorreu um erro de rede ao atualizar a tarefa.'] });
                });
            };
        });
    }

    addEventListenersToTasks(); // Add event listeners initially
});
