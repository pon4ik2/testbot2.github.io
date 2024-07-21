import logging
from flask import Flask, request, jsonify, send_file
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Dispatcher, CommandHandler, CallbackQueryHandler, CallbackContext
import json
import os

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

TOKEN = '7214325392:AAEGuEDFxdtPiPZDEZCiipkB9jebdDh9_7s'
bot = Bot(token=TOKEN)

USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as file:
            return json.load(file)
    return {}

def save_users(users):
    with open(USERS_FILE, "w") as file:
        json.dump(users, file)

def update_user(user_id, username, points=0, referrer=None):
    users = load_users()
    if str(user_id) not in users:
        users[str(user_id)] = {"username": username, "points": 50, "referred_by": referrer}
        if referrer:
            if str(referrer) in users:
                users[str(referrer)]["points"] += 50
    else:
        users[str(user_id)]["points"] += points
    save_users(users)
    return users[str(user_id)]

@app.route('/')
def home():
    return send_file('index.html')

@app.route('/webhook', methods=['POST'])
def webhook():
    logger.info("Received webhook request")
    try:
        update = Update.de_json(request.get_json(force=True), bot)
        logger.info(f"Update: {update}")
        dispatcher.process_update(update)
    except Exception as e:
        logger.error(f"Error processing update: {e}")
    return 'OK'

def start(update: Update, context: CallbackContext):
    logger.info("Start command received")
    user_id = update.effective_user.id
    username = update.effective_user.username
    referrer = context.args[0] if context.args else None

    user_data = update_user(user_id, username, referrer=referrer)

    webapp_button = InlineKeyboardButton("Играть", url=f"https://testbot2-github-io-62lc.vercel.app/?id={user_id}")
    keyboard = InlineKeyboardMarkup([[webapp_button]])
    update.message.reply_text("Добро пожаловать в игру!", reply_markup=keyboard)

dispatcher = Dispatcher(bot, None, use_context=True)
dispatcher.add_handler(CommandHandler("start", start))

if __name__ == '__main__':
    app.run(debug=True)
