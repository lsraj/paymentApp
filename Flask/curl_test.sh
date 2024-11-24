
curl -X POST http://127.0.0.1:5000/v1/api/customer/add   -H "Content-Type: application/json"   -d '{"customer_id": "vetagaadu1", "email": "vetagaadu1@abc.com"}'

curl -X POST http://127.0.0.1:5000/v1/api/customer/add   -H "Content-Type: application/json"   -d '{"customer_id": "vetagaadu2", "email": "vetagaadu2@abc.com"}'

curl -X POST http://127.0.0.1:5000/v1/api/customer/add   -H "Content-Type: application/json"   -d '{"customer_id": "vetagaadu3", "email": "vetagaadu3@abc.com"}'

curl -X POST http://127.0.0.1:5000/v1/api/customer/add   -H "Content-Type: application/json"   -d '{"customer_id": "vetagaadu4", "email": "vetagaadu4@abc.com"}'

curl -X POST http://127.0.0.1:5000/v1/api/customer/add   -H "Content-Type: application/json"   -d '{"customer_id": "vetagaadu5", "email": "vetagaadu5@abc.com"}'

curl -X POST http://127.0.0.1:5000/v1/api/customer/add   -H "Content-Type: application/json"   -d '{"customer_id": "vetagaadu6", "email": "vetagaadu6@abc.com"}'

curl -X POST http://127.0.0.1:5000/v1/api/payments -H "Content-Type: application/json"   -d '{"customer_id": "vetagaadu1", "amount": 10, "currency": "USD", "email":"vetagaadu1@abc.com"}'
