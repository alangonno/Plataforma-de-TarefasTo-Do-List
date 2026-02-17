from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from http import HTTPStatus
from .models import Task
from .forms import TaskForm

class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        # Garante que apenas as tarefas pertencentes ao usuário logado sejam retornadas.
        queryset = Task.objects.filter(user=self.request.user)
        completed_filter = self.request.GET.get('completed')
        if completed_filter == 'true':
            queryset = queryset.filter(completed=True)
        elif completed_filter == 'false':
            queryset = queryset.filter(completed=False)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = TaskForm() 
        return context

    def get(self, request, *args, **kwargs):
        # Sobreescreve o método get para lidar com requisições AJAX para filtro.
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            self.object_list = self.get_queryset()
            context = self.get_context_data()
            return render(request, 'tasks/_task_list_items.html', context)
        return super().get(request, *args, **kwargs)

class TaskCreateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest': #Headers AJAX
                return JsonResponse({'success': True, 'task': {
                    'id': task.id,
                    'title': task.title,
                    'description': task.description,
                    'due_date': task.due_date.strftime('%Y-%m-%d') if task.due_date else None,
                    'completed': task.completed
                }}, status=201)
            return redirect('tasks:task_list')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                errors = {field: form.errors[field][0] for field in form.errors} # Extrai o primeiro erro por campo
                return JsonResponse({'success': False, 'errors': errors}, status=400)
            return render(request, 'templates/tasks/task_list.html', {
                'form': form,
                'tasks': Task.objects.filter(user=request.user).order_by('completed', 'due_date', 'created_at')
            })

class TaskUpdateView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        task = get_object_or_404(Task, pk=pk, user=request.user) # Garante que a tarefa pertence ao usuário logado
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save()
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
    def post(self, request, pk, *args, **kwargs):
        task = get_object_or_404(Task, pk=pk, user=request.user) # Garante que a tarefa pertence ao usuário logado
        task.delete()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({}, status=HTTPStatus.NO_CONTENT)
        return redirect('tasks:task_list')