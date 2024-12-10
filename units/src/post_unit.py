import json
import random
import boto3
import logging
from botocore.exceptions import ClientError
from decimal import Decimal

# Initialize logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
units_table = dynamodb.Table('listUnits')  # Make sure this is the correct table name

# Function to list units from DynamoDB
def list_units(event):
    try:
        # Scan the units table to retrieve all items (you could also use query if needed)
        response = units_table.scan()
        units = response.get('Items', [])
        return units
    except ClientError as e:
        logger.error(f"Error retrieving units: {e}")
        return []

# Custom JSON encoder to handle Decimal types
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            # Convert Decimal to float or int (depends on the precision needed)
            if obj % 1 == 0:
                return int(obj)  # If it's a whole number, convert to int
            return float(obj)  # Otherwise convert to float
        return super(DecimalEncoder, self).default(obj)

# Lambda function handler
def lambda_handler(event, context):
    logger.info(f"Received event: {json.dumps(event)}")

    # Generate random unit ID
    unit_id = random.randint(100, 999)

    # Get new data for price, status, and type from the event (fall back to defaults if not provided)
    price = event.get("Price", f"R{random.randint(100, 500)}")  # Default random price if not provided
    status = event.get("Status", 'Available')  # Default if not provided
    unit_type = event.get("Type", random.choice(['Locker', 'Double Garage', 'Single Garage']))  # Default if not provided

    # Log the extracted attributes
    logger.info(f"Unit data:  UnitID={unit_id}, Price={price}, Type={unit_type}")

    # Put item in unitsTable
    try:
        # Put the new unit into DynamoDB
        units_table.put_item(
            Item={
                'UnitID': unit_id,  # Corrected case to match DynamoDB table schema
                'Price': price,
                'Status': status,
                'Type': unit_type
            }
        )

        # After inserting, fetch all units
        units = list_units(event)

        # Return response with CORS headers
        response = {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",  # Allow all origins or specify your frontend URL
                "Access-Control-Allow-Methods": "GET, OPTIONS",  # Allowed methods
                "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Api-Key",  # Allowed headers
                "Content-Type": "application/json"  # Set content type to JSON
            },
            "body": json.dumps({
                "message": "Unit created successfully",
                "units": units  # Data retrieved from DynamoDB
            }, cls=DecimalEncoder)  # Use custom encoder to handle Decimal types
        }
        return response

    except ClientError as e:
        logger.error(f"Error creating unit: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Error creating unit',
                'error': str(e)
            })
        }
