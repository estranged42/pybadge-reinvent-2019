import os
import boto3
from datetime import date, datetime, timezone
import dateutil
import decimal
import json
import logging
import decimal
from boto3.dynamodb.conditions import Key, Attr

region = 'us-west-2'
dynamodb = boto3.resource('dynamodb', region_name=region)
table = dynamodb.Table('aws_service_announcements')
metadata = dynamodb.Table('aws_service_announcements_metadata')

id = '02151245eb573252ccb627450bac14e0cc0fa84b'

r = table.get_item(
    Key={'id': id},
    ConsistentRead=True,
    ProjectionExpression='id'
)

def entry_exists(id):
    r = table.get_item(
        Key={'id': id},
        ConsistentRead=True,
        ProjectionExpression='id'
    )

    if 'Item' in r and r['Item']['id'] == id:
        return True
    
    return False

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
    metadata.update_item(
        Key={'id': key},
        UpdateExpression="set val = :val",
        ExpressionAttributeValues={
            ':val': val
        },
        ReturnValues="UPDATED_NEW"
    )


def incriment_count(n):
    cur_count = get_metadata('announcement_count')
    if cur_count == False:
        add_metadata('announcement_count', 5)
    else:
        new_count = cur_count + n
        update_metadata('announcement_count', new_count)
        return new_count


def get_announcements_since(ts=0):
    response = table.scan()
    all_announcements = []
    for ann in response['Items']:
        if int(ann['pub_date']) > ts:
            all_announcements.append(ann)

    return all_announcements

# print( entry_exists(id) )

# print(incriment_count(5))

a = get_announcements_since(1575170000)
print( len(a) )

