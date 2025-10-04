import json, gspread

def add_records_to_googletable(message, gc, base_id):
    spreadsheet = gc.open_by_key(base_id)
    ws_trati = spreadsheet.worksheet("Траты")
    data_to_add = []
    # подготовка данных дня внесения в базу
    with open("stuff_records.json", 'r', encoding='utf-8') as file:
        stuff_records = json.load(file)
    for rec in stuff_records:
        row_to_add = ["" for i in range(10)]
        if not rec["is_added_to_gt"]:
            row_to_add[0] = rec["date"]
            row_to_add[1] = rec["project"]
            row_to_add[2] = "глобал"
            row_to_add[3] = "васильев а"
            row_to_add[4] = "склад"
            row_to_add[5] = rec["comment"]
            row_to_add[6] = ""
            row_to_add[7] = rec["name"]
            row_to_add[8] = "зарплата"
            row_to_add[9] = rec["hours"]
            data_to_add.append(row_to_add)
    if len(data_to_add) == 0:
        add_info = {"error": False, "count": 0, "error_msg": ""}
        return add_info
    ws_data = ws_trati.get_all_values(value_render_option=gspread.utils.ValueRenderOption.unformatted)
    last_row = len(ws_data)
    update_range = "B" + str(last_row+1)
    try:
        ws_trati.update(update_range, data_to_add)
        add_count = 0
        for rec in stuff_records:
            if not rec["is_added_to_gt"]:
                rec["is_added_to_gt"] = True
                add_count = add_count + 1
        with open("stuff_records.json", 'w', encoding='utf-8') as file:
            json.dump(stuff_records, file, indent=4, ensure_ascii=False)         
        add_info = {"error": False, "count": add_count, "error_msg": ""}
    except Exception as e:
        add_info = {"error": True, "count": 0, "error_msg": e}
    return add_info