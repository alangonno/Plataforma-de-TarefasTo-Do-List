# Plataforma-de-Tarefas (To-Do List)

Minha resolução do Desafio FullStack Plataforma de Tarefas (To-Do List).

## 1. Descrição Geral

### Objetivo do Projeto
Desenvolver uma aplicação web completa utilizando Django para gerenciamento pessoal de tarefas (To-Do List), com autenticação segura e isolamento estrito de dados por usuário. Esta aplicação foi concebida como uma aplicação web full-stack, utilizando templates renderizados pelo servidor e interações AJAX para atualizações parciais da interface.

### Tecnologias Utilizadas

#### Backend
*   **Python 3.11+**
*   **Django 5.1+**: Framework web de alto nível para desenvolvimento rápido e design pragmático.
*   **PostgreSQL**: Banco de dados relacional.
*   **SQLite**: Banco de dados paradesenvolvimento rápido e testes.

#### Frontend
*   **Django Templates**: Sistema de template para renderização de HTML no servidor.
*   **CSS**: Para estilização e responsividade da interface.
*   **JS**: Para interações assíncronas (AJAX) e Lib JS.

#### Testes
*   **Pytest**: Framework de testes para Python.
*   **pytest-django**: Plugin para integração de testes Pytest com projetos Django.

#### Infraestrutura
*   **Docker & Docker Compose**: Para orquestração da aplicação e do banco de dados PostgreSQL.
*   **Gunicorn**: Servidor WSGI de produção.
*   **Variáveis de Ambiente (.env.example)**: Para gerenciamento seguro de segredos e troca dinâmica de banco de dados.

## 2. Estrutura de Pastas e Arquivos

```
Plataforma-de-TarefasTo-Do-List/
│
├── config/             # Configuração do projeto (settings, urls, wsgi/asgi)
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py     # Configurações globais do Django.
│   ├── urls.py         # Mapeamento de URLs globais do projeto.
│   ├── views.py        # Views genéricas do projeto (ex: página inicial).
│   └── wsgi.py
│
├── apps/
│   ├── __init__.py
│   ├── users/          # Aplicação para autenticação e gerenciamento de usuários
│   │   ├── __init__.py
│   │   ├── admin.py    # Registro de modelos no admin do Django.
│   │   ├── apps.py     # Configuração da aplicação.
│   │   ├── forms.py    # Formulários para registro de usuário.
│   │   ├── models.py   # Definição do modelo de Usuário personalizado.
│   │   ├── tests/      # Pacote de testes modular (Models, Views, Forms)
│   │   │   ├── __init__.py
│   │   │   ├── test_models.py
│   │   │   ├── test_views.py
│   │   │   └── test_forms.py
│   │   ├── urls.py     # Mapeamento de URLs específicas da aplicação de usuários.
│   │   ├── views.py    # Lógica de views para registro, login e logout de usuários.
│   │   └── migrations/ # Migrações do banco de dados para o modelo de usuário.
│   │
│   └── tasks/          # Aplicação para o domínio das tarefas (To-Do)
│       ├── __init__.py 
│       ├── admin.py    # Registro de modelos no admin do Django.
│       ├── apps.py     # Configuração da aplicação.
│       ├── forms.py    # Formulários para criação e atualização de tarefas.
│       ├── models.py   # Definição do modelo de Tarefa.
│       ├── tests/      # Pacote de testes modular (Models, Views, Forms)
│       │   ├── __init__.py
│       │   ├── test_models.py
│       │   ├── test_views.py
│       │   └── test_forms.py
│       ├── urls.py     # Mapeamento de URLs específicas da aplicação de tarefas.
│       └── views.py    # Lógica de views para CRUD de tarefas.
│       └── migrations/ # Migrações do banco de dados para o modelo de tarefa.
│
├── templates/          # Templates HTML globais e específicos de apps
│   ├── base.html       # Template base para todas as páginas.
│   ├── home.html       # Template para a página inicial.
│   ├── error.html      # Template para erros 500 e 404
│   ├── users/          # Templates específicos da aplicação de usuários
│   │   ├── register.html # Template para o formulário de registro.
│   │   └── login.html    # Template para o formulário de login.
│   └── tasks/          # Templates específicos da aplicação de tarefas
│       ├── task_list.html        # Exibe a lista de tarefas e o formulário de criação.
│       └── _task_list_items.html # Partial template para renderização de itens da lista de tarefas.
│
├── docker/             # Configurações de containerização
│   ├── docker-compose.yml  # Orquestração de containers (aponta para docker/)
│   ├── Dockerfile      # Imagem Docker otimizada
│   ├── .dockerignore   # Arquivos ignorados pelo Docker
│   └── scripts/
│       └── entrypoint.py # Script de inicialização em Python
│
├── static/             # Arquivos estáticos (CSS, JS)
│   ├── css/            # Estilos organizados por componente (layout, tasks, forms)
│   └── js/
│       ├── tasks.js    # Lógica principal de interações AJAX e manipulação do DOM
│       └── vendor/     # Bibliotecas externas gerenciadas localmente para maior segurança e performance
│
├── .env                # Variáveis de ambiente (ignorado pelo Git)
├── .env.example        # Exemplo de configuração de ambiente
├── manage.py           # Utilitário de linha de comando do Django.
├── README.md           # Este arquivo.
├── requirements.txt    # Dependências do projeto Python.
├── pytest.ini          # Configuração para testes rodar
└── venv/               # Ambiente virtual Python (ignorado pelo Git)
└── .gitignore          # Lista de arquivos e pastas a serem ignorados pelo Git.
```

## 3. Modelagem do Banco de Dados

### 3.1. Tabela de Usuários (`users_user`)

Representa os usuários da aplicação.

*   **`id`**: `SERIAL` / `BIGINT PRIMARY KEY`, identificador único do usuário.
*   **`password`**: `VARCHAR(128) NOT NULL`, armazena a senha do usuário hashed e salt.
*   **`last_login`**: `TIMESTAMP WITH TIME ZONE`, registra o último login do usuário.
*   **`is_superuser`**: `BOOLEAN NOT NULL`, indica se o usuário tem todas as permissões.
*   **`first_name`**: `VARCHAR(150) NOT NULL`, nome pessoal do usuário. (não utilizado)
*   **`last_name`**: `VARCHAR(150) NOT NULL` , sobrenome do usuário. (não utilizado)
*   **`is_staff`**: `BOOLEAN NOT NULL`, indica se o usuário pode acessar o painel administrativo.
*   **`is_active`**: `BOOLEAN NOT NULL`, indica se a conta do usuário está ativa.
*   **`date_joined`**: `TIMESTAMP WITH TIME ZONE NOT NULL`, data e hora de registro do usuário.
*   **`name`**: `VARCHAR(100) NOT NULL`, nome completo do usuário.
*   **`email`**: `VARCHAR(254) NOT NULL UNIQUE`, endereço de e-mail do usuário, usado para login e deve ser único.

**Observações:**
*   A autenticação é baseada no campo `email`.

### 3.2. Tabela de Tarefas (`tasks_task`)

Representa uma tarefa individual na lista de afazeres. Cada tarefa é associada a um usuário específico.

*   **`id`**: `SERIAL` / `BIGINT PRIMARY KEY`, identificador único da tarefa.
*   **`user_id`**: `BIGINT NOT NULL`, Chave Estrangeira referenciando `id` da tabela `users_user`.
*   **`title`**: `VARCHAR(200) NOT NULL`, descrição breve da tarefa.
*   **`description`**: `TEXT`, detalhes adicionais sobre a tarefa (opcional).
*   **`created_at`**: `TIMESTAMP WITH TIME ZONE NOT NULL`, data e hora de criação da tarefa.
*   **`due_date`**: `DATE`, data de vencimento para a tarefa (opcional).
*   **`completed`**: `BOOLEAN NOT NULL`, indica se a tarefa foi concluída.

### 3.3. Relacionamento entre Tabelas

Existe uma relação de **Um-para-Muitos** entre a tabela `users_user` e a tabela `tasks_task`.

*   **Uma entrada em `users_user`** (um usuário) pode estar associada a **múltiplas entradas em `tasks_task`** (muitas tarefas).
*   **Cada entrada em `tasks_task`** (uma tarefa) está associada a **apenas uma entrada em `users_user`** (um usuário).

Esta relação é estabelecida através de uma **Chave Estrangeira (`FOREIGN KEY`)**:
*   O campo `user_id` na tabela `tasks_task` referencia o campo `id` na tabela `users_user`.

**Restrição de Integridade (Ação de Exclusão):**
*   A Chave Estrangeira `user_id` em `tasks_task` possui uma restrição `ON DELETE CASCADE`.

---

## 4. Funções Principais (Fluxo de Usuário Implementado)

### Registro de Usuário
*   **Formulário**: `apps/users/forms.py - UserRegistrationForm`
    *   **Herança**: Herda de `forms.ModelForm`, baseado no modelo `User`.
    *   **Campos Personalizados**: Define `password` e `password_confirm` como campos obrigatórios com `PasswordInput` para garantir a segurança da entrada.
    *   **Campos do Modelo**: Inclui `name` e `email`.
    *   **Validações Integradas**:
        *   `clean_password_confirm()`: Verifica se `password` e `password_confirm` são idênticos, levantando `ValidationError` se não forem.
        *   `clean_email()`: Verifica a unicidade do e-mail no banco de dados, impedindo o registro de e-mails já existentes.
    *   **Método `save()`**: Sobrescreve o método `save` para realizar o hashing da senha (`user.set_password()`) antes de salvar o usuário no banco de dados.

*   **View**: `apps/users/views.py - register` (função baseada em função)
    *   **Rota**: `POST /users/register/` (submissão do formulário) ou `GET /users/register/` (exibição do formulário).
    *   **Fluxo de Processamento**:
        1.  Verifica se a requisição é `POST`.
        2.  Instancia `UserRegistrationForm` com os dados do `POST`.
        3.  Chama `form.is_valid()`: Isso dispara todas as validações definidas no formulário (`clean_email`, `clean_password_confirm`, campos obrigatórios, etc.).
        4.  **Se válido**: `form.save()` cria o novo usuário (com a senha já hashed), e `login(request, user)` autentica o usuário automaticamente. Redireciona para a página `home`.
        5.  **Se inválido**: O formulário é renderizado novamente com os erros de validação, exibindo-os para o usuário.

*   **URL**: `apps/users/urls.py`
    *   **Padrão**: `path('register/', views.register, name='register')`
    *   **Função**: Mapeia a URL `/users/register/` para a função `register` na view, usando o nome `register` para referência.

*   **Template**: `templates/users/register.html`
    *   Exibe o formulário de registro e mensagens de erro de validação.

### Login de Usuário
*   **Formulário**: `apps/users/forms.py - UserAuthenticationForm`
    *   **Herança**: Herda de `django.contrib.auth.forms.AuthenticationForm`.
    *   **Campos Personalizados**: Sobrescreve o campo `username` para ser `email`, com `label="E-mail"`, `max_length=254` e widget `TextInput(attrs={'autofocus': True})`.
    *   **Mensagens de Erro Customizadas**: No método `__init__`, sobrescreve as mensagens de erro padrão (`invalid_login`, `inactive`) para fornecer feedback em português.
    *   **Validações**: O formulário se encarrega da validação das credenciais (email e senha) via o backend de autenticação do Django.

*   **View**: `apps/users/views.py - UserLoginView` (classe baseada em classe)
    *   **Herança**: Herda de `django.contrib.auth.views.LoginView`.
    *   **Configurações**:
        *   `template_name = 'users/login.html'`: Define o template a ser usado para exibir o formulário de login.
        *   `redirect_authenticated_user = True`: Redireciona usuários já autenticados para a `get_success_url`, prevenindo que acessem a página de login novamente.
        *   `authentication_form = UserAuthenticationForm`: Especifica o formulário customizado a ser usado para a autenticação.
    *   **Métodos**:
        *   `get_success_url()`: Define para onde o usuário será redirecionado após um login bem-sucedido, que é a página 'home'.
    *   **Validações**: A classe `LoginView` e o `UserAuthenticationForm` realizam as validações de credenciais.

*   **URL**: `apps/users/urls.py`
    *   **Padrão**: `path('login/', UserLoginView.as_view(), name='login')`
    *   **Função**: Mapeia a URL `/users/login/` para a view baseada em classe `UserLoginView`, usando o nome `login` para referência.

*   **Template**: `templates/users/login.html`
    *   Exibe o formulário de login configurado para usar o e-mail e mensagens de erro.

### Logout de Usuário
*   **View**: `apps/users/views.py - user_logout` (função baseada em função)
    *   **Rota**: `/users/logout/`
    *   **Função Principal**: Chama a função `django.contrib.auth.logout(request)`, que encerra a sessão do usuário.
    *   **Redirecionamento**: Redireciona o usuário para a página 'home' após o logout.

*   **URL**: `apps/users/urls.py`
    *   **Padrão**: `path('logout/', views.user_logout, name='logout')`
    *   **Função**: Mapeia a URL `/users/logout/` para a função `user_logout` na view, usando o nome `logout` para referência.

### Página Inicial
*   **View**: `config/views.py - home` (função baseada em função)
    *   **Rota**: `/`
    *   **Função**: Renderiza o template `home.html`. Não realiza validações específicas ou processamento complexo, servindo como ponto de entrada para a aplicação.

*   **URL**: `config/urls.py`
    *   **Padrão**: `path('', config_views.home, name='home')`
    *   **Função**: Mapeia a URL raiz (`/`) para a função `home` na view, usando o nome `home` para referência.

*   **Template**: `templates/home.html`
    *   Exibe uma mensagem de boas-vindas e links de login/registro se o usuário não estiver autenticado, ou um link para as tarefas se estiver logado.

### Gerenciamento de Tarefas

Esta funcionalidade central permite aos usuários criar, listar, atualizar e excluir suas próprias tarefas, com interações dinâmicas e assíncronas via AJAX. As views foram projetadas para utilizar métodos HTTP e códigos de status apropriados. O isolamento de dados por usuário é rigorosamente aplicado em todas as operações.

*   **Listagem e Filtragem de Tarefas**
    *   **View**: `apps/tasks/views.py - TaskListView` (Classe, `LoginRequiredMixin`, `ListView`)
        *   **`get_queryset()`**:  Filtra as tarefas para retornar apenas as que pertencem ao `request.user`. Adicionalmente, verifica o parâmetro `completed` na URL (`?completed=true` ou `?completed=false`) para filtrar tarefas por status de conclusão.
        *   **`get_context_data()`**: Adiciona uma instância vazia de `TaskForm` ao contexto, permitindo que o formulário de criação de tarefas seja exibido na mesma página de listagem.
        *   **`get()`**: Se a requisição for AJAX (detectado pelo cabeçalho `x-requested-with`), a view renderiza apenas o partial template `_task_list_items.html` com as tarefas filtradas, permitindo atualizações dinâmicas da lista sem recarregar a página inteira. Para requisições HTTP normais, renderiza `task_list.html`.
    *   **URL**: `apps/tasks/urls.py`
        *   **Padrão**: `path('', TaskListView.as_view(), name='task_list')`
        *   **Função**: Mapeia a URL `/tasks/` para a `TaskListView`, com o nome `task_list`.
    *   **Template**: `templates/tasks/task_list.html`
        *   Exibe o formulário de criação de tarefas e inclui o partial template `_task_list_items.html` para a lista de tarefas.
        *   Contém botões de filtro (`Todas`, `Pendentes`, `Concluídas`).
    *   **JavaScript**: `static/js/tasks.js`
        *   Manipula cliques nos botões de filtro.
        *   Faz requisições AJAX para `/tasks/?completed=...` para obter a lista filtrada.
        *   Atualiza dinamicamente o `task-list-container` no frontend com a resposta HTML parcial recebida da view.

*   **Criação de Tarefas**
    *   **Formulário**: `apps/tasks/forms.py - TaskForm`
        *   **Herança**: `forms.ModelForm` baseado no modelo `Task`.
        *   **Campos**: Inclui `title`, `description`, `due_date`, `completed`.
        *   **Validações Integradas**:
            *   `clean_due_date()`: Garante que a data de vencimento (`due_date`) não possa ser uma data no passado, levantando `ValidationError` se for.
            *   **`title`**: É um campo obrigatório.
    *   **View**: `apps/tasks/views.py - TaskCreateView` (Classe, `LoginRequiredMixin`, `View`)
        *   **Rota**: `/tasks/create/`
        *   **Fluxo de Processamento**:
            1.  Instancia `TaskForm` com os dados do `POST`.
            2.  Chama `form.is_valid()` para validar os dados, incluindo `clean_due_date` e a obrigatoriedade do `title`.
            3.  **Se válido**:
                *   `form.save(commit=False)`: Cria uma instância de `Task` sem salvar no banco.
                *   `task.user = request.user`: Atribui a tarefa ao usuário logado, garantindo o isolamento.
                *   `task.save()`: Salva a tarefa no banco de dados.
                *   **Resposta AJAX**: Se a requisição for AJAX, retorna `JsonResponse` com `success: True`, os dados da nova tarefa e status HTTP `201 Created`.
                *   **Resposta Normal**: Redireciona para a `task_list`.
            4.  **Se inválido**:
                *   **Resposta AJAX**: Retorna `JsonResponse` com `success: False`, um dicionário de `errors` e status HTTP `400 Bad Request`.
                *   **Resposta Normal**: Renderiza novamente a página de listagem de tarefas com o formulário contendo os erros.
    *   **URL**: `apps/tasks/urls.py`
        *   **Padrão**: `path('create/', TaskCreateView.as_view(), name='task_create')`
        *   **Função**: Mapeia a URL `/tasks/create/` para a `TaskCreateView`, com o nome `task_create`.
    *   **JavaScript**: `static/js/tasks.js`
        *   Interpreta a resposta JSON da view.
        *   Em caso de sucesso, adiciona dinamicamente a nova tarefa à lista e reseta o formulário de criação.
        *   Em caso de erro, utiliza a função `displayFormErrors` para injetar as mensagens de validação diretamente nos campos correspondentes do formulário.

*   **Atualização de Tarefas**
    *   **View**: `apps/tasks/views.py - TaskUpdateView` (Classe, `LoginRequiredMixin`, `View`)
        *   **Rota**: `/tasks/<int:pk>/update/`
        *   **Fluxo de Processamento**:
            1.  `task = get_object_or_404(Task, pk=pk)`: Busca a tarefa pelo `pk`.
            2.  **Verifica se a tarefa pertence ao usuário logado (`request.user`) através de um filtro seguro. Se não pertencer, retorna um HTTP 404 (Not Found), prevenindo a enumeração de IDs.**
            2.  Instancia `TaskForm` com os dados e a instância da `task` existente.
            3.  Chama `form.is_valid()` para validar os dados.
            4.  **Se válido**:
                *   `form.save()`: Salva as alterações na tarefa no banco de dados.
                *   **Resposta AJAX**: Se a requisição for AJAX, retorna `JsonResponse` com `success: True` e os dados atualizados da tarefa.
                *   **Resposta Normal**: Redireciona para a `task_list`.
            5.  **Se inválido**:
                *   **Resposta AJAX**: Retorna `JsonResponse` com `success: False`, um dicionário de `errors` e status HTTP `400 Bad Request`.
                *   **Resposta Normal**: Redireciona para a `task_list`.
    *   **URL**: `apps/tasks/urls.py`
        *   **Padrão**: `path('<int:pk>/update/', TaskUpdateView.as_view(), name='task_update')`
        *   **Função**: Mapeia URLs como `/tasks/123/update/` para a `TaskUpdateView`, com o nome `task_update`.
    *   **JavaScript**: `static/js/tasks.js`
        *   **Toggle de Conclusão**: O JavaScript manipula o checkbox `completed` de uma tarefa. Ao ser clicado, envia uma requisição AJAX contendo o novo status `completed` para a `TaskUpdateView`, e atualiza dinamicamente a aparência do título da tarefa na lista.
        *   **Edição Completa (Inline)**: Ao clicar em "Editar", o JavaScript pode exibir/ocultar um formulário de edição inline. Após a submissão via AJAX, os detalhes da tarefa são atualizados dinamicamente na lista, sem recarregar a página. Em caso de erro na edição, utiliza a função `displayFormErrors` para mostrar as validações no formulário inline.

*   **Exclusão de Tarefas**
    *   **View**: `apps/tasks/views.py - TaskDeleteView` (Classe, `LoginRequiredMixin`, `View`)
        *   **Rota**: `/tasks/<int:pk>/delete/`
        *   **Fluxo de Processamento**:
            1.  `task = get_object_or_404(Task, pk=pk)`: Assim como na atualização, esta linha busca a tarefa pelo `pk`.
            2.  **Verifica se a tarefa pertence ao usuário logado (`request.user`) através de um filtro seguro. Se não pertencer, retorna um HTTP 404 (Not Found)** antes de permitir a exclusão.
            2.  `task.delete()`: Remove a tarefa do banco de dados.
            3.  **Resposta AJAX**: Se a requisição for AJAX, retorna `JsonResponse` com `{'success': True}` e status HTTP `200 OK`.
            4.  **Resposta Normal**: Redireciona para a `task_list`.
    *   **URL**: `apps/tasks/urls.py`
        *   **Padrão**: `path('<int:pk>/delete/', TaskDeleteView.as_view(), name='task_delete')`
        *   **Função**: Mapeia URLs como `/tasks/123/delete/` para a `TaskDeleteView`, com o nome `task_delete`.
    *   **JavaScript**: `static/js/tasks.js`
        *   Interpreta a resposta JSON da view.
        *   Em caso de sucesso, remove dinamicamente o elemento HTML da tarefa da lista no frontend, sem recarregar a página.

---

## 5. Segurança Aplicada

*   **Hash de Senhas**: As senhas são automaticamente hashed e salted pelo sistema de autenticação do Django, através do método `set_password` chamado no `CustomUserManager`.
*   **Proteção de Rotas Privadas**: O Django garante que rotas que exigem autenticação (como todas as rotas de gerenciamento de tarefas) só possam ser acessadas por usuários logados, utilizando o `LoginRequiredMixin` nas views.
*   **Isolamento de Dados por Usuário**: Implementado em todas as views de tarefa. Cada requisição para listar, criar, atualizar ou excluir tarefas é filtrada para garantir que o usuário logado apenas interaja com suas próprias tarefas (`Task.objects.filter(user=request.user)`), prevenindo acesso não autorizado aos dados de outros usuários.
*   **Validação de Input**: Implementada via Django Forms, garantindo que os dados submetidos atendam aos requisitos (ex: e-mail único, formato correto, campos obrigatórios).
*   **CSRF Protection**: O Django fornece proteção contra ataques de Cross-Site Request Forgery (CSRF) automaticamente para formulários renderizados com `{% csrf_token %}` e para requisições POST seguras.
*   **Prevenção de XSS (Cross-Site Scripting)**: O sistema de templates do Django, por padrão, faz o *escape* automático do output de variáveis (ex: `{{ variavel }}`), convertendo caracteres como `<`, `>`, `'`, `"` em suas entidades HTML correspondentes. Isso previne a injeção de código malicioso no HTML renderizado.

    No entanto, para dados enviados para o frontend via `JsonResponse` (JSON) e que são dinamicamente inseridos no DOM via JavaScript, uma camada adicional de proteção é aplicada. Utiliza-se a biblioteca **DOMPurify** para sanitizar todo o conteúdo gerado dinamicamente no cliente (`static/js/tasks.js`) antes de ser injetado no DOM. Isso garante que qualquer HTML potencialmente malicioso presente nos dados do servidor seja neutralizado antes de ser renderizado pelo navegador, protegendo contra XSS em cenários de manipulação de DOM client-side.
*   **Tratamento de Erros e Mensagens**: Erros de validação de formulário são exibidos ao usuário. A aplicação agora possui um sistema de tratamento de erros unificado e robusto para requisições AJAX e não-AJAX:
        *   **Erros Globais (404 Not Found, 500 Internal Server Error)**: Implementado através de `handler404` e `handler500` globais. Para requisições **AJAX**, retorna `JsonResponse` com o status e mensagem de erro. Para requisições comuns, renderiza uma página de erro unificada (`error.html`), garantindo uma experiência de usuário consistente e informativa.
        *   **Isolamento Seguro (404 Not Found)**: Para tentativas de acesso a recursos de outros usuários (ex: tentar atualizar a tarefa de outro usuário), a aplicação retorna um status `404 Not Found` de forma consistente. Isso previne a **enumeração de IDs**, garantindo que um usuário não consiga descobrir se uma tarefa que não é dele sequer existe no banco de dados.
    No frontend (`static/js/tasks.js`), as chamadas a `displayGlobalError` garantem que erros de rede ou do servidor (que não são erros de validação específicos de formulário) exibam mensagens amigáveis ao usuário, sem expor detalhes técnicos sensíveis.

---

## 6. Como Rodar Localmente (Híbrido: SQLite ou PostgreSQL)

Siga os passos abaixo para configurar e executar o projeto em seu ambiente local. O projeto está configurado para permitir a troca rápida entre SQLite e PostgreSQL.

### 6.1. Pré-requisitos

*   **Python 3.11+**
*   **pip**: Gerenciador de pacotes do Python.
*   **PostgreSQL (Opcional)**: Caso deseje utilizar este banco de dados em vez do SQLite.

### 6.2. Configuração do Ambiente

1.  **Clone o Repositório**:
    ```bash
    git clone https://github.com/alangonno/Plataforma-de-TarefasTo-Do-List.git
    cd Plataforma-de-TarefasTo-Do-List
    ```

2.  **Crie um Ambiente Virtual**:
    É altamente recomendável usar um ambiente virtual para isolar as dependências do projeto.
    ```bash
    python -m venv venv
    ```

3.  **Ative o Ambiente Virtual**:
    *   **Windows**:
        ```bash
        .\venv\Scripts\activate
        ```
    *   **macOS/Linux**:
        ```bash
        source venv/bin/activate
        ```

4.  **Instale as Dependências**:
    ```bash
    pip install -r requirements.txt
    ```

### 6.3. Configuração do Projeto(Opcional)

1.  **Variáveis de Ambiente (`.env.example`)**:
    O projeto está configurado no `settings.py` para carregar as variáveis diretamente do arquivo `.env.example` na raiz do projeto.

    *   Se pretende utilizar o banco Postgres é necessario atualizar as variaveis
    
        *   Certifique-se de que o banco de dados definido em `DB_NAME` já exista no seu servidor PostgreSQL.
        *   `USE_POSTGRES=True`

3.  **Crie um Superusuário (Opcional, mas Recomendado)**:
    Para acessar o painel administrativo do Django, crie um superusuário.
    ```bash
    python manage.py createsuperuser
    ```
    Siga as instruções no terminal para definir nome de usuário, e-mail e senha.

### 6.4 Execute as migrações

```bash
python manage.py migrate
```

Sempre que alterar o banco no `.env.example`, você deve aplicar as migrações para o novo banco.

**Atenção:** Os dados do SQLite e do PostgreSQL são independentes. Se você alternar o banco, precisará criar um novo superusuário para o banco que estiver ativo.

### 6.5. Execute o Servidor de Desenvolvimento

Finalmente, inicie o servidor de desenvolvimento do Django.
```bash
python manage.py runserver
```
O projeto estará acessível em `http://127.0.0.1:8000/` em seu navegador.

---

## 7. Como Rodar com Docker

Esta é a forma recomendada para rodar o projeto em um ambiente isolado e pronto para produção, utilizando PostgreSQL.

### 7.1. Passo a Passo

1.  **Certifique-se de ter o Docker e Docker Compose instalados.**
2.  **Inicie os containers:**
    Na raiz do projeto, execute:
    ```bash
    docker-compose -f docker/docker-compose.yml up --build
    ```
    *   Este comando vai construir a imagem Django, baixar o Postgres e configurar tudo automaticamente.
    *   O script `entrypoint.py` cuidará das migrations e da coleta de arquivos estáticos.

3.  **Acesse a aplicação:**
    Abra `http://localhost:8000` no seu navegador.

---

## 8. Como Rodar os Testes

Este projeto utiliza `pytest` e `pytest-django` para a execução dos testes. Siga os passos abaixo para rodar os testes localmente.

### 8.1. Pré-requisitos

*   O projeto deve estar configurado conforme a seção "6. Como Rodar Localmente" 

### 8.2. Executando os Testes

1.  **Ative o Ambiente Virtual.**
2.  **Execute o Pytest:**
    ```bash
    pytest
    ```
    Isso executará todos os testes encontrados nos diretórios `apps/users/tests` e `apps/tasks/tests`.

---
## 9. Próximos Passos

### 9.1. Gerenciamento de Erros e Logging no Servidor (Django)

Para preparar a aplicação para um ambiente de produção, as seguintes melhorias na gestão de erros e logging seriam feitas:

*   **Configurar `ADMINS`**: No `config/settings.py`, defina uma lista de administradores que receberão notificações por e-mail sobre erros críticos (HTTP 500).
    ```python
    ADMINS = [
        ('Seu Nome', 'seu_email@exemplo.com'),
    ]
    ```
*   **Configurar Backend de E-mail**: Ajuste as configurações de e-mail no `config/settings.py` para um serviço SMTP real (ex: `EMAIL_HOST`, `EMAIL_PORT`, etc.) em vez do backend de console, para que os e-mails de erro sejam realmente enviados.
*   **Configurar `LOGGING`**: No `config/settings.py`, adicione uma configuração `LOGGING` detalhada para:
    *   Capturar erros em arquivos de log.
    *   Enviar e-mails aos `ADMINS` para erros críticos do servidor (HTTP 500).
    *   Monitorar logs em ambiente de produção (ferramentas podem ser integradas para monitoramento avançado).

### 9.2. Migração para HTMX

Para futuras iterações e um projeto de longo prazo, a migração para HTMX seria uma boa consideração para reduzir a complexidade do JavaScript no cliente e aproveitar a abordagem de renderização server-side do Django de forma mais eficiente.

