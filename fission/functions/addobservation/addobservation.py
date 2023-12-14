import logging, json
from flask import current_app, request
from elasticsearch8 import Elasticsearch

def main():
    client = Elasticsearch (
        'https://elasticsearch-master.elastic.svc.cluster.local:9200',
        verify_certs= False,
        basic_auth=('elastic', 'elastic')
    )

    current_app.logger.info(f'Array of observations read')

    #return json.dumps(client.get(index='observations', id='1').body)
    for obs in request.get_json(force=True):
        res = client.index(
            index='observations',
            id=f'{obs["wmo"]}-{obs["local_date_time_full"]}',
            body=obs
        )
        current_app.logger.info(f'Observation added: {res["result"]}')

    return 'OK'

