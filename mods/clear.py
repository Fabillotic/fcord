import fcord
from requests import request
from datetime import datetime, timedelta
from dateutil.parser import isoparse
import json

def event(e):
    if e["t"].lower() == "message_create":
        if e["d"]["content"].startswith("!clear"):
            if fcord.has_permission(e["d"]["guild_id"], e["d"]["member"]["roles"], 13):
                r = request("GET", "https://discord.com/api/v8/channels/" + e["d"]["channel_id"] + "/messages", headers={"User-Agent": fcord.user_agent, "Authorization": "Bot " + fcord.token})
                
                remove = []
                
                for m in r.json():
                    delta = (isoparse(m["timestamp"]) - timedelta(weeks=2)).timestamp()
                    if not delta < 0:
                        remove.append(m["id"])
                
                request("POST", "https://discord.com/api/v8/channels/" + e["d"]["channel_id"] + "/messages/bulk-delete", data=json.dumps({"messages": remove}), headers={"User-Agent": fcord.user_agent, "Authorization": "Bot " + fcord.token, "Content-Type": "application/json"})
            else:
                fcord.send("You shall not clear this channel!", e["d"]["channel_id"])
