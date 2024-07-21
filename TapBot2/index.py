import logging
from flask import Flask, send_file, request, jsonify
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Dispatcher, CommandHandler, CallbackQueryHandler, CallbackContext
import json
import os
from datetime import datetime

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

TOKEN = '7214325392:AAEGuEDFxdtPiPZDEZCiipkB9jebdDh9_7s'
bot = Bot(token=TOKEN)

USERS_FILE = "/tmp/users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as file:
            return json.load(file)
    return {}

def save_users(users):
    with open(USERS_FILE, "w") as file:
        json.dump(users, file)

def update_user(user_id, username, points=0, referrals=0, referrer=None):
    users = load_users()
    user_id = str(user_id)
    is_new_user = user_id not in users
    if is_new_user:
        users[user_id] = {
            "username": username,
            "points": 50 if referrer else 0,  # Начальные очки для новых пользователей
            "referrals": 0,
            "lastClickTime": datetime.now().isoformat(),
            "referrer": referrer
        }
    
    users[user_id]["username"] = username  # Обновляем имя пользователя
    users[user_id]["points"] += points
    users[user_id]["referrals"] += referrals
    users[user_id]["lastClickTime"] = datetime.now().isoformat()
    
    save_users(users)
    return users[user_id], is_new_user

def start(update: Update, context: CallbackContext):
    logger.info("Start command received")
    user_id = update.effective_user.id
    username = update.effective_user.username
    referrer_id = context.args[0] if context.args else None

    user_data, is_new_user = update_user(user_id, username, referrer=referrer_id)

    if is_new_user and referrer_id:
        referrer_data, _ = update_user(int(referrer_id), "", referrals=1)
        update_user(int(referrer_id), "", points=50)  # Добавляем очки рефереру
        welcome_text = f"Welcome! You were invited by {referrer_data['username']}. 50 points have been added to your balance!"
    elif is_new_user:
        welcome_text = "Welcome! Let's start playing."
    else:
        welcome_text = "Welcome back! Let's continue playing."

    webapp_button = InlineKeyboardButton("Play", web_app=WebAppInfo(url="https://testbot2-github-io-62lc.vercel.app/"))
    keyboard = InlineKeyboardMarkup([[webapp_button]])
    update.message.reply_text(welcome_text, reply_markup=keyboard)

@app.route('/')
def home():
    return send_file('index.html')

@app.route('/api/saveUser', methods=['POST'])
def save_user():
    data = request.json
    user_data, is_new_user = update_user(
        data['id'],
        data['username'],
        points=data['points'] - user_data['points'] if 'points' in user_data else data['points'],
        referrals=data['referrals'] - user_data['referrals'] if 'referrals' in user_data else data['referrals']
    )
    return jsonify({"success": True, "isNewUser": is_new_user, "userData": user_data})

@app.route('/api/getUser/<user_id>')
def get_user(user_id):
    users = load_users()
    user_data = users.get(str(user_id), {
        "username": "",
        "points": 0,
        "referrals": 0,
        "lastClickTime": datetime.now().isoformat()
    })
    return jsonify(user_data)

@app.route('/webhook', methods=['POST'])
def webhook():
    logger.info("Received webhook request")
    update = Update.de_json(request.get_json(force=True), bot)
    logger.info(f"Update: {update}")
    dispatcher.process_update(update)
    return 'OK'

dispatcher = Dispatcher(bot, None, use_context=True)
dispatcher.add_handler(CommandHandler("start", start))

if __name__ == '__main__':
    app.run(debug=True)
