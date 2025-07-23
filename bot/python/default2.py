import requests
import time

TOKEN = "7723969529:AAF_7Y4O4t4k2s0CiQXsW1EtxoCliiQYLzk"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}/"

last_update_id = 0

while True:
    try:
        response = requests.get(
            BASE_URL + "getUpdates",
            params = {"offset":last_update_id}
        )

        data = response.json()

        if not data.get("ok"):
            print("Ошибка в ответе API:", data)
            time.sleep(2)
            continue

        for update in data.get("result"):
            current_update_id = update.get("update_id")

            if current_update_id > last_update_id:
                last_update_id = current_update_id

                print(f"Напиши id сообщение:{last_update_id}")

                message = update.get("message")
                chat_info = message.get("chat")
                chat_id = chat_info.get("id")
                text = message.get("text")
                username = chat_info.get("username", "нет никнейма")

                if text and chat_id:
                    requests.post(
                        BASE_URL + "sendMessage", 
                        params = { 
                            "chat_id": chat_id,
                            "text": f"{text}"
                        }                   
                    )

                    print(f"Отправлен ответ в чат {chat_id}")

        time.sleep(1)


    except Exception as exp:
        print(f"Произошла ошибка:{exp}")
        time.sleep(5)

       #  query-строки 