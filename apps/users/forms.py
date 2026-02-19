from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import User

class UserRegistrationForm(forms.ModelForm): # Agora herda de ModelForm
    password = forms.CharField(label="Senha", widget=forms.PasswordInput,
                               error_messages={'required': 'Este campo é obrigatório.'})
    password_confirm = forms.CharField(label="Confirme a Senha", widget=forms.PasswordInput,
                                       error_messages={'required': 'Este campo é obrigatório.'})

    class Meta:
        model = User
        fields = ('name', 'email')
        error_messages = {
            'name': {
                'required': 'Este campo é obrigatório.',
            },
            'email': {
                'required': 'Este campo é obrigatório.',
                'invalid': 'Insira um endereço de e-mail válido.',
            }
        } # Apenas os campos do modelo que queremos no formulário

    def clean_password_confirm(self):
        password = self.cleaned_data.get("password")
        password_confirm = self.cleaned_data.get("password_confirm")
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("As senhas não coincidem.")
        return password_confirm

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este e-mail já está em uso.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class UserAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="E-mail", max_length=254,
                                widget=forms.TextInput(attrs={'autofocus': True}),
                                error_messages={'required': 'Preencha este campo.',
                                                'invalid': 'Insira um endereço de e-mail válido.'})
    password = forms.CharField(label="Senha", widget=forms.PasswordInput,
                               error_messages={'required': 'Preencha este campo.'})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_messages['invalid_login'] = "Por favor, insira um e-mail e senha corretos."
        self.error_messages['inactive'] = "Esta conta está inativa."

