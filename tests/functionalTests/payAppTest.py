
# run: python3 payAppTest.py

import requests
import json

AWS_API_GATEWAY_URL = "https://yyodyf7fsi.execute-api.us-east-2.amazonaws.com/dev/v1/api/customer"

# test /v1/api/customer

def test_add_customer_success(customer_id, email, status_code_expected):
    req_body = {}
    req_body['customer_id'] = customer_id
    req_body['email'] = email
    req_headers = {}
    req_headers['Content-Type'] = 'application/json'
    resp = requests.post(AWS_API_GATEWAY_URL, json=req_body, headers=req_headers)
    assert resp.status_code == status_code_expected, f"expected 200 but got {resp.status_code}"
    print(f"({customer_id}, {email}) added. statusCode: {resp.status_code}, {resp.json()}")
    # assert response.json() == expected_response, f"Expected {expected_response} but got {response.json()}"

def test_add_customer_empty_customer():
    test_add_customer_success("", f"paypaluser1@example.com", 400)
    test_add_customer_success("paypaluser1", "", 400)

def add_customer():

    # add 10 customers
    for i in range(1, 11):
        test_add_customer_success(f"paypaluser{i}", f"paypaluser{i}@example.com", 200)

    test_add_customer_empty_customer()

# test /v1/api/customer/{customer_id}
def test_get_customer():
    pass

# test /v1/api/payments
def test_pay_customer():
    pass


def main():
    add_customer()

if __name__ == "__main__":
    main()