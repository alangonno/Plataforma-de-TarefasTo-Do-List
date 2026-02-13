from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from apps.users.forms import UserRegistrationForm
from apps.users.models import CustomUserManager # Importe CustomUserManager para testar

User = get_user_model()

class UserModelTests(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            email="normal@example.com",
            name="Normal User",
            password="normalpassword"
        )
        self.assertEqual(user.email, "normal@example.com")
        self.assertTrue(user.check_password("normalpassword"))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertEqual(str(user), "Normal User")

    def test_create_user_no_email_raises_error(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", name="No Email", password="password")

    def test_create_superuser(self):
        superuser = User.objects.create_superuser(
            email="super@example.com",
            name="Super User",
            password="superpassword"
        )
        self.assertEqual(superuser.email, "super@example.com")
        self.assertTrue(superuser.check_password("superpassword"))
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)

    def test_create_superuser_is_staff_false_raises_error(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="fail@example.com",
                name="Fail User",
                password="password",
                is_staff=False # Forçando is_staff=False
            )

    def test_create_superuser_is_superuser_false_raises_error(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="fail2@example.com",
                name="Fail User2",
                password="password",
                is_superuser=False # Forçando is_superuser=False
            )

    def test_email_unique(self):
        User.objects.create_user(email="unique@example.com", name="User One", password="password1")
        with self.assertRaises(Exception): # Integridade do banco de dados deve levantar exceção
            User.objects.create_user(email="unique@example.com", name="User Two", password="password2")

    def test_user_manager_custom_create_user_method(self):
        # Testar o método _create_user diretamente via manager
        manager = CustomUserManager()
        manager.model = User # Atribuir o modelo ao manager
        user = manager._create_user(email="custom@example.com", password="password", name="Custom User")
        self.assertEqual(user.email, "custom@example.com")
        self.assertTrue(user.check_password("password"))

class UserFormTests(TestCase):
    def test_registration_form_valid(self):
        form_data = {
            'name': 'New User',
            'email': 'newuser@example.com',
            'password': 'password123',
            'password_confirm': 'password123'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertIsInstance(user, User)
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertTrue(user.check_password('password123'))

    def test_registration_form_email_exists(self):
        User.objects.create_user(email='existing@example.com', name='Existing User', password='password')
        form_data = {
            'name': 'Another User',
            'email': 'existing@example.com',
            'password': 'password123',
            'password_confirm': 'password123'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertIn('Este e-mail já está em uso.', form.errors['email'])

    def test_registration_form_passwords_dont_match(self):
        form_data = {
            'name': 'User Pass',
            'email': 'userpass@example.com',
            'password': 'password123',
            'password_confirm': 'differentpassword'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password_confirm', form.errors)
        self.assertIn('As senhas não coincidem.', form.errors['password_confirm'])

    def test_registration_form_required_fields(self):
        # Testar sem 'name'
        form_data = {
            'email': 'noname@example.com',
            'password': 'password123',
            'password_confirm': 'password123'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

        # Testar sem 'email'
        form_data = {
            'name': 'No Email',
            'password': 'password123',
            'password_confirm': 'password123'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

class UserViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('users:register')
        self.login_url = reverse('users:login')
        self.logout_url = reverse('users:logout')
        self.home_url = reverse('home')

        self.test_user_email = "test@example.com"
        self.test_user_name = "Test User"
        self.test_user_password = "securepassword123"
        self.user = User.objects.create_user(email=self.test_user_email, name=self.test_user_name, password=self.test_user_password)

    def test_register_page_get(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')
        self.assertIsInstance(response.context['form'], UserRegistrationForm)

    def test_register_successful_post(self):
        new_user_data = {
            'name': 'Registered User',
            'email': 'registered@example.com',
            'password': 'newpassword123',
            'password_confirm': 'newpassword123'
        }
        response = self.client.post(self.register_url, new_user_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, self.home_url)
        self.assertTrue(User.objects.filter(email='registered@example.com').exists())
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertEqual(response.context['user'].email, 'registered@example.com')

    def test_register_invalid_post(self):
        # Email já existente
        new_user_data = {
            'name': 'Existing Email User',
            'email': self.test_user_email,
            'password': 'invalidpassword',
            'password_confirm': 'invalidpassword'
        }
        response = self.client.post(self.register_url, new_user_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')
        self.assertFalse(response.context['form'].is_valid())
        self.assertIn('email', response.context['form'].errors)

        # Senhas não batem
        new_user_data = {
            'name': 'Mismatch User',
            'email': 'mismatch@example.com',
            'password': 'password123',
            'password_confirm': 'differentpassword'
        }
        response = self.client.post(self.register_url, new_user_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')
        self.assertFalse(response.context['form'].is_valid())
        self.assertIn('password_confirm', response.context['form'].errors)
        self.assertIn('As senhas não coincidem.', response.context['form'].errors['password_confirm'])

    def test_login_page_get(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')
        self.assertIn('form', response.context)

    def test_login_successful_post(self):
        login_data = {
            'username': self.test_user_email,
            'password': self.test_user_password
        }
        response = self.client.post(self.login_url, login_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, self.home_url)
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertEqual(response.context['user'].email, self.test_user_email)

    def test_login_invalid_post(self):
        login_data = {
            'username': self.test_user_email,
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')
        self.assertFalse(response.context['user'].is_authenticated)
        self.assertIn('form', response.context)
        self.assertFalse(response.context['form'].is_valid())
        self.assertIn('__all__', response.context['form'].errors)

    def test_redirect_authenticated_user_from_login_page(self):
        self.client.login(email=self.test_user_email, password=self.test_user_password)
        response = self.client.get(self.login_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, self.home_url)
        self.assertTrue(response.context['user'].is_authenticated)

    def test_logout_successful(self):
        self.client.login(email=self.test_user_email, password=self.test_user_password)
        self.assertTrue(self.client.session.get('_auth_user_id'))

        response = self.client.get(self.logout_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, self.home_url)
        self.assertFalse(response.context['user'].is_authenticated)
        self.assertIsNone(self.client.session.get('_auth_user_id'))
