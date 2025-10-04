import telebot
import gspread
import os, json, time
from telebot import types
from dotenv import load_dotenv
from user_info import check_reg, add_user_to_reg
from stuff_list import add_name_to_stuff_list, get_stuff_list, switch_stuff_name, get_all_passe_stuff_names, delete_stuff_name, get_today_records
from googleTable import add_records_to_googletable
from add_record import add_record, pre_adding_rec, get_record_from_session

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
# открытие базы данных и базы регистрации
service_account_info_json = os.getenv('GSPREAD_SERVICE_ACCOUNT_JSON')
base_id =os.getenv('BASE_GOOGLE_TABLE_ID')
service_account_info = json.loads(service_account_info_json)
gc = gspread.service_account_from_dict(service_account_info)

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
        return 0    
    if not check_reg(message.from_user.id):
        bot.send_message(message.from_user.id, "Вы не зарегистрированы. Для регистрации введите секретный код")
    else:  
        msg = []  
        msg.append(f'Порядок внесения данных в базу:\n  1. Выберете имя текущего наемника (через меню или введя имя)\n')
        msg.append(f'  2. Внесите данные в формате <часы проект комментарий> (через пробел, напрмер: 8 13133 уборка склада, можно без комментария)\n\n')
        msg.append(f'Для добавления в бот нового наемника введите имя, начиная с + (например, +сергей борисов). Имя лучше выбирать как можно подробнее\n\n')
        msg.append(f'Команды меню:\n\\switch_name --- переключить имя текущего наемника\n\\delete_name --- удаление имени из бота\n')
        msg.append(f'\\today_records --- посмотреть все записи за сегодня\n')
        msg.append(f'\\add_records_to_googletable --- внести записи в гугл таблицу\n')
        bot.send_message(message.chat.id, "".join(msg))

@bot.message_handler(commands=['today_records'])
def today_records(message):
    if not check_reg(message.from_user.id):
        bot.send_message(message.from_user.id, "Вы не зарегистрированы. Для регистрации введите секретный код")
        return 0    
    t_rec = get_today_records()
    msg = []
    r_count = 0
    for name_hours in t_rec["names_hours"]:
        msg.append(f'{name_hours} --- {t_rec["names_hours"][name_hours]}')
        r_count = r_count + 1
    msg = "\n".join(msg)
    if r_count > 0:
        bot.send_message(message.chat.id, f"Записи за сегодня:\n{msg}")
    else:
        bot.send_message(message.chat.id, f"Записей за сегодня не найдено")
    bot.send_message(message.chat.id, f'Записи, ожидающие добавления в базу: {t_rec["need_download_rec_count"]}')

@bot.message_handler(commands=['switch_name'])
def set_current_name(message):
    if not check_reg(message.from_user.id):
        bot.send_message(message.from_user.id, "Вы не зарегистрированы. Для регистрации введите секретный код")
        return 0    
    stuff_list = get_stuff_list()
    markup = types.InlineKeyboardMarkup()
    button_data = []
    for stuff in stuff_list:
        button_data.append ({"text" : stuff, "callback_data" : "switch_stuff_name" + stuff})
    for item in button_data:
        button = types.InlineKeyboardButton(text=item["text"], callback_data=item["callback_data"])
        markup.add(button)
    if len(stuff_list) == 0:
        bot.send_message(message.chat.id, f'В боте пока нет наемников. Для добавления введите имя, начиная с +')
    else:
        bot.send_message(message.chat.id, f'Выберете текущее имя наемника:', reply_markup=markup)

@bot.message_handler(commands=['delete_name'])
def delete_stuff_name_from_bot(message):
    if not check_reg(message.from_user.id):
        bot.send_message(message.from_user.id, "Вы не зарегистрированы. Для регистрации введите секретный код")
        return 0    
    stuff_list = get_stuff_list()
    markup = types.InlineKeyboardMarkup()
    button_data = []
    for stuff in stuff_list:
        button_data.append ({"text" : stuff, "callback_data" : "delete_stuff_name" + stuff})
    for item in button_data:
        button = types.InlineKeyboardButton(text=item["text"], callback_data=item["callback_data"])
        markup.add(button)
    if len(stuff_list) == 0:
        bot.send_message(message.chat.id, f'В боте пока нет наемников. Для добавления введите имя, начиная с +')
    else:
        bot.send_message(message.chat.id, f'Выберете имя для удаления:', reply_markup=markup)

@bot.message_handler(commands=['add_records_to_googletable'])
def add_to_googletable(message):
    if not check_reg(message.from_user.id):
        bot.send_message(message.from_user.id, "Вы не зарегистрированы. Для регистрации введите секретный код")
        return 0    
    global gc, base_id
    add_rec_to_gt_info = add_records_to_googletable(message, gc, base_id)
    if not add_rec_to_gt_info["error"]:
        bot.send_message(message.chat.id, f'Добавленно {add_rec_to_gt_info["count"]} записей')
    else:
        bot.send_message(message.chat.id, f'Не удалось записать данные. Ошибка: {add_rec_to_gt_info["error_msg"]}')
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if not check_reg(call.message.from_user.id):
        bot.send_message(call.message.from_user.id, "Вы не зарегистрированы. Для регистрации введите секретный код")
        return 0    
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
    if call.data == "add_record_from_session":
        record = get_record_from_session()
        add_record_info = add_record(record)
        if add_record_info["adding_record_error"]:
            bot.send_message(call.message.chat.id, f'Не удалось добавить запись {" ".join(record)} для {add_record_info["name"]}')
        else:
            bot.send_message(call.message.chat.id, f'Добавлена новая запись:\n{add_record_info["name"]} --- {add_record_info["record"]["hours"]} ч --- проект {add_record_info["record"]["project"]}')
        return 0

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == '5378':
        reg_ans = add_user_to_reg(message.from_user.id)        
        if reg_ans['success']:
            bot.send_message(message.from_user.id, "Регистрация прошла успешно")
            bot.send_message(message.from_user.id, "Перед внесением данных выберете текущего наемника")
        else:
            bot.send_message(message.from_user.id, "Не удалось зарегистрироваться")
        return 0    
    if not check_reg(message.from_user.id):
        bot.send_message(message.from_user.id, "Вы не зарегистрированы. Для регистрации введите секретный код")
        return 0    
    record = message.text.split(" ")

    if message.text[0] == "+":
        add_info = add_name_to_stuff_list(message.text[1:])
        name = add_info["name"]
        if add_info["is_allready_added"]:
            bot.send_message(message.chat.id, f'Имя {name} уже есть в списке. Добавлен {add_info["add_date"]}')
        else:
            bot.send_message(message.chat.id, f'Имя {name} добавленно в бот')        
        return 0
    if record[0].isdigit():
        pre_adding_info = pre_adding_rec(record)
        if not pre_adding_info["adding_record_error"]:
            adding_caption = f'{pre_adding_info["name"]} --- {pre_adding_info["record"]["hours"]}ч --- проект {pre_adding_info["record"]["project"]} --- {pre_adding_info["record"]["comment"]}'
            button1 = types.InlineKeyboardButton(text=adding_caption, callback_data="add_record_from_session")
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(button1)
            bot.send_message(message.chat.id, "Внести следующую запись:", reply_markup=keyboard)
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
# bot.polling(non_stop=True, interval=0)
if __name__=='__main__':
    while True:
        try:
            bot.polling(non_stop=True, interval=0)
        except Exception as e:
            print(e)
            time.sleep(5)
            continue
