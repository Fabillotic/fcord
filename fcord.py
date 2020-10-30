from requests import request
from socket import *
import json
from threading import Thread
import sys
import os
import fcord
import pathlib

token = None
user_agent = None

listeners = []
events = []

def main():
    global sock, token, user_agent, events, listeners
    
    sys.path.append(os.path.abspath(pathlib.Path(pathlib.Path(__file__).parent, "mods").resolve()))
    print(sys.path)
    import simple_command
    listeners.append(simple_command.event)
    
    fcord.call = call
    
    auth = open("auth.txt", "r")
    auth_data = auth.read()
    auth_data = json.loads(auth_data)
    token = auth_data["token"]
    user_agent = auth_data["user_agent"]
    auth.close()
    print("Loaded authorization data. Connecting to server...")
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect(("127.0.0.1", 2020))
    
    t = Thread(target=recv, daemon=True, name="Receive thread")
    t.start()
    
    while True:
        done = []
        for n, e in enumerate(events):
            print("Event: " + json.dumps(e))
            for l in listeners:
                l(e)
            done.append(n)
        for n in done:
            events = events[:n] + events[n+1:]
    
    print("Goodbye!")

def recv():
    global sock, messages, events
    
    while True:
        data = sock.recv(8192).decode("utf-8")
        event = json.loads(data)
        print("Message")
        events.append(event)

def call(method, endpoint, data=None, headers={}):
    global token, user_agent
    
    h = {"User-Agent": user_agent, "Authorization": "Bot " + token}
    for x in headers:
        h[x] = headers[x]
    return request(method, "https://discord.com/api/v8" + endpoint, data=data, headers=h)

if __name__ == "__main__":
    main()
