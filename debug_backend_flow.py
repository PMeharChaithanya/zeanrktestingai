import requests
import time

BASE_URL = "https://backend-zenark.onrender.com"
SESSION_ID = "final-test-999"
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

print(f"Using Session ID: {SESSION_ID}")

# 1. Create a conversation via /chat
print(f"\n--- Step 1: Sending Message via /chat ---")
chat_payload = {
    "text": "I am very stressed about JEE exams",
    "session_id": SESSION_ID,
    "token": TEST_TOKEN
}
if test_endpoint("/chat", chat_payload):
    # Wait a bit for persistence
    time.sleep(2)
    
    # 2. Generate Report
    # Engineer's curl command for generate_report ONLY has the token.
    print(f"\n--- Step 2: Generating Report (Token ONLY) ---")
    report_payload = {
        "token": TEST_TOKEN
    }
    test_endpoint("/generate_report", report_payload)
else:
    print("Skipping report generation because /chat failed.")
