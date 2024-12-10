import json
import boto3

dynamodb = boto3.resource('dynamodb')
booking_table = dynamodb.Table('BookingTable')

def create_response(status_code, message, data=None):
    response = {
        'statusCode': status_code,
        'body': json.dumps({
            'message': message,
            'data': data if data else {}
        })
    }
    return response

def get_booking_by_booking_id(booking_id):
    try:
        response = booking_table.get_item(Key={'BookingId': booking_id})
        
        if 'Item' in response:
            return create_response(200, 'Booking found', response['Item'])
        
        return create_response(404, 'Booking not found')
    
    except Exception as e:
        return create_response(500, 'Error fetching booking', {'error': str(e)})

def lambda_handler(event, context):
    booking_id = event['BookingId']
    
    try:
        result = get_booking_by_booking_id(booking_id) 
        return result
    except Exception as err:
        return create_response(500, 'Error in lambda_handler', {'error': str(err)})