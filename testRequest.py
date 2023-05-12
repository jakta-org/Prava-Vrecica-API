import requests, json


url = 'http://127.0.0.1:8000/accounts/token/'
url = 'http://127.0.0.1:8000/accounts/group/'

data = {
    #'username': 'testuser',
    'password': '1234',
    'email': 'karlovrd@gmail.com',
    'type': 'test',
}
header = {
    'content-type': 'application/json',
    'Authorization': 'Token b0294294d4324ff59373e3696c09982c' 
}

# karlovrd@gmail.com - 7d67cc874c6d4bf4918ad2d07cbab989

response = requests.post(url, data=json.dumps(data), headers=header)

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
