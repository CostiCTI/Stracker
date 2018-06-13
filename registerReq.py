import requests
import json

#specify url
url = 'http://localhost:8085/api/analysis/register'

token = "my token"
#http://ec2-54-158-148-180.compute-1.amazonaws.com:5000
data = {
        "configurationURL": "http://localhost:5000",
        "description": "Stracker tool for measure",
        "name": "Stracker"
        }

headers = {"Content-Type": "application/json", "data":json.dumps(data)}

response = requests.put(url, data=json.dumps(data), headers=headers)

print ('***')
print(response.text)
print ('***')