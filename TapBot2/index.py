import logging
from flask import Flask, send_file, request, jsonify
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Dispatcher, CommandHandler, CallbackQueryHandler, CallbackContext
import json
import os

# Настройка логирования
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Замените на ваш токен бота
TOKEN = '7214325392:AAEGuEDFxdtPiPZDEZCiipkB9jebdDh9_7s'
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

def start(update: Update, context: CallbackContext):
    logger.info("Start command received")
    user_id = update.effective_user.id
    username = update.effective_user.username
    users = load_users()
    
    is_new_user = str(user_id) not in users
    referrer_id = context.args[0] if context.args else None

    if is_new_user and referrer_id:
        user_data = update_user(user_id, username, points=0)
        referrer_data = update_user(referrer_id, "", points=50, referrals=1)
        user_data["points"] += 50  # Add 50 points to new user
        save_users(users)
        welcome_text = f"Приветствуем! Тебя пригласил {referrer_data['username']}. На твой баланс начислено 50 поинтов!"
    elif is_new_user:
        user_data = update_user(user_id, username, points=0)
        welcome_text = "Приветствуем! Давай играть.."
    else:
        user_data = users[str(user_id)]
        welcome_text = f"С возвращением! Ты пригласил уже {user_data['referrals']} игроков и заработал за это {user_data['points']} поинтов."

    webapp_button = InlineKeyboardButton("Играть", web_app=WebAppInfo(url="http://www.nbuv.gov.ua/"))
    keyboard = InlineKeyboardMarkup([[webapp_button]])
    update.message.reply_text(welcome_text, reply_markup=keyboard)

def button_click(update: Update, context: CallbackContext):
    logger.info("Button click received")
    query = update.callback_query
    query.answer()

    if query.data == "play":
        user_id = query.from_user.id
        user_data = load_users().get(str(user_id), {"points": 0})
        query.edit_message_text(f"Начинаем игру! Твой текущий баланс: {user_data['points']} поинтов.")
        logger.info(f"Game started for user {user_id}")

def error_handler(update: Update, context: CallbackContext):
    logger.error(f"An error occurred: {context.error}")

# Настройка диспетчера
dispatcher = Dispatcher(bot, None, use_context=True)
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CallbackQueryHandler(button_click))
dispatcher.add_error_handler(error_handler)

@app.route('/')
def home():
    return send_file('index.html')

@app.route('/webhook', methods=['POST'])
def webhook():
    logger.info("Received webhook request")
    update = Update.de_json(request.get_json(force=True), bot)
    logger.info(f"Update: {update}")
    dispatcher.process_update(update)
    return 'OK'

if __name__ == '__main__':
    app.run(debug=True)
