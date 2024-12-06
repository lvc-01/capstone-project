import simplejson as json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
booking_table = os.getenv('Bookings')

def remove_authorized_user(booking_id, event):
    table = dynamodb.Table(booking_table)

    response = table.update_item(
        Key={'bookingId': booking_id},
        UpdateExpression="set #authorizedUser = :user",
        ExpressionAttributeNames={
            "#authorizedUser": "authorizedUser"
        },
        ExpressionAttributeValues={
            ":user": '-'
        },
        ReturnValues="UPDATED_NEW"
    )
    
    return {
        "message": f"Removed authorized user from booking {booking_id}.",
        "updatedAttributes": response.get('Attributes')
    }


def lambda_handler(event, context):
    booking_id = event['pathParameters']['bookingId']

    try:
        result = remove_authorized_user(booking_id, event)
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
