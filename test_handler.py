import boto3
import pytest
from botocore.exceptions import ClientError
from moto import mock_s3
from moto import mock_dynamodb2
from handler import call

BUCKET = "some-bucket"
OBJECT_NAME = "transaction-0001.txt"
TARGET_OBJECT_NAME = "transaction-0001_processed.txt"
KEY = "incoming/" + OBJECT_NAME
INCOMING_KEY = "incoming/"
PROCESSED_KEY = "processed/"
BODY = "Hello World!"
TXNS_TABLE = "my-transactions-table"

## Test Setup Functions

from contextlib import contextmanager

@contextmanager
def do_test_setup():
    with mock_s3():
        with mock_dynamodb2():
            set_up_s3()
            set_up_dynamodb()
            yield

def set_up_s3():
    conn = boto3.resource('s3', region_name='eu-central-1')
    conn.create_bucket(Bucket=BUCKET)
    boto3.client('s3', region_name='eu-central-1').put_object(Bucket=BUCKET, Key=KEY, Body=BODY)

def set_up_dynamodb():
    client = boto3.client('dynamodb', region_name='eu-central-1')
    client.create_table(
        AttributeDefinitions=[
            {
                'AttributeName': 'transaction_id',
                'AttributeType': 'N'
            },
        ],
        KeySchema=[
            {
                'AttributeName': 'transaction_id',
                'KeyType': 'HASH'
            }
        ],
        TableName=TXNS_TABLE,
        ProvisionedThroughput={
            'ReadCapacityUnits': 1,
            'WriteCapacityUnits': 1
        }
    )

## Tests

def test_handler_moves_incoming_object_to_processed():
    with do_test_setup():
        # Run call with an event describing the file:
        call(s3_object_created_event(BUCKET, INCOMING_KEY + OBJECT_NAME), None)

        conn = boto3.resource('s3', region_name='eu-central-1')

        assert_object_doesnt_exist(conn, BUCKET, KEY)
        # Check that it exists in `processed/`
        obj = conn.Object(BUCKET, PROCESSED_KEY + TARGET_OBJECT_NAME).get()
        assert obj['Body'].read() == b'Hello World!'

def test_handler_adds_record_in_dynamo_db_about_object():
    with do_test_setup():
        call(s3_object_created_event(BUCKET, KEY), None)

        table = boto3.resource('dynamodb', region_name='eu-central-1').Table(TXNS_TABLE)
        item = table.get_item(Key={'transaction_id': '0001'})['Item']
        assert item['body'] == 'Hello World!'

## Helpers

def assert_object_doesnt_exist(conn, bucket_name, key):
    with pytest.raises(ClientError) as e_info:
        conn.Object(bucket_name, key).get()
        assert e_info.response['Error']['Code'] == 'NoSuchKey'

def s3_object_created_event(bucket_name, key):
    return {
      "Records": [
        {
          "eventVersion": "2.0",
          "eventTime": "1970-01-01T00:00:00.000Z",
          "requestParameters": {
            "sourceIPAddress": "127.0.0.1"
          },
          "s3": {
            "configurationId": "testConfigRule",
            "object": {
              "eTag": "0123456789abcdef0123456789abcdef",
              "sequencer": "0A1B2C3D4E5F678901",
              "key": key,
              "size": 1024
            },
            "bucket": {
              "arn": "bucketarn",
              "name": bucket_name,
              "ownerIdentity": {
                "principalId": "EXAMPLE"
              }
            },
            "s3SchemaVersion": "1.0"
          },
          "responseElements": {
            "x-amz-id-2": "EXAMPLE123/5678abcdefghijklambdaisawesome/mnopqrstuvwxyzABCDEFGH",
            "x-amz-request-id": "EXAMPLE123456789"
          },
          "awsRegion": "eu-central-1",
          "eventName": "ObjectCreated:Put",
          "userIdentity": {
            "principalId": "EXAMPLE"
          },
          "eventSource": "aws:s3"
        }
      ]
    }
