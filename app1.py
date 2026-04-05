import telebot
from telebot import types
import sqlite3

token = "8393683363:AAGoj9O7LLl-Y_NiTPtA9nnH4Y3DcLtFdUI"
bot = telebot.TeleBot(token)

conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER,
    day TEXT,
    text TEXT
)
""")
conn.commit()


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
                     "Привіт! Це твій тижневий планер\n\n"
                     "/add — додати запис\n"
                     "/show — показати всі записи")


@bot.message_handler(commands=['add'])
def add_note(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    days = ["Понеділок", "Вівторок", "Середа", "Четвер",
            "П’ятниця", "Субота", "Неділя"]

    markup.add(*days)

    msg = bot.send_message(message.chat.id, "Обери день:", reply_markup=markup)
    bot.register_next_step_handler(msg, get_day)


def get_day(message):
    day = message.text
    msg = bot.send_message(message.chat.id, f"Що потрібно зробити у {day}?")
    bot.register_next_step_handler(msg, save_note, day)


def save_note(message, day):
    chat_id = message.chat.id
    text = message.text

    cursor.execute("INSERT INTO notes (chat_id, day, text) VALUES (?, ?, ?)",
                   (chat_id, day, text))
    conn.commit()

    bot.send_message(chat_id, f" Запис додано на {day}")


@bot.message_handler(commands=['show'])
def show_notes(message):
    chat_id = message.chat.id

    cursor.execute("SELECT day, text FROM notes WHERE chat_id = ?", (chat_id,))
    rows = cursor.fetchall()

    if not rows:
        bot.send_message(chat_id, "У тебе ще немає записів ")
        return

    result = "Твій тиждень:\n\n"

    for day, text in rows:
        result += f"{day}:\n- {text}\n\n"

    bot.send_message(chat_id, result)


bot.polling()