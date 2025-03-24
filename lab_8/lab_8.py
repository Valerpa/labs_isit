# -*- coding: utf-8 -*-
import os
import telebot
from telebot import types

TOKEN = '7857195127:AAGTRF7NNXkYnc7vsCTMuwz9S9waeCKvPAI'
bot = telebot.TeleBot(token=TOKEN)

BACK_TO_MAIN = "Назад в главное меню"
BACK_TO_LEVELS = "Назад к уровням"

professions = [
    "Frontend Developer",
    "Backend Developer",
    "Full Stack Developer",
    "DevOps Engineer",
    "Data Scientist",
    "QA Engineer",
    "Mobile Developer",
    "UI/UX Designer"
]

levels = ["Junior", "Middle", "Senior"]

profession_counters = {prof: 0 for prof in professions}

grade_counters = {prof: {level: 0 for level in levels} for prof in professions}

requirements = {
    "Frontend Developer": {
        "Junior": "Базовые знания HTML, CSS, JavaScript, основы адаптивной верстки, знакомство с Git.",
        "Middle": "Углубленные знания JavaScript, опыт работы с React или Angular, CSS-препроцессоры, сборщики (Webpack).",
        "Senior": "Эксперт в JavaScript и современных фреймворках, архитектурное проектирование, оптимизация производительности, наставничество."
    },
    "Backend Developer": {
        "Junior": "Базовые знания Python/Java/Node.js, основы SQL, понимание REST API.",
        "Middle": "Опыт работы с фреймворками (Django, Flask, Spring, Express), микросервисная архитектура, работа с базами данных.",
        "Senior": "Эксперт в построении масштабируемых систем, глубокое понимание распределенных систем, CI/CD, безопасность, наставничество."
    },
    "Full Stack Developer": {
        "Junior": "Базовые знания фронтенда (HTML, CSS, JavaScript) и бэкенда (один язык, SQL, Git).",
        "Middle": "Опыт разработки на стеке (например, React + Node.js или Python), интеграция API, основы DevOps.",
        "Senior": "Эксперт во всех слоях разработки, проектирование архитектуры, оптимизация производительности, опыт с облачными платформами, наставничество."
    },
    "DevOps Engineer": {
        "Junior": "Базовые знания Linux, основы скриптинга (Bash, Python), понимание CI/CD, знакомство с Git.",
        "Middle": "Опыт работы с Docker, Kubernetes, инструментами автоматизации (Jenkins, Ansible), облачными сервисами, IaC (Terraform).",
        "Senior": "Эксперт в проектировании CI/CD, продвинутые навыки облачной архитектуры, мониторинг, безопасность инфраструктуры, наставничество."
    },
    "Data Scientist": {
        "Junior": "Базовые знания Python или R, основы статистики, работа с библиотеками (pandas, NumPy, scikit-learn).",
        "Middle": "Опыт применения алгоритмов машинного обучения, визуализация данных, работа с большими данными, SQL.",
        "Senior": "Эксперт в машинном обучении и глубоких нейронных сетях (TensorFlow, PyTorch), работа с Big Data (Spark, Hadoop), архитектура данных, наставничество."
    },
    "QA Engineer": {
        "Junior": "Базовые знания тестирования ПО, написание тест-кейсов, знакомство с баг-трекинговыми системами, ручное тестирование.",
        "Middle": "Опыт автоматизированного тестирования (Selenium, Postman), знание скриптовых языков, интеграция тестов в CI.",
        "Senior": "Эксперт в построении тестовых фреймворков, нагрузочное и безопасность тестирование, разработка тестовой стратегии, наставничество."
    },
    "Mobile Developer": {
        "Junior": "Базовые знания мобильных платформ (Android или iOS), основы языков (Java/Kotlin или Swift), базовые UI-решения.",
        "Middle": "Опыт разработки полноценных мобильных приложений, знание SDK, API, современных фреймворков, работа с системами контроля версий.",
        "Senior": "Эксперт в мобильной архитектуре, оптимизации производительности, кроссплатформенной разработке, отладке и безопасности, наставничество."
    },
    "UI/UX Designer": {
        "Junior": "Базовые знания принципов дизайна, работа с инструментами (Figma, Sketch, Adobe XD), создание wireframe.",
        "Middle": "Опыт проведения исследований пользователей, продвинутый прототипинг, взаимодействие с разработчиками, адаптивный дизайн.",
        "Senior": "Эксперт в UX-стратегиях, разработке дизайн-систем, глубинных исследованиях пользователей, кросс-функциональное сотрудничество, лидерство."
    }
}

user_states = {}

IMAGES_FOLDER = "images/"


def main_menu():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(0, len(professions), 2):
        row = [types.KeyboardButton(professions[i])]
        if i + 1 < len(professions):
            row.append(types.KeyboardButton(professions[i + 1]))
        keyboard.row(*row)
    return keyboard


def level_menu(profession):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("Junior", "Middle", "Senior")
    keyboard.row(BACK_TO_MAIN)
    return keyboard


def detail_menu():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(BACK_TO_LEVELS, BACK_TO_MAIN)
    return keyboard


def send_profession_image(chat_id, profession):
    image_path = os.path.join(IMAGES_FOLDER, f"{profession}.jpeg")

    if os.path.exists(image_path):
        with open(image_path, 'rb') as photo:
            bot.send_photo(chat_id, photo)
    else:
        bot.send_message(chat_id, "Изображение для этой профессии не найдено.")


@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(message.chat.id,
                     "Добро пожаловать в IT Карьерный Бот!\nВыберите профессию:",
                     reply_markup=main_menu())


@bot.message_handler(func=lambda message: True)
def message_handler(message):
    chat_id = message.chat.id
    text = message.text.strip()

    if text == BACK_TO_MAIN:
        if chat_id in user_states:
            del user_states[chat_id]
        bot.send_message(chat_id, "Возвращаемся в главное меню.", reply_markup=main_menu())
        return

    if text == BACK_TO_LEVELS:
        if chat_id in user_states:
            profession = user_states[chat_id]
            bot.send_message(chat_id,
                             f"Профессия: {profession}\nВыберите уровень (Junior, Middle, Senior):",
                             reply_markup=level_menu(profession))
        else:
            bot.send_message(chat_id, "Сначала выберите профессию.", reply_markup=main_menu())
        return

    if text in professions:
        profession_counters[text] += 1
        user_states[chat_id] = text
        bot.send_message(chat_id,
                         f"Вы выбрали профессию: {text}\nКоличество нажатий на эту кнопку: {profession_counters[text]}\n\nВыберите уровень (Junior, Middle, Senior):",
                         reply_markup=level_menu(text))

        send_profession_image(chat_id, text)

        return

    if text in levels:
        if chat_id not in user_states:
            bot.send_message(chat_id, "Сначала выберите профессию.", reply_markup=main_menu())
            return
        profession = user_states[chat_id]
        grade_counters[profession][text] += 1
        req = requirements.get(profession, {}).get(text, "Информация отсутствует.")
        bot.send_message(chat_id,
                         f"Профессия: {profession}\nУровень: {text}\nКоличество нажатий на этот уровень: {grade_counters[profession][text]}\n\nТребования по стэку:\n{req}",
                         reply_markup=detail_menu())
        return

    bot.send_message(chat_id,
                     "Пожалуйста, используйте кнопки меню для навигации.",
                     reply_markup=main_menu())


bot.polling(none_stop=True)
