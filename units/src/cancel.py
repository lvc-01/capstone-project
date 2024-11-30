import boto3
import json
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools import Logger, Metrics
from aws_lambda_powertools.metrics import MetricUnit
from status import *
import os

units_table = os.getenv('TABLE_NAME')
dynamodb = boto3.resource('dynamodb')

logger = Logger()
metrics = Metrics()

class BookingStatusError(Exception):
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.status_code = status_code

def check_booking_status_and_owner(user_id, unit_id):
    table = dynamodb.Table(units_table)
    response = table.get_item(Key={'userId': user_id, 'unitId': unit_id})
    
    if 'Item' not in response:
        raise BookingStatusError(f"Booking for unit {unit_id} not found.")
    
    booking_data = response['Item']['data']
    booking_status = booking_data.get('status')

    if booking_status not in [UnitStatus.RESERVED, UnitStatus.PROBLEM]:
        raise BookingStatusError(f"Booking for unit {unit_id} cannot be canceled. Current status: {booking_status}")
    
    return booking_data

def cancel_booking(user_id, unit_id):
    booking_data = check_booking_status_and_owner(user_id, unit_id)

    table = dynamodb.Table(units_table)
    response = table.update_item(
        Key={'userId': user_id, 'unitId': unit_id},
        UpdateExpression="set #data.#status = :new_status",
        ConditionExpression="(#data.#status = :current_status)",
        ExpressionAttributeNames={
            "#data": "data",
            "#status": "status"
        },
        ExpressionAttributeValues={
            ":current_status": booking_data['status'],
            ":new_status": UnitStatus.CANCELLED
        },
        ReturnValues="ALL_NEW"
    )
    
    logger.info(f"Booking for unit {unit_id} has been successfully canceled.")
    metrics.add_metric(name="SuccessfulCancellation", unit=MetricUnit.Count, value=1)
    
    return response['Attributes']['data']

@metrics.log_metrics
@logger.inject_lambda_context
def lambda_handler(event, context: LambdaContext):
    try:
        user_id = event['requestContext']['authorizer']['claims']['sub']
        unit_id = event['pathParameters']['unitId']
        
        updated_booking = cancel_booking(user_id, unit_id)
        
        response = {
            "statusCode": 200,
            "headers": {},
            "body": json.dumps(updated_booking)
        }
        
        return response

    except BookingStatusError as e:
        return {
            "statusCode": e.status_code,
            "body": str(e)
        }
    except Exception as err:
        logger.error(f"Unexpected error: {str(err)}")
        raise