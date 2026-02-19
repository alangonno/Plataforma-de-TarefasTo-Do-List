from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.users.forms import UserRegistrationForm

User = get_user_model()

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

        response = self.client.post(self.logout_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, self.home_url)
        self.assertFalse(response.context['user'].is_authenticated)
        self.assertIsNone(self.client.session.get('_auth_user_id'))
