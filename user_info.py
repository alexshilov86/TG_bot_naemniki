import json

def check_reg (chat_id):
    file_path = 'user_info_reg.json'
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            registered_id_list = data['registered_id_list']
            if chat_id in registered_id_list:
                return True
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{file_path}'. Check file format.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    return False

def add_user_to_reg(chat_id):
    file_path = 'user_info_reg.json'
    reg_ans = {'success' : False}
    try:
        with open(file_path, 'r') as file:    
            data = json.load(file)
            registered_id_list = data['registered_id_list']
        registered_id_list.append(chat_id)
        with open(file_path, 'w') as file:
            data['registered_id_list'] = registered_id_list
            json.dump(data, file, indent=4)
        reg_ans['success'] = True
    except Exception as e:
        reg_ans['success'] = False
    return reg_ans
