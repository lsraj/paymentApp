
# run: python3 payAppTest.py

import requests
import json
import random
import boto3
from dotenv import load_dotenv
import os

# pip install python-dotenv
# Load environment variables from .env file
load_dotenv()

API_GATEWAY_BASE_URL = os.getenv("API_GATEWAY_BASE_URL")
X_API_KEY = os.getenv("X-API-KEY")

def get_cognito_auth_token():
    user_pool_id = os.getenv("USER_POOL_ID")
    client_id = os.getenv("CLIENT_ID")
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")

    client = boto3.client('cognito-idp', region_name='us-east-2')

    resp = client.admin_initiate_auth(
        UserPoolId=user_pool_id,
        ClientId=client_id,
        AuthFlow='ADMIN_NO_SRP_AUTH',
        AuthParameters={
            'USERNAME': username,
            'PASSWORD': password
        }
    )
    if 'AuthenticationResult' in resp:
        id_token = resp['AuthenticationResult']['IdToken']
        return id_token
    else:
       return None

def test_add_customer_success():
    '''
    Send valid customer_id and email to API Gateway POST method on /v1/api/customer.
    The requests passes through API Gateway, Lambda and into dynamodb.
    '''
    req_body = {}
    req_headers = {}
    req_headers['Content-Type'] = 'application/json'
    if X_API_KEY:
        req_headers['x-api-key'] = X_API_KEY
    auth_token = get_cognito_auth_token()
    if auth_token is None:
        print(f"test_add_customer_success() FAILED. cognito auth token not found")
        return
    req_headers['Authorization'] = f"Bearer {auth_token}"
    add_customer_url = f'{API_GATEWAY_BASE_URL}/v1/api/customer'
    for i in range(1, 11):
        req_body['customer_id'] = f'paypaluser{i}';
        req_body['email'] = f'paypaluser{i}@example.com'
        resp = requests.post(add_customer_url, json=req_body, headers=req_headers)
        assert resp.status_code == 200, f"expected 200 but got {resp.status_code}"
        # print(f"(paypaluser{i}, paypaluser{i}@example.com): statusCode: {resp.status_code}, {resp.json()}")
    print(f"test_add_customer_success() PASSED")


def test_invalid_customer_id():
    '''
    This test focusses on API Gateway POST method on /v1/api/customer validating
    params in request body. It sends variety of invalid customer_id.
    '''
    add_customer_url = f'{API_GATEWAY_BASE_URL}/v1/api/customer'
    req_body = {}
    req_body['email'] = f'paypaluser1@example.com'
    req_headers = {}
    req_headers['Content-Type'] = 'application/json'
    if X_API_KEY:
        req_headers['x-api-key'] = X_API_KEY
    auth_token = get_cognito_auth_token()
    if auth_token is None:
        print(f"test_invalid_customer_id() FAILED. cognito auth token not found")
        return
    req_headers['Authorization'] = f"Bearer {auth_token}"

    # invalid customer_id variations such as empty, long, and invalid characters.
    invalid_customer_id_list = [
        "",
        "user1", "I told my computer I needed a break, and now it’s frozen",
        "paypaluse1@"
    ]

    for customer_id in invalid_customer_id_list:
        req_body['customer_id'] =  customer_id
        resp = requests.post(add_customer_url, json=req_body, headers=req_headers)
        assert resp.status_code == 400, f"expected 200 but got {resp.status_code}"
        # print(resp.text)
    print(f"test_invalid_customer_id() PASSED")


def test_invalid_customer_email():
    '''
    This test focusses on API Gateway POST method on /v1/api/customer validating
    params in request body. It passes variety of invalid email.
    '''
    add_customer_url = f'{API_GATEWAY_BASE_URL}/v1/api/customer'
    req_body = {}
    req_body['customer_id'] = 'paypaluser1'
    req_headers = {}
    req_headers['Content-Type'] = 'application/json'
    if X_API_KEY:
        req_headers['x-api-key'] = X_API_KEY
    auth_token = get_cognito_auth_token()
    if auth_token is None:
        print(f"test_invalid_customer_email() FAILED. cognito auth token not found")
        return
    req_headers['Authorization'] = f"Bearer {auth_token}"

    # invalid email variations such as empty, long, and invalid characters.
    invalid_customer_email_list = [
        "",
        "a@bc",
        "a" * 64 + "@b" * 188 + ".com"
    ]

    for email in invalid_customer_email_list:
        req_body['email'] =  email
        resp = requests.post(add_customer_url, json=req_body, headers=req_headers)
        assert resp.status_code == 400, f"expected 200 but got {resp.status_code}"
        # print(resp.json())

    print(f"test_invalid_customer_email() PASSED")

def add_customer_tests():
    test_add_customer_success()
    test_invalid_customer_id()
    test_invalid_customer_email()

# test /v1/api/customer/{customer_id}
def test_get_customer():
    pass

# test /v1/api/payments
def test_pay_customer():
    '''
    Test API Gateway POST method on /v1/api/payments.
    The requests passes through API Gateway, Lambda and into dynamodb.
    '''
    add_customer_url = f'{API_GATEWAY_BASE_URL}/v1/api/payments'
    req_body = {}
    req_headers = {}
    req_headers['Content-Type'] = 'application/json'
    if X_API_KEY:
        req_headers['x-api-key'] = X_API_KEY
    auth_token = get_cognito_auth_token()
    if auth_token is None:
        print(f"test_pay_customer() FAILED. cognito auth token not found")
        return
    req_headers['Authorization'] = f"Bearer {auth_token}"

    # Note: quite interestingly paypal sandbox url https://developer.paypal.com/docs/api/payments/v1
    # is not accepting JPY and INR.
    # currencies = ["USD", "INR", "EUR", "JPY", "GBP"]
    currencies = ["USD", "EUR", "GBP"]
    for i in range(1, 11):
        req_body['customer_id'] = f'paypaluser{i}';
        req_body['email'] = f'paypaluser{i}@example.com'
        # generate random number between 1 and 1M and round the value to 2 decimal places.
        req_body['amount'] = round(random.uniform(1, 1000000), 2)
        req_body['currency'] = random.choice(currencies)
        # print(f"debug {req_body}")
        resp = requests.post(add_customer_url, json=req_body, headers=req_headers)
        assert resp.status_code == 200, f"expected 200 but got {resp.status_code}"
        # print(f"(paypaluser{i}, paypaluser{i}@example.com): statusCode: {resp.status_code}, {resp.json()}")
    print(f"test_pay_customer() PASSED")


def main():
    add_customer_tests()
    test_pay_customer()

if __name__ == "__main__":
    main()
