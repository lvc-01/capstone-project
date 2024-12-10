import json
import boto3
import logging
from decimal import Decimal

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('BookingTable')  # Replace with your actual table name

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Custom JSON encoder for handling Decimal type in DynamoDB response
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)  # Convert Decimal to float
        return super(DecimalEncoder, self).default(obj)

def lambda_handler(event, context):
    # Get the UserID from the event (query string or body)
    user_id = event.get('UserID')  # Assuming UserID is passed in the query string or body
    
    if not user_id:
        logger.error("No UserID provided")
        return {
            'statusCode': 400,
            'body': json.dumps({"error": "UserID is required"})
        }

    try:
        # Query DynamoDB for bookings by UserID
        response = table.scan(
            FilterExpression="UserID = :user_id",
            ExpressionAttributeValues={
                ":user_id": user_id
            }
        )

        # Check if bookings are found
        if 'Items' in response and response['Items']:
            # Serialize the response using the custom Decimal encoder
            return {
                'statusCode': 200,
                'body': json.dumps({
                    "bookings": response['Items']
                }, cls=DecimalEncoder)  # Use custom encoder to handle Decimals
            }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps({
                    "message": "No bookings found for this user"
                })
            }
    
    except Exception as e:
        # Log the error and return a 500 status code
        logger.error(f"Error retrieving bookings: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                "error": "Failed to retrieve bookings",
                "details": str(e)
            })
        }
