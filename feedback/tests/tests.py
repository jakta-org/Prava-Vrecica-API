from django.urls import reverse
from rest_framework.test import APITestCase
from ..models import Feedback
from accounts.models import User, Token
from ..serializers import CreateFeedbackSerializer

import os, base64

# Create your tests here.
class FeedbackTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", 
            username='test_user', 
            password='test_password'
        )
        self.user.save()
        self.token = Token.objects.create(user=self.user)
        self.token.save()

    def tearDown(self) -> None:
        for feedback in Feedback.objects.all():
            feedback.delete()
        return super().tearDown()

    def test_creating_feedback(self):
        with open('test_image.png', 'rb') as f:
            image = f.read()
            image_base64 = base64.b64encode(image).decode('utf-8')

        data = {
            'message': 'test_message', 
            'objects_data': 'test_frames_data',
            'image': image_base64,
            'file_name': 'test_image.png',
            'user': self.user.id
        }

        serializer = CreateFeedbackSerializer(data=data)
        serializer.is_valid()
        serializer.save()

        self.assertEqual(Feedback.objects.count(), 1)
        self.assertEqual(Feedback.objects.get().message, 'test_message')
        self.assertEqual(Feedback.objects.get().objects_data, 'test_frames_data')
        self.assertEqual(Feedback.objects.get().user, self.user)
        self.assertEqual(Feedback.objects.get().image.read(), image)

    def test_feedback_deletion(self):
        with open('test_image.png', 'rb') as f:
            image = f.read()
            image_base64 = base64.b64encode(image).decode('utf-8')

        feedback = Feedback.objects.create(
            image=image_base64,
            objects_data={},
            user=self.user,
            is_trusted=True,
            message='Test message'
        )
        path = feedback.image.path
        feedback.delete()

        assert not os.path.isfile(path)

    def test_post_feedback(self):
        with open('test_image.png', 'rb') as f:
            image = f.read()
            image_base64 = base64.b64encode(image).decode('utf-8')

        data = {
            'message': 'test_message', 
            'objects_data': '{"data":"test_frames_data"}',
            'image': image_base64, 
            'file_name': 'test_image.png'
        }
        
        url = reverse('feedback')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.token)
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Feedback.objects.count(), 1)

        path = Feedback.objects.first().image.path
        self.assertTrue(os.path.isfile(path))
        
    def test_post_feedback_without_image(self):
        data = {
            'message': 'test_message', 
            'objects_data': '{"data":"test_frames_data"}'
        }
        
        url = reverse('feedback')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.token)
        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Feedback.objects.count(), 0)
    
    def test_post_feedback_without_message(self):
        with open('test_image.png', 'rb') as f:
            image = f.read()
            image_base64 = base64.b64encode(image).decode('utf-8')

        data = {
            'objects_data': '{"data":"test_frames_data"}',
            'image': image_base64, 
            'file_name': 'test_image.png'
        }
        # message is optional
        url = reverse('feedback')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.token)
        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Feedback.objects.count(), 1)
        self.assertEqual(Feedback.objects.get().message, None)

        path = Feedback.objects.first().image.path
        self.assertTrue(os.path.isfile(path))

    def test_post_feedback_without_objects_data(self):
        with open('test_image.png', 'rb') as f:
            image = f.read()
            image_base64 = base64.b64encode(image).decode('utf-8')

        data = {
            'message': 'test_message', 
            'image': image_base64, 
            'file_name': 'test_image.png'
        }
        
        url = reverse('feedback')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.token)
        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Feedback.objects.count(), 1)
        self.assertEqual(Feedback.objects.get().objects_data, None)

    def test_post_feedback_without_file_name(self):
        with open('test_image.png', 'rb') as f:
            image = f.read()
            image_base64 = base64.b64encode(image).decode('utf-8')

        data = {
            'message': 'test_message', 
            'objects_data': '{"data":"test_frames_data"}',
            'image': image_base64
        }
        
        url = reverse('feedback')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.token)
        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Feedback.objects.count(), 0)

    def test_post_feedback_extra_data(self):
        with open('test_image.png', 'rb') as f:
            image = f.read()
            image_base64 = base64.b64encode(image).decode('utf-8')

        data = {
            'message': 'test_message', 
            'objects_data': '{"data":"test_frames_data"}',
            'image': image_base64, 
            'file_name': 'test_image.png',
            'extra_data': 'test_extra_data'
        }
        
        url = reverse('feedback')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.token)
        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Feedback.objects.count(), 1)

        path = Feedback.objects.first().image.path
        self.assertTrue(os.path.isfile(path))

    def test_post_feedback_token_missing(self):
        with open('test_image.png', 'rb') as f:
            image = f.read()
            image_base64 = base64.b64encode(image).decode('utf-8')

        data = {
            'message': 'test_message', 
            'objects_data': '{"data":"test_frames_data"}',
            'image': image_base64, 
            'file_name': 'test_image.png'
        }
        
        url = reverse('feedback')
        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(Feedback.objects.count(), 0)

    def test_post_feedback_token_invalid(self):
        with open('test_image.png', 'rb') as f:
            image = f.read()
            image_base64 = base64.b64encode(image).decode('utf-8')

        data = {
            'message': 'test_message', 
            'objects_data': '{"data":"test_frames_data"}',
            'image': image_base64, 
            'file_name': 'test_image.png'
        }
        
        url = reverse('feedback')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + 'invalid_token')
        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(Feedback.objects.count(), 0)

    def test_post_feedback_token_expired(self):
        self.token.expires_at = '2020-01-01T00:00:00Z'
        self.token.save()

        with open('test_image.png', 'rb') as f:
            image = f.read()
            image_base64 = base64.b64encode(image).decode('utf-8')

        data = {
            'message': 'test_message', 
            'objects_data': '{"data":"test_frames_data"}',
            'image': image_base64, 
            'file_name': 'test_image.png'
        }
        
        url = reverse('feedback')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.token)
        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(Feedback.objects.count(), 0)

    def test_post_feedback_token_user_inactive(self):
        self.user.is_active = False
        self.user.save()

        with open('test_image.png', 'rb') as f:
            image = f.read()
            image_base64 = base64.b64encode(image).decode('utf-8')

        data = {
            'message': 'test_message', 
            'objects_data': '{"data":"test_frames_data"}',
            'image': image_base64, 
            'file_name': 'test_image.png'
        }
        
        url = reverse('feedback')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.token)
        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(Feedback.objects.count(), 0)

class GetFeedbackTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            username='test_user',
            password='test_password',
            is_active=True,
            is_staff=True,
        )
        self.user.save()
        self.token = Token.objects.create(user=self.user)
        self.token.save()

        with open('test_image.png', 'rb') as f:
            image = f.read()
        image_base64 = base64.b64encode(image).decode('utf-8')

        data = {
            'message': 'test_message', 
            'objects_data': '{"data":"test_frames_data"}',
            'image': image_base64, 
            'file_name': 'test_image.png',
            'user': self.user.id
        }

        serializer = CreateFeedbackSerializer(data=data)
        if serializer.is_valid():
            feedback = serializer.save(user=self.user)
    	
        data2 = {
            'message': 'test_message_2', 
            'objects_data': '{"data":"test_frames_data_2"}',
            'image': image_base64, 
            'file_name': 'test_image.png',
            'user': self.user.id
        }

        serializer = CreateFeedbackSerializer(data=data2)
        serializer.is_valid()
        serializer.save()

    def test_get_feedback(self):
        url = reverse('feedback')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.token)
        response = self.client.get(url)
        print(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_get_feedback_num(self):
        url = reverse('feedback')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.token)
        response = self.client.get(url, {'num': 1})
        print(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_get_feedback_since(self):
        url = reverse('feedback')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.token)
        response = self.client.get(url, {'since': '2020-01-01T00:00:00Z'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_get_feedback_num_and_since(self):
        url = reverse('feedback')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.token)
        response = self.client.get(url, {'num': 1, 'since': '2020-01-01T00:00:00Z'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_get_feedback_return_all(self):
        url = reverse('feedback')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.token)
        response = self.client.get(url, {'return_all': True})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_get_feedback_num_and_return_all(self):
        url = reverse('feedback')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.token)
        response = self.client.get(url, {'num': 1, 'return_all': True})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
