import requests
import uuid
import time

BASE_URL = "https://backend-zenark.onrender.com"
SESSION_ID = str(uuid.uuid4())
TEST_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjEyMzQ1Njc4OTAifQ.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"

def test_endpoint(endpoint, payload):
    print(f"Testing {endpoint}...")
    try:
        response = requests.post(f"{BASE_URL}{endpoint}", json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False
    print("-" * 20)

# 1. Save Chat
print(f"--- Step 1: Saving Chat (Session: {SESSION_ID}) ---")
save_payload = {
    "conversation": [
        {"role": "user", "content": "Hello, this is a test."},
        {"role": "assistant", "content": "Hi! I am a test assistant."}
    ],
    "name": f"Debug_Chat_{int(time.time())}",
    "session_id": SESSION_ID,
    "token": TEST_TOKEN
}
if test_endpoint("/save_chat", save_payload):
    # 2. Generate Report
    print(f"\n--- Step 2: Generating Report ---")
    report_payload = {
        "token": TEST_TOKEN,
        "session_id": SESSION_ID
    }
    test_endpoint("/generate_report", report_payload)
else:
    print("Skipping report generation because save_chat failed.")
