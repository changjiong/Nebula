import requests
import json
import sys

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
    # print("Creating conversation...")
    # response = requests.post(
    #     f"{API_URL}/chat/",
    #     headers=headers,
    #     json={"title": "Stream Test"}
    # )
    # conv_id = response.json()["id"]
    
    # Just use stream endpoint directly, it doesn't strictly need a conv_id in payload if we just want to see the stream events.
    # Wait, frontend sends conversation_id in payload, but backend stream_chat endpoint 
    # doesn't clearly require it in MessageCreate... wait, let's check MessageCreate.
    # Backend defines `MessageCreate` with: role, content, model, provider_id. NOT conversation_id.
    # The `send_message` endpoint takes `conversation_id` in path.
    # The `stream_chat` endpoint (POST /stream) DOES NOT take conversation_id in path or body according to `chat.py`.
    # It takes `session: SessionDep, current_user: CurrentUser, message_in: MessageCreate, agent_id: uuid.UUID | None`.
    
    # So we can just hit /stream directly.
    
    print(f"Streaming message to {API_URL}/chat/stream")
    
    payload = {
        "role": "user",
        "content": "Calculate 128 + 355", # Trigger a tool call if possible
        "content": "Calculate 128 + 355", # Trigger a tool call if possible
        "model": "deepseek-reasoner"
    }
    
    try:
        with requests.post(
            f"{API_URL}/chat/stream",
            headers=headers,
            json=payload,
            stream=True
        ) as resp:
            print(f"Status: {resp.status_code}")
            if resp.status_code != 200:
                print(resp.text)
                return

            for line in resp.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    print(decoded_line)
                    # flush to see output immediately
                    sys.stdout.flush()

    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    main()
