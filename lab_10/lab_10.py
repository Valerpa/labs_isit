import os
import requests
import telebot

TELEGRAM_TOKEN = "7396647884:AAGoK-ZPrjz5AWQHUSFDBj3gsvz9MH6Wa9g"

VK_ACCESS_TOKEN = "vk1.a.GcX22vqgf_7axG3HbISzovKtKspTgCwGGR8qXvjTZwNfdgo7dxtT2q5yeh1BuQlkn_yA470mYmVUZiREIJxiYTDjlw-rs6CHfks8pHwzMtaQ76oVHJnEWwHpQYZmiHdhgKuuo-2DaxnI4HhsI0HdBYm2n9LgScB0iY0ccRr2s-N938oGlO5HqLAzH70ewm7X6EcKTlM75hsoc3khc5PgPQ"
VK_API_VERSION = '5.119'

bot = telebot.TeleBot(TELEGRAM_TOKEN)


def set_vk_status(text):
    if len(text) > 140:
        raise ValueError("Текст статуса не должен превышать 140 символов")

    response = requests.post(
        'https://api.vk.com/method/status.set',
        params={
            'text': text,
            'access_token': VK_ACCESS_TOKEN,
            'v': VK_API_VERSION
        }
    )

    data = response.json()
    if 'error' in data:
        raise Exception(f"VK API Error: {data['error']['error_msg']}")

    return data

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "👋 Привет! Я бот для обновления статуса ВКонтакте.\n\n"
        "Просто отправь мне текст сообщения (до 140 символов), "
        "и я установлю его в качестве статуса твоего профиля VK!\n\n"
    )
    bot.send_message(text=welcome_text, chat_id=message.chat.id)

@bot.message_handler(content_types=['text'])
def handle_message(message):
    user_text = message.text

    try:
        result = set_vk_status(user_text)

        if result.get('response', 0) == 1:
            bot.reply_to(message, "Статус обновлен!")
        else:
            bot.reply_to(message, "Не удалось обновить статус")

    except Exception as e:
        error_message = f"Ошибка: {str(e)}"
        bot.reply_to(message, error_message)


bot.polling(none_stop=True)