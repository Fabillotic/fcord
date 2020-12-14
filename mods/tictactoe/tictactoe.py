import fcord
import util
import tictactoe
import os
import pathlib
from requests import request
from PIL import Image, ImageDraw, ImageFont

def register():
    t = util.register_game("tic", [[str(x) for x in range(1, 10)]], tictactoe.move, 0, tictactoe.send_help)
    
def move(e, move, player, state, preview):
    if preview:
        send_board(e["d"]["channel_id"], state)
        return
    i = int(move[0]) - 1
    if ((state >> (i * 2)) & 0b11) == 0:
        state = state | ((player + 1) << (i * 2))
        win = send_board(e["d"]["channel_id"], state)
        if (win & 0b11) != 0:
            fcord.send("You have won!", e["d"]["channel_id"])
            return state, True
        else:
            full = True
            for i in range(9):
                if (state >> (i * 2)) & 0b11 == 0:
                    full = False
            if full:
                fcord.send("It's a tie! Nobody won. Good job!", e["d"]["channel_id"])
                return state, True
    else:
        fcord.send("Invalid move!", e["d"]["channel_id"])
        return

    return state, False

def send_help(c):
    fcord.send("The help screen will be implemented later. Sometime... Maybe... If I remember...", c)

def make_board(num):
    state = []
    
    for i in range(9):
        state.append((num >> (i * 2)) & 0b11)
    
    win = get_win(state)
    
    img = Image.new("RGB", (600, 600), color=(255, 255, 255))
    font = ImageFont.truetype(os.path.abspath(pathlib.Path(pathlib.Path(__file__).parent, "Roboto/Roboto-Medium.ttf")), 100)
    g = ImageDraw.Draw(img)
    g.line((200, 0, 200, 600), fill=0, width=4, joint="curve")
    g.line((400, 0, 400, 600), fill=0, width=4, joint="curve")
    g.line((0, 200, 600, 200), fill=0, width=4, joint="curve")
    g.line((0, 400, 600, 400), fill=0, width=4, joint="curve")
    
    for i in range(9):
        x = (i % 3) * 200
        y = (2 - (i // 3)) * 200
        
        if state[i] == 1:
            g.line((x + 20, y + 20, x + 180, y + 180), fill=0, width=4, joint="curve")
            g.line((x + 180, y + 20, x + 20, y + 180), fill=0, width=4, joint="curve")
        elif state[i] == 2:
            g.ellipse((x + 20, y + 20, x + 180, y + 180), fill=None, outline=0, width=4)
        else:
            g.text((x + 100, y + 100), str(i + 1), fill=(200, 200, 200), font=font, anchor="mm")
    
    if win[0] != 0:
        x1 = (win[2][0] % 3) * 200
        y1 = (2 - (win[2][0] // 3)) * 200
        x2 = (win[2][2] % 3) * 200
        y2 = (2 - (win[2][2] // 3)) * 200
        
        if x1 != x2 and y1 != y2: #Must be a diagonal
            if x1 < x2: #Left to right
                g.line((0, 0, 600, 600), fill=255, width=8, joint="curve")
            else: #Right to left
                g.line((600, 0, 0, 600), fill=255, width=8, joint="curve")
        elif y1 == y2: #Must be a horizontal
            g.line((0, y1 + 100, 600, y1 + 100), fill=255, width=8, joint="curve")
        else: #Must be a vertical
            g.line((x1 + 100, 0, x1 + 100, 600), fill=255, width=8, joint="curve")
    
    img.save(os.path.abspath(pathlib.Path(pathlib.Path(__file__).parent, "tic.png")))
    img.close()
    return win[0]

def get_win(state):
    if state[4] != 0: #Is the center set?
        if state[5] == state[4] and state[4] == state[3]:
            return (state[4] | (5 << 2 | 4 << 6 | 3 << 10), "mr", (5, 4, 3)) #Middle row
        if state[6] == state[4] and state[4] == state[2]:
            return (state[4] | (6 << 2 | 4 << 6 | 2 << 10), "lr", (6, 4, 2)) #Left to right diagonal
        if state[7] == state[4] and state[4] == state[1]:
            return (state[4] | (7 << 2 | 4 << 6 | 1 << 10), "mc", (7, 4, 1)) #Middle column
        if state[8] == state[4] and state[4] == state[0]:
            return (state[4] | (8 << 2 | 4 << 6 | 0 << 10), "rl", (8, 4, 0)) #Right to left diagonal
    
    if state[7] != 0 and state[6] == state[7] and state[7] == state[8]:
        return (state[7] | (6 << 2 | 7 << 6 | 8 << 10), "ur", (6, 7, 8)) #Upper row
    if state[1] != 0 and state[0] == state[1] and state[1] == state[2]:
        return (state[1] | (0 << 2 | 1 << 6 | 2 << 10), "dr", (0, 1, 2)) #Lower row
    if state[5] != 0 and state[2] == state[5] and state[5] == state[8]:
        return (state[5] | (2 << 2 | 5 << 6 | 8 << 10), "rc", (2, 5, 8)) #Right column
    if state[3] != 0 and state[0] == state[3] and state[3] == state[6]:
        return (state[3] | (0 << 2 | 3 << 6 | 6 << 10), "lc", (0, 3, 6)) #Left column
    return (0, "", (0, 0, 0))

def send_board(channel, state):
    win = make_board(state)
    f = open(os.path.abspath(pathlib.Path(pathlib.Path(__file__).parent, "tic.png")), "rb")
    r = request("POST", "https://discord.com/api/channels/" + channel + "/messages", headers={"Authorization": "Bot " + fcord.token, "User-Agent": fcord.user_agent}, files={"tic.png": f.read(), "payload_json": (None, '{"content": "Board:", "embed": {"image": {"url": "attachment://tic.png"}}}'.encode("utf-8"))})
    f.close()
    os.remove(os.path.abspath(pathlib.Path(pathlib.Path(__file__).parent, "tic.png")))
    return win
