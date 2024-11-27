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

    # extract resource path and API method from the event object
    resource_path = event.get('resource', '')
    http_method = event.get('httpMethod', '')

    # log incoming request
    print(f"Resource Path: {resource_path}")
    print(f"API Method: {http_method}")

    # route based on resource path and API Method
    match resource_path:

        case '/v1/api/customer' if http_method == 'POST':
            return add_customer(event, context)

        case '/v1/api/customer/{customer_id}' if http_method == 'GET':
            return get_customer(event, context)

        case '/v1/api/payments' if http_method == 'POST':
            return process_payment(event, context)

        case _:
            lambda_resp = {}
            lambda_resp['statusCode'] = 404
            lambda_resp['body'] = json.dumps({'message': 'resource not found or method supported'})
            return lambda_resp


def add_customer(event, context):

    """
    process POST method on /v1/api/customer to add a new customer.
    """

    body = json.loads(event['body'])
    customer_id = body.get('customer_id', '').strip()
    customer_email = body.get('email', '').strip()
    api_resp = {}

    # sanitise params
    if not customer_id or not customer_email:
        api_resp['statusCode'] = 400
        api_resp['body'] = json.dumps({'message': f'customer_id and email fields are required'})
        return api_resp
    
    # store customer record in DynamoDB
    customer_record = {
        'customer_id': customer_id,
        'email': customer_email
    }

    try:
        dynamodb = boto3.resource('dynamodb')
        customer_table = dynamodb.Table('Customers')
        put_item_resp = customer_table.put_item(Item=customer_record)
        api_resp['statusCode'] = put_item_resp['ResponseMetadata']['HTTPStatusCode']
        api_resp['body'] = json.dumps({'message': f'{customer_id} added successfully'})
    except ClientError as e:
        api_resp['statusCode'] = 500
        api_resp['body'] = json.dumps({'message': f"Error occurred: {e.response['Error']['Message']}"})

    return api_resp


def get_customer(event, context):

    """
    process GET method on /v1/api/customer/{customer_id} to retrieve a customer record.
    """
    api_resp = {}
    customer_id = event.get('pathParameters', {}).get('customer_id', '').strip()

    print(f'customer_id: {customer_id}')

    if not customer_id:
        api_resp['statusCode'] = 400
        api_resp['body'] = json.dumps({'message': 'customer_id is required'})
        return api_resp

    try:
        dynamodb = boto3.resource('dynamodb')
        customer_table = dynamodb.Table('Customers')
        get_item_resp = customer_table.get_item(Key={'customer_id': customer_id})
        if 'Item' in get_item_resp:
            api_resp['statusCode'] = 200
            api_resp['body'] = json.dumps({
                'customer_id': get_item_resp['Item']['customer_id'],
                'email': get_item_resp['Item']['email']
            })
        else:
            api_resp['statusCode'] = 404
            api_resp['body'] = json.dumps({'message' : f'{customer_id} not in records'})
    except ClientError as e:
            api_resp['statusCode'] = 500
            api_resp['body'] = json.dumps({'message' : f"error occurred: {e.response['Error']['Message']}"})

    print(f'api_resp: {api_resp}')
    return api_resp

 
def process_payment(event, context):

    """
    process POST method on /v1/api/payments to process payment to a customer.
    """

    body = json.loads(event['body'])
    customer_id = body.get('customer_id', '')
    email = body.get('email', '')
    amount = body.get('amount', 0)
    currency = body.get('currency', 'USD')

    api_resp = {}
    if not customer_id or not email:
        api_resp['statusCode'] = 400
        api_resp['body'] = json.dumps({'message': 'customer_id and email required'})
        return api_resp

    dynamodb = boto3.resource('dynamodb')

    # lookup customer in records
    item_found = False
    try:
        customer_table = dynamodb.Table('Customers')
        get_item_resp = customer_table.get_item(Key={'customer_id': customer_id})
        item = get_item_resp.get('Item')
        if item is None or not isinstance(item, dict):
            api_resp['statusCode'] = 404
            api_resp['body'] = json.dumps({'message' : f'{customer_id} not in records'})
        elif item.get('email') != email:
            api_resp['statusCode'] = 400
            api_resp['body'] = json.dumps({'message' : f'user {email} not matched with {item.get('email')}'})
        else:
            item_found = True
    except ClientError as e:
        api_resp['statusCode'] = 500
        api_resp['body'] = json.dumps({'message' : f"error occurred: {e.response['Error']['Message']}"})

    if not item_found:
        return api_resp

    access_token = get_access_token()
    if access_token is None:
        print(f"failed to get PayPal API OAuth token")
        api_resp['statusCode'] = 500
        api_resp['body'] = json.dumps({'message' : 'error : failed to get PayPal API OAuth token'})
        return api_resp

    paypal_base_url = os.environ['PAYPAL_SANDBOX_URL']
    paypal_url = f'{paypal_base_url}/v1/payments/payment'
    paypal_req_headers = {}
    paypal_req_headers['Authorization'] = f'Bearer {access_token}'
    paypal_req_headers['Content-Type'] = 'application/json'
    paypal_req = {
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
    paypal_req['transactions'][0]['payee'] = {
        "email": email
    }

    paypal_resp = requests.post(paypal_url, json=paypal_req, headers=paypal_req_headers)

    if paypal_resp.status_code in [200, 201]:
        print('Payment Authorization created successfully.')
    else:
        print(f"Failed to process payment: status code = {paypal_resp.status_code}, message: {paypal_resp.text}")
        api_resp['statusCode'] = paypal_resp.status_code
        api_resp['body'] = json.dumps({'message' : f'error : payment failed for {customer_id} - {paypal_resp.text}'})
        return api_resp

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
        disbursement_table = dynamodb.Table('Disbursements')
        resp = disbursement_table.put_item(Item=payment_record)
        print(f"disbursement table put resp code: {resp['ResponseMetadata']['HTTPStatusCode']}")
        api_resp['statusCode'] = resp['ResponseMetadata']['HTTPStatusCode']
        api_resp['body'] = json.dumps({'message' : f'{customer_id} payment successful'})
    except ClientError as e:
        api_resp = {}
        api_resp['statusCode'] = 500
        api_resp['body'] = json.dumps({'message' : f"Error occurred: {e.response['Error']['Message']}"})

    return api_resp

# Get OAuth token from PayPal
def get_access_token():

    paypal_base_url = os.environ['PAYPAL_SANDBOX_URL']
    paypal_client_id = os.environ['PAYPAL_CLIENT_ID']
    paypal_secret = os.environ['PAYPAL_SECRET']
    paypal_url = f'{paypal_base_url}/v1/oauth2/token'

    paypal_req_headers = {}
    paypal_req_headers ['Accept'] = 'application/json'
    paypal_req_headers['Accept-Language'] = 'en_US'

    paypal_req_data = {}
    paypal_req_data['grant_type'] = 'client_credentials'

    response = requests.post(paypal_url, headers=paypal_req_headers,
        data=paypal_req_data,
        auth=(paypal_client_id, paypal_secret)
    )

    if response.status_code in [200, 201]:
        access_token = response.json()['access_token']
        return access_token
    else:
        print(f"Failed to get access token: {response.status_code} {response.text}")
        return None
