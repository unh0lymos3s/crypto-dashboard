from fastapi.testclient import TestClient
from app import app

client = TestClient(app)
# Test cases for the API
# Happy path post and get
response = client.post("/quote", json={"symbol": "AAPL", "price": 150.00})
print(f"result: {response.json()} \n status: {response.status_code}")

response = client.get("/quote/AAPL")
print(f"result: {response.json()} \n status: {response.status_code}")

# Invalid symbol (not uppercase)
response = client.post("/quote", json={"symbol": "aapl", "price": 150.00})
print(f"result: {response.json()} \n status: {response.status_code}")

# Invalid price (Below or equal to zero)
response = client.post("/quote", json={"symbol": "GOOG", "price": -1.00})
print(f"result: {response.json()} \n status: {response.status_code}")

# Valid post and get for another symbol
response = client.post("/quote", json={"symbol": "GOOG", "price": 200.00})
print(f"result: {response.json()} \n status: {response.status_code}")

response = client.get("/quote/GOOG")
print(f"result: {response.json()} \n status: {response.status_code}")

# Unknown symbol 
response = client.get("/quote/MSFT")
print(f"result: {response.json()} \n status: {response.status_code}")