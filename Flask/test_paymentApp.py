
# pip install flask boto3 pytest unittest-mock
# run: pytest -v

import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
import boto3
from botocore.exceptions import ClientError
from paymentApp import paymentApp, get_access_token
import os

# Mock PayPal sandbox URLs and credentials
PAYPAL_SANDBOX_URL = "https://api.sandbox.paypal.com"

class TestCustomerAPI(unittest.TestCase):

    @patch('boto3.resource')  # Mocking boto3 resource to avoid actual DynamoDB calls
    def test_add_customer_success(self, mock_boto_resource):
        # Simulate a successful DynamoDB put_item response
        mock_dynamo_db = MagicMock()
        mock_table = MagicMock()
        mock_dynamo_db.Table.return_value = mock_table
        mock_table.put_item.return_value = {
            'ResponseMetadata': {'HTTPStatusCode': 200}
        }
        mock_boto_resource.return_value = mock_dynamo_db

        # Test data
        customer_data = {
            'customer_id': 'vetagaadu3',
            'email': 'vetagaadu3@abc.com'
        }

        # Send a POST request to add customer
        with paymentApp.test_client() as client:
            response = client.post('/v1/api/customer/add', json=customer_data)

        # Check the status code and response
        self.assertEqual(response.status_code, 200)
        self.assertIn('added successfully', response.json['status'])

    @patch('boto3.resource')
    def test_get_customer_success(self, mock_boto_resource):
        # Simulate a successful DynamoDB get_item response
        mock_dynamo_db = MagicMock()
        mock_table = MagicMock()
        mock_dynamo_db.Table.return_value = mock_table
        mock_table.get_item.return_value = {
            'Item': {
                'customer_id': 'vetagaadu3',
                'email': 'vetagaadu3@abc.com'
            }
        }
        mock_boto_resource.return_value = mock_dynamo_db

        # Send a GET request to fetch customer info
        with paymentApp.test_client() as client:
            response = client.get('/v1/api/customer/vetagaadu3')

        # Check the status code and response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['customer_id'], 'vetagaadu3')

    @patch('boto3.resource')
    def test_get_customer_not_found(self, mock_boto_resource):
        # Simulate a DynamoDB response with no customer
        mock_dynamo_db = MagicMock()
        mock_table = MagicMock()
        mock_dynamo_db.Table.return_value = mock_table
        mock_table.get_item.return_value = {}
        mock_boto_resource.return_value = mock_dynamo_db

        # Send a GET request to fetch non-existent customer info
        with paymentApp.test_client() as client:
            response = client.get('/v1/api/customer/nonexistent123')

        # Check the status code and response
        self.assertEqual(response.status_code, 404)
        self.assertIn('Customer not found', response.json['error'])

    @patch('boto3.resource')
    def test_add_customer_missing_fields(self, mock_boto_resource):
        # Send POST request with missing customer_id field
        with paymentApp.test_client() as client:
            response = client.post('/v1/api/customer/add', json={'email': 'missingid@example.com'})

        # Check the status code and response
        self.assertEqual(response.status_code, 400)
        self.assertIn('Missing required fields', response.json['error'])

    @patch('boto3.resource')
    def test_add_customer_dynamodb_error(self, mock_boto_resource):
        # Simulate a DynamoDB error (e.g., permission issues)
        mock_dynamo_db = MagicMock()
        mock_table = MagicMock()
        mock_dynamo_db.Table.return_value = mock_table
        mock_table.put_item.side_effect = ClientError(
            {"Error": {"Message": "Test DynamoDB error"}}, 'PutItem'
        )
        mock_boto_resource.return_value = mock_dynamo_db

        # Test data
        customer_data = {'customer_id': 'vetagaadu3', 'email': 'vetagaadu3@abc.com'}

        # Send a POST request to add customer
        with paymentApp.test_client() as client:
            response = client.post('/v1/api/customer/add', json=customer_data)

        # Check the status code and response
        self.assertEqual(response.status_code, 500)
        self.assertIn('Error occurred', response.json['error'])

    @patch('requests.post')
    def test_get_access_token(self, mock_post):

        # Simulate successful PayPal response with an access token
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'access_token': 'mock_access_token'}
        mock_post.return_value = mock_response

        # Override the credentials inside the function itself (if necessary)
        with patch('paymentApp.PAYPAL_CLIENT_ID', 'test_client_id'), \
             patch('paymentApp.PAYPAL_SECRET', 'test_secret'):
            # Call the function to get the token
            token = get_access_token()

        # Assert that the token is returned correctly
        self.assertEqual(token, 'mock_access_token')
        mock_post.assert_called_once_with(
            'https://api.sandbox.paypal.com/v1/oauth2/token',
            headers={'Accept': 'application/json', 'Accept-Language': 'en_US'},
            data={'grant_type': 'client_credentials'},
            auth=('test_client_id', 'test_secret')
        )

    @patch('paymentApp.get_access_token')  # Patch the get_access_token function here
    @patch('boto3.resource')
    @patch('requests.post')
    def test_process_payment_success(self, mock_post, mock_boto_resource, mock_get_token):

        # Mock the access token function to return a mock token
        mock_get_token.return_value = "mock_access_token"  # Mock successful access token

        # Mock DynamoDB response for customer lookup (mocking that the customer exists)
        mock_dynamo_db = MagicMock()
        mock_boto_resource.return_value = mock_dynamo_db

        # Create mock tables for customer and disbursement
        mock_customer_table = MagicMock()
        mock_disb_table = MagicMock()

        # Use side_effect to mock different tables based on table name
        mock_dynamo_db.Table.side_effect = lambda table_name: mock_customer_table if table_name == 'Customers' else mock_disb_table

        # Mock successful response where the customer exists
        mock_customer_table.get_item.return_value = {
            'Item': {'customer_id': 'vetagaadu3', 'email': 'vetagaadu3@example.com'}
        }

        # Simulate PayPal payment response
        mock_paypal_response = MagicMock()
        mock_paypal_response.status_code = 201  # Success status code for PayPal payment
        mock_paypal_response.text = "Payment authorized"
        mock_post.return_value = mock_paypal_response

        # Mock DynamoDB response for inserting the payment record
        mock_disb_table.put_item.return_value = {
            'ResponseMetadata': {
                'HTTPStatusCode': 200,
                }
        }

        # Request data for the payment
        request_data = {
            "customer_id": "vetagaadu3",  # This is the customer that should exist in DynamoDB
            "amount": 100.0,
            "currency": "USD",
            "email": "vetagaadu3@example.com"
        }

        # Simulate a POST request to process the payment
        with paymentApp.test_client() as client:
            response = client.post('/v1/api/payments', json=request_data)

        # Assert the success status and response
        self.assertEqual(response.status_code, 200)  # Expecting a 200 OK response
        self.assertTrue(response.is_json)
        self.assertIn("payment successful", response.json['status'])

    @patch('boto3.resource')
    @patch('requests.post')
    def test_process_payment_customer_not_found(self, mock_post, mock_boto_resource):
        # Simulate PayPal payment response (failure)
        mock_paypal_response = MagicMock()
        mock_paypal_response.status_code = 404
        mock_paypal_response.text = "Payment failed"
        mock_post.return_value = mock_paypal_response

        # Mock DynamoDB response for customer lookup (customer not found)
        mock_dynamo_db = MagicMock()
        mock_table = MagicMock()
        mock_dynamo_db.Table.return_value = mock_table
        mock_table.get_item.return_value = {}
        mock_boto_resource.return_value = mock_dynamo_db

        # Request data for the payment
        request_data = {
            "customer_id": "nonexistent_customer",
            "amount": 100.0,
            "currency": "USD",
            "email": "nonexistent@example.com"
        }

        # Simulate a POST request to process payment
        with paymentApp.test_client() as client:
            response = client.post('/v1/api/payments', json=request_data)

        # Assert the error response for customer not found
        self.assertEqual(response.status_code, 404)
        self.assertIn("not in records", response.json['error'])

        # Ensure no PayPal API request was made due to customer not being found
        mock_post.assert_not_called()

    @patch('boto3.resource')
    @patch('requests.post')
    def test_process_payment_oauth_failure(self, mock_post, mock_boto_resource):
        # Simulate PayPal OAuth failure
        mock_post.return_value.status_code = 500
        mock_post.return_value.text = "OAuth failed"

         # Simulate a DynamoDB mock response where customer is found
        mock_dynamodb = MagicMock()
        mock_table = MagicMock()
        mock_boto_resource.return_value.Table.return_value = mock_table
        mock_table.get_item.return_value = {'Item': {'customer_id': 'vetagaadu3'}}  # Simulating that the customer exists


        # Request data for the payment
        request_data = {
            "customer_id": "vetagaadu3",
            "amount": 100.0,
            "currency": "USD",
            "email": "vetagaadu3@example.com"
        }

        # Simulate a POST request to process payment
        with paymentApp.test_client() as client:
            response = client.post('/v1/api/payments', json=request_data)

        # Assert that the failure message is returned due to OAuth failure
        self.assertEqual(response.status_code, 500)
        self.assertIn("Error occurred: failed to get PayPal API OAuth token", response.json['error'])


if __name__ == '__main__':
    unittest.main()

