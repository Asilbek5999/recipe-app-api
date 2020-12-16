from django.test import TestCase
from django.contrib.auth import get_user_model
from  .. import models


def sample_user(email="asilbek@novalab.uz", password="12345"):
    """Create sample user"""
    return get_user_model().objects.create_user(email=email, password=password)


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Testing user creation with email successfully"""
        email = "asilbek.aliev.1999@gmail.com"
        password = "Qwerty12345"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_user_normalized_email(self):
        email = "asilbek@NOVALAB.UZ"
        password = "12345"

        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, email.lower())

    def test_user_invalid_email(self):
        """Test creating user with no  email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, '12345')

    def test_create_new_super_user(self):
        user = get_user_model().objects.create_superuser(
            'someemail@mail.ru',
            'password12345',
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """Test tag string representation"""
        tag= models.Tag.objects.create(
            user=sample_user(),
            name= "title"
        )
        self.assertEqual(str(tag), tag.name)
