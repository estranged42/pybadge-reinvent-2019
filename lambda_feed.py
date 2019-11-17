import os
import boto3
from datetime import date, datetime, timezone
import dateutil
import decimal
import json
import logging
import ptvsd
import decimal
import feedparser

region = "us-west-2"
ssm = boto3.client('ssm', region_name=region)
dynamodb = boto3.resource('dynamodb', region_name=region)
table = dynamodb.Table('aws_service_announcements')
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


def entry_exists(id):
    r = table.get_item(
        Key={ 'id': id},
        ConsistentRead=True,
        ProjectionExpression='id'
    )

    if 'Item' in r and r['Item']['id'] == id:
        return True
    
    return False


def store_entry(e):
    # Dates look like this: Tue, 12 Nov 2019 01:09:07 +0000
    pub_date = dateutil.parser.parse(e.published)
    pub_timestamp = pub_date.timestamp()
    item = {
        'id': e.id,
        'description': e.title,
        'pub_date': decimal.Decimal(pub_timestamp)
    }

    if entry_exists(e.id):
        return False

    try:
        table.put_item(Item=item)
        loginfo(f"Logged new announcement: {e.title}")
        return True
    except Exception as ex:
        msg = str(ex)
        loginfo(f"store_entry error: {msg}")
        loginfo(item)
        return None


def get_metadata(id):
    r = metadata.get_item(
        Key={ 'id': id},
        ConsistentRead=True
    )

    if 'Item' in r and r['Item']['id'] == id:
        return r['Item']['val']
    
    return False


def add_metadata(key, val):
    item = {
        'id': key,
        'val': val,
    }
    metadata.put_item(Item=item)


def update_metadata(key, val):
    if get_metadata(key):
        metadata.update_item(
            Key={'id': key},
            UpdateExpression="set val = :val",
            ExpressionAttributeValues={
                ':val': val
            },
            ReturnValues="UPDATED_NEW"
        )
    else:
        add_metadata(key, val)


def incriment_count(n):
    cur_count = get_metadata('announcement_count')
    if cur_count == False:
        add_metadata('announcement_count', 5)
    else:
        new_count = cur_count + n
        update_metadata('announcement_count', new_count)
        return new_count


def handler(event, context):
    new_item_count = 0
    d = feedparser.parse(feed_url)
    feed_title = d.feed.title
    num_items = len(d.entries)
    loginfo( f"'{feed_title}' has {num_items} entries.")
    most_recent_announcement = ""
    most_recent_timestamp = 0
    for e in d.entries:
        added = store_entry(e)
        if added:
            new_item_count = new_item_count + 1
        
        pub_date = dateutil.parser.parse(e.published)
        pub_timestamp = pub_date.timestamp()
        if pub_timestamp > most_recent_timestamp:
            most_recent_timestamp = pub_timestamp
            most_recent_announcement = e.title
    
    incriment_count(new_item_count)
    count = get_metadata('announcement_count')

    update_metadata('recent_announcement', most_recent_announcement)

    return {
        'num_added': new_item_count,
        'count': count,
        'most_recent': most_recent_announcement
    }
