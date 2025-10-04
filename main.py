import telebot
import gspread
import os, time
from telebot import types
from dotenv import load_dotenv
from user_info import check_reg, add_user_to_reg
from stuff_list import add_name_to_stuff_list, get_stuff_list, switch_stuff_name, get_all_passe_stuff_names, delete_stuff_name, get_today_records

from add_record import add_record
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start_message(message):
    if not check_reg(message.from_user.id):
        bot.send_message(message.from_user.id, "Вы не зарегистрированы. Для регистрации введите секретный код")
    else:
        bot.send_message(message.from_user.id, "Вы зарегистрированы")

@bot.message_handler(commands=['help'])
def help_message(message):
    # start_message(message)
    if not check_reg(message.from_user.id):
        bot.send_message(message.from_user.id, "Вы не зарегистрированы. Для регистрации введите секретный код")
    else:  
        msg = []  
        msg.append(f'Порядок внесения данных в базу:\n  1. Выберете имя текущего наемника (через меню или введя имя)\n')
        msg.append(f'  2. Внесите данные в формате <часы проект комментарий> (через пробел, напрмер: 8 13133 уборка склада, можно без комментария)\n\n')
        msg.append(f'Для добавления в бот нового наемника введите имя, начиная с + (например, +Баймамбет киргиз). Имя нужно вводить как можно подробнее\n\n')
        msg.append(f'Команды меню:\n\switch_stuff_name --- переключить имя текущего наемника\n\delete_name --- удаление имени из бота')
        bot.send_message(message.chat.id, "".join(msg))

@bot.message_handler(commands=['today_records'])
def today_records(message):
    t_rec = get_today_records()
    msg = []
    r_count = 0
    for name_hours in t_rec["names_hours"]:
        msg.append(f'{name_hours} --- {t_rec["names_hours"][name_hours]}')
        r_count = r_count + 1
    msg = "\n".join(msg)
    if r_count > 0:
        bot.send_message(message.chat.id, f"Записи за сегодня:\n{msg}")
        bot.send_message(message.chat.id, f'Записи, ожидающие добавления в базу: {t_rec["need_download_rec_count"]}')
    else:
        bot.send_message(message.chat.id, f"Записей за сегодня не найдено")

@bot.message_handler(commands=['switch_stuff_name'])
def set_current_name(message):
    stuff_list = get_stuff_list()
    markup = types.InlineKeyboardMarkup()
    button_data = []
    for stuff in stuff_list:
        button_data.append ({"text" : stuff, "callback_data" : "switch_stuff_name" + stuff})
    for item in button_data:
        button = types.InlineKeyboardButton(text=item["text"], callback_data=item["callback_data"])
        markup.add(button)
    bot.send_message(message.chat.id, f'Выберете текущее имя наемника:', reply_markup=markup)

@bot.message_handler(commands=['delete_name'])
def delete_stuff_name_from_bot(message):
    stuff_list = get_stuff_list()
    markup = types.InlineKeyboardMarkup()
    button_data = []
    for stuff in stuff_list:
        button_data.append ({"text" : stuff, "callback_data" : "delete_stuff_name" + stuff})
    for item in button_data:
        button = types.InlineKeyboardButton(text=item["text"], callback_data=item["callback_data"])
        markup.add(button)
    bot.send_message(message.chat.id, f'Выберете имя для удаления:', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if "switch_stuff_name" in call.data:
        current_stuff_name = call.data.replace("switch_stuff_name", "")
        switch_info = switch_stuff_name(current_stuff_name)
        bot.send_message(call.message.chat.id, f'Текущее имя наемника {current_stuff_name}')
        return 0
    if "delete_stuff_name" in call.data:
        current_stuff_name = call.data.replace("delete_stuff_name", "")
        delete_info = delete_stuff_name(current_stuff_name)
        print (delete_info)
        bot.send_message(call.message.chat.id, f'Имя {current_stuff_name} удалено из бота')
        return 0

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    record = message.text.split(" ")
    if message.text == '5378':
        reg_ans = add_user_to_reg(message.from_user.id)        
        if reg_ans['success']:
            bot.send_message(message.from_user.id, "Регистрация прошла успешно")
            bot.send_message(message.from_user.id, "Перед внесением данных выберете текущего наемника")
        else:
            bot.send_message(message.from_user.id, "Не удалось зарегистрироваться")
        return 0
    if message.text[0] == "+":
        add_info = add_name_to_stuff_list(message.text[1:])
        name = add_info["name"]
        if add_info["is_allready_added"]:
            bot.send_message(message.chat.id, f'Имя {name} уже есть в списке. Добавлен {add_info["add_date"]}')
        else:
            bot.send_message(message.chat.id, f'Имя {name} добавленно в бот')        
        return 0
    if record[0].isdigit():
        add_record_info = add_record(record)
        if add_record_info["adding_record_error"]:
            bot.send_message(message.chat.id, f'Не удалось добавить запись {" ".join(record)} для {add_record_info["name"]}')
        else:
            bot.send_message(message.chat.id, f'Добавлена новая запись:\n{add_record_info["name"]} --- {add_record_info["record"]["hours"]} ч --- проект {add_record_info["record"]["project"]}')
        return 0
    all_passe_stuff_names = get_all_passe_stuff_names(message.text)
    if len(all_passe_stuff_names) > 0:
        markup = types.InlineKeyboardMarkup()
        button_data = []
        for stuff in all_passe_stuff_names:
            button_data.append ({"text" : stuff, "callback_data" : "switch_stuff_name" + stuff})
        for item in button_data:
            button = types.InlineKeyboardButton(text=item["text"], callback_data=item["callback_data"])
            markup.add(button)
        bot.send_message(message.chat.id, f'Выберете текущее имя наемника:', reply_markup=markup)


# запуск бота
bot.polling(non_stop=True, interval=0)
# if __name__=='__main__':
#     while True:
#         try:
#             bot.polling(non_stop=True, interval=0)
#         except Exception as e:
#             print("EEEEE" + e)
#             time.sleep(5)
#             continue
