import fcord
import util
import chess

def register():
    util.register_game("chess", chess.get_moves(), chess.move, chess.get_default(), chess.send_help)

def get_default():
    return [["RW", "PW", None, None, None, None, "PB", "RB"], ["NW", "PW", None, None, None, None, "PB", "NB"], ["BW", "PW", None, None, None, None, "PB", "BB"], ["QW", "PW", None, None, None, None, "PB", "QB"], ["KW", "PW", None, None, None, None, "PB", "KB"], ["BW", "PW", None, None, None, None, "PB", "BB"], ["NW", "PW", None, None, None, None, "PB", "NB"], ["RW", "PW", None, None, None, None, "PB", "RB"]]

def get_moves():
    return [[], []]

def move(e, move, player, state, preview):
    pass

def send_help(c):
    fcord.send("Can't help ya right now.", c)
