import simplejson as json
from boto3.dynamodb.conditions import Key
import boto3
import os

dynamodb = boto3.resource('dynamodb')
units_table = os.getenv('listUnits')

def update_status(unit_id):
    table = dynamodb.Table(units_table)
    table.update_item(
        Key={'unitId': unit_id},
        UpdateExpression="set #data.#status = :status_value",
        ExpressionAttributeNames={
            "#data": "data",
            "#status": "Status"
        },
        ExpressionAttributeValues={
            ":status_value": "Available"
        },
    )
    
    return {"message": f"Unit {unit_id} status updated to Available."}

def lambda_handler(event, context):
    unit_id = event['UnitId']

    try:
        units = update_status(unit_id)
        response = {
            "statusCode": 200,
            "headers": {},
            "body": json.dumps(units)
        }
        return response
    except Exception as err:
        return {
            "statusCode": 500,
            "body": json.dumps({
                'message': str(err)
            })
        }