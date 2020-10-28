from requests import request
from socket import *
import json
from threading import Thread

token = None
user_agent = None
sock = None

messages = []

def main():
    global sock, token, user_agent, running
    auth = open("auth.txt", "r")
    auth_data = json.loads(auth.read())
    token = auth_data["token"]
    user_agent = auth_data["user_agent"]
    auth.close()
    print("Loaded authorization data. Connecting to server...")
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect(("127.0.0.1", 2020))
    
    t = Thread(target=recv, daemon=True, name="Receive thread")
    t.start()
    
    while True:
        if len(messages) > 0:
            for m in messages:
                print(json.dumps(m, indent=4))
            messages.clear()
    
    print("Goodbye!")

def recv():
    global sock
    
    while True:
        msg = json.loads(sock.recv(8192).decode("utf-8"))
        messages.append(msg)

def call(method, endpoint, data=None):
    global token, user_agent
    h = {"User-Agent": user_agent, "Authorization": "Bot " + token}
    return request(method, "https://discord.com/api/v8" + endpoint, data=data, headers=h)

if __name__ == "__main__":
    main()