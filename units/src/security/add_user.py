import simplejson as json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
booking_table = os.getenv('BookingTable')

def add_authorized_user(booking_id, event):
    try:
        user_id = event['requestContext']['authorizer']['claims']['sub']
        table = dynamodb.Table(booking_table)

        response = table.update_item(
            Key={'BookingId': booking_id},
            UpdateExpression="set #AuthorizedUser = :user",
            ExpressionAttributeNames={
                "#AuthorizedUser": "AuthorizedUser"
            },
            ExpressionAttributeValues={
                ":user": user_id
            },
            ReturnValues="UPDATED_NEW"
        )
        
        return {
            "message": f"Added authorized user {user_id} to booking {booking_id}.",
            "updatedAttributes": response.get('Attributes')
        }
    
    except Exception as e:
        print(f"Error updating booking for BookingId {booking_id}: {e}")
        raise


def lambda_handler(event, context):
    booking_id = event['BookingId']

    try:
        result = add_authorized_user(booking_id, event)

        response = {
            "statusCode": 200,
            "headers": {},
            "body": json.dumps(result)
        }
        return response
    
    except Exception as err:
        print(f"Error: {err}")
        return {
            "statusCode": 500,
            "headers": {},
            "body": json.dumps({"message": "Internal server error"})
        }