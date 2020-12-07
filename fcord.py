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
    sys.path.append(os.path.abspath(pathlib.Path(pathlib.Path(__file__).parent, "mods/tictactoe").resolve()))
    sys.path.append(os.path.abspath(pathlib.Path(pathlib.Path(__file__).parent, "mods/chess").resolve()))

    import simple_command; listeners.append(simple_command.event)
    import util; listeners.append(util.event)
    import xyz; xyz.register()
    import tictactoe; tictactoe.register()
    import clear; listeners.append(clear.event)
    import chess; listeners.append(chess.event)

    fcord.call = call
    fcord.has_permission = has_permission
    fcord.send = send
    
    auth = open("auth.txt", "r")
    auth_data = auth.read()
    auth_data = json.loads(auth_data)
    token = auth_data["token"]
    user_agent = auth_data["user_agent"]
    fcord.token = token
    fcord.user_agent = user_agent
    auth.close()
    print("Loaded authorization data. Connecting to server...")
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect(("127.0.0.1", 2020))
    
    t = Thread(target=recv, daemon=True, name="Receive thread")
    t.start()
    
    while True:
        done = []
        for n, e in enumerate(events):
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
        events.append(event)

def has_permission(guild, member_roles, permission):
    roles = request("GET", "https://discord.com/api/v8/guilds/" + guild + "/roles", headers={"Authorization": "Bot " + fcord.token, "User-Agent": fcord.user_agent}).json()
    hasPerm = False
    for r in roles:
        for mr in member_roles:
            if r["id"] == mr and ((int(r["permissions"]) >> permission) & 1) == 1:
                hasPerm = True
                break
    return hasPerm

def send(content, channel):
    return request("POST", "https://discord.com/api/channels/" + channel + "/messages", headers={"Authorization": "Bot " + fcord.token, "User-Agent": fcord.user_agent, "Content-Type": "application/json"}, data='{"content": "' + content + '"}')

def send_embed(content, embed, channel):
    return request("POST", "https://discord.com/api/channels/" + channel + "/messages", headers={"Authorization": "Bot " + fcord.token, "User-Agent": fcord.user_agent, "Content-Type": "application/json"}, data='{"content": "' + content + '", "embed": ' + json.dumps(embed) + '}')
    
def call(method, endpoint, data=None, headers={}):
    global token, user_agent
    
    h = {"User-Agent": user_agent, "Authorization": "Bot " + token}
    for x in headers:
        h[x] = headers[x]
    return request(method, "https://discord.com/api/v8" + endpoint, data=data, headers=h)

if __name__ == "__main__":
    main()
