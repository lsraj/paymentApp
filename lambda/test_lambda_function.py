#
# run: pytest -v
#

import unittest
from unittest.mock import patch, MagicMock
import json
from lambda_function import lambda_handler, add_customer, get_customer, process_payment, get_access_token

class TestLambdaFunctions(unittest.TestCase):

    @patch('lambda_function.boto3.resource')
    def test_add_customer_success(self, mock_boto_resource):
        # Mock the response from DynamoDB
        mock_dynamo_table = MagicMock()
        mock_boto_resource.return_value.Table.return_value = mock_dynamo_table
        mock_dynamo_table.put_item.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}

        event = {
            'body': json.dumps({'customer_id': '123', 'email': 'test@example.com'}),
            'resource': '/v1/api/customer',
            'httpMethod': 'POST'
        }
        context = {}

        # Call the lambda_handler function
        result = lambda_handler(event, context)

        # Assert the response
        self.assertEqual(result['statusCode'], 200)
        self.assertIn('123 added successfully', result['body'])

    @patch('lambda_function.boto3.resource')
    def test_add_customer_missing_fields(self, mock_boto_resource):
        event = {
            'body': json.dumps({'customer_id': '123'}),
            'resource': '/v1/api/customer',
            'httpMethod': 'POST'
        }
        context = {}

        # Call the lambda_handler function
        result = lambda_handler(event, context)

        # Assert bad request due to missing email
        self.assertEqual(result['statusCode'], 400)
        self.assertIn('customer_id and email fields are required', result['body'])

    @patch('lambda_function.boto3.resource')
    def test_get_customer_success(self, mock_boto_resource):
        # Mock the response from DynamoDB
        mock_dynamo_table = MagicMock()
        mock_boto_resource.return_value.Table.return_value = mock_dynamo_table
        mock_dynamo_table.get_item.return_value = {
            'Item': {'customer_id': '123', 'email': 'test@example.com'}
        }

        event = {
            'pathParameters': {'customer_id': '123'},
            'resource': '/v1/api/customer/{customer_id}',
            'httpMethod': 'GET'
        }
        context = {}

        # Call the lambda_handler function
        result = lambda_handler(event, context)

        # Assert the response
        self.assertEqual(result['statusCode'], 200)
        self.assertIn('customer_id', result['body'])
        self.assertIn('email', result['body'])

    @patch('lambda_function.boto3.resource')
    def test_get_customer_not_found(self, mock_boto_resource):
        # Mock the response from DynamoDB
        mock_dynamo_table = MagicMock()
        mock_boto_resource.return_value.Table.return_value = mock_dynamo_table
        mock_dynamo_table.get_item.return_value = {}

        event = {
            'pathParameters': {'customer_id': '123'},
            'resource': '/v1/api/customer/{customer_id}',
            'httpMethod': 'GET'
        }
        context = {}

        # Call the lambda_handler function
        result = lambda_handler(event, context)

        # Assert the response
        self.assertEqual(result['statusCode'], 404)
        self.assertIn('not in records', result['body'])

    '''
    @patch('lambda_function.boto3.resource')
    @patch('lambda_function.requests.post')
    @patch.dict('os.environ', {
        'PAYPAL_SANDBOX_URL': 'https://sandbox.paypal.com',
        'PAYPAL_CLIENT_ID': 'your_client_id',
        'PAYPAL_SECRET': 'your_secret'
    })
    def test_process_payment_success(self, mock_requests_post, mock_boto_resource):
        # Mock the response from DynamoDB for customer lookup
        mock_dynamo_table = MagicMock()
        mock_boto_resource.return_value.Table.return_value = mock_dynamo_table
        mock_dynamo_table.get_item.return_value = {'Item': {'customer_id': '123', 'email': 'test@example.com'}}

        # Mock the PayPal API response
        mock_requests_post.return_value = MagicMock(status_code=201, text='{"id":"PAY-123"}')

        event = {
            'body': json.dumps({
                'customer_id': '123',
                'email': 'test@example.com',
                'amount': 100,
                'currency': 'USD'
            }),
            'resource': '/v1/api/payments',
            'httpMethod': 'POST'
        }
        context = {}

        # Call the lambda_handler function
        result = lambda_handler(event, context)

        # Assert the response
        self.assertEqual(result['statusCode'], 200)
        self.assertIn('message : 123 payment successful', result['body'])
    '''

    @patch('lambda_function.boto3.resource')
    @patch('lambda_function.requests.post')
    @patch.dict('os.environ', {
        'PAYPAL_SANDBOX_URL': 'https://sandbox.paypal.com',
        'PAYPAL_CLIENT_ID': 'your_client_id',
        'PAYPAL_SECRET': 'your_secret'
    })
    def test_process_payment_fail_paypal(self, mock_requests_post, mock_boto_resource):
        # Mock the response from DynamoDB for customer lookup
        mock_dynamo_table = MagicMock()
        mock_boto_resource.return_value.Table.return_value = mock_dynamo_table
        mock_dynamo_table.get_item.return_value = {'Item': {'customer_id': '123', 'email': 'test@example.com'}}

        # Mock a failed PayPal API response
        mock_requests_post.return_value = MagicMock(status_code=400, text='Error')

        event = {
            'body': json.dumps({
                'customer_id': '123',
                'email': 'test@example.com',
                'amount': 100,
                'currency': 'USD'
            }),
            'resource': '/v1/api/payments',
            'httpMethod': 'POST'
        }
        context = {}

        # Call the lambda_handler function
        result = lambda_handler(event, context)

        # Assert the response
        self.assertEqual(result['statusCode'], 500)
        self.assertIn('error : failed to get PayPal API OAuth token', result['body'])

    @patch('lambda_function.requests.post')
    @patch.dict('os.environ', {'PAYPAL_SANDBOX_URL': 'https://sandbox.paypal.com', 'PAYPAL_CLIENT_ID': 'your_client_id', 'PAYPAL_SECRET': 'your_secret'})
    def test_get_access_token_success(self, mock_requests_post):
        # Mock the PayPal token response
        mock_requests_post.return_value = MagicMock(status_code=200, json=MagicMock(return_value={'access_token': 'test_token'}))

        token = get_access_token()

        # Assert that the token was successfully retrieved
        self.assertEqual(token, 'test_token')

    @patch('lambda_function.requests.post')
    @patch.dict('os.environ', {'PAYPAL_SANDBOX_URL': 'https://sandbox.paypal.com', 'PAYPAL_CLIENT_ID': 'your_client_id', 'PAYPAL_SECRET': 'your_secret'})
    def test_get_access_token_fail(self, mock_requests_post):
        # Mock a failed PayPal token response
        mock_requests_post.return_value = MagicMock(status_code=400, text='Error')

        token = get_access_token()

        # Assert that no token is returned
        self.assertIsNone(token)


if __name__ == '__main__':
    unittest.main()

