import logging, json, requests, socket
from flask import current_app
from aiokafka import AIOKafkaProducer
import asyncio

async def publish(payload):
    producer = AIOKafkaProducer(bootstrap_servers='my-cluster-kafka-bootstrap.kafka.svc:9092')
    await producer.start()
    try:
        await producer.send_and_wait('weather', payload)
        current_app.logger.info(f'Message sent')
    finally:
        current_app.logger.info(f'Cleanup')
        await producer.stop()

def main():
    current_app.logger.info(f'Started')
    r = requests.get('http://reg.bom.gov.au/fwo/IDV60901/IDV60901.95936.json')
    current_app.logger.info(f'Status BOM request: {r.status_code}')
    asyncio.run(publish(json.dumps(r.json()).encode('utf-8')))
    return 'OK'

