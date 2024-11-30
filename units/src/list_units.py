import simplejson as json
import os
import boto3
from boto3.dynamodb.conditions import *

units_table = os.getenv('TABLE_NAME')
dynamodb = boto3.resource('dynamodb')


def list_units(event):
    user_id = event['requestContext']['authorizer']['claims']['sub']

    table = dynamodb.Table(units_table)
    response = table.query(KeyConditionExpression=Key('userId').eq(user_id))
    user_units = [item['data'] for item in response['Items']]

    return user_units


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