import asyncio
import websockets
import json
from telegram import Bot

TELEGRAM_TOKEN = "TON_TOKEN"
CHAT_ID = "TON_CHAT_ID"

bot = Bot(token=TELEGRAM_TOKEN)

MIN_BUYS = 10
MIN_VOLUME = 3
SCORE_THRESHOLD = 80

def calculate_score(token):
    score = 0

    if token["buys"] > 20:
        score += 30
    elif token["buys"] > 10:
        score += 20

    if token["volume"] > 10:
        score += 25
    elif token["volume"] > 5:
        score += 15

    if token["top_holder_pct"] < 15:
        score += 20
    else:
        score -= 20

    return score

async def send_alert(token, score):
    message = f"""
🚨 PUMP ALERT

Token: {token['name']}
CA: {token['ca']}

Buys: {token['buys']}
Volume: {token['volume']} SOL
Top holder: {token['top_holder_pct']}%

Score: {score}/100
"""
    await bot.send_message(chat_id=CHAT_ID, text=message)

async def monitor():
    uri = "wss://pumpportal.fun/api/data"

    async with websockets.connect(uri) as ws:
        while True:
            data = json.loads(await ws.recv())

            if data.get("type") == "new_token":
                token = {
                    "name": data.get("name"),
                    "ca": data.get("mint"),
                    "buys": data.get("buy_count", 0),
                    "volume": data.get("volume", 0),
                    "top_holder_pct": data.get("top_holder_pct", 0)
                }

                if token["buys"] < MIN_BUYS or token["volume"] < MIN_VOLUME:
                    continue

                score = calculate_score(token)

                if score >= SCORE_THRESHOLD:
                    await send_alert(token, score)

asyncio.run(monitor())