import os, sys
from decouple import config
import requests
from bs4 import BeautifulSoup
import lxml
import telebot
from telebot import types
from requests.exceptions import RequestException
from requests.exceptions import ConnectionError, ReadTimeout

TOKEN = config('TOKEN',default='')
bot = telebot.TeleBot(TOKEN)

URL = 'https://cbu.uz/ru/'
page = requests.get(URL)
soup = BeautifulSoup(page.text, 'lxml')
scripts = soup.find_all('script')
for script in scripts:
    script = script.text
    if 'arCurrencyRates' in str(script):
      test = str(script)
i = test.find('{')
test = test[i:]
i = test.find('}')
test = test[:i+1]
data = eval(test)
USD = float(data['USD'])
RUB = float(data['RUB'])
EUR = float(data['EUR'])

@bot.message_handler(content_types=['text'])
def start(message):
    try:
        global money
        money = float(message.text)
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton('SUM/RUB', callback_data='RUB')
        btn2 = types.InlineKeyboardButton('USD/SUM', callback_data='USD')
        markup.add(btn1, btn2)
        bot.send_message(message.chat.id, 'Выберете валюту!', reply_markup=markup)
    except ValueError:
        bot.send_message(message.chat.id, 'Введите число')

@bot.callback_query_handler(func=lambda callback:True)
def callback_button(callback):
    if callback.data == 'RUB':
        message = str(round((money*1000)/RUB))+' рублей'
        bot.send_message(callback.message.chat.id, message)
    elif callback.data == 'USD':
        message = str(round(money*USD))+' сумов'
        bot.send_message(callback.message.chat.id, message)

while True:
    try:
        bot.polling(none_stop=True)
    except RequestException as err:
        print(err)
        print('* Connection failed, waiting to reconnect...')
        time.sleep(15)
        print('* Reconnecting.')