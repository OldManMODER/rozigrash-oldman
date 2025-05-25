
from flask import Flask, request, jsonify, render_template
import asyncio
import threading
import random
import websockets
import json

app = Flask(__name__)
participants = set()
KEYWORD = "!участь"
CHANNEL_NAME = "OLDMAN7777"
BOT_USERNAME = "OldManMODER"
bot_socket = None

async def send_message(ws, message):
    await ws.send(json.dumps({
        "event": "chat.send",
        "data": { "content": message }
    }))

async def bot_loop():
    global bot_socket
    uri = "wss://chat.kick.com/socket.io/?EIO=4&transport=websocket"
    async with websockets.connect(uri) as websocket:
        bot_socket = websocket
        for _ in range(5):
            await websocket.recv()

        join_payload = json.dumps({
            "event": "chat.join",
            "data": {
                "channel": CHANNEL_NAME,
                "username": BOT_USERNAME
            }
        })
        await websocket.send(join_payload)

        while True:
            response = await websocket.recv()
            try:
                data = json.loads(response)
                if data.get("event") == "chat.message":
                    username = data["data"]["username"]
                    content = data["data"]["content"]
                    if content.strip() == KEYWORD:
                        participants.add(username)
            except:
                continue

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/set_keyword", methods=["POST"])
def set_keyword():
    global KEYWORD
    KEYWORD = request.json.get("keyword", "!участь").strip()
    return jsonify({"status": "ок", "keyword": KEYWORD})

@app.route("/announce_keyword", methods=["POST"])
def announce_keyword():
    asyncio.run(send_message(bot_socket, f"Кодове слово розіграшу: {KEYWORD}"))
    return jsonify({"status": "ок"})

@app.route("/pick_winner", methods=["POST"])
def pick_winner():
    if not participants:
        asyncio.run(send_message(bot_socket, "Немає учасників для розіграшу!"))
        return jsonify({"winner": None})
    winner = random.choice(list(participants))
    asyncio.run(send_message(bot_socket, f"Переможець — @{winner}! Вітаємо!"))
    return jsonify({"winner": winner})

# Запускаємо Flask у потоці
threading.Thread(target=lambda: app.run(host="0.0.0.0", port=5000)).start()

# Запуск бота
asyncio.run(bot_loop())
