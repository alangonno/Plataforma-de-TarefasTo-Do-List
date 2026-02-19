from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.users.forms import UserRegistrationForm

User = get_user_model()

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
