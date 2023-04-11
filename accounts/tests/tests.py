from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ..models import User, Token, EntranceKey
from django.utils import timezone

class CustomUserTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpassword'
        )
        Token.objects.create(user=self.user)

    def test_create_user(self):
        url = reverse('create_user')
        data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'newpassword'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(User.objects.get(username='newuser').email, 'newuser@example.com')

    def test_create_user_invalid_data(self):
        url = reverse('create_user')
        data = {
            'email': 'invalidemail',
            'username': '',
            'password': 'password'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
    
    def test_create_user_duplicate_email(self):
        url = reverse('create_user')
        data = {
            'email': 'test@example.com',
            'username':'testuser',
            'password':'testpassword'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)

    def test_token_authentication(self):
        url = reverse('get_token')
        data = {
            'username': 'testuser',
            'password': 'testpassword'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_token_authentication_invalid_credentials(self):
        url = reverse('get_token')
        data = {
            'username': 'testuser',
            'password': 'invalidpassword'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', response.data)

    # test entrance key creation
    def test_create_entrance_key(self):
        url = reverse('create_entrance_key')
        data = {
            'group_id': 1,
            'expires_at': '2021-05-01 00:00:00',
            'uses_left': 5
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(EntranceKey.objects.count(), 1)
        self.assertEqual(EntranceKey.objects.get(group_id=1).uses_left, 5)

    # test entrance key creation with invalid data
    def test_create_entrance_key_invalid_data(self):
        url = reverse('create_entrance_key')
        data = {
            'group_id': 1,
            'expires_at': '2021-05-01 00:00:00',
            'uses_left': 'invalid'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(EntranceKey.objects.count(), 0)
    
    # test entrance key creation with no data (should default to unlimited uses and no expiration)
    def test_create_entrance_key_no_uses_or_expiration(self):
        url = reverse('create_entrance_key')
        data = {}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(EntranceKey.objects.count(), 1)
        self.assertEqual(EntranceKey.objects.first().uses_left, None)
        self.assertEqual(EntranceKey.objects.first().expires_at, None)

    # test create user with entrance code
    def test_create_user_with_entrance_code(self):
        # create entrance key
        url = reverse('create_entrance_key')
        date_tommorow = timezone.now() + timezone.timedelta(days=1)
        data = {
            'expires_at': date_tommorow,
            'uses_left': 5
        }
        response = self.client.post(url, data)

        code = response.data['entrance_code']

        url = reverse('create_user')
        data = {
            'email': 'test@gmail.com',
            'password': 'testpassword',
            'entrance_code': code
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(EntranceKey.objects.first().uses_left, 4)
        self.assertEqual(EntranceKey.objects.first().expires_at, date_tommorow)

    # test create user with entrance code that has expired
    def test_create_user_with_expired_entrance_code(self):
        # create entrance key
        url = reverse('create_entrance_key')
        date_yesterday = timezone.now() - timezone.timedelta(days=1)
        data = {
            'expires_at': date_yesterday,
            'uses_left': 5
        }
        response = self.client.post(url, data)

        code = response.data['entrance_code']

        url = reverse('create_user')
        data = {
            'email': 'test@gmail.com',
            'password': 'testpassword',
            'entrance_code': code
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(EntranceKey.objects.first().uses_left, 5)
        self.assertEqual(EntranceKey.objects.first().expires_at, date_yesterday)

    # test create user with entrance code that has no uses left
    def test_create_user_with_entrance_code_with_no_uses_left(self):
        # create entrance key
        url = reverse('create_entrance_key')
        date_tommorow = timezone.now() + timezone.timedelta(days=1)
        data = {
            'expires_at': date_tommorow,
            'uses_left': 0
        }
        response = self.client.post(url, data)

        code = response.data['entrance_code']

        url = reverse('create_user')
        data = {
            'email': 'test@gmail.com',
            'password': 'testpassword',
            'entrance_code': code
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(EntranceKey.objects.first().uses_left, 0)
        self.assertEqual(EntranceKey.objects.first().expires_at, date_tommorow)
    
    # test create user with entrance code but duplicate email
    def test_create_user_with_entrance_code_duplicate_email(self):
        # create entrance key
        url = reverse('create_entrance_key')
        date_tommorow = timezone.now() + timezone.timedelta(days=1)
        data = {
            'expires_at': date_tommorow,
            'uses_left': 5
        }
        response = self.client.post(url, data)

        code = response.data['entrance_code']

        url = reverse('create_user')
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'testpassword',
            'entrance_code': code
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(EntranceKey.objects.first().uses_left, 5)
        self.assertEqual(EntranceKey.objects.first().expires_at, date_tommorow)

