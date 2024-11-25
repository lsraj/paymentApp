# paymentApp

A simple payment app developed with AWS managed services API Gateway, Lambda, and Dynamodb. The basic architecture diagram and workflow:

1) Dynamodb has two tables 'Customers' and 'Disbursements':
     * Customers table stores customer information: It has a customer_id partition key (string such as unixuser1) and an attribute 'email'. There is no sort key. Other attributes can be added, but I will work on limiting them (TBD).
     * Disbursements table contains all disbursements made to a customer (for audit and other purposes): This table has partition key 'customer_id' and sort key 'payment_id' (date in ISO 8601 format), it also has other attributes amount, currency, payment_method, and email.

2) API Gateway is hosted with 4 REST APIs as below:
    * POST on resource /v1/api/customer: inserts customer_id and email into Customers table. API Gateway request body modle:
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
    * POST on /v1/api/payment: Process the payment for a customer. I have used PayPal Sandbox for fictional payment processing. See Notes below.
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

![Alt text](images/payAppArchDiag.png?raw=true "Architecture Digram")



   
