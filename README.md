# Payment App Prototype

## 1) AWS Services Used

A simple payment app developed with AWS managed services:

1) **AWS API Gateway**: Provides and endpoint for incoming HTTPS requests such as payment disbursement to a customer.
2) **AWS Cognito**: Handles authentication and authorization for users accessing the payment system.
3) **Lambda**: Processes payments by interacting with 3rd party payment receivers (Paypal, Stripe, ACH etc). Also interacts with Dynamodb for validating the user and storing the disbursements for auditing and other purposes. 
4) **Secrets Manager**: Stores sensitive information such as 3rd party vendors API secret and access keys.
5) **SNS**: Sends notifications to users after payment is complete.
6) **DynamoDB**: Stores payment records and user data.
7) **CloudWatch**: Monitors logs, metrics.
8) **IAM**: For IAM roles.


![Alt text](images/payAppArchDiag.png?raw=true "Architecture Digram")


## 2) Payment Workflow Example

Deploy the AWS services with the terraform code in this source code repo. Send POST request on API Gateway endpoint. Example:

```
curl -X POST https://6uld4n6xw7.execute-api.us-east-2.amazonaws.com/test/v1/api/payments -d '{"customer_id": "user1", "email": "user1@example.com", "amount": 2000, "currency": "USD"}'

```
API Gateway sends this request to Lambda which processes the request by interacting with other AWS services and 3rd party vendors and replies with the status back to API Gateway.


## 3) High Level Architecture Overview

1) Dynamodb has two tables **Customers** and **Disbursements**:
     * **Customers table** stores customer information: It has a **customer_id as a partition key** (string such as **user1**) and 'email' as an attribute. There is no sort key. Other attributes can be added, but I will work on limiting them (TBD).
     * **Disbursements table** contains all disbursements made to a customer (for audit and other purposes): This table has **customer_id as partition key and payment_id (date in ISO 8601 format) as sort key**, it also has other attributes amount, currency, payment_method, and email.

2) API Gateway is hosted with 4 REST APIs as below:
    * **POST on resource /v1/api/customer**: inserts customer_id and email into Customers table. API Gateway request body model:
      ```
      # see RFC 5321 and RFC 5322 for email specs/format
      { 
          "properties" : {
              "customer_id" : {
                  "type" : "string"
                  "pattern" : "^[A-Za-z0-9]{8,20}$",
                  "minLength" : 8,
                  "maxLength" : 20
              },
              "email" : {
                  "type" : "string",
                  "format" : "email",
                  "pattern" : "^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
                  "minLength" : 5,
                  "maxLength" : 254
              }
          },
          "required" : ["customer_id", "email"]
      }
  
      ```
      
    * **GET on /v1/api/customer/{customer_id}**: Gets the customer record from Customers table.
      
    * **POST on /v1/api/payments**: Process the payment for a customer. Request body model in API Gateway:
     ```
    # see RFC 5321 and RFC 5322 for email specs/format
    {
         "type": "object",
         "properties": {
             "customer_id": {
                 "type": "string",
                 "pattern": "^[A-Za-z0-9]{8,20}$",
                 "minLength": 8,
                 "maxLength": 20
             },
             "email": {
                 "type": "string",
                 "format": "email",
                 "pattern": "^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
                 "minLength": 5,
                 "maxLength": 254
             },
             "amount": {
                 "type": "number",
                 "minimum": 1,
                 "maximum": 1000000
             },
             "currency": {
                 "type": "string",
                 "enum": ["USD", "INR", "EUR", "JPY", "GBP"]
             }
         },
         "required": ["customer_id", "email", "amount", "currency"]
    }

     ```

    * **GET on /v1/api/payment/{customer_id}**: Gets the payment records of a customer.

4) PayPal sandbox endpoint https://api.sandbox.paypal.com is used to mimic the payment processing. See [Paypal rest API doc](https://developer.paypal.com/api/rest) for more details. I plan to integrate [Stripe](https://docs.stripe.com/api), [ACH](https://achbanking.com/apiDoc) etc(TBD).
   
5)  AWS Lambda is written in Python (tested on python3.12). **timeout setting raised to 60 seconds** as paypal endpoint is sometimes taking more than the default 3 seconds (How to process payment quickly? - TBD).


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
│   │   ├── outputs.tf
│   │   ├── providers.tf
│   │   ├── terraform.tf
│   │   ├── terraform.tfvars
│   │   └── variables.tf
│   ├── azure
│   └── gcp
├── gotchas.txt
── images
│   └── payAppArchDiag.png
├── lambda
│   ├── aws-cli-lambda-test
│   │   ├── addCustomerTest.json
│   │   ├── getCustomerTest.json
│   │   ├── gotchas.txt
│   │   ├── output.txt
│   │   └── payCustomerTest.json
│   ├── build_lambda_zip.sh
│   ├── lambda_function.py
│   ├── paymentApp-lambda.zip
│   ├── requirements.txt
│   └── test_lambda_function.py
└── tests
    ├── functionalTests
    │   └── payAppTest.py
    └── soakTests
```

## 5) Infrastructure Deployment

Build Lambda zip. And deploy the infrastructure onto AWS with terraform.

```
$ cd lambda
$ ./build_lambda_zip.sh 
$ ls paymentApp-lambda.zip 
  paymentApp-lambda.zip
$ cd ../deply/aws/
$ terraform init
$ terraform plan -var="paypal_sandbox_url=https://api.sandbox.paypal.com" -var="paypal_clinet_id=<CLINET_ID>" -var="paypal_secret=<SECRET>"
$ terraform apply -var="paypal_sandbox_url=https://api.sandbox.paypal.com" -var="paypal_clinet_id=<CLINET_ID>" -var="paypal_secret=<SECRET>"
$
```
Note: Ideally, API keys should not be sent this way. They have to be managed in services such as AWS Secret Manager or similar - TBD.

Take a look at build script:
```
$ cat build_lambda_zip.sh  
  #
  # Run this from the dir where lambda_function.py is
  #
  pip install -r requirements.txt -t package/
  cp lambda_function.py package/
  cd package && zip -r9 ../paymentApp-lambda.zip . && cd ..
  rm -rf package
$
$ cat requirements.txt 
   requests==2.31.0
   boto3==1.35.68
   botocore==1.35.68
$
$
```

## 6) Testing

curl or python requests module or postman can be used for testing. I will be scripting detailed tests with python requests module soon.

```
curl -X POST https://6uld4n6xw7.execute-api.us-east-2.amazonaws.com/test/v1/api/customer -d '{"customer_id": "user1", "email": "user1@abc.com"}'

curl -X POST https://6uld4n6xw7.execute-api.us-east-2.amazonaws.com/test/v1/api/customer  -d '{"customer_id": "user2", "email": "user2@abc.com"}'

curl -X POST https://6uld4n6xw7.execute-api.us-east-2.amazonaws.com/test/v1/api/customer  -d '{"customer_id": "user3", "email": "user3@abc.com"}'

curl -X POST https://6uld4n6xw7.execute-api.us-east-2.amazonaws.com/test/v1/api/payments -d '{"customer_id": "user1", "amount": 10, "currency": "USD", "email":"user11@abc.com"}'

curl -X POST https://6uld4n6xw7.execute-api.us-east-2.amazonaws.com/test/v1/api/payments -d '{"customer_id": "user2", "amount": 10, "currency": "USD", "email":"user2@abc.com"}'
```

## 7) Work in Progress
 
 * API gateway deployment with terraform
 * SNS deployment with terraform. And Sending the notification from Lambda code
 * Cognito deployment with terraform

## 8) Notes from Testing
* https://developer.paypal.com/docs/api/payments/v1 does support only limited currencies. I tried with ["USD", "INR", "EUR", "JPY", "GBP"] and found that ["USD", "EUR", "GBP"] supported
 and ["INR", "JPY"] not supported.

## 8) References
* [Amazon API Gateway](https://docs.aws.amazon.com/apigateway/latest/developerguide/welcome.html)
* [AWS Lambda](https://docs.aws.amazon.com/lambda/latest/dg/welcome.html)
* [AWS Dynamodb](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Introduction.html)
* [AWS Cognito](https://docs.aws.amazon.com/cognito/latest/developerguide/what-is-amazon-cognito.html)
* [AWS Secret Manager](https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html)
* [AWS Simple Notification Service](https://docs.aws.amazon.com/sns/latest/dg/welcome.html)
* [AWS CloudWatch](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/WhatIsCloudWatch.html)
* [Paypal rest API doc](https://developer.paypal.com/api/rest)
* [Stripe APIs](https://docs.stripe.com/api)
* [ACH APIs ](https://achbanking.com/apiDoc)
* [AWS Architecture Icons](https://aws.amazon.com/architecture/icons)
* [Free tool to draw architecture diagrams](https://app.diagrams.net)
* [Request validation for REST APIs in API Gateway](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-method-request-validation.html)
* [IETF JSON Schema](https://datatracker.ietf.org/doc/html/draft-zyp-json-schema-04)
* [AWS Blog post - API Gateway request validation](https://aws.amazon.com/blogs/compute/how-to-remove-boilerplate-validation-logic-in-your-rest-apis-with-amazon-api-gateway-request-validation/)


