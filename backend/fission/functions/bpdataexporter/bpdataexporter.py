import json
import requests
import time
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
    dataset = requests.get("https://data.melbourne.vic.gov.au/api/explore/v2.1/catalog/datasets/building-permits/exports/json?lang=en&timezone=Australia%2FSydney")
    json_data = dataset.json()
    json_data = pd.DataFrame(json_data)
    json_data = json_data[(json_data.issue_date <= json_data.commence_by_date) & (json_data.issue_date <= json_data.completed_by_date) & ((json_data.estimated_cost_of_works > 0))]
    return json_data

def main():
    es_client = Elasticsearch (
        'https://elasticsearch-master.elastic.svc.cluster.local:9200',
        verify_certs= False,
        ssl_show_warn= False,
        basic_auth=(config('ES_USERNAME'), config('ES_PASSWORD')))
    data = dataset()
    data = data.to_dict(orient='records')
    INDEX_NAME = "building-permits"
    initial_time = time.time()
    index_documents(data, INDEX_NAME, es_client)
    print("Finished")
    finish_time = time.time()
    print('Documents indexed in {:f} seconds\n'.format(finish_time - initial_time))
    return "OK"
