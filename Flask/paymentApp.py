import boto3
from botocore.exceptions import ClientError
from datetime import datetime
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import requests

# pip install python-dotenv
# Load environment variables from .env file
load_dotenv()

# Access environment variables using os.environ
paymentApp = Flask(__name__)

PAYPAL_CLIENT_ID   = os.getenv("PAYPAL_CLIENT_ID")
PAYPAL_SECRET      = os.getenv("PAYPAL_SECRET")
PAYPAL_SANDBOX_URL = os.getenv("PAYPAL_SANDBOX_URL")

# POST method to add a customer
@paymentApp.route('/v1/api/customer/add', methods=['POST'])
def add_customer():

    data = request.get_json()

    # sanitise params
    if not data or 'customer_id' not in data or 'email' not in data:
        return jsonify({"error": "Missing required fields: customer_id or email"}), 400

    # Store customer record in DynamoDB
    cust_record = {
        'customer_id': data['customer_id'],
        'email': data['email']
    }

    try:
        dynamodb = boto3.resource('dynamodb')
        cust_table = dynamodb.Table('Customers')
        resp = cust_table.put_item(Item=cust_record)
        return jsonify({"status": data['customer_id'] + " added successfully"}), resp['ResponseMetadata']['HTTPStatusCode']

    except ClientError as e:
        return jsonify({"error": f"Error occurred: {e.response['Error']['Message']}"}), 500


# GET method retrieve customer info based on customer_id
@paymentApp.route('/v1/api/customer/<customer_id>', methods=['GET'])
def get_customer(customer_id):

    if customer_id is None:
        return jsonify({"error": "Invalid customer_id"}), 400

    dynamodb = boto3.resource('dynamodb')

    try:
        cust_table = dynamodb.Table('Customers')
        resp = cust_table.get_item(Key={'customer_id': customer_id})

        # Check if the item exists in the response
        if 'Item' in resp:
            customer = resp['Item']
            return jsonify(customer), 200
        else:
            return jsonify({"error": "Customer not found"}), 404

    except ClientError as e:
        return jsonify({"error": f"Error occurred: {e.response['Error']['Message']}"}), 500


# Get OAuth token from PayPal
def get_access_token():

    url = f'{PAYPAL_SANDBOX_URL}/v1/oauth2/token'
    headers = {
        'Accept': 'application/json',
        'Accept-Language': 'en_US'
    }

    response = requests.post(
        url,
        headers=headers,
        data={'grant_type': 'client_credentials'},
        auth=(PAYPAL_CLIENT_ID, PAYPAL_SECRET)
    )

    if response.status_code == 200:
        access_token = response.json()['access_token']
        return access_token
    else:
        print(f"Failed to get access token: {response.status_code} {response.text}")
        return None

# POST method to process payment to customer
@paymentApp.route('/v1/api/payments', methods=['POST'])
def process_payment():

    req_data = request.get_json()

    dynamodb = boto3.resource('dynamodb')

    if req_data['customer_id']:
        try:
            cust_table = dynamodb.Table('Customers')
            resp = cust_table.get_item(Key={'customer_id': req_data['customer_id']})
            if 'Item' not in resp:
                print(f"Customer {req_data['customer_id']} not found in records")
                return jsonify({"error": f"customer {req_data['customer_id']} not in records"}), 404

        except ClientError as e:
            return jsonify({"error": f"Error fetching customer: {e.response['Error']['Message']}"}), 500

    access_token = get_access_token()
    if access_token is None:
        print(f"failed to get PayPal API OAuth token")
        return jsonify({"error": "Error occurred: failed to get PayPal API OAuth token"}), 500

    url = f'{PAYPAL_SANDBOX_URL}/v1/payments/payment'
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
                "total": req_data['amount'],
                "currency": req_data['currency'],
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
        "email": req_data['email']  # Specify the recipient's email address here
    }

    response = requests.post(url, json=payment_data, headers=headers)

    if response.status_code == 201:
        print('Payment Authorization created successfully.')
    else:
        print(f"Failed to create payment: {response.status_code} {response.text}")
        return jsonify({"error": f"payment failed for {data['customer_id']} - {response.text}"}), response.status_code

    # Store payment record in DynamoDB
    payment_record = {
        'customer_id': req_data['customer_id'],
        'email': req_data['email'],
        'payment_id': datetime.utcnow().isoformat() + "Z",
        'amount': req_data['amount'],
        'payment_method': 'paypal',
        'status': 'Completed',
        'currency': req_data['currency'],
        #'timestamp': str(context.aws_request_id)
    }

    try:
        disb_table = dynamodb.Table('Disbursements')
        resp = disb_table.put_item(Item=payment_record)
        print(f"Rajesham Debug: {resp['ResponseMetadata']['HTTPStatusCode']}")
        return jsonify({"status": req_data['customer_id'] + " payment successful"}), resp['ResponseMetadata']['HTTPStatusCode']

    except ClientError as e:
        return jsonify({"error": f"Error occurred: {e.response['Error']['Message']}"}), 500


    '''
    # Send a notification
    notification_message = f"Payment of ${amount} has been processed via {payment_method} for payee {payee_id}."
    #send_event_notification(notification_message)

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Payment successfully processed', 'result': result})
    }
    '''

if __name__ == '__main__':
    paymentApp.run(debug=True)
