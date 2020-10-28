const needle = require("needle");
const WebSocketClient = require("websocket").client;
const fs = require("fs");
const net = require("net");

let confile = "config.txt";
let authfile = "auth.txt";
let config = {};
let url = undefined;
let sequence = null;
let interval = null;
let resume = false;
let session = undefined;

let token = "";
let user_agent = "";

let connection = null;
let receivedAck = true;

function start() {
    try {
        let data = JSON.parse(fs.readFileSync(authfile));
        token = data.token;
        user_agent = data.user_agent;
        console.log("Successfully parsed auth file!");
    }
    catch(err) {
        console.log("Authentication file couldn't be parsed: " + err);
        process.exit(1);
    }
	try {
		let data = fs.readFileSync(confile);
		console.log("Found config: " + data);
		try {
			config = JSON.parse(data);
			session = config.session;
			sequence = config.sequence;
			url = config.url;
			if(session == undefined || sequence == undefined) {console.log("Parse error: Config invalid.");}
			else {resume = true;}
		} catch(err) {console.log("Parse error!"); return;}
	} catch(err) {
		console.log("Config not found.");
		fs.writeFileSync(confile, "{}");
	}
	if(url == undefined) {
		call("GET", "/gateway/bot")
		.then((r) => {
			let d = r.body;
			console.log(d);
			url = d.url + "/?v=8&encoding=json";
			config["url"] = url;
			writeConfig();
			connect();
		})
		.catch((err) => {console.log("Couldn’t get gateway endpoint! " + err);});
	}
	else {
		connect();
	}
}

let server = null;

function connect() {
	clearInterval(interval);
	receivedAck = true;
	
	let websocket = new WebSocketClient();
    clients = [];
    if(server != null) {
        server.close();
        server = null;
    }
    server = net.createServer(tcpserver);
	server.listen(2020, () => {console.log("TCP server listening...");});
    
	websocket.on("connectFailed", function(error) {console.log("Connection error: " + error.toString()); server.close();});
	websocket.on("connect", function(c) {
		console.log("Connected!");
		connection = c;
		connection.on("error", function(error) {console.log("Error: " + error);});
		connection.on("close", function(code, description) {
			console.log("\x1b[31mConnection closed: " + code + " (" + description + ")\x1b[0m");
			if(code == 1006) {
                server.close();
				console.log("\x1b[31m1006 -> Connection terminated! Attempting resume...\x1b[0m");
				resume = true;
				reconnect(false);
			}
		});
		connection.on("message", function(message) {
			if(message.type === "utf8") {
				packet = JSON.parse(message.utf8Data);
				
				if("s" in packet && packet.s != null) {
					sequence = packet.s;
					console.log("\x1b[2mNew seqence: " + sequence + "\x1b[0m");
					config["sequence"] = sequence;
					writeConfig();
				}
				switch(packet.op) {
					case 0:
						event(packet);
						break;
					case 1:
						console.log("received heartbeat!");
						ack();
						break;
					case 7:
						console.log("I need to reconnect!");
						resume = true;
						reconnect(false);
						break;
					case 9:
						console.log("Invalid session! I need to reconnect and identify!");
						clearSession();
						resume = false;
						reconnect(true);
						break;
					case 10:
						console.log("hellowo! interval: " + packet.d.heartbeat_interval);
						interval = setInterval(heart, packet.d.heartbeat_interval);
						break;
					case 11:
						console.log("\x1b[2mHeartbeat acknowledgement!\x1b[0m");
						receivedAck = true;
						break;
					default:
						console.log("Unknown opcode!");
						console.log(packet);
						break;
				}
			}
		});
		identify();
	});
	
	websocket.connect(url);
}

let clients = [];

function tcpserver(client) {
    console.log("TCP client connection!");
    client.setEncoding("utf8");
    client.on("close", (a) => {
        console.log("TCP client disconnect!");
        let r = -1;
        for(c in clients) {
            if(clients[c] === client) {
                r = c;
            }
        }
        clients.splice(r, 1);
    });
    client.on("error", (e) => {
        console.log("TCP ERROR: " + e);
    });
    clients.push(client);
}

function broadcast(data) {
    console.log("Clients: " + clients.length);
    let pack = JSON.stringify(data);
    for(client of clients) {
        client.write(pack);
    }
}

function writeConfig() {
	try {
		fs.writeFileSync(confile, JSON.stringify(config));
	} catch(err) {console.log("Couldn't write config: " + err);}
}

function heart() {
	if(receivedAck == false) {
		console.log("\x1b[31mDidn't receive Ack!\x1b[0m");
		//To reset
		receivedAck = true;
		resume = true;
		reconnect();
		return;
	}
	receivedAck = false;
	let packet = {
		"op": 1,
		"d": sequence
	};
	console.log("\x1b[2mheartbeat\x1b[0m");
	send(packet);
}

function ack() {
	send({"op": 11, "d": null});
}

function identify() {
	if(resume) {
		resume = false;
		send({"op": 6, "d": {"token": token, "session_id": session, "seq": sequence}});
		console.log("\x1b[36mSent resume!\x1b[0m");
	}
	else {
		send({"op": 2, "d": {"token": token, "properties": {"$os": process.platform, "$browser": "fcord", "$device": "fcord"}, "compress": false, "presence": {"since": null, "activities": null, "status": "online", "afk": false}, "guild_subscription": false, "intents": 13824}});
		console.log("\x1b[36mSent identify!\x1b[0m");
	}
}

function clearSession() {
	session = undefined;
	sequence = null;
	config["session"] = session;
	config["sequence"] = sequence;
	writeConfig();
}

function event(packet) {
	console.log(packet);
    
	switch(packet.t) {
		case "READY":
			console.log("READY");
			session = packet.d.session_id;
			config["session"] = session;
			writeConfig();
			break;
		case "RESUMED":
			console.log("Session resumed!");
			break;
		default:
            broadcast(packet);
			break;
	}
}

function reconnect(wait) {
	if(wait) setTimeout(_reconnect, 3000);
	else _reconnect();
}

function _reconnect() {
	connection.close(1001);
	start();
}

function send(packet) {
	connection.sendUTF(JSON.stringify(packet));
}

function call(method, endpoint, data=undefined) {
	let headers = {"User-Agent": user_agent, "Authorization": "Bot " + token};
	return needle(method, "https://discord.com/api" + endpoint, data, {headers:headers});
}

start();
