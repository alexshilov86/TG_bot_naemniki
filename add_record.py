import json, datetime

def add_record(record):
    # считываем текущего пользователя
    with open("user_session.json", 'r', encoding='utf-8') as file:
        user_session = json.load(file)  
    name = user_session["current_stuff_name"]
    today = datetime.date.today().strftime("%d.%m.%y")
    try:
        hours = int(record["hours"])
        project = record["project"]
        comment = record["comment"]
        new_record = {"name": name, "hours": hours, "project": project, "comment": comment, "is_added_to_gt": False, "date": today}
        add_error = False
    except Exception as e:
        add_error = True
        new_record ={}
    if not add_error:
        with open("stuff_records.json", 'r', encoding='utf-8') as file:
            stuff_records = json.load(file)
        stuff_records.append(new_record)
        with open("stuff_records.json", 'w', encoding='utf-8') as file:
            json.dump(stuff_records, file, indent=4, ensure_ascii=False)
    return {"adding_record_error": add_error, "record": new_record, "name": name}

def pre_adding_rec(record):
    # считываем текущего пользователя
    with open("user_session.json", 'r', encoding='utf-8') as file:
        user_session = json.load(file)  
    name = user_session["current_stuff_name"]
    today = datetime.date.today().strftime("%d.%m.%y")
    try:
        hours = int(record[0])
        project = record[1]
        comment = " ".join(record[2:])
        new_record = {"name": name, "hours": hours, "project": project, "comment": comment, "is_added_to_gt": False, "date": today}
        add_error = False
    except Exception as e:
        add_error = True
        new_record ={}
    if not add_error:
        with open("user_session.json", 'r', encoding='utf-8') as file:
            user_session = json.load(file)
        user_session["record"] = new_record
        with open("user_session.json", 'w', encoding='utf-8') as file:
            json.dump(user_session, file, indent=4, ensure_ascii=False)
    return {"adding_record_error": add_error, "record": new_record, "name": name} 

def get_record_from_session():
    # считываем текущего пользователя
    with open("user_session.json", 'r', encoding='utf-8') as file:
        user_session = json.load(file) 
    record = user_session["record"]
    return record
