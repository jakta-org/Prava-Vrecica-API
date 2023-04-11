import requests, json

url = 'https://karlo13.pythonanywhere.com/accounts/user/'
url = 'http://127.0.0.1:8000/accounts/user/'

data = {'username': 'testuser', 'password': 'testpassword', 'email': 'test2@example.com'}
header = {'content-type': 'application/json'}
response = requests.post(url, data=json.dumps(data), headers=header)
print(response.status_code)
print(response.content)
