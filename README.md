# Payment App Prototype

A simple payment app developed with AWS managed services API Gateway, Lambda, and Dynamodb. High level overview:

1) Dynamodb has two tables 'Customers' and 'Disbursements':
     * Customers table stores customer information: It has a customer_id partition key (string such as unixuser1) and an attribute 'email'. There is no sort key. Other attributes can be added, but I will work on limiting them (TBD).
     * Disbursements table contains all disbursements made to a customer (for audit and other purposes): This table has partition key 'customer_id' and sort key 'payment_id' (date in ISO 8601 format), it also has other attributes amount, currency, payment_method, and email.

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
    * POST on /v1/api/payment: Process the payment for a customer. Request body model in API Gateway:
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
4) AWS Lambda is written in Python (tested on python3.12). timeout setting raised to 60 seconds as paypal endpoint is sometimes taking more than default 3 seconds (How to process payment quickly? - TBD).
5) Dynamodb, Lambda and API gateway deployed on AWS with terraform. Terraform code is in for dynamodb, lambda. WIP for API Gateway.

# Architecture Diagram

![Alt text](images/payAppArchDiag.png?raw=true "Architecture Digram")


# Code Tree

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
   
