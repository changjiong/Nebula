import requests
import json

API_URL = "http://localhost:8000/api/v1"
EMAIL = "admin@example.com"
PASSWORD = "changethis"

def login():
    response = requests.post(
        f"{API_URL}/login/access-token",
        data={"username": EMAIL, "password": PASSWORD}
    )
    if response.status_code != 200:
        print(f"Login failed: {response.status_code} {response.text}")
        return None
    return response.json()["access_token"]

def main():
    token = login()
    if not token:
        return

    headers = {
        "Authorization": f"Bearer {token}",
        "Origin": "http://localhost:5173"
    }

    # 1. Create Conversation
    print("Creating conversation...")
    response = requests.post(
        f"{API_URL}/chat/",
        headers=headers,
        json={"title": "CORS Test"}
    )
    if response.status_code != 200:
        print(f"Failed to create conversation: {response.status_code} {response.text}")
        return
    
    conv_id = response.json()["id"]
    print(f"Conversation ID: {conv_id}")

    # 2. Send Message (GET/POST)
    print(f"Sending message to {API_URL}/chat/{conv_id}/send")
    
    # Simulate the request that failed
    payload = {
        "role": "assistant",
        "content": "Test content",
        # "model": "deepseek-chat" # Optional
    }
    
    try:
        resp = requests.post(
            f"{API_URL}/chat/{conv_id}/send",
            headers=headers,
            json=payload
        )
        print(f"Status: {resp.status_code}")
        print("Headers:", json.dumps(dict(resp.headers), indent=2))
        print("Body:", resp.text)
        
        # Check for CORS headers (though requests client doesn't enforce them, we can see if they exist)
        if "access-control-allow-origin" not in resp.headers.get("access-control-allow-origin", "").lower() and \
           "access-control-allow-origin" not in {k.lower(): v for k, v in resp.headers.items()}:
             print("WARNING: Access-Control-Allow-Origin header MISSING!")
        else:
             print("CORS Header present.")

    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    main()
