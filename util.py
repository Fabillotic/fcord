import fcord
import util
from requests import request
from urllib.parse import quote

util.buttons = []

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

def button(emoji, message, channel, callback, arguments, allowed=None):
	b = {"emoji": emoji, "message": message, "channel": channel, "callback": callback, "arguments": arguments}
	if allowed:
		b["allowed"] = allowed
	util.buttons.append(b)
	r = request("PUT", "https://discord.com/api/channels/" + channel + "/messages/" + message + "/reactions/" + quote(chr(emoji)) + "/@me", headers={"User-Agent": fcord.user_agent, "Authorization": "Bot " + fcord.token})
	return len(util.buttons) - 1

def remove_button(id):
	del util.buttons[id]
