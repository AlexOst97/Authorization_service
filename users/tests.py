from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from users.models import User
import random


class UserCreateAPIViewTestCase(APITestCase):
    def setUp(self):
        self.url = reverse("users:api-register")
        self.phone_number = "79991234567"
        self.data = {"phone_number": self.phone_number}

    def test_create_new_user(self):
        """Тест создания нового пользователя"""
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(phone_number=self.phone_number).exists())
        self.assertIn("Код подтверждения отправлен на номер", response.data["detail"])


class UserCheckAPIViewTestCase(APITestCase):
    def setUp(self):
        self.url = reverse("users:api-register-check")
        self.phone_number = "79991234567"
        self.authorization_code = str(random.randint(1000, 9999))
        self.user = User.objects.create(
            phone_number=self.phone_number,
            authorization_code=self.authorization_code,
            is_active=True,
        )

    def test_successful_authorization(self):
        """Тест успешной авторизации"""
        data = {
            "phone_number": self.phone_number,
            "authorization_code": self.authorization_code,
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Успешная авторизация номера", response.data["detail"])
        self.assertIn("tokens", response.data)

    def test_invalid_code(self):
        """Тест с неверным кодом подтверждения"""
        data = {"phone_number": self.phone_number, "authorization_code": "0000"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "Неверный код подтверждения")

    def test_missing_phone_or_code(self):
        """Тест с отсутствующим номером или кодом"""
        # Без номера
        response = self.client.post(
            self.url, {"authorization_code": self.authorization_code}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Без кода
        response = self.client.post(self.url, {"phone_number": self.phone_number})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invite_code_activation(self):
        """Тест активации инвайт-кода при авторизации"""
        inviter = User.objects.create(
            phone_number="79998887766", invite_code="ABCDEF", is_active=True
        )
        data = {
            "phone_number": self.phone_number,
            "authorization_code": self.authorization_code,
        }
        response = self.client.post(self.url, data)
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ProfileAPIViewTestCase(APITestCase):
    def setUp(self):
        self.url = reverse("users:api-profile")
        self.user = User.objects.create(
            phone_number="79991234567", is_active=True, invite_code="ABCDEF"
        )
        self.client.force_authenticate(user=self.user)

    def test_get_profile(self):
        """Тест получения профиля"""
        User.objects.create(
            phone_number="79991112233",
            vicarious_invite_code=self.user.invite_code,
            is_active=True,
        )

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["phone_number"], self.user.phone_number)
        self.assertEqual(response.data["invite_code"], self.user.invite_code)
        self.assertIn("79991112233", response.data["related_users"])

    def test_activate_vicarious_invite_code(self):
        """Тест активации чужого инвайт-кода"""
        inviter = User.objects.create(
            phone_number="79998887766", invite_code="GHIJKL", is_active=True
        )
        data = {"vicarious_invite_code": inviter.invite_code}
        response = self.client.post(self.url, data)
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.vicarious_invite_code, inviter.invite_code)

    def test_activate_invalid_invite_code(self):
        """Тест активации несуществующего инвайт-кода"""
        data = {"vicarious_invite_code": "INVALID"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "Указанный инвайт-код не существует")
