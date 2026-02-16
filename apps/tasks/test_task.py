from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.tasks.models import Task
import json

User = get_user_model()

class TaskCRUDAJAXTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(email='user1@example.com', name='User One', password='password123')
        self.user2 = User.objects.create_user(email='user2@example.com', name='User Two', password='password123')

        self.client.login(email='user1@example.com', password='password123')
        self.task1_user1 = Task.objects.create(user=self.user1, title='Task 1 User 1', description='Desc 1', completed=False)
        self.task2_user1 = Task.objects.create(user=self.user1, title='Task 2 User 1', description='Desc 2', completed=True)
        self.task_user2 = Task.objects.create(user=self.user2, title='Task User 2', description='Desc U2', completed=False)

    def test_task_list_view_authenticated(self):
        response = self.client.get(reverse('tasks:task_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Task 1 User 1')
        self.assertContains(response, 'Task 2 User 1')
        self.assertNotContains(response, 'Task User 2') # Should not see other user's task

    def test_task_list_view_filter_completed_true(self):
        response = self.client.get(reverse('tasks:task_list') + '?completed=true')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Task 2 User 1')
        self.assertNotContains(response, 'Task 1 User 1')

    def test_task_list_view_filter_completed_false(self):
        response = self.client.get(reverse('tasks:task_list') + '?completed=false')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Task 1 User 1')
        self.assertNotContains(response, 'Task 2 User 1')

    def test_task_create_ajax_success(self):
        response = self.client.post(reverse('tasks:task_create'),
                                    {'title': 'New Task AJAX', 'description': 'AJAX Description', 'completed': False},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(Task.objects.filter(user=self.user1).count(), 3)
        self.assertTrue(Task.objects.filter(title='New Task AJAX', user=self.user1).exists())

    def test_task_create_ajax_invalid(self):
        response = self.client.post(reverse('tasks:task_create'),
                                    {'title': '', 'description': 'AJAX Description'}, # Empty title
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertIn('title', data['errors'])
        self.assertEqual(Task.objects.filter(user=self.user1).count(), 2) # No new task created

    def test_task_update_ajax_success(self):
        response = self.client.post(reverse('tasks:task_update', args=[self.task1_user1.pk]),
                                    {'title': 'Updated Title', 'description': 'Updated Desc', 'completed': True},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.task1_user1.refresh_from_db()
        self.assertEqual(self.task1_user1.title, 'Updated Title')
        self.assertTrue(self.task1_user1.completed)

    def test_task_update_ajax_invalid(self):
        response = self.client.post(reverse('tasks:task_update', args=[self.task1_user1.pk]),
                                    {'title': '', 'description': 'Updated Desc'}, # Empty title
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertIn('title', data['errors'])
        self.task1_user1.refresh_from_db()
        self.assertNotEqual(self.task1_user1.title, '') # Title should not be updated

    def test_task_update_other_user_task(self):
        response = self.client.post(reverse('tasks:task_update', args=[self.task_user2.pk]),
                                    {'title': 'Attempted Update', 'description': 'Attempted Desc'},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 404) # Should return 404 as task not found for user1
        self.task_user2.refresh_from_db()
        self.assertNotEqual(self.task_user2.title, 'Attempted Update') # Task should not be updated

    def test_task_delete_ajax_success(self):
        response = self.client.post(reverse('tasks:task_delete', args=[self.task1_user1.pk]),
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertFalse(Task.objects.filter(pk=self.task1_user1.pk).exists())
        self.assertEqual(Task.objects.filter(user=self.user1).count(), 1) # Only one task left for user1

    def test_task_delete_other_user_task(self):
        response = self.client.post(reverse('tasks:task_delete', args=[self.task_user2.pk]),
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 404) # Should return 404
        self.assertTrue(Task.objects.filter(pk=self.task_user2.pk).exists()) # Task should not be deleted

    def test_task_list_view_unauthenticated(self):
        self.client.logout()
        response = self.client.get(reverse('tasks:task_list'))
        self.assertEqual(response.status_code, 302) # Redirect to login

    def test_task_create_unauthenticated(self):
        self.client.logout()
        response = self.client.post(reverse('tasks:task_create'),
                                    {'title': 'New Task', 'description': 'Description'},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 302) # Redirect to login

    def test_task_update_unauthenticated(self):
        self.client.logout()
        response = self.client.post(reverse('tasks:task_update', args=[self.task1_user1.pk]),
                                    {'title': 'Updated Title', 'completed': True},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 302) # Redirect to login

    def test_task_delete_unauthenticated(self):
        self.client.logout()
        response = self.client.post(reverse('tasks:task_delete', args=[self.task1_user1.pk]),
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 302) # Redirect to login

