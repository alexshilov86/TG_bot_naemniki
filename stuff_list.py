import json, datetime

def add_name_to_stuff_list(name):
    add_info = {"is_allready_added": False, "name": "", "add_date": ""}
    with open("staff_list.json", 'r', encoding='utf-8') as file:
        stuff_names = json.load(file)
    for stuff in stuff_names:
        if stuff["name"].lower().strip() == name.lower().strip():
            add_info = {"is_allready_added": True, "name": stuff["name"], "add_date": stuff["add_date"]}
            break
    if not add_info["is_allready_added"]:
        today = datetime.date.today().strftime("%Y-%m-%d")
        name = name.strip().title()
        stuff_names.append({"name": name, "add_date": today})
        with open("staff_list.json", 'w', encoding='utf-8') as file:
            json.dump(stuff_names, file, indent=4, ensure_ascii=False)
        add_info = {"is_allready_added": False, "name": name, "add_date": today}
    return add_info

def get_stuff_list():
    stuff_list = []
    with open("staff_list.json", 'r', encoding='utf-8') as file:
        stuff_names = json.load(file)
    for stuff in stuff_names:
        stuff_list.append(stuff["name"])
    return stuff_list

def switch_stuff_name(name):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("user_session.json", 'r', encoding='utf-8') as file:
        user_session = json.load(file)    
    user_session["current_stuff_name"] = name
    user_session["change_time"] = now
    with open("user_session.json", 'w', encoding='utf-8') as file:
        json.dump(user_session, file, indent=4, ensure_ascii=False)
    return {"change_time": now}

def get_all_passe_stuff_names(text):
    stuff_list = []
    with open("staff_list.json", 'r', encoding='utf-8') as file:
        stuff_names = json.load(file)
    for stuff in stuff_names:
        if text.lower().strip() in stuff["name"].lower().strip():
            stuff_list.append(stuff["name"])
    return stuff_list

def delete_stuff_name(name):
    del_info = {"is_deleted": False, "name": ""}
    with open("staff_list.json", 'r', encoding='utf-8') as file:
        stuff_names = json.load(file)            
    for stuff in stuff_names:
        print (stuff["name"])
        if stuff["name"] == name:
            stuff_names.remove(stuff)
            with open("staff_list.json", 'w', encoding='utf-8') as file:
                json.dump(stuff_names, file, indent=4, ensure_ascii=False)            
            del_info = {"is_deleted": True, "name": name}
            break
    
    return del_info

def get_today_records():
    t_rec = {"need_download_rec_count": 0, "names_hours": {}}
    today = datetime.date.today().strftime("%Y-%m-%d")
    with open("stuff_records.json", 'r', encoding='utf-8') as file_object:
        
        stuff_records_str = file_object.read()
        
        stuff_records = json.loads("[" + stuff_records_str + "]")
    for rec in stuff_records[1:]:
        if rec["date"] == today:
            if not rec["name"] in t_rec["names_hours"]:
                t_rec["names_hours"][rec["name"]] = rec["hours"]
            else:
                t_rec["names_hours"][rec["name"]] = t_rec["names_hours"][rec["name"]] + rec["hours"]
            t_rec["need_download_rec_count"] = t_rec["need_download_rec_count"] + 1 - rec["is_added_to_gt"]
    return t_rec
