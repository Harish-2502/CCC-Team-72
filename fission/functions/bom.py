from flask import request
from flask import current_app
import requests
import logging

def main():
    current_app.logger.info(f'Received request: ${request.headers}')
    r = requests.get('http://reg.bom.gov.au/fwo/IDV60901/IDV60901.95936.json')
    current_app.logger.info(f'Status BOM request: {r.status_code}')
    return r.json()


