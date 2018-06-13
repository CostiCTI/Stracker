import requests
import json

#specify url
url = 'http://localhost:8085/api/analysis/configure'

token = "my token"
#http://ec2-54-158-148-180.compute-1.amazonaws.com:5000
data = {
  "cards": [
            {
            "cardUrl": "http://localhost:5000",
            "label": "http://localhost:5000",
            "preferedHeight": 300,
            "preferedWidth": 200
            }
        ],
        "configurationUrl": "http://localhost:5000",
        "projectAnalysisId": 0,
        "viewUrl": "http://localhost:5000"
        }

headers = {"Content-Type": "application/json", "data":json.dumps(data)}

response = requests.put(url, data=json.dumps(data), headers=headers)

print ('***')
print(response.text)
print ('***')