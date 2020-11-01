import fcord

def event(e):
	if e["t"].lower() == "message_create":
		if e["d"]["content"].startswith("!"):
			command(e["d"]["content"][1:], e["d"]["channel_id"])

def command(c, channel):
	s = c.split(" ")
	if s[0].lower() == "test":
		print("(SIMPLE) testing...")
		fcord.call("POST", "/channels/" + channel + "/messages", data='{"content": "TEST!"}', headers={"Content-Type": "application/json"}).text