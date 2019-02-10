import boto3
import re
import logging
import objectname


logger = logging.getLogger()
logger.setLevel(logging.INFO)

def read_file(s3_client, bucket, key):
    return s3_client.get_object(
        Bucket=bucket,
        Key=key
    )['Body'].read().decode('utf-8')

def move_object_to_processed(s3_client, original_bucket, original_key):
    new_key = re.sub("incoming\/", "processed/", original_key)
    target_key = objectname.get_target_obj_name(new_key)
    s3_client.copy_object(
        Bucket=original_bucket,
        Key=target_key,
        CopySource={'Bucket': original_bucket, 'Key': original_key}
    )
    s3_client.delete_object(Bucket=original_bucket, Key=original_key)

def call(event, context):
    s3_client = boto3.client('s3')
    record = event['Records'][0]
    bucket = record['s3']['bucket']['name']
    key = record['s3']['object']['key']

    logger.info('>> got event{}'.format(event))

    table = boto3.resource('dynamodb', region_name='eu-central-1').Table("my-transactions-table")
    txn_id = re.search("incoming\/transaction-(\d*).txt", key).group(1)
    table.put_item(
        Item={
            'transaction_id': txn_id,
            'body': read_file(s3_client, bucket, key)
        }
    )

    move_object_to_processed(s3_client, bucket, key)
