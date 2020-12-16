from django.test import TestCase

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

CREATE_USER_URL = reverse("user:create")
TOKEN_URL = reverse("user:token")
ME_URL = reverse("user:me")


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the users API (public)"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating user with valid payload is successful"""
        payload = {
            "email": "test@londonappdev.com",
            "password": "testpass",
            "name": "Test name"
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload["password"]))
        self.assertNotIn("password", res.data)

    def test_user_exists(self):
        """Test creating existing user which fails"""
        payload = {"email": "test@londondev.com", "password": "testpass",
                   "name": "test"}
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test password length which should be more than 5 """
        payload = {"email": "test@londondev.com",
                   "password": "qw",
                   "name": "Test"}

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload["email"]).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test  that token created for the user"""
        payload = {"email": "test@londondev.com", "password": "testpass"}
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('token', res.data)

    def test_create_token_invalid_credentials(self):
        """Test  that token is not created if invalid credentails are given"""
        payload = {"email": "test@londondev.com", "password": "testpass"}
        create_user(email="test@londondev.com", password="qwerty")
        res = self.client.post(TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_create_token_no_user(self):
        payload = {"email": "test@londondev.com", "password": "testpass"}
        res = self.client.post(TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_create_token_missing_field(self):
        """Test that email and password required"""
        payload = {"email": "test@londondev.com", "password": ""}
        res = self.client.post(TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_retrieve_user_unauthorized(self):
        """Test that authentication is required for users"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    class PrivateUserApiTest(TestCase):
        """Test API request thar require authentication"""

        def setUp(self):
            self.user = create_user(
                email="asilbe@novalab.uz",
                password="testpass",
                name="name"
            )
            self.client = APIClient()
            self.client.force_authenticate(self.user)

        def test_retrieve_profile_success(self):
            """Test retrieving profile for logged in user"""
            res = self.client.get(ME_URL)
            self.assertEqual(res.status_code, status.HTTP_200_OK)
            self.assertEqual(res.data, {
                "name": self.user.name,
                "email": self.user.email
            })

        def test_post_method_not_allowed(self):
            """Test that POST is not allowed on the me url"""
            res = self.client.post(ME_URL)
            self.assertEqual(res.status_code,
                             status.HTTP_405_METHOD_NOT_ALLOWED)

        def test_update_user_profile(self):
            """Test updating user profile for authenticated user"""

            payload = {"name": "asilbek", "password": "new_password"}

            res = self.client.patch(ME_URL, payload)

            self.user.refresh_from_db()
            self.assertEqual(self.user.name, payload["name"])
            self.assertTrue(self.user.check_password(payload["password"]))
            self.assertEqual(res.status_code, status.HTTP_200_OK)
