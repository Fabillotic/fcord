import fcord
import util
import chess
from requests import request

def register():
    util.register_game("chess", chess.get_moves(), chess.move, chess.get_default(), chess.send_help)

def get_default():
    return [["RW", "PW", None, None, None, None, "PB", "RB"], ["NW", "PW", None, None, None, None, "PB", "NB"], ["BW", "PW", None, None, None, None, "PB", "BB"], ["QW", "PW", None, None, None, None, "PB", "QB"], ["KW", "PW", None, None, None, None, "PB", "KB"], ["BW", "PW", None, None, None, None, "PB", "BB"], ["NW", "PW", None, None, None, None, "PB", "NB"], ["RW", "PW", None, None, None, None, "PB", "RB"]]

def get_moves():
    x = []
    for y in range(1, 9):
        a = chr(96 + y)
        for z in range(1, 9):
            a += str(z)
            x.append(a)
    return [x, x]

def move(e, move, player, state, preview):
    if preview:
        send_board(state, e["d"]["channel_id"])
        return


def send_board(state, channel):
    board = "  1 2 3 4 5 6 7 8\n"
    for r in range(7, -1, -1):
        board += chr(97 + r) + " "
        for c in range(0, 8):
            board += get_piece_char(state[r][c])
        board += "\n"
    board = board[:-1]
    print(board)
    r = request("POST", "https://discord.com/api/channels/" + channel + "/messages", data={"content": "Board:\n" + board}, headers={"Authorization": "Bot " + fcord.token, "User-Agent": fcord.user_agent})
    print(r.text)

def get_piece_char(p):
    if not p:
        return chr(int("2b1c", 16))
    elif p == "RW":
        return chr(int("2656", 16))
    elif p == "PW":
        return chr(int("2659", 16))
    elif p == "PB":
        return chr(int("265F", 16))
    elif p == "RB":
        return chr(int("265C", 16))
    elif p == "NW":
        return chr(int("2658", 16))
    elif p == "NB":
        return chr(int("265E", 16))
    elif p == "BW":
        return chr(int("2657", 16)) + chr(int("2009", 16))
    elif p == "BB":
        return chr(int("265D", 16)) + chr(int("2009", 16))
    elif p == "QW":
        return chr(int("2655", 16))
    elif p == "QB":
        return chr(int("265B", 16))
    elif p == "KW":
        return chr(int("2654", 16))
    elif p == "KB":
        return chr(int("265A", 16))

def send_help(c):
    fcord.send("Can't help ya right now.", c)
