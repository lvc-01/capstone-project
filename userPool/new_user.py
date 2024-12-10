import json
import boto3

# Initialize Cognito Identity Provider client
cognito_client = boto3.client('cognito-idp')

# Lambda function handler
def lambda_handler(event, context):
    # Extract user attributes from the event
    user_pool_id = event['userPoolId']
    username = event['userName']
    group_name = 'Users'  # The group you want to add the user to

    try:
        # Add the user to the Cognito group
        response = cognito_client.admin_add_user_to_group(
            UserPoolId=user_pool_id,
            Username=username,
            GroupName=group_name
        )

        # Log response for debugging
        print(f"User {username} added to group {group_name}.")

        # Return success response
        return event

    except Exception as e:
        # Log the error and raise it again to indicate failure
        print(f"Error adding user to group: {str(e)}")
        raise e
