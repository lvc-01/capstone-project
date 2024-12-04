import boto3
import json
import os
import logging
from status import *

units_table = os.getenv('StorageUnits')
bookings_table = os.getenv('Bookings')
dynamodb = boto3.resource('dynamodb')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


class BookingStatusError(Exception):
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.status_code = status_code


def check_booking_status_and_owner(user_id, unit_id):
    table = dynamodb.Table(bookings_table)
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

    table = dynamodb.Table(bookings_table)
    response = table.delete_item(
        Key={'userId': user_id, 'unitId': unit_id},
        ConditionExpression="(#data.#status = :current_status)",
        ExpressionAttributeNames={
            "#data": "data",
            "#status": "status"
        },
        ExpressionAttributeValues={
            ":current_status": booking_data['status']
        }
    )

    table = dynamodb.Table(units_table)
    unit_status = UnitStatus.CANCELLING
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
    
    logger.info(f"Booking for unit {unit_id} has been successfully deleted and unit status updated.")
    
    return {"message": f"Booking for unit {unit_id} successfully deleted and unit status updated."}


def lambda_handler(event, context):
    try:
        user_id = event['requestContext']['authorizer']['claims']['sub']
        unit_id = event['pathParameters']['unitId']
        
        result = cancel_booking(user_id, unit_id)
        
        response = {
            "statusCode": 200,
            "headers": {},
            "body": json.dumps(result)
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