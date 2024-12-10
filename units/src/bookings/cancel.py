import simplejson as json
import os
import boto3

client = boto3.client('dynamodb')

def fetch_item(table, key):
    response = client.get_item(TableName=table, Key=key)
    return response.get('Item')

def update_unit_status(unit_id, status):
    return client.update_item(
        TableName='listUnits',
        Key={'UnitID': {'N': str(unit_id)}},
        UpdateExpression="set #Status = :Status",
        ExpressionAttributeNames={'#Status': 'Status'},
        ExpressionAttributeValues={':Status': {'S': status}}
    )

def delete_booking(booking_id):
    return client.delete_item(
        TableName='BookingTable',
        Key={'BookingId': {'N': str(booking_id)}}
    )

def lambda_handler(event, context):
    try:
        booking_details = json.loads(event['body'])
        booking_id = booking_details['BookingId']
        unit_id = booking_details['UnitID']
        
        booking = fetch_item('BookingTable', {'BookingId': {'N': str(booking_id)}})
        
        if not booking:
            return {
                "statusCode": 404,
                "body": json.dumps({"message": f"Booking with BookingId {booking_id} not found."})
            }

        owner_user_id = booking.get('UserID', {}).get('S', '')
        user_id = event['requestContext']['authorizer']['claims']['sub']

        if owner_user_id != user_id:
            return {
                "statusCode": 403,
                "body": json.dumps({"message": "Unauthorized access. Only the owner can cancel the booking."})
            }

        delete_data = delete_booking(booking_id)
        update_data = update_unit_status(unit_id, 'Cancelling')

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": f"Booking with BookingId {booking_id} has been successfully deleted and Unit {unit_id} status updated to Available.",
                "data": {"delete_data": delete_data, "update_data": update_data}
            })
        }
    
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }