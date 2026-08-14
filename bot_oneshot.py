#!/usr/bin/env python3
"""Одноразовый обработчик апдейтов для GitHub Actions: отвечает на
команды и сохраняет offset в offset.txt между запусками."""
import json
import os
import urllib.parse
import urllib.request

TOKEN = os.environ["BOT_TOKEN"]
APP_URL = os.environ.get("APP_URL", "https://klimat69.github.io/nexa-games")
API = "https://api.telegram.org/bot" + TOKEN
OFFSET_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "offset.txt")


def call(method, **params):
    data = json.dumps(params).encode()
    req = urllib.request.Request(API + "/" + method, data=data,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def app_keyboard():
    return {"inline_keyboard": [[
        {"type": "web_app", "text": "🎮 Играть", "web_app": {"url": APP_URL}}
    ]]}


def handle(msg):
    chat_id = msg["chat"]["id"]
    text = msg.get("text", "").split("@")[0].lower()

    if text in ("/start", "/play"):
        call("sendMessage", chat_id=chat_id,
             text="🚀 *Добро пожаловать в Nexa Games!*\n\n"
                  "Крипто-казино прямо в Telegram:\n"
                  "🚀 *Crash* — забери ставку до взрыва\n"
                  "🪙 *Coin Flip* — BTC или ETH, ×1.96\n"
                  "🎲 *Dice* — настрой шанс и выплату\n\n"
                  "Играем на виртуальные NXC — бесплатно, без депозитов.",
             parse_mode="Markdown",
             reply_markup=app_keyboard())
    elif text == "/balance":
        call("sendMessage", chat_id=chat_id,
             text="🪙 Баланс хранится в игре — открой Mini App, чтобы посмотреть и сыграть.",
             reply_markup=app_keyboard())
    elif text == "/help":
        call("sendMessage", chat_id=chat_id,
             text="ℹ️ *Как играть*\n\n"
                  "1. Нажми кнопку *Играть* (или 🎮 в меню чата)\n"
                  "2. Ставь NXC и забирай выигрыш вовремя\n"
                  "3. Кончились монеты — жми «+1K», они бесплатные\n\n"
                  "Provably fair: преимущество площадки всего 3%.",
             parse_mode="Markdown",
             reply_markup=app_keyboard())


def main():
    try:
        with open(OFFSET_FILE) as f:
            offset = int(f.read().strip())
    except (OSError, ValueError):
        offset = None

    params = {"timeout": 0, "allowed_updates": ["message"]}
    if offset is not None:
        params["offset"] = offset
    with urllib.request.urlopen(
            urllib.request.Request(API + "/getUpdates?" +
                                   urllib.parse.urlencode(params)), timeout=30) as r:
        updates = json.loads(r.read())["result"]

    answered = 0
    for u in updates:
        offset = u["update_id"] + 1
        if "message" in u:
            handle(u["message"])
            answered += 1

    if offset is not None:
        with open(OFFSET_FILE, "w") as f:
            f.write(str(offset))
    print(f"processed {len(updates)} updates, answered {answered}")


if __name__ == "__main__":
    main()
