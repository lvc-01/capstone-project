import simplejson as json
from boto3.dynamodb.conditions import Key
import boto3
import os

units_table = os.getenv('TABLE_NAME')
dynamodb = boto3.resource('dynamodb')

def get_order(user_id, unit_id):
    table = dynamodb.Table(units_table)
    response = table.query(
        KeyConditionExpression=(Key('userId').eq(user_id) & Key('unitId').eq(unit_id))
    )
    
    user_units = []
    for item in response['Items']:
      user_units.append(item['data'])
      
    return user_units[0]

def lambda_handler(event, context):
    user_id = event['requestContext']['authorizer']['claims']['sub']
    unit_id = event['pathParameters']['unitId']

    try:
        units = get_order(user_id, unit_id)
        response = {
            "statusCode": 200,
            "headers": {},
            "body": json.dumps(units)
        }
        return response
    except Exception as err:
        raise