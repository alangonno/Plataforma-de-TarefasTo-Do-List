from django.db import models
from django.conf import settings # Importar settings para referenciar o modelo User

class Task(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200, null=False, blank=False)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    completed = models.BooleanField(default=False)

    class Meta:
        ordering = ['completed', 'due_date', 'created_at']

    def __str__(self):
        return self.title