import requests
import io


url = 'http://localhost:8000/update/ai_model/'
headers = {'Content-Type': 'multipart/form-data'}

#headers = {'Content-Type': 'multipart/form-data; boundary=MyBoundary'}
#data = '--MyBoundary\r\nContent-Disposition: form-data; name="version"\r\n\r\n1.0\r\n--MyBoundary\r\nContent-Disposition: form-data; name="ai_model"; filename="file.txt"\r\n\r\nFile contents\r\n--MyBoundary--'

version = '1.0.4'

# create a SimpleUploadedFile object
file = open(f"{version}.txt", 'rb')

url = '/update/ai_model/'

file_data = {'ai_model': file,
                'version': version}

headers = {'Content-Type': 'application/gzip'}
# Send the POST request and get the response
response = requests.post(url, data=file_data, headers=headers)
print(response.status_code)
print(response.content)

# from django.core.files.uploadedfile import SimpleUploadedFile
# from update.models import AI_regions
# file = SimpleUploadedFile("1.0.4.txt", b"Hallo Welt!")
# a = AI_regions(version="1.0.4", file=file)
# a.save()