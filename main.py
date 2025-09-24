import telebot
import gspread
import os, time
from dotenv import load_dotenv
from user_info import check_reg, add_user_to_reg
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start_message(message):
    if not check_reg(message.from_user.id):
        bot.send_message(message.from_user.id, "Вы не зарегистрированы. Для регистрации введите секретный код")
    else:
        bot.send_message(message.from_user.id, "Внесите данные в формате ФИО; Проект; Часы; Комментарий. Например,\nСергей; 13031; 8; Выгрузка фур")

@bot.message_handler(commands=['help'])
def help_message(message):
    start_message(message)

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == '5378':
        reg_ans = add_user_to_reg(message.from_user.id)        
        if reg_ans['success']:
            bot.send_message(message.from_user.id, "Регистрация прошла успешно")
            bot.send_message(message.from_user.id, "Внесите данные в формате ФИО; Проект; Часы; Комментарий. Например,\nСергей; 13031; 8; Выгрузка фур")
        else:
            bot.send_message(message.from_user.id, "Не удалось зарегистрироваться")


if __name__=='__main__':
    while True:
        try:
            bot.polling(non_stop=True, interval=0)
        except Exception as e:
            print("EEEEE" + e)
            time.sleep(5)
            continue
