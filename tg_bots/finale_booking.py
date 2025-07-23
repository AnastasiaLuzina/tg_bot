import requests
import time
import threading


TOKEN = "7425335973:AAGeqG2Rk0FXOJE7cewejl9Op2Dg6vhCi_0"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}/"

offset = 0
states = {}
user_tasks = {}
const_tasks = {}
active_reminders = {}

def send_reminder(chat_id, task_name):
    requests.post(
        BASE_URL + "sendMessage",
        json={
            "chat_id": chat_id, 
            "text": f"🔔 Напоминание!\nЗадача: {task_name}"
        }
    )

def schedule_reminder(chat_id, task_name, minutes):
    def reminder_job():
        time.sleep(minutes * 60)
        send_reminder(chat_id, task_name)
    
    thread = threading.Thread(target=reminder_job)
    thread.start()

    if chat_id not in active_reminders: 
        active_reminders[chat_id] = []

    active_reminders[chat_id].append({
    "task_name": task_name,
    "remind_minutes": minutes, 
    "thread": thread,
    "end_time": time.time() + minutes * 60
    })


def send_inline_buttons(chat_id, text):
    keyboard = {
        "inline_keyboard": [
            [{"text": "➕ Добавить задачу", "callback_data": "reminder"}],
            [{"text": "📃 Список всех задач", "callback_data": "list_tasks"}],
             [{"text": "Тыкни не пожалеешь :)", "callback_data": "meme_bro"}]  #забыла запятую    
        ]
    }
    requests.post(
        BASE_URL + "sendMessage",
        json={
            "chat_id": chat_id,
            "text": text,
            "reply_markup": keyboard
        }
    )


def send_inline_buttons_for_list(chat_id,text):
    keyboard = {
        "inline_keyboard": [
            [{"text": "Редактировать имя задачи", "callback_data": "editor"}],
            [{"text": "Удалить задачу", "callback_data": "delete"}]
           
        ]
    }

    requests.post(
        BASE_URL + "sendMessage",
        json={
            "chat_id": chat_id,
            "text": text,
            "reply_markup": keyboard
        }
    )

def print_all_tasks_const(chat_id):
    message = "📋 Ваши задачи:\n"
    if chat_id in const_tasks and const_tasks[chat_id]:
        for task in const_tasks[chat_id]:  # Убрали enumerate
            message += f"• {task['task_name']} через {task['remind_minutes']} мин\n"
    else:
        message = "📭 Список задач пуст!"
    return message


def handle_reminder_flow(chat_id, text):

    current_state = states.get(chat_id)
    
    if current_state == "waiting_for_task_name":
        user_tasks[chat_id] = {"task_name": text}

        states[chat_id] = "waiting_for_remind_minutes"
        requests.post(
            BASE_URL + "sendMessage",
            json={"chat_id": chat_id, "text": f"Задача '{text}' добавлена. Через сколько минут напомнить?"}
        )
    
    elif current_state == "waiting_for_remind_minutes":
        try:
            remind_minutes = float(text)
                
            task_name = user_tasks[chat_id]["task_name"]
            
            if chat_id not in const_tasks:
                const_tasks[chat_id] = []

            const_tasks[chat_id].append({
                "task_name": task_name,
                "remind_minutes": remind_minutes
            })
            
            schedule_reminder(chat_id, task_name, remind_minutes)
            
            del states[chat_id]
            del user_tasks[chat_id]
            
            requests.post(
                BASE_URL + "sendMessage",
                json={"chat_id": chat_id, "text": f"✅ Напоминание установлено!\nЗадача: {task_name}\nЧерез {remind_minutes} минут"}
            )
            send_inline_buttons(chat_id, "Выберите действие:")
            
        except ValueError:
            requests.post(
                BASE_URL + "sendMessage",
                json={"chat_id": chat_id, "text": "❌ Наш бот не может кинуть на прогиб время введите положительное количество минут!"}
            )



def handle_list_flow(chat_id, text):
    global offset

    current_state = states.get(chat_id)

    if current_state == "waiting_for_editor":
         try:
            print("мы остановились на этом шаге 1 ")

            make_button_editor_tasks(chat_id, const_tasks, "Выберите задачу для редактирования")

            updates = requests.get(
            BASE_URL + "getUpdates",
            params={"offset": offset, "timeout": 30}
            ).json()

            print("мы остановились на этом шаге 2 ")

            for update in updates.get("result", []): # исправление т к этого параметра может и не быть
                offset = update["update_id"] + 1
                
                if "callback_query" in update:

                    callback = update["callback_query"]
                    data = callback["data"]   

                    states[chat_id] = "waiting_for_new_name"
                    user_tasks[chat_id] = {"selected_task": data} #моя ошибка забыла сохранить -> чтобы 

                    requests.post(
                            BASE_URL + "sendMessage",
                            json={"chat_id": chat_id, "text": "Введите новое название для задачи"}
                        )
                    print("мы остановились на этом шаге 3 ")

         except ValueError:
            requests.post(
                BASE_URL + "sendMessage",
                json={"chat_id": chat_id, "text": "ну какая-то ошибка я хз какая"}
            )


    
    elif current_state == "waiting_for_new_name": 
        
        try:
            print("мы остановились на этом шаге 4")

            task_id = int(user_tasks[chat_id].get("selected_task"))
            new_name = text # не поняла что это нужно сохранять под новую переменную

            if chat_id in const_tasks and 0 <= task_id < len(const_tasks[chat_id]):
                const_tasks[chat_id][task_id]["task_name"] = new_name #task_id = user_tasks[chat_id].get("selected_task")

           
            print("мы остановились на этом шаге 5")
            
            const_tasks[chat_id][task_id]["task_name"] = new_name

            print("мы остановились на этом шаге 6")

            requests.post(
                    BASE_URL + "sendMessage",
                    json={"chat_id": chat_id, "text": f"✅ Название задачи {task_id} изменено на: {new_name}. Можете продолжить работу с ботом :)"}
                )
            make_button_editor_tasks(chat_id, const_tasks, "Может еще что-нибудь исправить)")

            print("мы остановились на этом шаге 7")

                
            del states[chat_id]
            del user_tasks[chat_id] # забыла сбросить состояние чтобы по новой запускать :)

        except ValueError:
            requests.post(
                BASE_URL + "sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": "Нут тут ошибка я хз какая"}
            )





    elif current_state == "waiting_for_delete":
        try:

            input_task_name = text.strip().lower() 
            
            if chat_id not in const_tasks or len(const_tasks[chat_id]) == 0:
                requests.post(BASE_URL + "sendMessage", json={
                    "chat_id": chat_id, 
                    "text": "🚫 У вас нет задач для удаления!"
                })
                del states[chat_id]  
                return

            # Ищем задачу в списке
            found = False
            for task in const_tasks[chat_id]:
                
                if task["task_name"].lower() == input_task_name:
                    
                    const_tasks[chat_id].remove(task)
                    found = True
                    
                    if chat_id in active_reminders:
                        active_reminders[chat_id] = [r for r in active_reminders[chat_id] 
                                                if r["task_name"].lower() != input_task_name]
                    
                    requests.post(BASE_URL + "sendMessage", json={
                        "chat_id": chat_id,
                        "text": f"✅ Задача '{task['task_name']}' удалена!"
                    })
                    break
                    
            if not found:
                requests.post(BASE_URL + "sendMessage", json={
                    "chat_id": chat_id,
                    "text": "Такой задачи нет я хз где она потерялась"
                })


            del states[chat_id]
            send_inline_buttons(chat_id, "Что дальше?:")

        except Exception as e:
            print(f"ОШИБКА: {e}")
            requests.post(BASE_URL + "sendMessage", json={
                "chat_id": chat_id,
                "text": "😢 Что-то пошло не так, попробуйте еще раз"
            })

def make_button_editor_tasks(chat_id, const_tasks, text):
    keyboard = []
    if chat_id in const_tasks:  # Убрать and data in active_reminders[chat_id]  if chat_id in const_tasks:❌
        for task_id, task_data in enumerate(const_tasks[chat_id]): # та же самая проблема нужно брать именно айди чата
            keyboard.append([{
                "text": task_data["task_name"], # task_data["name"] -  указала не тот ключ
                "callback_data": str(task_id)  # Индекс как строка
            }])
    
    requests.post(
        BASE_URL + "sendMessage",
        json={
            "chat_id": chat_id,
            "text":  text,
            "reply_markup": {"inline_keyboard": keyboard}
        }
    )


while True:
    try:

        updates = requests.get(
            BASE_URL + "getUpdates",
            params={"offset": offset, "timeout": 30}
        ).json()
        


        if "result" in updates:
            for update in updates.get("result", []): #добавляем для безопасности
                offset = update["update_id"] + 1 

                if "message" in update:
                    message = update["message"]
                    chat_id = message["chat"]["id"]
                    text = message.get("text", "")
                    

                    if text == "/start":
                        send_inline_buttons(chat_id, "Выберите действие:")
                    else:

                      
                        if chat_id in states:
                            current_state = states[chat_id]
                            
                            if  current_state in ["waiting_for_editor", "waiting_for_delete","waiting_for_new_name"]:
                                handle_list_flow(chat_id, text)

                            else:
                                handle_reminder_flow(chat_id, text)
                        else:
                             send_inline_buttons(chat_id, "Выможете вот эти действия еще поделать :D") 


                elif "callback_query" in update:

                    callback = update["callback_query"]
                    chat_id = callback["message"]["chat"]["id"]
                    data = callback["data"]

                    requests.post(
                        BASE_URL + "answerCallbackQuery",
                        json={"callback_query_id": callback["id"]}
                    )

                    if data == "reminder":
                        states[chat_id] = "waiting_for_task_name"

                        requests.post(
                            BASE_URL + "sendMessage",
                            json={"chat_id": chat_id, "text": "📝 Напишите название вашей задачи:"}
                        )
                    
                    elif data == "list_tasks":
                        tasks_message = print_all_tasks_const(chat_id)

                        requests.post(
                            BASE_URL + "sendMessage",
                            json={"chat_id": chat_id, "text": tasks_message}
                        )

                        send_inline_buttons_for_list(chat_id,"Вы можете совершить следующие действия над задачами")
                    
                    elif data == "editor":
                        states[chat_id] = "waiting_for_editor"

                        requests.post(
                            BASE_URL + "sendMessage",
                            json={"chat_id": chat_id, "text": "Выберите какой из активных задач хотите изменить"}
                        )
                        handle_list_flow(chat_id, text)
                    
                    elif data == "delete":
                        states[chat_id] = "waiting_for_delete"

                        requests.post(
                            BASE_URL + "sendMessage",
                            json={
                                "chat_id": chat_id,
                                "text": "✏️ Введите точное название задачи для удаления:"
                            }
                        )
                    elif data == "meme_bro":
                        requests.post(
                            BASE_URL + "sendMessage",
                            json={
                                "chat_id": chat_id,
                                "text": "   -> @My_memas_bot"
                            }
                        )
        time.sleep(3)
    except Exception as e:
        print(f"Ошибка: {e}")
        time.sleep(5)



