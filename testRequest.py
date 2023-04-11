import requests, json

# post new entrance key
url = 'https://karlo13.pythonanywhere.com/accounts/entrance_key/'
url = 'http://127.0.0.1:8000/accounts/entrance-key/'

data = {'expires_at': '2024-12-31T23:59:59Z', 'uses_left': 5}
header = {'content-type': 'application/json'}
response = requests.post(url, data=json.dumps(data), headers=header)
print(response.status_code)
print(response.content)

code = response.json()['entrance_code']

url = 'https://karlo13.pythonanywhere.com/accounts/user/'
url = 'http://127.0.0.1:8000/accounts/user/'

data = {'username': 'testuser', 'password': 'testpassword', 'email': 'test4@example.com', 'entrance_code': code}
header = {'content-type': 'application/json'}
response = requests.post(url, data=json.dumps(data), headers=header)

print(response.status_code)
print(response.content)
