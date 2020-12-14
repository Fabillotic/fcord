import fcord
import util
from requests import request
from urllib.parse import quote
from random import getrandbits

def event(e):
    if e["t"].lower() == "message_reaction_add" and not "bot" in e["d"]["member"]["user"]:
        emoji = ord(e["d"]["emoji"]["name"])
        message = e["d"]["message_id"]
        channel = e["d"]["channel_id"]
        
        for b in buttons:
            if b["emoji"] == emoji and b["message"] == message and b["channel"] == channel:
                a = False
                if "allowed" in b:
                    if e["d"]["member"]["user"]["id"] in b["allowed"]:
                        a = True
                else:
                    a = True
                r = request("DELETE", "https://discord.com/api/channels/" + channel + "/messages/" + message + "/reactions" + "/" + quote(chr(emoji)) + "/" + e["d"]["user_id"], headers={"User-Agent": fcord.user_agent, "Authorization": "Bot " + fcord.token})
                if a:
                    b["callback"](e, b["arguments"])

    elif e["t"].lower() == "message_create" and not "bot" in e["d"]["author"]:
        if e["d"]["content"].startswith("!"):
            game = None
            c = e["d"]["content"][1:]
            c = c[:(c.find(" ") if (" " in c) else None)] #Some python trickery to get everything between "!" and " " or END
            
            for g in util.games:
                if g[0] == c:
                    game = g
                    break
            
            if not game:
                return
            
            com = e["d"]["content"].lower()[(2 + len(game[0])):]
            coms = com.split(" ")

            if len(coms) > 0 and not com == "":
                a = e["d"]["author"]["id"]
                if coms[0] == "start":
                    #check if already waiting, playing, add to waiting
                    for x in game[3]:
                        if x[0] == a:
                            fcord.send("You are already waiting!", e["d"]["channel_id"])
                            return
                    for x in game[4]:
                        if x[0] == a or x[1] == a:
                            fcord.send("You are already ingame!", e["d"]["channel_id"])
                            return
                    u = None
                    if len(coms) > 1:
                        u = util.parse_mention(coms[1])
                        if not u:
                            fcord.send("Invalid mention!", e["d"]["channel_id"])
                            return
                    else:
                        fcord.send("Syntax: !" + game[0] + " start @User")
                        return
                    
                    game[3].append([a, u, None, e["d"]["channel_id"]])
                    fcord.send("Added to waiting!", e["d"]["channel_id"])
                elif coms[0] == "join":
                    #check if invited by that person, check if not in game, remove inviter from waiting, remove invitee from waiting?, channel check, make a match
                    u = None
                    if len(coms) > 1:
                        u = util.parse_mention(coms[1])
                        if not u:
                            fcord.send("Invalid mention!", e["d"]["channel_id"])
                            return
                    else:
                        fcord.send("Syntax: !" + game[0] + " join @User")
                        return
                    w = None
                    wn = -1
                    for n, x in enumerate(game[3]):
                        if x[1] == a and x[0] == u:
                            w = x
                            wn = n
                    if not w:
                        fcord.send("You have not been invited!", e["d"]["channel_id"])
                        return
                    if w[3] != e["d"]["channel_id"]:
                        fcord.send("You have to join in the same channel that you were invited in!", e["d"]["channel_id"])
                        return
                    for x in game[4]:
                        if x[0] == a or x[1] == a:
                            fcord.send("You are already ingame!", e["d"]["channel_id"])
                            return
                    del game[3][wn]
                    wn = -1
                    for n, x in enumerate(game[3]):
                        if x[0] == a:
                            wn = n
                            break
                    if wn != -1:
                        del game[3][wn]
                    s = getrandbits(1)
                    fcord.send("<@" + [a, u][s] + "> has the first turn!", e["d"]["channel_id"])
                    game[4].append([a, u, s, game[5]])
                    game[2](e, None, s, game[5], True) #Invoke preview
                elif coms[0] == "stop":
                    #check if waiting -> stop waiting, check if playing -> stop playing
                    y = -1
                    for n, x in enumerate(game[3]):
                        if x[0] == a:
                            y = n
                            break
                    if y != -1:
                        del game[3][y]
                        fcord.send("You were removed from waiting.", e["d"]["channel_id"])
                    y = -1
                    for n, x in enumerate(game[4]):
                        if x[0] == a or x[1] == a:
                            y = n
                            break
                    if y != -1:
                        del game[4][y]
                        fcord.send("You left the match.", e["d"]["channel_id"])
                elif coms[0] == "help":
                    game[6](e["d"]["channel_id"])
                    return
                elif coms[0] in game[7]: #Check for extra subcommands.
                    game[7][coms[0]](e, game, coms[1:])
                else:
                    valid = True
                    for n, x in enumerate(coms):
                        if not x in game[1][n]:
                            valid = False
                            break
                    if not valid:
                        fcord.send("Invalid command or move!", e["d"]["channel_id"])
                        return
                    #check if in game, check if current player, if yes, run callback, update state, update current, check end
                    p = None
                    pn = -1
                    for n, x in enumerate(game[4]):
                        if x[0] == a or x[1] == a:
                            p = x
                            pn = n
                    if p:
                        if p[p[2]] == a:
                            r = game[2](e, coms, p[2], p[3], False)
                            if not r:
                                r = (None, False)
                            state, end = r
                            p[3] = state
                            p[2] = 1 - p[2]
                            if end:
                                del game[4][pn]
                        else:
                            fcord.send("Wait for your turn!", e["d"]["channel_id"])
                            return
                    else:
                        fcord.send("You are not in a game!", e["d"]["channel_id"])
                        return
            else:
                game[6](e["d"]["channel_id"])
                return

util.buttons = []

def button(emoji, message, channel, callback, arguments, allowed=None):
    b = {"emoji": emoji, "message": message, "channel": channel, "callback": callback, "arguments": arguments}
    if allowed:
        b["allowed"] = allowed
    util.buttons.append(b)
    r = request("PUT", "https://discord.com/api/channels/" + channel + "/messages/" + message + "/reactions/" + quote(chr(emoji)) + "/@me", headers={"User-Agent": fcord.user_agent, "Authorization": "Bot " + fcord.token})
    return len(util.buttons) - 1

def remove_button(id):
    del util.buttons[id]

util.games = [] #Contains: command(without !), moves(array(array(combinations))), on_move(callback on move), waiting(array(player, waiting_for, response_message, channel)), playing(array(player0, player1, current_player(0 / 1), state)), default_state, on_help(callback for help screen), extra_commands(dict(string(command), function(callback)))
#On move callbacks -> parameters: default -> event, move(array(combinations)), current_player(0 / 1), state, False
#                                 preview -> event, None, current_player(0 / 1), default_state, True
#                     returns: valid move -> new state, end(boolean)
#                              invalid move -> None
#                              start preview -> None
#On help callbacks -> parameters: channel
#                     returns: None
#Game subcommand callbacks -> parameters: event, game instance, subsubcommands
#                             returns: None

def register_game(command, moves, on_move, state, on_help):
    util.games.append([command, moves, on_move, [], [], state, on_help, dict()])
    return len(util.games) - 1

def register_game_subcommand(game_id, command, callback):
    util.games[game_id][7][command] = callback

def parse_mention(mention):
    i = None
    if mention.startswith("<@") and mention.endswith(">") and not "<@" in mention[2:] and not ">" in mention[:-1]:
        i = mention[2:-1]
        if i.startswith("!"):
            i = i[1:]
    return i
