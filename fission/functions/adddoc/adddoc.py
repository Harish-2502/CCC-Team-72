import logging
import json
from flask import current_app
from elasticsearch8 import Elasticsearch

def main():
    client = Elasticsearch (
        'https://elasticsearch-master.elastic.svc.cluster.local:9200',
        verify_certs= False,
        basic_auth=('elastic', 'elastic')
    )

    return json.dumps(client.get(index='students', id='1').body)

