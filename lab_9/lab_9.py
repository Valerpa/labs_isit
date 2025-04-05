# -*- coding: utf-8 -*-
import telebot
from telebot import types
import json

TOKEN = ""
bot = telebot.TeleBot(token=TOKEN)

COUNTS_FILE = "reaction_counts.json"
MULTI_VOTE_FILE = "multi_vote_counts.json"

def load_counts(file_name):
    try:
        with open(file_name, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_counts(file_name, counts):
    with open(file_name, "w", encoding="utf-8") as file:
        json.dump(counts, file, ensure_ascii=False, indent=4)

counts = load_counts(COUNTS_FILE)
like_count = counts.get("like", 0)
dislike_count = counts.get("dislike", 0)

multi_vote_counts = load_counts(MULTI_VOTE_FILE)


multi_vote_options = ["Опция 1", "Опция 2", "Опция 3", "Опция 4", "Опция 5"]

@bot.message_handler(commands=['start'])
def start_handler(message):
    markup = types.InlineKeyboardMarkup()
    like_button = types.InlineKeyboardButton(text=f"Мне нравится ({like_count})", callback_data="like")
    dislike_button = types.InlineKeyboardButton(text=f"Мне не нравится ({dislike_count})", callback_data="dislike")
    multi_vote_button = types.InlineKeyboardButton(text="Голосование с выбором (5 вариантов)", callback_data="multi_vote")
    markup.add(like_button, dislike_button, multi_vote_button)

    bot.send_message(message.chat.id, "Оцените сообщение:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    global like_count, dislike_count, multi_vote_counts

    if call.data == "like":
        like_count += 1
        save_counts(COUNTS_FILE, {"like": like_count, "dislike": dislike_count})

    elif call.data == "dislike":
        dislike_count += 1
        save_counts(COUNTS_FILE, {"like": like_count, "dislike": dislike_count})

    elif call.data == "multi_vote":
        markup = types.InlineKeyboardMarkup()
        for i, option in enumerate(multi_vote_options):
            button = types.InlineKeyboardButton(text=f"{option} ({multi_vote_counts.get(option, 0)})", callback_data=f"vote_{i}")
            markup.add(button)
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text="Выберите одну из опций:",
                              reply_markup=markup)

    elif call.data.startswith("vote_"):
        option_index = int(call.data.split("_")[1])
        selected_option = multi_vote_options[option_index]

        if selected_option in multi_vote_counts:
            multi_vote_counts[selected_option] += 1
        else:
            multi_vote_counts[selected_option] = 1

        save_counts(MULTI_VOTE_FILE, multi_vote_counts)

        markup = types.InlineKeyboardMarkup()
        for i, option in enumerate(multi_vote_options):
            button = types.InlineKeyboardButton(text=f"{option} ({multi_vote_counts.get(option, 0)})", callback_data=f"vote_{i}")
            markup.add(button)

        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text="Выберите одну из опций:",
                              reply_markup=markup)

        bot.answer_callback_query(call.id, text=f"Ваш голос за '{selected_option}' учтен!")

    bot.answer_callback_query(call.id, text="Ваш голос учтен!")

bot.polling(none_stop=True)
