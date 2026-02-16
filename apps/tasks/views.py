from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from .models import Task
from .forms import TaskForm

class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        # Ensure only tasks belonging to the logged-in user are returned
        queryset = Task.objects.filter(user=self.request.user)
        completed_filter = self.request.GET.get('completed')
        if completed_filter == 'true':
            queryset = queryset.filter(completed=True)
        elif completed_filter == 'false':
            queryset = queryset.filter(completed=False)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = TaskForm() # Add an empty form for creation
        return context

    # Override the get method to handle AJAX requests for filtering  ///TALVEZ RANCAR ISSO
    def get(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            self.object_list = self.get_queryset() # Get the filtered queryset
            context = self.get_context_data() # Get context, which will include filtered tasks
            return render(request, 'tasks/_task_list_items.html', context)
        return super().get(request, *args, **kwargs)

class TaskCreateView(LoginRequiredMixin, View):
    # No contexto de HTTP, POST é usado para criar/enviar dados.
    # Outros métodos incluem GET (recuperar), PUT (atualizar completo), PATCH (atualizar parcial), DELETE (remover).
    # Para submissões de formulário HTML, POST é o padrão. Para AJAX, podemos usar outros métodos.
    def post(self, request, *args, **kwargs): # **kwargs: captura argumentos de palavras-chave adicionais da URL (ex: pk)
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            # 'x-requested-with': 'XMLHttpRequest' é um cabeçalho usado para identificar requisições AJAX.
            # Não é uma medida de segurança, mas um indicador para o servidor saber como responder.
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'task': {
                    'id': task.id,
                    'title': task.title,
                    'description': task.description,
                    'due_date': task.due_date.strftime('%Y-%m-%d') if task.due_date else None,
                    'completed': task.completed
                }})
            # 'tasks:task_list' é uma URL reversa. 'tasks' é o namespace do app e 'task_list' é o nome da URL.
            # redirect() instrui o navegador a ir para esta URL.
            return redirect('tasks:task_list')
        else:
            # Em caso de erro de validação (status 400 Bad Request é apropriado para erros do cliente)
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                errors = {field: form.errors[field][0] for field in form.errors} # Extrai o primeiro erro por campo
                return JsonResponse({'success': False, 'errors': errors}, status=400)
            # Para submissões de formulário não-AJAX com erros, re-renderiza a lista com o formulário e erros.
            # Apenas um 'return' é executado por requisição, dependendo das condições.
            return render(request, 'templates/tasks/task_list.html', { # Caminho do template corrigido
                'form': form,
                'tasks': Task.objects.filter(user=request.user).order_by('completed', 'due_date', 'created_at') # Garante a ordenação
            })

class TaskUpdateView(LoginRequiredMixin, View):
    # Embora PUT seja semanticamente ideal para atualizações RESTful, formulários HTML só suportam GET/POST.
    # Usamos POST aqui para simplicidade, tanto para AJAX quanto para formulários HTML.
    def post(self, request, pk, *args, **kwargs):
        task = get_object_or_404(Task, pk=pk, user=request.user) # Garante que a tarefa pertence ao usuário logado
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save()
            # 'x-requested-with': 'XMLHttpRequest' é um cabeçalho usado para identificar requisições AJAX. Não é segurança.
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'task': {
                    'id': task.id,
                    'title': task.title,
                    'description': task.description,
                    'due_date': task.due_date.strftime('%Y-%m-%d') if task.due_date else None,
                    'completed': task.completed
                }})
            return redirect('tasks:task_list')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                errors = {field: form.errors[field][0] for field in form.errors}
                return JsonResponse({'success': False, 'errors': errors}, status=400)
            return redirect('tasks:task_list')

class TaskDeleteView(LoginRequiredMixin, View):
    # Usamos POST para simplicidade para botões de exclusão AJAX e não-AJAX.
    def post(self, request, pk, *args, **kwargs):
        task = get_object_or_404(Task, pk=pk, user=request.user) # Garante que a tarefa pertence ao usuário logado
        task.delete()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        return redirect('tasks:task_list')
