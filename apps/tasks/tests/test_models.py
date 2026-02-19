from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.tasks.models import Task
from datetime import date, timedelta

User = get_user_model()

class TaskModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', name='Test User', password='password123')

    def test_task_creation_minimal(self):
        task = Task.objects.create(user=self.user, title='Minimal Task')
        self.assertEqual(task.user, self.user)
        self.assertEqual(task.title, 'Minimal Task')
        self.assertIsNone(task.description)
        self.assertIsNone(task.due_date)
        self.assertFalse(task.completed)
        self.assertIsNotNone(task.created_at)

    def test_task_creation_all_fields(self):
        future_date = date.today() + timedelta(days=7)
        task = Task.objects.create(
            user=self.user,
            title='Full Task',
            description='This is a complete task description.',
            due_date=future_date,
            completed=True
        )
        self.assertEqual(task.user, self.user)
        self.assertEqual(task.title, 'Full Task')
        self.assertEqual(task.description, 'This is a complete task description.')
        self.assertEqual(task.due_date, future_date)
        self.assertTrue(task.completed)
        self.assertIsNotNone(task.created_at)

    def test_task_str_representation(self):
        task = Task.objects.create(user=self.user, title='Test Task Str')
        self.assertEqual(str(task), 'Test Task Str')

    def test_task_ordering(self):
        today = date.today()
        tomorrow = today + timedelta(days=1)
        yesterday = today - timedelta(days=1)

        # Usamos update para forçar created_at se necessário ou apenas criamos em ordem
        task3 = Task.objects.create(user=self.user, title='Task 3', completed=False, due_date=today)
        task1 = Task.objects.create(user=self.user, title='Task 1', completed=False, due_date=tomorrow)
        task5 = Task.objects.create(user=self.user, title='Task 5', completed=False, due_date=tomorrow)
        task2 = Task.objects.create(user=self.user, title='Task 2', completed=True, due_date=yesterday)
        task4 = Task.objects.create(user=self.user, title='Task 4', completed=True, due_date=tomorrow)

        tasks = list(Task.objects.filter(user=self.user))
        self.assertEqual(tasks[0], task3)
        self.assertEqual(tasks[1], task1)
        self.assertEqual(tasks[2], task5)
        self.assertEqual(tasks[3], task2)
        self.assertEqual(tasks[4], task4)
