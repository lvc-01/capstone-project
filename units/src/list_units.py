import simplejson as json
import os
import boto3
from boto3.dynamodb.conditions import *

units_table = os.getenv('StorageUnits')
dynamodb = boto3.resource('dynamodb')


def list_units(event):
    table = dynamodb.Table(units_table)
    response = table.scan()
    units = [item['data'] for item in response['Items']]
    return units


def lambda_handler(event, context):
    try:
        units = list_units(event)
        response = {
            "statusCode": 200,
            "headers": {},
            "body": json.dumps({
                "units": units
            })
        }
        return response
    except Exception as err:
        raise