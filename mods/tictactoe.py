import fcord
import subprocess
import os
import pathlib
from requests import request

waiting = []
matches = []

def event(e):
	if e["t"].lower() == "message_create":
		if e["d"]["content"].startswith("!tic"):
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
				else:
					print("PLAY")
					play(e)

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
			u = u[2:-1]
			if u.startswith("!"):
				u = u[1:]
			waiting.append((e["d"]["author"]["id"], u))
			print("Added to waiting!")
			send("Waiting for partner!", e)

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
			print("Found mention!")
			u = u[2:-1]
			if u.startswith("!"):
				u = u[1:]
			notwaiting = None
			print("Waiting:")
			print(waiting)
			for x in waiting:
				if x[1] == e["d"]["author"]["id"]:
					if x[0] == u:
						print("Started match!")
						send("Game started!", e)
						matches.append([[x[0], x[1], 1], 0])
						notwaiting = x
						break
			print("Notwaiting:")
			print(notwaiting)
			if notwaiting:
				waiting.remove(notwaiting)
			else:
				print("No match started.")
				send("No one wanted to play with you.", e)
	
	print("Matches:")
	print(matches)
	print("Waiting:")
	print(waiting)

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
				os.chdir(os.path.abspath(pathlib.Path(__file__).parent.resolve()))
				p = subprocess.Popen(["java", "-jar", "TicTacToe.jar", "tic.png", str(match[1])], stdout=subprocess.PIPE)
				win = int(p.stdout.read().decode("utf-8"))
				print(win)
				f = open("tic.png", "rb")
				d = f.read()
				f.close()
				r = request("POST", "https://discord.com/api/channels/" + e["d"]["channel_id"] + "/messages", headers={"Authorization": "Bot " + fcord.token, "User-Agent": fcord.user_agent}, files={"tic.png": d, "payload_json": (None, '{"content": "Board:", "embed": {"image": {"url": "attachment://tic.png"}}}'.encode("utf-8"))})
				os.remove("tic.png")
				if (win & 0b11) != 0:
					print("WIN: " + str(win & 0b11))
					matches.remove(match)
					print("REMOVED MATCH!")
					print(matches)
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
	r = request("POST", "https://discord.com/api/channels/" + e["d"]["channel_id"] + "/messages", headers={"Authorization": "Bot " + fcord.token, "User-Agent": fcord.user_agent, "Content-Type": "application/json"}, data='{"content": "' + content + '"}')