from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.users.models import CustomUserManager

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
                is_staff=False
            )

    def test_create_superuser_is_superuser_false_raises_error(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="fail2@example.com",
                name="Fail User2",
                password="password",
                is_superuser=False
            )

    def test_email_unique(self):
        User.objects.create_user(email="unique@example.com", name="User One", password="password1")
        with self.assertRaises(Exception):
            User.objects.create_user(email="unique@example.com", name="User Two", password="password2")

    def test_user_manager_custom_create_user_method(self):
        manager = CustomUserManager()
        manager.model = User
        user = manager._create_user(email="custom@example.com", password="password", name="Custom User")
        self.assertEqual(user.email, "custom@example.com")
        self.assertTrue(user.check_password("password"))
