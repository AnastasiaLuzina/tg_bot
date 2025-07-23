import requests
import time
import random

TOKEN = "7822297204:AAEu1kG0BXMMkedOSmpnlBJcn71WOfvJQZ0"

BASE_URL = f"https://api.telegram.org/bot{TOKEN}/"
print("Бот запущен...")

url_side = "https://img.randme.me/"  

url_cat  = "https://cataas.com/cat"

url_fun = "https://i.pinimg.com/736x/52/3e/e7/523ee7a05068db3f8925f451497b4952.jpg"

last_update_id = 0

while True:
    try:
        updates = requests.get(BASE_URL + "getUpdates", params={"offset": last_update_id + 1, "timeout": 30}).json()

        time.sleep(3)

        print("Вы взяли с сайта обновление")

        if "result" in updates:
            for update in updates.get("result", []):
                last_update_id = update["update_id"]

                if "message" in update:
                    message = update["message"]
                    chat_id = message["chat"]["id"]
                    text = message.get("text", "")
                   

                    print("Вы вошли в словарь message")

                    keyboard = {
                        "inline_keyboard": [
                            [{"text": " ➖🧐➖ \n 🔜Т〰Ы〰К〰Н〰И🔙\n ➖➖➖ ", "callback_data": "meme_bro"}],
                            [{"text": " ➖🐱➖ \n 🔜Т〰Ы〰К〰Н〰И🔙\n ➖➖➖ ", "callback_data": "cat_bro"}],
                            [{"text": " ➖😂➖ \n 🔜Сделай〰свой〰мем🔙\n ➖➖➖ ", "callback_data": "fun_bro"}]
                        ]
                    }
                    print("Мы создали клавиатуру")

                    if text == "/start": 
                        response = requests.post(
                            BASE_URL + "sendMessage",
                            json={  
                                "chat_id": chat_id,
                                "text": "Good! Добро пожаловать в мемного ХИ-ХИ ХА-ХА бота!",
                                "reply_markup": keyboard
                            }
                        )

                        print(response.json())

                        print("Мы отправили клавиатуру")
                        time.sleep(5)

                elif "callback_query" in update:
                    callback = update["callback_query"]
                    data = callback["data"]
                    chat_id = callback["message"]["chat"]["id"]  

                    requests.post(
                        BASE_URL + "answerCallbackQuery",
                        json={"callback_query_id": callback["id"]}  
                    )

                    if data == "meme_bro":
                      
                        requests.post(
                            BASE_URL + "sendPhoto",
                            json={
                                "chat_id": chat_id,
                                "photo":  f"{url_side}?nocache={random.randint(1,1000000)}",  
                                "caption": '                             ╭────────────────╮\n       │  😱 ВАШ МЕМ СУДАРЬ 🤯 │\n       ╰────────────────╯',
                                "reply_markup": keyboard
                            }
                        )
                    elif data == "cat_bro":

                        requests.post(
                            BASE_URL + "sendPhoto",
                            json={
                                "chat_id": chat_id,
                                "photo":  f"{url_cat}?nocache={random.randint(1,1000000)}", 
                                "caption": ' ╭────────────────╮    \n    │  🌚 ВАШ КОТ СУДАРЬ 💃│\n╰────────────────╯',
                                "reply_markup": keyboard
                            }
                        )

                    elif data == "fun_bro":

                        text = message.get("text", "")



                        requests.post(
                            BASE_URL + "sendMessage",
                            json={
                                "chat_id": chat_id,
                                "text": "Введите текст к картинке "
                            }
                        )

                        requests.post(
                            BASE_URL + "sendPhoto",
                            json={
                                "chat_id": chat_id,
                                "photo":  f"{url_fun}?nocache={random.randint(1,1000000)}",  # Используем прямую ссылку
                                "caption": ' ╭────────────────╮    \n    │  🌚 ВАШ МЕМАСИК СУДАРЬ 💃│\n╰────────────────╯',
                                "reply_markup": keyboard
                            }
                        )


                        time.sleep(6)

                    else:
                        requests.post(
                            BASE_URL + "sendMessage",
                            json={
                                "chat_id": chat_id,
                                "text": "Случилась ошибочка при взятии картинки :("
                            }
                        )

    except Exception as e:
        print(e)
        time.sleep(10)
                    














            

            
