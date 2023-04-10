import os
from django.core.files.uploadedfile import SimpleUploadedFile
import datetime
from ..models import AI_regions, Mapping_regions
from .test_util import create_ai_test_model
from .. import settings
from django.test import TestCase
import time
import gzip

# Create your tests here.
class AI_model_tests(TestCase):
    # set up the test
    def setUp(self):
        # create a test instance of the model
        print("New case started")
        self.obj1 = create_ai_test_model(self, '1.0.1')
        self.obj2 = create_ai_test_model(self, '1.0.2')
        self.obj3 = create_ai_test_model(self, '1.0.3')

    def tearDown(self) -> None:
        # delete all left files stored in database
        list_ = AI_regions.objects.all()
        for obj in list_:
            try:
                path = obj.file.path
                os.remove(path)
            except:
                time.sleep(0.1)
                os.remove(obj.file.path)
        return super().tearDown()
    
    def test_models_count(self):
        # test database count
        self.assertEqual(AI_regions.objects.count(), settings.MAX_FILES_STORED)

        # test if correct files are present in media folder, check len() content of directory
        self.assertEqual(len(os.listdir(settings.AI_MODELS_DIR)), settings.MAX_FILES_STORED)

    #@transaction.atomic
    def test_post(self):
        version = '1.0.4'
    
        # create a SimpleUploadedFile object
        file = SimpleUploadedFile(f"{version}.txt", b"text")

        url = '/update/ai_model/'

        file_data = {'ai_model': file,
                     'version': version}

        headers = {'Content-Type': 'application/gzip'}
        # Send the POST request and get the response
        response = self.client.post(url, data=file_data, headers=headers)

        self.assertEqual(response.status_code, 201)

        # assert if new file was created at ai_models folder
        self.assertTrue(os.path.exists(f'media/ai_models/{version}.txt'))

        # assert instance was created in the database
        self.assertTrue(AI_regions.objects.filter(version=version).exists())

    def test_post_bytecode(self):
        version = '1.0.4'
    
        with open('filename', 'rb') as f:
            contents = f.read()

        # Compress the contents using gzip
        compressed_contents = gzip.compress(contents)
        url = '/update/ai_model/'

        file_data = {'ai_model': compressed_contents,
                     'version': version}

        headers = {'Content-Type': 'application/gzip'}
        # Send the POST request and get the response
        response = self.client.post(url, data=file_data, headers=headers)

        self.assertEqual(response.status_code, 201)

        # assert if new file was created at ai_models folder
        self.assertTrue(os.path.exists(f'media/ai_models/{version}.txt'))

        # assert instance was created in the database
        self.assertTrue(AI_regions.objects.filter(version=version).exists())

    # test for getting the latest ai model
    def test_get(self):
        
        url = '/update/ai_model/'
        # Send the GET request and get the response
        response = self.client.get(url)

        # assert if the latest file was returned is same as latest file in the database
        response_file = response.content
        latest_AI_region = AI_regions.objects.latest('version')
        with latest_AI_region.file.open() as file:
            file_content = file.read()

        self.assertEqual(response_file, file_content)

        self.assertEqual(response.status_code, 200)

    # test for getting latest files (ai model and mapping regions) depending on the last update date
    def test_get_with_date_1(self):

        last_update_date = datetime.datetime(2022, 3, 1)
        url = '/update/ai_model/'
        # create a dictionary of headers
        headers = {'If-Modified-Since': last_update_date.strftime('%a, %d %b %Y %H:%M:%S GMT')}


        # Send the GET request and get the response
        response = self.client.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)

    # test for returning 304 if the latest file is newer than the last update date
    def test_get_with_date_2(self):
        
        # create a now datetime object wich is newer than the latest file in the database
        last_update_date = datetime.datetime.now() + datetime.timedelta(days=1)

        url = '/update/ai_model/'

        # create a dictionary of headers
        params = {'If-Modified-Since': last_update_date.strftime('%a, %d %b %Y %H:%M:%S GMT')}

        # Send the GET request and get the response
        response = self.client.get(url, params=params)

        # assert that the response is 304
        self.assertEqual(response.status_code, 304)

    def test_put(self):
        print("Put test depricated")
        return
        version = '1.0.3'
        content = b'put_test'
    
        # create a SimpleUploadedFile object
        file = open('example.txt', 'rb')

        url = '/update/ai_model/'

        conten_type = file

        # Send the PUT request and get the response
        headers = {'version': version,
                   'filename': f'{version}.txt',
                   'Content-Type': 'application/x-www-form-urlencoded',}
        
        response = self.client.put(url, {'ai_model': file}, format='multipart', **headers)

        print(response.content)
        # assert that the response is 201
        self.assertEqual(response.status_code, 201)

        # assert that the file was updated
        with open(f'media/ai_models/1.0.3.txt', 'rb') as file:
            file_content = file.read()
        
        self.assertEqual(file_content, content)

