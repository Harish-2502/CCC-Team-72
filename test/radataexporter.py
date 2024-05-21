import json
import requests
import io
import time
import numpy as np
import pandas as pd
from elasticsearch8 import Elasticsearch
from elasticsearch8.helpers import bulk

def config(k):
    with open(f'/configs/default/shared-data/{k}', 'r') as f:
        return f.read()

def index_documents(json_data, index_name, es_client):
    actions = [
        {
            "_index": index_name,
            "_source": doc
        }
        for doc in json_data
    ]
    indexing = bulk(es_client, actions, index=index_name)
    print("Success - %s , Failed - %s" % (indexing[0], len(indexing[1])))
    return "OK"

def dataset():
    user=config('GITHUB_USERNAME')
    pao=config('GITHUB_TOKEN')
    github_session = requests.Session()
    github_session.auth = (user, pao)
    csv_url = 'https://raw.githubusercontent.com/Harish-2502/CCC-Team-72/master/data/response/rental_affordability.csv'
    download = github_session.get(csv_url).content
    downloaded_csv = pd.read_csv(io.StringIO(download.decode('utf-8')))
    return downloaded_csv

def main():
    es_client = Elasticsearch (
        'https://elasticsearch-master.elastic.svc.cluster.local:9200',
        verify_certs= False,
        ssl_show_warn= False,
        basic_auth=(config('ES_USERNAME'), config('ES_PASSWORD')))
    data = dataset()
    data = data.replace({np.nan: None})
    data = data.to_dict(orient='records')
    INDEX_NAME = "rental_affordability"
    initial_time = time.time()
    index_documents(data, INDEX_NAME, es_client)
    print("Finished")
    finish_time = time.time()
    print('Documents indexed in {:f} seconds\n'.format(finish_time - initial_time))
    return "OK"
