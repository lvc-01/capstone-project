import simplejson as json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
booking_table = os.getenv('BookingTable')

def toggle_unit_lock(booking_id, event):
    user_id = event['requestContext']['authorizer']['claims']['sub']
    booking_table = dynamodb.Table(booking_table)
    response = booking_table.get_item(Key={'BookingId': booking_id})
    
    if 'Item' not in response:
        raise Exception(f"Booking {booking_id} not found.")
    
    booking = response['Item']
    
    if user_id in [booking.get('UserID'), booking.get('AuthorizedUser')]:
        current_unlocked = booking.get('Unlocked', False)
        new_unlocked = not current_unlocked
        
        unit_response = booking_table.update_item(
            Key={'BookingId': booking_id},
            UpdateExpression="set #unlocked = :val",
            ExpressionAttributeNames={
                "#unlocked": "Unlocked"
            },
            ExpressionAttributeValues={
                ":val": new_unlocked
            },
            ReturnValues="UPDATED_NEW"
        )
        return {
            "message": f"Unit for booking {booking_id} has been {'unlocked' if new_unlocked else 'locked'}.",
            "updatedAttributes": unit_response.get('Attributes')
        }
    else:
        raise Exception("Unauthorized access. User is not allowed to toggle the unit's lock.")

def lambda_handler(event, context):
    booking_id = event['BookingId']
    
    try:
        result = toggle_unit_lock(booking_id, event)
        response = {
            "statusCode": 200,
            "headers": {},
            "body": json.dumps(result)
        }
        return response
    
    except Exception as err:
        print(f"Error: {err}")
        return {
            "statusCode": 403,
            "headers": {},
            "body": json.dumps({"message": str(err)})
        }