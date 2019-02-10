import boto3
import re
import logging
import objectname
import json


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def call(event, context):
    client = boto3.client('dynamodb', region_name='eu-central-1')
    paginator = client.get_paginator('scan')

    mydic = {}
    index = 0

    for page in paginator.paginate(
        TableName='my-transactions-table'):
        mydic[page.Items.transaction_id.S] = page.Items.body.S
        index += 1

    response = {
        "statusCode": 200,
        "body": json.dumps(mydic)
    }

    return response
