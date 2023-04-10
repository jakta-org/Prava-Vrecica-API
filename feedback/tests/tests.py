from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from ..models import Feedback, Object
import os

# Create your tests here.
class FeedbackTest(TestCase):
    def test_post_feedback(self):
        with open('test_image.jpg', 'rb') as f:
            image = f.read()

        data = {'user_id': 1, 
                'message': 'test_message', 
                'detected_object_id': 1,
                'correct_object_id': 1,
                'frames_data': 'test_frames_data',
                'image_data': image}
        response = self.client.post('/feedback/', data=data, format='json')
        self.assertEqual(response.status_code, 201)
        
        # test if image is in database
        self.assertEqual(Feedback.objects.count(), 1)

        # test if image is in folder
        path = Feedback.objects.first().image.path
        # check if file exists
        self.assertTrue(os.path.isfile(path))
        
    def test_get_(self):
        return
        response = self.client.get('/feedback/')
        self.assertEqual(response.status_code, 200)