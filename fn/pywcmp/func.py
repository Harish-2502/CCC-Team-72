import io
import json
import logging

from fdk import response

def handler(ctx, data: io.BytesIO = None):
    try:
        counts = dict()
        logger = logging.getLogger()

        for word in data.getvalue().split():
            counts[word.decode('utf-8')]= (counts.get(word.decode('utf-8')) or 0) + 1

    except (Exception, ValueError) as ex:
        logging.getLogger().info('error: ' + str(ex))

    return response.Response(
        ctx, response_data=json.dumps(counts), headers={"Content-Type": "application/json"}
    )
