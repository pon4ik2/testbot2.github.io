import os
import json
from flask import Flask, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

app = Flask(__name__)

# Замените на свой токен бота
TOKEN = "7214325392:AAEGuEDFxdtPiPZDEZCiipkB9jebdDh9_7s"

# Путь к файлу с данными пользователей
USERS_FILE = "/tmp/users.json"

# Функция для загрузки данных пользователей
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as file:
            return json.load(file)
    return {}

# Функция для сохранения данных пользователей
def save_users(users):
    with open(USERS_FILE, "w") as file:
        json.dump(users, file)

# Функция для обновления данных пользователя
def update_user(user_id, username, points=0, referrals=0):
    users = load_users()
    if str(user_id) not in users:
        users[str(user_id)] = {"username": username, "points": points, "referrals": referrals}
    else:
        users[str(user_id)]["points"] += points
        users[str(user_id)]["referrals"] += referrals
    save_users(users)
    return users[str(user_id)]

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

    game_button = InlineKeyboardButton("Играть", callback_data="play")
    keyboard = InlineKeyboardMarkup([[game_button]])
    await update.message.reply_text(welcome_text, reply_markup=keyboard)

# Обработчик нажатия на кнопку
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "play":
        user_id = query.from_user.id
        user_data = load_users().get(str(user_id), {"points": 0})
        await query.edit_message_text(f"Начинаем игру! Твой текущий баланс: {user_data['points']} поинтов.")
        # Здесь должна быть логика запуска игры

# Обработчик для Vercel
@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    application.process_update(update)
    return "OK"

# Основная функция
def main():
    global bot, application
    bot = Bot(TOKEN)
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_click))

    # Установка вебхука
    bot.set_webhook(url=f"https://testbot2-github-io-62lc.vercel.app/webhook")

if __name__ == "__main__":
    main()
    app.run()
