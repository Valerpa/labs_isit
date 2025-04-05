import xml.dom.minidom
import requests
import telebot
from telebot import types
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io

TOKEN = ""
CBR_URL = "https://www.cbr.ru/scripts/XML_daily.asp?date_req={date}"

bot = telebot.TeleBot(TOKEN)
user_data = {}


def show_main_menu(chat_id):
    markup = types.InlineKeyboardMarkup()
    btn_single = types.InlineKeyboardButton("Курс на дату", callback_data='mode_single')
    btn_graph = types.InlineKeyboardButton("Графика за период", callback_data='mode_graph')
    markup.add(btn_single, btn_graph)
    bot.send_message(chat_id, "Выберите режим работы:", reply_markup=markup)


@bot.message_handler(commands=['start'])
def start(message):
    show_main_menu(message.chat.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('mode_'))
def handle_mode(call):
    user_data[call.message.chat.id] = {'mode': call.data.split('_')[1]}
    show_currency_buttons(call.message.chat.id)


def show_currency_buttons(chat_id):
    markup = types.InlineKeyboardMarkup()
    btn_usd = types.InlineKeyboardButton("USD", callback_data='currency_USD')
    btn_eur = types.InlineKeyboardButton("EUR", callback_data='currency_EUR')
    markup.add(btn_usd, btn_eur)
    bot.send_message(chat_id, "Выберите валюту:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('currency_'))
def handle_currency(call):
    chat_id = call.message.chat.id
    user_data[chat_id]['currency'] = call.data.split('_')[1]

    if user_data[chat_id]['mode'] == 'single':
        msg = bot.send_message(chat_id, "Введите дату в формате ДД/ММ/ГГГГ:")
        bot.register_next_step_handler(msg, process_single_date)
    else:
        msg = bot.send_message(chat_id, "Введите начальную дату периода (ДД/ММ/ГГГГ):")
        bot.register_next_step_handler(msg, process_start_date)


def process_single_date(message):
    chat_id = message.chat.id
    date_input = message.text

    try:
        date_obj = datetime.strptime(date_input, "%d/%m/%Y")
        if date_obj > datetime.now():
            raise ValueError("Дата не может быть в будущем")

        date_cbr = date_input.replace('/', '.')
        currency = user_data[chat_id]['currency']
        result = get_currency_rate(currency, date_cbr)

        markup = types.InlineKeyboardMarkup()
        btn_graph = types.InlineKeyboardButton("Построить график", callback_data='show_graph_menu')
        btn_new = types.InlineKeyboardButton("Новый запрос", callback_data='return_to_menu')
        markup.add(btn_graph, btn_new)

        bot.send_message(chat_id, result, reply_markup=markup)

    except ValueError as ve:
        handle_date_error(chat_id, ve)
    except Exception as e:
        bot.send_message(chat_id, f"Ошибка: {str(e)}")
    finally:
        clean_user_data(chat_id)


def process_start_date(message):
    chat_id = message.chat.id
    date_input = message.text

    try:
        start_date = datetime.strptime(date_input, "%d/%m/%Y")
        if start_date > datetime.now():
            raise ValueError("Начальная дата не может быть в будущем")

        user_data[chat_id]['start_date'] = start_date
        msg = bot.send_message(chat_id, "Введите конечную дату периода (ДД/ММ/ГГГГ):")
        bot.register_next_step_handler(msg, process_end_date)

    except ValueError as ve:
        handle_date_error(chat_id, ve)
    except Exception as e:
        bot.send_message(chat_id, f"Ошибка: {str(e)}")
        clean_user_data(chat_id)


def process_end_date(message):
    chat_id = message.chat.id
    date_input = message.text

    try:
        end_date = datetime.strptime(date_input, "%d/%m/%Y")
        if end_date > datetime.now():
            raise ValueError("Конечная дата не может быть в будущем")
        if end_date < user_data[chat_id]['start_date']:
            raise ValueError("Конечная дата должна быть после начальной")
        if (end_date - user_data[chat_id]['start_date']).days > 60:
            raise ValueError("Максимальный период - 60 дней")

        user_data[chat_id]['end_date'] = end_date
        generate_and_send_plot(chat_id)

    except ValueError as ve:
        handle_date_error(chat_id, ve)
    except Exception as e:
        bot.send_message(chat_id, f"Ошибка: {str(e)}")
    finally:
        clean_user_data(chat_id)


def get_currency_rate(currency: str, date: str) -> str:
    try:
        date_cbr = date.replace('/', '.')
        response = requests.get(CBR_URL.format(date=date_cbr))
        response.raise_for_status()

        dom = xml.dom.minidom.parseString(response.text)
        dom.normalize()

        valutes = dom.getElementsByTagName("Valute")
        for valute in valutes:
            char_code = valute.getElementsByTagName("CharCode")[0]
            if char_code.childNodes[0].nodeValue == currency:
                nominal = valute.getElementsByTagName("Nominal")[0].childNodes[0].nodeValue
                value = valute.getElementsByTagName("Value")[0].childNodes[0].nodeValue
                return f"На {date.replace('.', '/')}:\n\n{nominal} {currency} = {value} RUB"
        return "Валюта не найдена"

    except requests.exceptions.RequestException:
        return "Ошибка подключения к серверу ЦБ"
    except Exception as e:
        return f"Ошибка: {str(e)}"
def generate_and_send_plot(chat_id):
    try:
        currency = user_data[chat_id]['currency']
        start_date = user_data[chat_id]['start_date']
        end_date = user_data[chat_id]['end_date']

        dates, values = get_currency_data(currency, start_date, end_date)

        plt.figure(figsize=(10, 5))
        plt.plot(dates, values, marker='o', linestyle='-')
        plt.title(f"Курс {currency} к RUB\n{start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}")
        plt.xlabel("Дата")
        plt.ylabel("Курс, RUB")
        plt.grid(True)

        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d.%m.%Y'))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=max(1, (end_date - start_date).days // 5)))
        plt.gcf().autofmt_xdate()

        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)

        markup = types.InlineKeyboardMarkup()
        btn_new = types.InlineKeyboardButton("Новый запрос", callback_data='return_to_menu')
        markup.add(btn_new)

        bot.send_photo(chat_id, buf, reply_markup=markup)
        plt.close()

    except Exception as e:
        bot.send_message(chat_id, f"Ошибка при построении графика: {str(e)}")


def get_currency_data(currency, start_date, end_date):
    dates = []
    values = []
    current_date = start_date

    while current_date <= end_date:
        try:
            date_str = current_date.strftime("%d/%m/%Y")
            cbr_date = date_str.replace('/', '.')

            response = requests.get(CBR_URL.format(date=cbr_date))
            response.raise_for_status()

            dom = xml.dom.minidom.parseString(response.text)
            dom.normalize()

            valutes = dom.getElementsByTagName("Valute")
            for valute in valutes:
                char_code = valute.getElementsByTagName("CharCode")[0]
                if char_code.childNodes[0].nodeValue == currency:
                    value = float(valute.getElementsByTagName("Value")[0]
                                  .childNodes[0].nodeValue.replace(',', '.'))
                    dates.append(current_date)
                    values.append(value)
                    break

        except Exception:
            pass

        current_date += timedelta(days=1)

    return dates, values


def handle_date_error(chat_id, error):
    error_msg = "Ошибка ввода даты:\n"
    if "неизвестный формат" in str(error):
        error_msg += "Используйте формат ДД/ММ/ГГГГ (например: 15/10/2023)"
    elif "будущем" in str(error):
        error_msg += "Дата не может быть позже текущей"
    else:
        error_msg += str(error)

    bot.send_message(chat_id, error_msg)
    show_main_menu(chat_id)


def clean_user_data(chat_id):
    if chat_id in user_data:
        del user_data[chat_id]


@bot.callback_query_handler(func=lambda call: call.data == 'return_to_menu')
def handle_return(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    show_main_menu(call.message.chat.id)


@bot.callback_query_handler(func=lambda call: call.data == 'show_graph_menu')
def handle_show_graph(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    user_data[call.message.chat.id] = {'mode': 'graph'}
    show_currency_buttons(call.message.chat.id)


if __name__ == "__main__":
    bot.polling(none_stop=True)