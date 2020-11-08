import fcord
import subprocess
import os
import pathlib
from requests import request
from PIL import Image, ImageDraw, ImageFont
from urllib.parse import quote
import time

waiting = []
matches = []

def event(e):
	if e["t"].lower() == "message_create":
		if e["d"]["content"].startswith("!tic") and not "bot" in e["d"]["author"]:
			if e["d"].get("guild_id"):
				c = e["d"]["content"]
				s = c.split(" ")
				if len(s) > 1:
					if s[1].lower() == "start":
						print("START")
						start(e)
					elif s[1].lower() == "join":
						print("JOIN")
						join(e)
					elif s[1].lower() == "stop" or s[1].lower() == "exit":
						print("STOP")
						stop(e)
					elif s[1].lower() == "help":
						send_help(e)
					else:
						print("PLAY")
						play(e)
				elif len(s) == 1:
					send_help(e)
			else:
				print("Not in guild!")
				send("You have to be in a guild chat to play tictactoe!", e)
	if e["t"].lower() == "message_reaction_add" and not "bot" in e["d"]["member"]["user"]:
		emoji = ord(e["d"]["emoji"]["name"])
		print(emoji)
		
		if emoji == 9989 or emoji == 10060:
			w = None
			for x in waiting:
				if x[1] == e["d"]["member"]["user"]["id"]:
					if x[2][0] == e["d"]["message_id"]:
						w = x
						break
			
			if w:
				if emoji == 9989: #Accept
					print("Accept")
					if x[0][0] == e["d"]["member"]["user"]["id"]:
						print("Currently in game!")
						return
				
				request("DELETE", "https://discord.com/api/v8/channels/" + e["d"]["channel_id"] + "/messages/" + e["d"]["message_id"] + "/reactions/" + quote(chr(10060)), headers={"Authorization": "Bot " + fcord.token, "User-Agent": fcord.user_agent})
				time.sleep(0.25)
				request("DELETE", "https://discord.com/api/v8/channels/" + e["d"]["channel_id"] + "/messages/" + e["d"]["message_id"] + "/reactions/" + quote(chr(9989)), headers={"Authorization": "Bot " + fcord.token, "User-Agent": fcord.user_agent})
				
				waiting.remove(w)
				print("Removed from waiting.")
				
				if emoji == 10060: #Deny
					print("Deny")
					return
				
				match = [[w[0], w[1], 1], 0]
				matches.append(match)
				send_board(e["d"]["channel_id"], match)
			else:
				print("YOU SHALL NOT REACT!")
				request("DELETE", "https://discord.com/api/v8/channels/" + e["d"]["channel_id"] + "/messages/" + e["d"]["message_id"] + "/reactions/" + quote(chr(emoji)) + "/" + e["d"]["user_id"], headers={"Authorization": "Bot " + fcord.token, "User-Agent": fcord.user_agent})
def send_help(e):
	print("HELP")
	fcord.send_embed("Tic Tac Toe", {"fields": [{"name": "Commands", "value": "!tic start @User -> Start a match.\n!tic join @User -> Join a match you have been invited to.\n!tic (number from 1 to 9) -> Make a move.\n!tic stop -> Stop waiting / playing.", "inline": True}]}, e["d"]["channel_id"])

def start(e):
	s = e["d"]["content"].split(" ")
	
	for x in waiting:
		if x[0] == e["d"]["author"]["id"]:
			print("Already in waiting!")
			send("You are already waiting.", e)
			return
	for x in matches:
		if x[0][0] == e["d"]["author"]["id"]:
			print("Currently in game!")
			send("You are already in a game!", e)
			return
	
	if len(s) > 2:
		u = s[2]
		if u.startswith("<@") and u.endswith(">"):
			if "<@" in u[2:]:
				send("Invalid mention!", e)
				return
			u = u[2:-1]
			if u.startswith("!"):
				u = u[1:]
			w = [e["d"]["author"]["id"], u]
			print("About to add to waiting!")
			msg = send("Waiting for partner! You partner can click on the reaction to join easily.", e).json()
			request("PUT", "https://discord.com/api/v8/channels/" + msg["channel_id"] + "/messages/" + msg["id"] + "/reactions/" + quote(chr(9989)) + "/@me", headers={"Authorization": "Bot " + fcord.token, "User-Agent": fcord.user_agent})
			time.sleep(0.25)
			request("PUT", "https://discord.com/api/v8/channels/" + msg["channel_id"] + "/messages/" + msg["id"] + "/reactions/" + quote(chr(10060)) + "/@me", headers={"Authorization": "Bot " + fcord.token, "User-Agent": fcord.user_agent})
			w.append((msg["id"], msg["channel_id"]))
			waiting.append(tuple(w))

def join(e):
	s = e["d"]["content"].split(" ")
	
	for x in matches:
		if x[0][0] == e["d"]["author"]["id"]:
			print("Currently in game!")
			send("You are already in a game!", e)
			return
	
	if len(s) > 2:
		u = s[2]
		if u.startswith("<@") and u.endswith(">"):
			u = u[2:-1]
			if u.startswith("!"):
				u = u[1:]
			notwaiting = None
			for x in waiting:
				if x[1] == e["d"]["author"]["id"]:
					if x[0] == u:
						print("Started match!")
						send("Game started!", e)
						match = [[x[0], x[1], 1], 0]
						matches.append(match)
						send_board(e["d"]["channel_id"], match)
						notwaiting = x
						break
			if notwaiting:
				waiting.remove(notwaiting)
			else:
				print("No match started.")
				send("No one wanted to play with you.", e)

def play(e):
	s = e["d"]["content"].split(" ")
	a = e["d"]["author"]["id"]
	
	match = None
	for m in matches:
		if m[0][0] == a or m[0][1] == a:
			match = m
			break
	
	if not match:
		print("NOT IN A MATCH!")
		send("You are not in a game.", e)
		return
	
	match = None
	for m in matches:
		if m[0][0] == a and m[0][2] == 1:
			match = m
			break
		if m[0][1] == a and m[0][2] == 2:
			match = m
			break
	
	if not match:
		print("NOT YOUR TURN!")
		send("Wait for your turn!", e)
		return
	
	if len(s) > 1:
		try:
			i = int(s[1])
			if i < 1 or i > 9:
				print("INVALID!")
				send("Invalid number.", e)
				return
			i = i - 1
			if ((match[1] >> (i * 2)) & 0b11) == 0:
				match[1] = match[1] | (match[0][2] << (i * 2))
				if match[0][2] == 1:
					match[0][2] = 2
				else:
					match[0][2] = 1
				print("Made move! Board: " + str(match[1]))
				win = send_board(e["d"]["channel_id"], match)
				print(win)
				if (win & 0b11) != 0:
					print("WIN: " + str(win & 0b11))
					matches.remove(match)
					print("REMOVED MATCH!")
					send(("circle" if (win & 0b11 == 2) else "cross") + " won!", e)
				else:
					full = True
					print(bin(match[1]))
					for i in range(9):
						if (match[1] >> (i * 2)) & 0b11 == 0:
							full = False
					if full:
						print("BOARD FULL!")
						send("It's a tie! Nobody won. Good job!", e)
						matches.remove(match)
					else:
						send("Next turn: " + ("circle" if match[0][2] == 2 else "cross"), e)
			else:
				print("INCORRECT POSITIONING!")
				send("Spot taken.", e)
		except ValueError:
			print("INVALID!")
			send("Invalid number.", e)

def stop(e):
	a = e["d"]["author"]["id"]
	remove_waiting = None
	for x in waiting:
		if x[0] == a:
			remove_waiting = x
			break
	if remove_waiting:
		waiting.remove(remove_waiting)
		print("Removed wait!")
		send("You are not waiting anymore.", e)
	
	remove_match = None
	for m in matches:
		if m[0][0] == a and m[0][2] == 1:
			remove_match = m
			break
		if m[0][1] == a and m[0][2] == 2:
			remove_match = m
			break
	if remove_match:
		matches.remove(remove_match)
		print("Removed match!")
		send("You left the game.", e)

def send(content, e):
	return fcord.send(content, e["d"]["channel_id"])

def make_board(num):
	state =[]
	
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

def send_board(channel, match):
	win = make_board(match[1])
	f = open(os.path.abspath(pathlib.Path(pathlib.Path(__file__).parent, "tic.png")), "rb")
	r = request("POST", "https://discord.com/api/channels/" + channel + "/messages", headers={"Authorization": "Bot " + fcord.token, "User-Agent": fcord.user_agent}, files={"tic.png": f.read(), "payload_json": (None, '{"content": "Board:", "embed": {"image": {"url": "attachment://tic.png"}}}'.encode("utf-8"))})
	f.close()
	os.remove(os.path.abspath(pathlib.Path(pathlib.Path(__file__).parent, "tic.png")))
	return win