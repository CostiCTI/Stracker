import requests
import json
import time

#specify url
url = 'http://localhost:8085/api/analysis/alert/list?id=Stracker'

while (True):
    response = requests.get(url)
    print (response.text)

    al = (response.json())["alerts"]
    
    if len(al) > 0 and al[0]["alertType"] == "ANALYSIS_ENABLE":
        aid = al[0]["properties"][0]["property"]
        proj = al[0]["properties"][0]["value"]

        #specify url
        url2 = 'http://localhost:8085/api/analysis/configure'

        token = "my token"
        #http://ec2-54-158-148-180.compute-1.amazonaws.com:5000
        data = {
                "configurationUrl": "http://localhost:5000/projects",
                "projectAnalysisId": proj,
                "viewUrl": "http://localhost:5000/projects",
                "cards": [
                    {
                    "cardUrl": "http://localhost:5000/home",
                    "label": "card1",
                    "preferedHeight": 400,
                    "preferedWidth": 300
                    }
                ]
                }

        headers = {"Content-Type": "application/json", "data":json.dumps(data)}

        response = requests.put(url2, data=json.dumps(data), headers=headers)

        print ('***')
        print(response.text)
        print ('***')
    
    time.sleep(1)
    