import requests
import pprint as pp

def get_sonar_data(project_name):

    metrics = ['ncloc', 'complexity', 'bugs', 'code_smells', 'comment_lines', 'classes', 'files', 'functions',
                'violations', 'major_violations', 'minor_violations', 'vulnerabilities', 'lines']

    comp = project_name
    mlist = ""
    for m in metrics:
        mlist = mlist + m + ","
    mlist = mlist[:-1]

    URL = "http://localhost:9000/api/measures/component?metricKeys=" + mlist + "&component=" + comp
    
    r = requests.get(url = URL)
    
    resp = r.json()
    if ('component' not in resp):
        return None

    metric_list = resp['component']['measures']
    data = {}
    for d in metric_list:
        data[d['metric']] = d['value']

    return data
