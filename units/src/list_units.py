import simplejson as json
import os
import boto3
from boto3.dynamodb.conditions import *

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')

# Function to list units from the DynamoDB table
def list_units(event):
    table = dynamodb.Table('listUnits')
    response = table.scan()
    return response

def lambda_handler(event, context):
    try:
        # Fetch units from DynamoDB
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
                "units": units  # Data retrieved from DynamoDB
            })
        }

        return response
    except Exception as err:
        # Handle error and return a response with the error message
        response = {
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
        return response