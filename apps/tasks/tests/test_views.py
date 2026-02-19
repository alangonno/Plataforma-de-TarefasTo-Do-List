from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.tasks.models import Task
from apps.tasks.forms import TaskForm
import json
from datetime import date, timedelta

User = get_user_model()

class TaskViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(email='viewuser1@example.com', name='View User One', password='password123')
        self.user2 = User.objects.create_user(email='viewuser2@example.com', name='View User Two', password='password123')
        self.client.login(email='viewuser1@example.com', password='password123')
        self.task1_user1 = Task.objects.create(user=self.user1, title='View Task 1 User 1', completed=False)
        self.task2_user1 = Task.objects.create(user=self.user1, title='View Task 2 User 1', completed=True)
        self.task_user2 = Task.objects.create(user=self.user2, title='View Task User 2', completed=False)

    def test_task_list_view_non_ajax_get_renders_template(self):
        response = self.client.get(reverse('tasks:task_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasks/task_list.html')
        self.assertIn('tasks', response.context)
        self.assertIn(self.task1_user1, response.context['tasks'])
        self.assertIn(self.task2_user1, response.context['tasks'])
        self.assertNotIn(self.task_user2, response.context['tasks'])

    def test_task_list_view_non_ajax_get_no_tasks(self):
        self.client.logout()
        user_no_tasks = User.objects.create_user(email='notasks@example.com', name='No Tasks User', password='password123')
        self.client.login(email='notasks@example.com', password='password123')
        response = self.client.get(reverse('tasks:task_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasks/task_list.html')
        self.assertQuerySetEqual(response.context['tasks'], [])
        self.assertContains(response, 'Nenhuma tarefa encontrada.')

    def test_task_list_view_ajax_get_no_filter(self):
        response = self.client.get(reverse('tasks:task_list'), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasks/_task_list_items.html')
        self.assertIn('tasks', response.context)
        self.assertIn(self.task1_user1, response.context['tasks'])
        self.assertIn(self.task2_user1, response.context['tasks'])
        self.assertNotIn(self.task_user2, response.context['tasks'])

    def test_task_list_view_ajax_get_filter_completed_true(self):
        response = self.client.get(reverse('tasks:task_list') + '?completed=true', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasks/_task_list_items.html')
        self.assertIn(self.task2_user1, response.context['tasks'])
        self.assertNotIn(self.task1_user1, response.context['tasks'])

    def test_task_list_view_ajax_get_filter_completed_false(self):
        response = self.client.get(reverse('tasks:task_list') + '?completed=false', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasks/_task_list_items.html')
        self.assertIn(self.task1_user1, response.context['tasks'])
        self.assertNotIn(self.task2_user1, response.context['tasks'])

    def test_task_create_non_ajax_success(self):
        initial_task_count = Task.objects.filter(user=self.user1).count()
        response = self.client.post(reverse('tasks:task_create'), {'title': 'New Non-AJAX Task', 'description': 'Desc', 'completed': False})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Task.objects.filter(user=self.user1).count(), initial_task_count + 1)

    def test_task_update_non_ajax_success(self):
        response = self.client.post(reverse('tasks:task_update', args=[self.task1_user1.pk]),
                                    {'title': 'Updated Non-AJAX Title', 'description': 'Updated Desc', 'completed': True})
        self.assertEqual(response.status_code, 302)
        self.task1_user1.refresh_from_db()
        self.assertEqual(self.task1_user1.title, 'Updated Non-AJAX Title')

    def test_task_update_non_existent_task(self):
        response = self.client.post(reverse('tasks:task_update', args=[9999]),
                                    {'title': 'Attempt Update', 'description': 'Desc'})
        self.assertEqual(response.status_code, 404)

    def test_task_update_other_user_task_non_ajax(self):
        # Mudamos de 403 para 404 (Isolamento Seguro)
        response = self.client.post(reverse('tasks:task_update', args=[self.task_user2.pk]),
                                    {'title': 'Attempt Update', 'description': 'Desc'})
        self.assertEqual(response.status_code, 404)

    def test_task_delete_non_ajax_success(self):
        initial_task_count = Task.objects.filter(user=self.user1).count()
        response = self.client.post(reverse('tasks:task_delete', args=[self.task1_user1.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Task.objects.filter(user=self.user1).count(), initial_task_count - 1)

    def test_task_delete_other_user_task_non_ajax(self):
        # Mudamos de 403 para 404 (Isolamento Seguro)
        response = self.client.post(reverse('tasks:task_delete', args=[self.task_user2.pk]))
        self.assertEqual(response.status_code, 404)


class TaskCRUDAJAXTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(email='user1@example.com', name='User One', password='password123')
        self.user2 = User.objects.create_user(email='user2@example.com', name='User Two', password='password123')
        self.client.login(email='user1@example.com', password='password123')
        self.task1_user1 = Task.objects.create(user=self.user1, title='Task 1 User 1', description='Desc 1', completed=False)
        self.task_user2 = Task.objects.create(user=self.user2, title='Task User 2', description='Desc U2', completed=False)

    def test_task_create_ajax_success(self):
        response = self.client.post(reverse('tasks:task_create'),
                                    {'title': 'New Task AJAX', 'description': 'AJAX Description', 'completed': False},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.content)
        self.assertTrue(data['success'])

    def test_task_create_ajax_invalid(self):
        response = self.client.post(reverse('tasks:task_create'),
                                    {'title': '', 'description': 'AJAX Description'},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data['success'])

    def test_task_update_ajax_success(self):
        response = self.client.post(reverse('tasks:task_update', args=[self.task1_user1.pk]),
                                    {'title': 'Updated Title', 'description': 'Updated Desc', 'completed': True},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])

    def test_task_update_other_user_task(self):
        # Mudamos de 403 para 404 (Isolamento Seguro)
        response = self.client.post(reverse('tasks:task_update', args=[self.task_user2.pk]),
                                    {'title': 'Attempted Update', 'description': 'Attempted Desc'},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 404)

    def test_task_delete_ajax_success(self):
        # Mudamos de 204 para 200 (Sucesso com corpo JSON para o AJAX)
        response = self.client.post(reverse('tasks:task_delete', args=[self.task1_user1.pk]),
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])

    def test_task_delete_other_user_task(self):
        # Mudamos de 403 para 404 (Isolamento Seguro)
        response = self.client.post(reverse('tasks:task_delete', args=[self.task_user2.pk]),
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 404)

    def test_task_unauthenticated_redirects(self):
        self.client.logout()
        urls = [
            reverse('tasks:task_list'),
            reverse('tasks:task_create'),
            reverse('tasks:task_update', args=[self.task1_user1.pk]),
            reverse('tasks:task_delete', args=[self.task1_user1.pk]),
        ]
        for url in urls:
            response = self.client.get(url) if 'list' in url else self.client.post(url)
            self.assertEqual(response.status_code, 302)
