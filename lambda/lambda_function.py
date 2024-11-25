import json
import boto3
from botocore.exceptions import ClientError
import os
import requests
from datetime import datetime
from decimal import Decimal

def lambda_handler(event, context):
    """
    Lambda handler function to route based on resource paths and HTTP methods.
    """

    # Extract resource path and HTTP method from the event object
    resource_path = event.get('resource', '')
    http_method = event.get('httpMethod', '')

    # Log incoming request for debugging purposes
    print(f"Resource Path: {resource_path}")
    print(f"HTTP Method: {http_method}")

    # Route to the appropriate handler based on resource path and API Method
    match resource_path:

        case '/v1/api/customer' if http_method == 'POST':
            return add_customer(event, context)

        case '/v1/api/customer/{customer_id}' if http_method == 'GET':
            return get_customer(event, context)

        case '/v1/api/payments' if http_method == 'POST':
            return process_payment(event, context)

        case _:
            return {
                'statusCode': 404,
                'body': json.dumps({'message': 'Resource not found or method not allowed'})
            }


def add_customer(event, context):

    """
    Handle POST request to /v1/api/customer to add a new customer.
    """

    body = json.loads(event['body'])
    customer_id = body.get('customer_id', '').strip()
    customer_email = body.get('email', '').strip()

    # sanitise params
    if not customer_id or not customer_email:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': f'customer_id and email fields are required'})
        }
    
    # Store customer record in DynamoDB
    cust_record = {
        'customer_id': customer_id,
        'email': customer_email
    }

    try:
        dynamodb = boto3.resource('dynamodb')
        cust_table = dynamodb.Table('Customers')
        resp = cust_table.put_item(Item=cust_record)
        return {
            'statusCode': resp['ResponseMetadata']['HTTPStatusCode'],
            'body': json.dumps({'message': f'{customer_id} added successfully'})
        }

    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': f"Error occurred: {e.response['Error']['Message']}"})
        }


def get_customer(event, context):

    """
    Handle GET request to /v1/api/customer/{customer_id} to retrieve a customer by ID.
    """

    customer_id = event.get('pathParameters', {}).get('customer_id', '').strip()
    if not customer_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'customer_id is required'})
        }
   
    try:
        dynamodb = boto3.resource('dynamodb')
        cust_table = dynamodb.Table('Customers')
        resp = cust_table.get_item(Key={'customer_id': customer_id})

        if 'Item' not in resp:
            return {
                'statusCode': 404,
                'body': json.dumps({'message' : f'{customer_id} not in records'})
            }

        # customer is in records
        return {
            'statusCode': 200,
            'body': json.dumps({
                'customer_id': resp['Item']['customer_id'],
                'email': resp['Item']['email']
            })
        }

    except ClientError as e:
            return {
                'statusCode': 500,
                'body': json.dumps({'message' : f'error occurred: {e.response['Error']['Message']}'})
            }

 
def process_payment(event, context):

    """
    Handle POST request to /v1/api/payments to create a payment.
    """

    body = json.loads(event['body'])
    customer_id = body.get('customer_id', '')
    email = body.get('email', '')
    amount = body.get('amount', 0)
    currency = body.get('currency', 'USD')

    if not customer_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'customer_id is required'})
        }
   
    dynamodb = boto3.resource('dynamodb')

    # lookup customer in records
    try:
        cust_table = dynamodb.Table('Customers')
        resp = cust_table.get_item(Key={'customer_id': customer_id})
        if 'Item' not in resp:
            print(f'Customer {customer_id} not in records')
            return {
                'statusCode': 404,
                'body': json.dumps({'message' : f'{customer_id} not in records'})
            }

    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message' : f'error occurred: {e.response['Error']['Message']}'})
        }

    access_token = get_access_token()
    if access_token is None:
        print(f"failed to get PayPal API OAuth token")
        return {
            'statusCode': 500,
            'body': json.dumps({'message' : 'error : failed to get PayPal API OAuth token'})
        }

    paypal_url = os.environ['PAYPAL_SANDBOX_URL']
    url = f'{paypal_url}/v1/payments/payment'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    payment_data = {
        "intent": "authorize",
        "payer": {
            "payment_method": "paypal"
        },
        "transactions": [{
            "amount": {
                "total": Decimal(str(amount)),
                "currency": currency,
            },
            "description": "Test payment"
        }],

        "redirect_urls": {
            "return_url": "http://localhost:3000/return",  # Dummy URL
            "cancel_url": "http://localhost:3000/cancel"   # Dummy URL
        }

    }

    # Add payee (recipient) details
    payment_data['transactions'][0]['payee'] = {
        "email": email  # Specify the recipient's email address here
    }

    response = requests.post(url, json=payment_data, headers=headers)

    if response.status_code == 201:
        print('Payment Authorization created successfully.')
    else:
        print(f"Failed to create payment: status code: {response.status_code}, message: {response.text}")
        return {
            'statusCode': response.status_code,
            'body': json.dumps({'message' : f'error : payment failed for {customer_id} - {response.text}'})
        }

    # Store payment record in DynamoDB
    payment_record = {
        'customer_id': customer_id,
        'email': email,
        'payment_id': datetime.utcnow().isoformat() + "Z",
        'amount': str(amount),
        'payment_method': 'paypal',
        'status': 'Completed',
        'currency': currency,
        #'timestamp': str(context.aws_request_id)
    }

    try:
        disb_table = dynamodb.Table('Disbursements')
        resp = disb_table.put_item(Item=payment_record)
        print(f"Rajesham Debug: {resp['ResponseMetadata']['HTTPStatusCode']}")
        return {
            'statusCode': resp['ResponseMetadata']['HTTPStatusCode'],
            'body': json.dumps({'message' : f'{customer_id} payment successful'})
        }

    except ClientError as e:
        return jsonify({"error": f"Error occurred: {e.response['Error']['Message']}"}), 500


# Get OAuth token from PayPal
def get_access_token():

    paypal_url = os.environ['PAYPAL_SANDBOX_URL']
    paypal_client_id = os.environ['PAYPAL_CLIENT_ID']
    paypal_secret = os.environ['PAYPAL_SECRET']

    url = f'{paypal_url}/v1/oauth2/token'
    headers = {
        'Accept': 'application/json',
        'Accept-Language': 'en_US'
    }

    response = requests.post(
        url,
        headers=headers,
        data={'grant_type': 'client_credentials'},
        auth=(paypal_client_id, paypal_secret)
    )

    if response.status_code == 200:
        access_token = response.json()['access_token']
        return access_token
    else:
        print(f"Failed to get access token: {response.status_code} {response.text}")
        return None
