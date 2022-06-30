import boto3
import json
import os
import logging


s3 = boto3.client('s3')
sns_client = boto3.client('sns')
logger = logging.getLogger('gradecalculator')
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    topic = os.environ.get('GRADE_CALCULATOR_TOPIC')
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    file_key = event['Records'][0]['s3']['object']['key']
    logger.info('Reading {} from {}'.format(file_key, bucket_name))
    obj = s3.get_object(Bucket=bucket_name, Key=file_key)
    file_content = obj['Body'].read().decode('utf-8')
    checkout_events = json.loads(file_content)
    for each_event in checkout_events:
        score = each_event['testScore']
        if score > 70:
            grade = 'A'
        elif score > 60:
            grade = 'B'
        else: grade = 'C'
        each_event['grade'] = grade
        logger.info('Message being published')
        logger.info(each_event)
        sns_client.publish(
            TopicArn=topic,
            Message=json.dumps({'default': json.dumps(each_event)}),
            MessageStructure='json'
        )