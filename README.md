# Payment App Prototype

## 1) AWS Services Used:

A simple payment app developed with AWS managed services:

1) AWS API Gateway: Provides and endpoint for incoming incoming HTTP(S) requests such as payment disbursement to a customer.
2) AWS Cognito: Handles authentication and authorization for users accessing the banking payment system.
3) Lambda: Processes payments by interacting with 3rd party payment receivers APIs (Paypal, Stripe, ACH etc). Also interacts with Dynamodb for validating the user and storing the disbursements for auditing and other purposes. 
4) Secrets Manager: Stores sensitive information such as 3rd party vendors API secret and access keys.
5) SNS: Sends notifications to users after payment is complete.
6) DynamoDB: Stores payment records and user data.
7) CloudWatch: Monitors logs, metrics.

Note: WIP (work in progress) to integrate Cognito and SNS).


![Alt text](images/payAppArchDiag.png?raw=true "Architecture Digram")


## 2) Payment Workflow Example:

Banks, Insurance companies etc can deploy the AWS services with the terraform code in this source code repo. They can send POST API request on API Gateway endpoint: ```curl -X POST https://6uld4n6xw7.execute-api.us-east-2.amazonaws.com/test/v1/api/payments -d '{"customer_id": "user1", "email": "user1@example.com", "amount": 2000, "currency": "USD"}'```. API Gateway sends this request to Lambda which processes the request by interacting with 3rd party vendors and other AWS services and replies the status back to API Gateway.


## 3) High Level Architecture Overview:

1) Dynamodb has two tables 'Customers' and 'Disbursements':
     * Customers table stores customer information: It has a customer_id as partition key (string such as unixuser1) and 'email' as an attribute . There is no sort key. Other attributes can be added, but I will work on limiting them (TBD).
     * Disbursements table contains all disbursements made to a customer (for audit and other purposes): This table has 'customer_id' as partition key and 'payment_id' (date in ISO 8601 format) as sort key, it also has other attributes amount, currency, payment_method, and email.

2) API Gateway is hosted with 4 REST APIs as below:
    * POST on resource /v1/api/customer: inserts customer_id and email into Customers table. API Gateway request body model:
      ```
      { 
          "type": "object",
          "properties": {
               "customer_id": {
                   "type": "string"
               },
              "email": {
                  "type": "string",
                  "format": "email"
              }
          },
          "required": ["customer_id", "email"]
      }
      ```
      
    * GET on /v1/api/customer/{customer_id}: Gets the customer record from Customers table.
      
    * POST on /v1/api/payments: Process the payment for a customer. Request body model in API Gateway:
     ```
     {
         "type": "object",
         "properties": {
             "customer_id": {
                 "type": "string"
             },
             "email": {
                 "type": "string",
                 "format": "email"
             },
             "amount": {
                 "type": "number",
                 "format": "float"
             },
             "currency": {
               "type": "string"
             }
          },
          "required": ["customer_id", "email", "amount", "currency"]
      }
     ```

    * GET on /v1/api/payment/{customer_id}: Gets the payment records of a customer.

3) I have used paypal sandbox endpoint https://api.sandbox.paypal.com to mimic the payment processing. See [Paypal rest API doc](https://developer.paypal.com/api/rest) for more details. I plan to integrate [Stripe](https://docs.stripe.com/api), [ACH](https://achbanking.com/apiDoc) etc(TBD).
   
4)  AWS Lambda is written in Python (tested on python3.12). timeout setting raised to 60 seconds as paypal endpoint is sometimes taking more than default 3 seconds (How to process payment quickly? - TBD).


## 4) Code Tree

```

├── Flask
│   ├── curl_test.sh
│   ├── paymentApp.py
│   └── test_paymentApp.py
├── LICENSE
├── README.md
├── deply
│   ├── aws
│   │   ├── README.md
│   │   ├── apigateway.tf
│   │   ├── dynamodb.tf
│   │   ├── gotchas.txt
│   │   ├── lambda.tf
│   │   ├── providers.tf
│   │   ├── terraform.tf
│   │   ├── terraform.tfvars
│   │   └── variables.tf
│   ├── azure
│   └── gcp
├── gotchas.txt
├── images
│   └── payAppArchDiagram.png
└── lambda
    ├── addCustomerTest.json
    ├── build_lambda_zip.sh
    ├── getCustomerTest.json
    ├── gotchas.txt
    ├── lambda_function.py
    ├── payCustomerTest.json
    ├── paymentApp-lambda.zip
    ├── requirements.txt
    └── test_lambda_function.py
```

## 5) Infrastructure Deployment:
1) Build Lambda zip:

```
$ cd lambda
$ cat build_lambda_zip.sh 
#
# Run this from the dir where lambda_function.py is
#
pip install -r requirements.txt -t package/
cp lambda_function.py package/
cd package && zip -r9 ../paymentApp-lambda.zip . && cd ..
rm -rf package
$
$
$ cat requirements.txt 
requests==2.31.0
boto3==1.35.68
botocore==1.35.68
$
$ ./build_lambda_zip.sh 
$ ls paymentApp-lambda.zip 
paymentApp-lambda.zip
$
$
$ cd ../deply/aws/
$ terraform init
$ terraform plan -var="paypal_sandbox_url=https://api.sandbox.paypal.com" -var="paypal_clinet_id=<CLINET_ID>" -var="paypal_secret=<SECRET>"
$ terraform apply -var="paypal_sandbox_url=https://api.sandbox.paypal.com" -var="paypal_clinet_id=<CLINET_ID>" -var="paypal_secret=<SECRET>"
$

Note: There is no need to pass these variables after these keys are stored in AWS Secret Manager. TBD.

## 6) Testing

You can use curl or python requests. I have tested with curl. But I will write the details test cases here shortly.

## 7) References

