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
        self.user.save()
        self.token = Token.objects.create(user=self.user)
        self.token.save()

    # TEST USER CREATION

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

    # TEST GET TOKEN

    def test_token_authentication(self):
        url = reverse('get_token')
        data = {
            'username': 'testuser',
            'password': 'testpassword'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertNotEqual(response.data['token'], self.token.token)

    def test_token_authentication_invalid_credentials(self):
        url = reverse('get_token')
        data = {
            'username': 'testuser',
            'password': 'invalidpassword'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', response.data)

    def test_token_authentication_no_credentials(self):
        url = reverse('get_token')
        data = {}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', response.data)

    def test_token_authentication_invalid_data(self):
        url = reverse('get_token')
        data = {
            'username': 123,
            'password': 123
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', response.data)

    def test_token_authentication_invalid_username(self):
        url = reverse('get_token')
        data = {
            'username': 'invaliduser',
            'password': 'testpassword'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', response.data)

    # TEST CREATE_ENTRANCE_KEY
    
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
    
    def test_create_entrance_key_no_uses_or_expiration(self):
        url = reverse('create_entrance_key')
        data = {}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(EntranceKey.objects.count(), 1)
        self.assertEqual(EntranceKey.objects.first().uses_left, None)
        self.assertEqual(EntranceKey.objects.first().expires_at, None)

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

    # TEST GET USER DETAILS

    def test_get_user_details(self):
        url = reverse('user_details', args=[self.user.id])
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@example.com')
        self.assertEqual(response.data['username'], 'testuser')

    def test_get_user_details_no_token(self):
        url = reverse('user_details', args=[self.user.id]) 
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_details_invalid_token(self):
        url = reverse('user_details', args=[self.user.id]) 
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + 'invalidtoken')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_details_invalid_user_id(self):
        url = reverse('user_details', args=["123"]) 
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_user_is_not_owner(self):
        user2 = User.objects.create_user(
            email='test2@example.com',
            username='testuser2',
            password='testpassword'
        )
        token = Token.objects.create(user=user2)
        id2 = user2.id

        url = reverse('user_details', args=[self.user.id])
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_user_not_active(self):
        self.user.is_active = False
        self.user.save()

        url = reverse('user_details', args=[self.user.id]) 
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_token_not_active(self):
        self.token.is_active = False
        self.token.save()

        url = reverse('user_details', args=[self.user.id]) 
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # TEST USER META DATA

    def test_get_user_meta_data(self):
        url = reverse('user_meta_data', args=[self.user.id]) 
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, None)

    def test_get_user_meta_data_no_token(self):
        url = reverse('user_meta_data', args=[self.user.id]) 
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_meta_data_invalid_token(self):
        url = reverse('user_meta_data', args=[self.user.id]) 
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + 'invalidtoken')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_meta_data_invalid_user_id(self):
        url = reverse('user_meta_data', args=["123"]) 
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_user_meta_data_is_not_owner(self):
        user2 = User.objects.create_user(
            email='test2@example.com',
            username='testuser2',
            password='testpassword'
        )
        token = Token.objects.create(user=user2)
        id2 = user2.id

        url = reverse('user_meta_data', args=[self.user.id])
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_user_meta_data_not_active(self):
        self.user.is_active = False
        self.user.save()

        url = reverse('user_meta_data', args=[self.user.id]) 
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_set_user_meta_data(self):
        url = reverse('user_meta_data', args=[self.user.id]) 
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.token)
        data = {
            'key': 'value'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['key'], 'value')

    def test_set_user_meta_data_no_token(self):
        url = reverse('user_meta_data', args=[self.user.id]) 
        data = {
            'key': 'value'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_set_user_meta_data_invalid_token(self):
        url = reverse('user_meta_data', args=[self.user.id]) 
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + 'invalidtoken')
        data = {
            'key': 'value'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_set_user_meta_data_invalid_user_id(self):
        url = reverse('user_meta_data', args=["123"]) 
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.token)
        data = {
            'key': 'value'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_set_user_meta_data_is_not_owner(self):
        user2 = User.objects.create_user(
            email='test2@example.com',
            username='testuser2',
            password='testpassword'
        )
        token = Token.objects.create(user=user2)
        id2 = user2.id

        url = reverse('user_meta_data', args=[self.user.id])
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.token)
        data = {
            'key': 'value'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_set_user_meta_data_not_active(self):
        self.user.is_active = False
        self.user.save()

        url = reverse('user_meta_data', args=[self.user.id])
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.token)
        data = {
            'key': 'value'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    

