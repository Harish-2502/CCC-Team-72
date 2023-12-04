import logging, json, requests, redis
from flask import current_app

def main():
    r = requests.get('http://reg.bom.gov.au/fwo/IDV60901/IDV60901.95936.json')
    current_app.logger.info(f'Status BOM request: {r.status_code}')

    rdb = redis.StrictRedis(host='redis-headless.ot-operators.svc.cluster.local')
    rdb.lpush('weather-bom-topic', json.dumps(r.json()))
    return 'OK'
