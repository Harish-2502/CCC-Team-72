import logging, json, requests, socket
from flask import current_app

def main():
    requests.post(url='http://router.fission/enqueue/weather',
        headers={'Content-Type': 'application/json'},
        data=json.dumps(requests.get('http://reg.bom.gov.au/fwo/IDV60901/IDV60901.95936.json').json())
    )
    return 'OK'

