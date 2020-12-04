import fcord
import util
import chess
from requests import request

chess.waiting = [] #Content -> [%channel%, %waiting_user%, %waiting_for_user%, %response_message_id%]
chess.matches = [] #Content -> [%channel%, %player0%, %player1%, %current_player -> 0 / 1%, [%piece_id / -1%]]
chess.pieces = dict(zip(["k", "q", "r1", "r2", "b1", "b2", "n1", "n2"] + ["p" + str(x) for x in range(1, 9)], [x for x in range(16)]))

def event(e):
    if e["t"].lower() == "message_create":
        if e["d"]["content"].lower().startswith("!chess") and not "bot" in e["d"]["author"]:
            a = e["d"]["content"].lower().split(" ")
            if len(a) > 1:
                if a[1] == "start":
                    start(e, a)
                elif a[1] == "join":
                    join(e, a)
                elif a[1] == "stop":
                    stop(e, a)
                elif a[1] == "help":
                    send_help(e)
                elif a[1] in chess.pieces.keys(): #Is it chess piece?
                    if len(a) > 2: #Coordinates specified?
                        if len(a[2]) == 2: #Coordinates right length?
                            if a[2][0] in [chr(x + 97) for x in range(0, 8)] and a[2][1] > 0 and a[2][1] < 9: #Coordinates in correct format?
                                move(e, chess.pieces[a[1]], ord(a[2][0]) - 97, a[2][1] - 1)
                            else:
                                fcord.send("Invalid coordinate! Example: 'a3'", e["d"]["channel_id"])
                        else:
                            fcord.send("Invalid coordinate! Example: 'a3'", e["d"]["channel_id"])
                    else:
                        fcord.send("Invalid syntax! Syntax: '!chess (piece) (position)'", e["d"]["channel_id"])
                else: #Invalid command!
                    send_help(e)

def start(e, a):
    for x in chess.waiting:
        if x[1] == e["d"]["author"]["id"]:
            fcord.send("You are already waiting for a user to join! Stop waiting by typing '!chess stop'.", e["d"]["channel_id"])
            return
    for x in chess.matches:
        if x[1] == e["d"]["author"]["id"] or x[2] == e["d"]["author"]["id"]:
            fcord.send("You are already in a game! Stop playing by typing '!chess stop'.", e["d"]["channel_id"])
            return
    if len(a) > 2:
        if a[2].startswith("<@") and a[2].endswith(">") and not ">" in a[2][:-1]:
            u = a[2][2:-1]
            if u.startswith("!"):
                u = u[1:]
            msg = fcord.send("Added to waiting. Your partner can use the reactions to join easily.").json()
            chess.waiting.append(e["d"]["channel_id"], e["d"]["author"]["id"], u, msg["id"])
        else:
            fcord.send("Syntax: '!tic start @User'")

def join(e, a):
    pass

def stop(e, a):
    pass

def send_help(e):
    pass

def move(e, p, x, y):
    pass
