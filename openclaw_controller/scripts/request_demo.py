#!/usr/bin/env python3
import os
import json
import requests

CONFIG_PATH = os.path.expanduser("~/.openclaw/openclaw.json")
with open(CONFIG_PATH) as f:
    config = json.load(f)
TOKEN = config['gateway']['auth']['token']

GATEWAY_URL = "http://127.0.0.1:18789"
SESSION_KEY = "claw_voice"

def send_message(text):
    url = f"{GATEWAY_URL}/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "openclaw/default",
        "messages": [{"role": "user", "content": text}],
        "user": SESSION_KEY
    }
    resp = requests.post(url, headers=headers, json=payload)
    result = resp.json()
    return result['choices'][0]['message']['content']

if __name__ == "__main__":
    reply = send_message("你好")
    print(reply)