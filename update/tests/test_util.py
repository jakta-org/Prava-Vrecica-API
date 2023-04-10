from update.models import AI_regions
from django.core.files.uploadedfile import SimpleUploadedFile

DEFAULT_VERSION = '1.0.0'
DEFAULT_CONTENT = b'test'
# create a test instance of the model
def create_ai_test_model(self, version=DEFAULT_VERSION, content=DEFAULT_CONTENT):
    file = SimpleUploadedFile(f'{version}.txt', content)
 
    obj = AI_regions(version=version, file=file) 
    obj.save()
    return obj