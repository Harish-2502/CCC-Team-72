import json
import requests
import io
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
    user=config('GITHUB_USERNAME')
    pao=config('GITHUB_TOKEN')
    github_session = requests.Session()
    github_session.auth = (user, pao)
    csv_url = 'https://raw.githubusercontent.com/Harish-2502/CCC-Team-72/master/data/response/abs_regional_population_lga_2001_2021.csv'
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
    columns = [' lga_code_2021', ' lga_name_2021', ' state_code_2021', ' state_name_2021', ' area_km2', ' erp_2001', ' erp_2002', ' erp_2003', ' erp_2004', ' erp_2005', ' erp_2006', ' erp_2007', ' erp_2008', ' erp_2009', ' erp_2010', ' erp_2011', ' erp_2012', ' erp_2013', ' erp_2014', ' erp_2015', ' erp_2016', ' erp_2017', ' erp_2018', ' erp_2019', ' erp_2020', ' erp_2021']
    final_data = pd.DataFrame(data, columns=columns)
    data = data.to_dict(orient='records')
    INDEX_NAME = "abs-regional_population_lga_2001-2021"
    initial_time = time.time()
    index_documents(data, INDEX_NAME, es_client)
    print("Finished")
    finish_time = time.time()
    print('Documents indexed in {:f} seconds\n'.format(finish_time - initial_time))
    return "OK"  
