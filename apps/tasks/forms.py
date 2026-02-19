from django import forms
from django.core.exceptions import ValidationError
from datetime import date
from .models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date', 'completed']
        error_messages = {
            'title' : {
                'required' : 'Este campo é obrigatório.'
            }
        }
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_due_date(self):
        due_date = self.cleaned_data.get('due_date')
        if due_date and due_date < date.today():
            raise ValidationError('A data de vencimento não pode ser no passado.')
        return due_date
