import sys
import json
import time
import requests
import websocket
import threading

def authenticate(token):
    headers = {"Authorization": token, "Content-Type": "application/json"}
    validate = requests.get('https://discordapp.com/api/v9/users/@me', headers=headers)
    if validate.status_code != 200:
        print(f"[ERROR] Token {token} might be invalid. Please check it again.")
        sys.exit()
    return headers

def onliner(token, status, custom_status):
    headers = authenticate(token)
    ws = websocket.WebSocket()
    while True:
        try:
            ws.connect("wss://gateway.discord.gg/?v=9&encoding=json")
            break
        except Exception as e:
            print(f"Error connecting: {str(e)}")
            print("Retrying connection...")
            time.sleep(10)
    start = json.loads(ws.recv())
    heartbeat = start["d"]["heartbeat_interval"]
    auth = {
        "op": 2,
        "d": {
            "token": token,
            "properties": {
                "$os": "Windows 10",
                "$browser": "Google Chrome",
                "$device": "Windows",
            },
            "presence": {"status": status, "afk": False},
        },
        "s": None,
        "t": None,
    }
    ws.send(json.dumps(auth))
    cstatus = {
        "op": 3,
        "d": {
            "since": 0,
            "activities": [
                {
                    "type": 4,
                    "state": custom_status,
                    "name": "Custom Status",
                    "id": "custom",
                }
            ],
            "status": status,
            "afk": False,
        },
    }
    ws.send(json.dumps(cstatus))
    online = {"op": 1, "d": "None"}
    time.sleep(heartbeat / 1000)
    ws.send(json.dumps(online))

def run_onliner(token, status, custom_status):
    headers = authenticate(token)
    userinfo = requests.get('https://discordapp.com/api/v9/users/@me', headers=headers).json()
    username = userinfo["username"]
    discriminator = userinfo["discriminator"]
    userid = userinfo["id"]
    print(f"Logged in as {username}#{discriminator} ({userid}).")
    while True:
        try:
            onliner(token, status, custom_status)
        except Exception as e:
            print(f"Error occurred: {str(e)}")
            print("Attempting to reconnect...")
            time.sleep(10)
            continue
        time.sleep(30)

if __name__ == "__main__":
    accounts = [
        {"token": "MTI4NDQzMDk3NzU1MjA4OTEyMw.GYMqxY.f_4j00s5C0cOOoSlELz1GLnVc-3HNHl7eHAv_k", "status": "dnd", "custom_status": "Flexibel (meine meimung)"},
        ]

    threads = []

    for account in accounts:
        thread = threading.Thread(target=run_onliner, args=(account["token"], account["status"], account["custom_status"]))
        threads.append(thread)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()
