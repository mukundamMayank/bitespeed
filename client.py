import requests

email=None
phoneNumber = '12345'

json_data = {}
json_data['email'] = email
json_data['phoneNumber'] = phoneNumber

response = requests.post('http://localhost:5000/identify', json = json_data).content
print(response)