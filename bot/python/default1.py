import requests
import time

TOKEN = "7723969529:AAF_7Y4O4t4k2s0CiQXsW1EtxoCliiQYLzk"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}/"

last_update_id = 0  # Храним ID последнего обработанного сообщения

while True:  # Бесконечный цикл для постоянной работы бота
    try:
        # 1. Делаем запрос к методу getUpdates с параметром offset
        response = requests.get(
            BASE_URL + "getUpdates",
            params={"offset": last_update_id + 1}  # Получаем только НОВЫЕ сообщения
        )

        data = response.json()
        
        # 3. Проверяем успешность ответа от Telegram
        if not data.get("ok"):
            print("Ошибка в ответе API:", data)
            time.sleep(2)
            continue

        # 4. Обрабатываем каждое обновление
        for update in data.get("result"):
            current_update_id = update.get("update_id")
            
            # 5. Обновляем ID последнего сообщения
            if current_update_id > last_update_id:
                last_update_id = current_update_id
                
                # 6. Извлекаем данные из сообщения
                message = update.get("message", {})
                chat_info = message.get("chat", {})
                chat_id = chat_info.get("id")
                text = message.get("text", "")
                
                # 7. Отправляем ответ только если есть текст и chat_id
                if text and chat_id:
                    requests.post(
                        BASE_URL + "sendMessage",
                        params={
                            "chat_id": chat_id,
                            "text": f"Вы написали: {text}"
                        }
                    )
                    print(f"Отправлен ответ в чат {chat_id}")

        # 8. Пауза между проверками обновлений
        time.sleep(1)

    except Exception as e:
        print(f"Произошла ошибка: {e}")
        time.sleep(5)