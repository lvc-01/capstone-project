import simplejson as json
from boto3.dynamodb.conditions import Key
import boto3
import os

units_table = os.getenv('StorageUnits')
dynamodb = boto3.resource('dynamodb')

def get_unit(unit_id):
    table = dynamodb.Table(units_table)
    response = table.query(
        KeyConditionExpression=(Key('unitId').eq(unit_id))
    )
    
    user_units = []
    for item in response['Items']:
      user_units.append(item['data'])
      
    return user_units[0]

def lambda_handler(event, context):
    unit_id = event['pathParameters']['unitId']

    try:
        units = get_unit(unit_id)
        response = {
            "statusCode": 200,
            "headers": {},
            "body": json.dumps(units)
        }
        return response
    except Exception as err:
        raise