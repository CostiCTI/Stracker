import requests
import pprint as pp


URL = "http://localhost:8085/#/api/analysis/alert/list/?id=Stracker"
    
r = requests.get(url = URL)

print (r.text)