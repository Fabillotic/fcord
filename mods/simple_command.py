import fcord
import util

def event(e):
    if e["t"].lower() == "message_create":
        if e["d"]["content"].startswith("!"):
            command(e["d"]["content"][1:], e["d"]["channel_id"], e["d"]["author"]["id"])

def command(c, channel, user):
    s = c.split(" ")
    if s[0].lower() == "test":
        print("(SIMPLE) testing...")
        j = fcord.send("TEST!", channel).json()
        util.button(0x1F36A, j["id"], channel, back, [], [user])

def back(e, args):
    fcord.send("click!", e["d"]["channel_id"])
