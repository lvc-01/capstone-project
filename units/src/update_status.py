import simplejson as json
from boto3.dynamodb.conditions import Key
import boto3
import os
from status import *

dynamodb = boto3.resource('dynamodb')
units_table = os.getenv('StorageUnits')

def update_status(unit_id):
    table = dynamodb.Table(units_table)
    unit_status = UnitStatus.AVAILABLE
    table.update_item(
        Key={'unitId': unit_id},
        UpdateExpression="set #data.#status = :unit_status",
        ExpressionAttributeNames={
            "#data": "data",
            "#status": "status"
        },
        ExpressionAttributeValues={
            ":unit_status": unit_status
        },
    )
    
    return {"message": f"Booking for unit {unit_id} successfully deleted and unit status updated."}


def lambda_handler(event, context):
    unit_id = event['pathParameters']['unitId']

    try:
        units = update_status(unit_id)
        response = {
            "statusCode": 200,
            "headers": {},
            "body": json.dumps(units)
        }
        return response
    except Exception as err:
        raise