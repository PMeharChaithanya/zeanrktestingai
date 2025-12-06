import requests
import uuid
import time

BASE_URL = "https://backend-zenark.onrender.com"
SESSION_ID = str(uuid.uuid4())

def test_endpoint(endpoint, payload):
    print(f"Testing {endpoint} with payload: {payload}")
    try:
        response = requests.post(f"{BASE_URL}{endpoint}", json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False
    print("-" * 20)

print("Waiting for deployment...")
# Poll for a few times
for i in range(10):
    print(f"Attempt {i+1}...")
    success = test_endpoint("/exam_buddy", {
        "question": "How should I prepare for JEE?",
        "session_id": SESSION_ID
    })
    if success:
        print("Success!")
        break
    time.sleep(10)
