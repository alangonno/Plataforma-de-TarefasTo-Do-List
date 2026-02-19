from django.test import TestCase
from apps.tasks.forms import TaskForm
from datetime import date, timedelta

class TaskFormTest(TestCase):
    def test_task_form_valid(self):
        form_data = {
            'title': 'Test Form Task',
            'description': 'Description for form task',
            'due_date': date.today(),
            'completed': False
        }
        form = TaskForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_task_form_invalid_due_date_past(self):
        yesterday = date.today() - timedelta(days=1)
        form_data = {
            'title': 'Task with Past Date',
            'due_date': yesterday
        }
        form = TaskForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('due_date', form.errors)
        self.assertEqual(form.errors['due_date'], ['A data de vencimento não pode ser no passado.'])

    def test_task_form_missing_title(self):
        form_data = {
            'title': '',
            'description': 'Description without title'
        }
        form = TaskForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
        self.assertEqual(form.errors['title'], ['Este campo é obrigatório.'])

    def test_task_form_optional_fields(self):
        form_data = {
            'title': 'Only Title Task'
        }
        form = TaskForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data.get('description'), '')
        self.assertIsNone(form.cleaned_data.get('due_date'))
        self.assertFalse(form.cleaned_data.get('completed'))
