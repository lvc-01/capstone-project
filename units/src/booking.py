import boto3
import os
import json
from decimal import Decimal
from datetime import datetime
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.idempotency import (
    IdempotencyConfig, DynamoDBPersistenceLayer, idempotent_function
)
from aws_lambda_powertools import Logger, Metrics
from aws_lambda_powertools.metrics import MetricUnit
from status import UnitStatus

dynamodb = boto3.resource('dynamodb')
logger = Logger()
metrics = Metrics()

units_table = os.getenv('TABLE_NAME') ####### use the booking table 
idempotency_table = os.getenv('IDEMPOTENCY_TABLE_NAME')

persistence_layer = DynamoDBPersistenceLayer(table_name=idempotency_table)
idempotency_config = IdempotencyConfig(event_key_jmespath="powertools_json(body).unitId")


def check_double_booking(unit_id, start_date, end_date):
    table = dynamodb.Table(units_table)
    response = table.query(
        KeyConditionExpression='unitId = :unitId',
        ExpressionAttributeValues={
            ':unitId': unit_id
        }
    )

    for item in response.get('Items', []):
        booked_start = item['data']['startDate']
        booked_end = item['data']['endDate']
        
        if (start_date < booked_end and end_date > booked_start):  # Check if dates overlap
            return True
    return False


def create_unit_booking(unit_id, user_id, cost, start_date, end_date):
    ddb_item = {
        'unitId': unit_id,
        'userId': user_id,
        'data': {
            'cost': cost,
            'status': UnitStatus.RESERVED,
            'startDate': start_date,
            'endDate': end_date,
        }
    }
    ddb_item = json.loads(json.dumps(ddb_item), parse_float=Decimal)
    table = dynamodb.Table(units_table)

    table.put_item(
        Item=ddb_item,
        ConditionExpression='attribute_not_exists(unitId) AND attribute_not_exists(userId)'
    )


@idempotent_function(data_keyword_argument="event", config=idempotency_config, persistence_store=persistence_layer)
def book_unit(event):
    logger.info("Processing unit booking request")

    detail = json.loads(event['body'])
    logger.info({"operation": "book_unit", "booking_details": detail})

    cost = detail['cost']
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

    if check_double_booking(unit_id, start_date, end_date):
        raise Exception(f"Unit {unit_id} is already booked for the selected dates.")

    create_unit_booking(unit_id, user_id, cost, start_date, end_date)

    detail['unitId'] = unit_id
    detail['startDate'] = start_date
    detail['endDate'] = end_date
    detail['status'] = UnitStatus.RESERVED

    logger.info(f"Unit {unit_id} has been successfully booked.")
    
    metrics.add_metric(name="SuccessfulBooking", unit=MetricUnit.Count, value=1)
    metrics.add_metric(name="BookingTotal", unit=MetricUnit.Count, value=cost)

    return detail


@metrics.log_metrics  
@logger.inject_lambda_context
def lambda_handler(event, context: LambdaContext):
    idempotency_config.register_lambda_context(context)
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