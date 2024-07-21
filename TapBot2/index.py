from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import CommandHandler, CallbackQueryHandler, Dispatcher
import os
#import json

app = Flask(__name__)

TOKEN = os.environ.get('TOKEN')
bot = Bot(token=TOKEN)

# Путь к файлу с данными пользователей
USERS_FILE = "/tmp/users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as file:
            return json.load(file)
    return {}

def save_users(users):
    with open(USERS_FILE, "w") as file:
        json.dump(users, file)

def update_user(user_id, username, points=0, referrals=0):
    users = load_users()
    if str(user_id) not in users:
        users[str(user_id)] = {"username": username, "points": points, "referrals": referrals}
    else:
        users[str(user_id)]["points"] += points
        users[str(user_id)]["referrals"] += referrals
    save_users(users)
    return users[str(user_id)]

def start(update, context):
    user_id = update.effective_user.id
    username = update.effective_user.username
    users = load_users()
    
    is_new_user = str(user_id) not in users
    referrer_id = context.args[0] if context.args else None

    if is_new_user and referrer_id:
        user_data = update_user(user_id, username, points=50)
        referrer_data = update_user(referrer_id, "", points=50, referrals=1)
        welcome_text = f"Приветствуем! Тебя пригласил {referrer_data['username']}. На твой баланс начислено 50 поинтов!"
    elif is_new_user:
        user_data = update_user(user_id, username)
        welcome_text = "Приветствуем! Давай играть."
    else:
        user_data = users[str(user_id)]
        welcome_text = f"С возвращением! Твой текущий баланс: {user_data['points']} поинтов."

    update.message.reply_text(welcome_text)

def button_click(update, context):
    query = update.callback_query
    query.answer()

    if query.data == "play":
        user_id = query.from_user.id
        user_data = load_users().get(str(user_id), {"points": 0})
        query.edit_message_text(f"Начинаем игру! Твой текущий баланс: {user_data['points']} поинтов.")

dispatcher = Dispatcher(bot, None, use_context=True)
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CallbackQueryHandler(button_click))

@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return 'OK'

@app.route('/')
def index():
    return 'Bot is running'

if __name__ == '__main__':
    app.run()
