import boto3
import os
import json
from decimal import Decimal
from uuid import uuid4
import logging
from status import UnitStatus

dynamodb = boto3.resource('dynamodb')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

booking_table = os.getenv('Bookings')
units_table = os.getenv('StorageUnits')

def check_double_booking(unit_id, start_date, end_date):
    table = dynamodb.Table(booking_table)
    response = table.query(
        KeyConditionExpression='unitId = :unitId',
        ExpressionAttributeValues={
            ':unitId': unit_id
        }
    )

    for item in response.get('Items', []):
        booked_start = item['data']['startDate']
        booked_end = item['data']['endDate']
        
        if (start_date < booked_end and end_date > booked_start):
            return True
    return False


def create_booking(unit_id, user_id, start_date, end_date, booking_id):
    ddb_item = {
        'BookingId': booking_id,
        'unitId': unit_id,
        'userId': user_id,
        'data': {
            # 'cost': cost,
            'status': UnitStatus.RESERVED,
            'startDate': start_date,
            'endDate': end_date,
            'billing': 'pre paid',
            'paymentMethod': 'card',
            'cancellationNotice': '3',
        }
    }
    ddb_item = json.loads(json.dumps(ddb_item), parse_float=Decimal)
    table = dynamodb.Table(booking_table)

    table.put_item(
        Item=ddb_item,
        ConditionExpression='attribute_not_exists(BookingId)'
    )


def book_unit(event):
    logger.info("Processing unit booking request")

    detail = json.loads(event['body'])
    logger.info({"operation": "book_unit", "booking_details": detail})

    user_id = event['requestContext']['authorizer']['claims']['sub']
    start_date = detail['startDate']
    end_date = detail['endDate']
    unit_id = detail['unitId']
    
    table = dynamodb.Table(units_table)
    response = table.get_item(Key={'unitId': unit_id})
    
    if 'Item' in response:
        unit_data = response['Item']
        current_status = unit_data['data']['status']
        
        if current_status != UnitStatus.AVAILABLE:
            raise Exception(f"Unit {unit_id} is not available. Current status: {current_status}")
    else:
        raise Exception(f"Unit {unit_id} does not exist.")
    
    if check_double_booking(unit_id, start_date, end_date):
        raise Exception(f"Unit {unit_id} is already booked for the selected dates.")

    booking_id = str(uuid4())

    create_booking(unit_id, user_id, start_date, end_date, booking_id)

    detail['unitId'] = unit_id
    detail['startDate'] = start_date
    detail['endDate'] = end_date
    detail['status'] = UnitStatus.RESERVED
    detail['BookingId'] = booking_id
    detail['billing'] = 'pre paid'
    detail['paymentMethod'] = 'card'
    detail['cancellationNotice'] = '3'

    logger.info(f"Unit {unit_id} has been successfully booked with BookingId {booking_id}.")

    return detail


def lambda_handler(event, context):
    try:
        booking_details = book_unit(event=event)
        response = {
            "statusCode": 200,
            "headers": {},
            "body": json.dumps(booking_details)
        }
        return response
    except Exception as err:
        response = {
            "statusCode": 400,
            "body": json.dumps({"error": str(err)})
        }
        return response