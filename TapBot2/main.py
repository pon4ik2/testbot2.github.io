import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Замените на свой токен бота
TOKEN = "7214325392:AAEGuEDFxdtPiPZDEZCiipkB9jebdDh9_7s"

# Путь к файлу с ID пользователей
USERS_FILE = "usersID.txt"

# Функция для загрузки существующих пользователей
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as file:
            return set(file.read().splitlines())
    return set()

# Функция для сохранения нового пользователя
def save_user(user_id):
    with open(USERS_FILE, "a") as file:
        file.write(f"{user_id}\n")

# Функция для обновления счета пользователя
def update_user_score(user_id, points):
    # Здесь должна быть логика обновления счета пользователя
    # Например, сохранение в базу данных или в файл
    print(f"Обновлен счет пользователя {user_id}: +{points} очков")

# Функция для обновления счетчика рефералов
def update_referral_count(user_id):
    # Здесь должна быть логика обновления счетчика рефералов
    # Например, сохранение в базу данных или в файл
    print(f"Обновлен счетчик рефералов пользователя {user_id}")

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    users = load_users()
    
    if str(user_id) not in users:
        save_user(user_id)
        is_new_user = True
    else:
        is_new_user = False

    referrer_id = context.args[0] if context.args else None

    if referrer_id and is_new_user:
        referrer = await context.bot.get_chat(referrer_id)
        update_user_score(referrer_id, 50)
        update_referral_count(referrer_id)
        welcome_text = f"Приветствуем! Тебя пригласил {referrer.username}."
        game_button = InlineKeyboardButton("Играть", callback_data=f"play_referred_{referrer_id}")
    else:
        welcome_text = "Приветствуем! Давай играть."
        game_button = InlineKeyboardButton("Играть", callback_data="play")

    keyboard = InlineKeyboardMarkup([[game_button]])
    await update.message.reply_text(welcome_text, reply_markup=keyboard)

# Обработчик нажатия на кнопку
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("play_referred_"):
        referrer_id = query.data.split("_")[2]
        referrer = await context.bot.get_chat(referrer_id)
        await query.edit_message_text(
            f"Вас пригласил {referrer.username}. Он получил 50 очков!\n\nНачинаем игру...",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Играть", callback_data="start_game")]])
        )
    elif query.data == "play" or query.data == "start_game":
        await query.edit_message_text("Начинаем игру...")
        # Здесь должна быть логика запуска игры

# Основная функция
def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_click))

    application.run_polling()

if __name__ == "__main__":
    main()