import requests
import uuid

BASE_URL = "https://backend-zenark.onrender.com"
SESSION_ID = str(uuid.uuid4())
TEST_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjEyMzQ1Njc4OTAifQ.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"

def test_chat(payload):
    print(f"Testing with payload: {payload}")
    try:
        response = requests.post(f"{BASE_URL}/chat", json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    print("-" * 20)

# Test 9: Valid Token
test_chat({
    "message": "Hello",
    "session_id": SESSION_ID,
    "token": TEST_TOKEN,
    "text": "Hello"
})
