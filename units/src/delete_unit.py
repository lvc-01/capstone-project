import simplejson as json
import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

# Initialize DynamoDB client
client = boto3.client('dynamodb')

# Lambda handler
def lambda_handler(event, context):
    try:
        # Extract data from the incoming event (e.g., API Gateway or another source)
        booking_details = json.loads(event['body'])  # Assuming the data is passed as JSON in the request body
        
        # Extract the UnitID from the event to delete the unit and associated bookings
        unit_id = booking_details['UnitID']  # Assuming the unit ID is provided to delete the unit and associated bookings

        # Step 1: Delete the unit from the listUnits table first
        delete_unit = client.delete_item(
            TableName='listUnits',
            Key={
                'UnitID': {'N': str(unit_id)}  # Use the UnitID from the event to delete the unit (as string for 'N')
            }
        )

        # Step 2: Scan the BookingTable to find all bookings with the given UnitID
        response = client.scan(
            TableName='BookingTable',
            FilterExpression="UnitID = :unit_id",  # Filter based on UnitID
            ExpressionAttributeValues={
                ':unit_id': {'N': str(unit_id)}  # Pass the unit ID as a number
            }
        )
        
        # If there are bookings for this unit, delete them
        deleted_bookings = []
        if response['Items']:
            for item in response['Items']:
                booking_id_in_db = item['BookingId']['N']
                # Now delete the associated booking using BookingId
                client.delete_item(
                    TableName='BookingTable',
                    Key={
                        'BookingId': {'N': booking_id_in_db}  # Use the BookingId to delete the booking (as string for 'N')
                    }
                )
                deleted_bookings.append(booking_id_in_db)

        # Prepare the response with CORS headers
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",  # Allow all origins or specify your frontend URL
                "Access-Control-Allow-Methods": "GET, OPTIONS",  # Allowed methods
                "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Api-Key",  # Allowed headers
                "Content-Type": "application/json"  # Set content type to JSON
            },
            "body": json.dumps({
                "message": f"Unit {unit_id} has been deleted and the associated booking(s) have been removed.",
# List of deleted BookingIds
            })
        }

    except ClientError as e:
        # Handle DynamoDB errors
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Error performing delete operation",
                "error": str(e)
            })
        }
    
    except Exception as err:
        # Handle any other errors that occur during the execution
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Api-Key",
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "error": str(err)
            })
        }