import requests, json

# post new entrance key
# url = 'http://127.0.0.1:8000/accounts/entrance-key/'
# url = 'https://karlo13.pythonanywhere.com/accounts/entrance-key/'

# data = {'expires_at': '2024-12-31T23:59:59Z', 'uses_left': 5}
# data = {'email': 'test@example.com', 'password': 'testpassword'}

# header = {'content-type': 'application/json'}
# response = requests.post(url, data=json.dumps(data), headers=header)
# print(response.status_code)
# print(response.content)

# test get token
url = 'http://127.0.0.1:8000/accounts/user/3'

data = {
    'username': 'testuser',
    'password': 'testpassword',
    'email': 'test@example.com'
}
header = {
    'content-type': 'application/json',
    'Authorization': 'Token c3adc59c4fe9477e955d7cc1cbb44fe1' 
}
# provide token b'{"token":"c3adc59c4fe9477e955d7cc1cbb44fe1"}'

response = requests.get(url, data=json.dumps(data), headers=header)

print(response.status_code)
print(response.content)







# code = response.json()['entrance_code']

# url = 'https://karlo13.pythonanywhere.com/accounts/user/'
# url = 'http://127.0.0.1:8000/accounts/user/'

# data = {'username': 'testuser', 'password': 'testpassword', 'email': 'test4@example.com', 'entrance_code': code}
# header = {'content-type': 'application/json'}
# response = requests.post(url, data=json.dumps(data), headers=header)

# print(response.status_code)
# print(response.content)
