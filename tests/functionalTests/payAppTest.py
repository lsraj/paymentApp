
# run: python3 payAppTest.py

import requests
import json

API_GATEWAY_BASE_URL = "https://<apigatewayid>.execute-api.us-east-2.amazonaws.com/test"

def test_add_customer_success():
    '''
    Send valid customer_id and email to API Gateway POST method on /v1/api/customer.
    The requests passes through API Gateway, Lambda and into dynamodb.
    '''
    add_customer_url = f'{API_GATEWAY_BASE_URL}/v1/api/customer'
    for i in range(1, 11):
        req_body = {}
        req_body['customer_id'] = f'paypaluser{i}';
        req_body['email'] = f'paypaluser{i}@example.com'
        req_headers = {}
        req_headers['Content-Type'] = 'application/json'
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

    # send invalid customer_id variations such as empty, long, and invalid characters.
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

    # send invalid email variations such as empty, long, and invalid characters.
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
    pass


def main():
    add_customer_tests()

if __name__ == "__main__":
    main()