import os
import boto3
from datetime import date, datetime, timezone
import dateutil
import decimal
import json
import logging
import ptvsd
import decimal

region = "us-west-2"
ssm = boto3.client('ssm', region_name=region)
dynamodb = boto3.resource('dynamodb', region_name=region)
metadata = dynamodb.Table('aws_service_announcements_metadata')

feed_url = 'https://aws.amazon.com/about-aws/whats-new/recent/feed/'

rootlogger = logging.getLogger()
rootlogger.setLevel(logging.INFO)

if os.getenv("AWS_SAM_LOCAL") or os.getenv("IS_LOCAL"):
    # Local Only Config
    rootlogger.setLevel(logging.INFO)
    if os.getenv("REMOTE_DEBUGGING") == 'true':
        logging.info("Activating Debugger")
        ptvsd.enable_attach(address=('0.0.0.0', 5678), redirect_output=True)
        ptvsd.wait_for_attach()
        logging.info("Debugger Connected")
else:
    # Regular AWS Config
    True


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()

    elif isinstance(obj, decimal.Decimal):
        if obj % 1 == 0:
            return int(obj)
        else:
            return float(obj)

    raise TypeError("Type %s not serializable" % type(obj))


def loginfo(obj):
    logging.info(json.dumps(obj, indent=2, default=json_serial))


def get_secure_parameter(p_name):
    try:
        response = ssm.get_parameter(Name=p_name, WithDecryption=True)
        v = response['Parameter']['Value']
        return v
    except Exception as ex:
        msg = str(ex)
        if "ParameterNotFound" in msg:
            return None
        else:
            raise ex


def get_metadata(id):
    r = metadata.get_item(
        Key={ 'id': id},
        ConsistentRead=True
    )

    if 'Item' in r and r['Item']['id'] == id:
        return r['Item']['val']
    
    return False


def handler(event, context):
    response = {
        'count': str(get_metadata('announcement_count')),
        'most_recent': str(get_metadata('recent_announcement'))
    }

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(response, indent=2, default=json_serial)
    }
