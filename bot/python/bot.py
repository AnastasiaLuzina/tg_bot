from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
    JobQueue
)
from datetime import datetime, timedelta
import logging
import os
import json
import uuid
import pytz








TIMEZONE = pytz.timezone('Asia/Vladivostok')

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)







TOKEN = "7625773300:AAHdvynF6MFxCZFzZNKxbZQs33txG_dPJz4"
DATA_FILE = "user_history.txt"
BOOKINGS_FILE = "bookings.json"
NOTIFICATION_TIME = 60  # Уведомление за 1 час







equipment = {
    "Амплификатор": {
        "time": 90,
        "audiences": ["G-агроколлаборация", "M311", "M313"]
    },
    "Микроскоп": {
        "time": 15,
        "audiences": ["M425", "L305", "G-агроколлаборация"]
    },
    "Холодильник": {
        "time": 0,
        "audiences": ["M311", "M425", "G-коллаборация"]
    },
    "Ламинарный шкаф": {
        "time": 120,
        "audiences": ["M425", "M313", "M311", "G-агроколлаборация"]
    },
    "Центрифуга": {
        "time": 30,
        "audiences": ["M311", "L305", "G-агроколлаборация"]
    },
    "Спектрофотометр": {
        "time": 30,
        "audiences": ["M311"]
    }
}




def save_user_choice(user_id: int, choice: str):                      
    timestamp = datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")
    with open(DATA_FILE, "a") as f:
        f.write(f"{user_id}|{choice}|{timestamp}\n")



def get_user_history(user_id: int) -> list:                      
    history = []
    try:
        with open(DATA_FILE, "r") as f:
            for line in f:
                parts = line.strip().split("|")
                if parts[0] == str(user_id):
                    history.append({
                        "choice": parts[1],
                        "timestamp": parts[2],
                        "full_entry": line.strip()
                    })
    except FileNotFoundError:
        pass
    return history


def clear_user_history(user_id: int):                              
    with open(DATA_FILE, "r") as f:
        lines = f.readlines()
    
    with open(DATA_FILE, "w") as f:
        for line in lines:
            if not line.startswith(f"{user_id}|"):
                f.write(line)

def delete_equipment_type(user_id: int, equipment_name: str):
    with open(DATA_FILE, "r") as f:
        lines = f.readlines()
    
    new_lines = []
    for line in lines:
        parts = line.strip().split("|")
        if parts[0] == str(user_id) and parts[1] == equipment_name:
            continue
        new_lines.append(line)
    
    with open(DATA_FILE, "w") as f:
        f.writelines(new_lines)


def load_bookings():
    try:
        with open(BOOKINGS_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []



def save_bookings(bookings):
    with open(BOOKINGS_FILE, 'w') as f:
        json.dump(bookings, f, indent=4)



def calculate_total_time(history):
    return sum(equipment[entry['choice']]['time'] for entry in history) #пробегается на оборудованию и вытаскивает время 

def generate_calendar(start_date: datetime):
    calendar = []
    current_date = start_date
    
    for _ in range(7):
        if current_date.weekday() < 5:
            date_str = current_date.strftime("%d.%m (%a)")
            callback_data = f"date_{current_date.strftime('%Y-%m-%d')}"
            calendar.append([InlineKeyboardButton(date_str, callback_data=callback_data)])
        current_date += timedelta(days=1)
    
    return InlineKeyboardMarkup(calendar)



def get_common_audiences(history):
    if not history:
        return set() #чтобы не возникало ошибки при обработке пустой истории
    
    audiences = set(equipment[history[0]['choice']]['audiences']) #извлекает первый прибор из стории и записывает ему подходящие аудитории
    for entry in history[1:]:
        audiences &= set(equipment[entry['choice']]['audiences'])
    
    return audiences


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    buttons = [
        ["Амплификатор", "Микроскоп"],
        ["Холодильник", "Ламинарный шкаф"],
        ["Центрифуга", "Спектрофотометр"],
        ["📜 История выборов", "📅 Мои бронирования"],
        ["🛑 Забронировать"]
    ]
    keyboard = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    
    await update.message.reply_text(
        f"Привет, {user.first_name}!\nВыбери оборудование:",
        reply_markup=keyboard
    )



async def show_history(update: Update, user):
    history = get_user_history(user.id)
    
    if not history:
        await update.message.reply_text("📭 История выборов пуста")
        return
    
    equipment_count = {}
    for entry in history:
        name = entry['choice']
        equipment_count[name] = equipment_count.get(name, 0) + 1
    
    keyboard = []
    for name, count in equipment_count.items():
        keyboard.append([
            InlineKeyboardButton(
                f"❌ Удалить {name} ({count})",
                callback_data=f"delete_all_{name}"
            )
        ])
    
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back")])
    
    await update.message.reply_text(
        "📖 Ваша история выбора:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def show_my_bookings(update: Update, user):

    bookings = load_bookings()
    user_bookings = [b for b in bookings if b['user_id'] == user.id and b['status'] == 'active']
    
    if not user_bookings:
        await update.message.reply_text("У вас нет активных бронирований")
        return
    
    response = "📅 Ваши активные бронирования:\n\n"
    buttons = []
    for booking in user_bookings:
        start_time = datetime.fromisoformat(booking['start']).astimezone(TIMEZONE)
        end_time = datetime.fromisoformat(booking['end']).astimezone(TIMEZONE)
        response += (
            f"🏫 Аудитория: {booking['audience']}\n"
            f"⌚️ Время: {start_time.strftime('%d.%m.%Y %H:%M')} - {end_time.strftime('%H:%M')}\n"
            f"🆔 ID: {booking['id']}\n\n"
        )
        buttons.append([InlineKeyboardButton(
            f"❌ Отменить {booking['id'][:8]}", 
            callback_data=f"cancel_{booking['id']}"
        )])
    

    await update.message.reply_text(response, reply_markup=InlineKeyboardMarkup(buttons))



async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text
    
    if text == "📜 История выборов":
        await show_history(update, user)
    elif text == "📅 Мои бронирования":
        await show_my_bookings(update, user)
    elif text == "🛑 Стоп":
        history = get_user_history(user.id)
        if not history:
            await update.message.reply_text("❌ Сначала выберите оборудование!")
            return
        
        common_audiences = get_common_audiences(history)
        if not common_audiences:
            await update.message.reply_text("❌ Нет общих аудиторий для выбранных приборов.")
            return
        
        buttons = [[InlineKeyboardButton(aud, callback_data=f"aud_{aud}")] for aud in common_audiences]
        keyboard = InlineKeyboardMarkup(buttons)
        await update.message.reply_text(
            "🏫 Выберите аудиторию:",
            reply_markup=keyboard
        )
    elif text in equipment:
        save_user_choice(user.id, text)
        await update.message.reply_text(
            f"✅ Добавлено: {text}\n"
            f"Теперь в вашем распоряжении {len(get_user_history(user.id))} приборов"
        )
    else:
        await update.message.reply_text("❌ Неизвестное оборудование")



async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data.startswith("delete_all_"):
        equipment_name = data[len("delete_all_"):]
        delete_equipment_type(query.from_user.id, equipment_name)
        await show_history(update, query.from_user)
    elif data == "back":
        await query.delete_message()
        await start(update, context)
    elif data.startswith("aud_"):
        selected_audience = data.split("_")[1]
        context.user_data['selected_audience'] = selected_audience
        start_date = datetime.now(TIMEZONE)
        keyboard = generate_calendar(start_date)
        await query.edit_message_text(
            "📅 Выберите дату бронирования:",
            reply_markup=keyboard
        )
        
    elif data.startswith("date_"):
        selected_date_str = data.split("_")[1]
        selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").replace(
            tzinfo=TIMEZONE
        )
        context.user_data['selected_date'] = selected_date
        await show_time_slots(update, context)
    elif data.startswith("time_"):
        selected_time = datetime.fromisoformat(data.split("_")[1]).astimezone(TIMEZONE)
        context.user_data['start_time'] = selected_time
        await create_booking(update, context)
    elif data.startswith("cancel_"):
        await confirm_cancel_booking(update, context)



async def show_time_slots(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    selected_date = context.user_data['selected_date']
    selected_audience = context.user_data['selected_audience']
    history = get_user_history(query.from_user.id)
    total_time = calculate_total_time(history)
    
    time_slots = generate_time_slots(selected_date, total_time, selected_audience)
    
    if not time_slots:
        await query.edit_message_text("❌ Нет доступных временных слотов")
        return
    
    buttons = []
    for slot in time_slots:
        time_str = slot.strftime("%H:%M")
        buttons.append(InlineKeyboardButton(time_str, callback_data=f"time_{slot.isoformat()}"))
    
    await query.edit_message_text(
        "🕒 Выберите время начала:",
        reply_markup=InlineKeyboardMarkup([buttons[i:i+4] for i in range(0, len(buttons), 4)])
    )




async def show_audiences(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    history = get_user_history(query.from_user.id)
    common_audiences = get_common_audiences(history)
    
    buttons = [[InlineKeyboardButton(aud, callback_data=f"book_{aud}")] for aud in common_audiences]
    await query.edit_message_text(
        "🏫 Выберите аудиторию:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


async def create_booking(update: Update, context: ContextTypes.DEFAULT_TYPE):  # Добавлена недостающая функция
    query = update.callback_query
    user_id = query.from_user.id
    history = get_user_history(user_id)
    total_time = calculate_total_time(history)
    start_time = context.user_data['start_time']
    end_time = start_time + timedelta(minutes=total_time)
    audience = context.user_data['selected_audience']
    
    booking_id = str(uuid.uuid4())
    booking = {
        "id": booking_id,
        "user_id": user_id,
        "audience": audience,
        "start": start_time.isoformat(),
        "end": end_time.isoformat(),
        "status": "active"
    }
    
    bookings = load_bookings()
    bookings.append(booking)
    save_bookings(bookings)
    clear_user_history(user_id)
    
    await query.edit_message_text(
        f"✅ Бронирование оформлено!\n"
        f"🏫 Аудитория: {audience}\n"
        f"🕒 Время: {start_time.strftime('%d.%m.%Y %H:%M')} - {end_time.strftime('%H:%M')}\n"
        f"🆔 ID: {booking_id}"
    )




    
async def confirm_cancel_booking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query.data.startswith("cancel_"):
        await query.answer("❌ Ошибка команды")
        return
    
    booking_id = query.data.split("_", 1)[1]
    bookings = load_bookings()
    
    for booking in bookings:
        if booking['id'] == booking_id:
            booking['status'] = 'cancelled'
            save_bookings(bookings)
            await query.edit_message_text("✅ Бронирование успешно отменено")
            return
    
    await query.answer("❌ Бронирование не найдено")
    
async def notify_users(context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now(TIMEZONE)
    bookings = load_bookings()
    
    for booking in bookings:
        if booking['status'] != 'active':
            continue
            
        start_time = datetime.fromisoformat(booking['start']).astimezone(TIMEZONE)
        if (start_time - now).total_seconds() // 60 == NOTIFICATION_TIME:
            try:
                await context.bot.send_message(
                    chat_id=booking['user_id'],
                    text=f"⏰ Напоминание: Ваше бронирование аудитории {booking['audience']} "
                         f"начнется через {NOTIFICATION_TIME} минут!\n"
                         f"Время: {start_time.strftime('%d.%m.%Y %H:%M')}"
                )
            except Exception as e:
                logger.error(f"Ошибка отправки уведомления: {e}")




def generate_time_slots(start_date: datetime, total_minutes: int, audience: str):
    slots = []
    start_date = TIMEZONE.localize(start_date) if start_date.tzinfo is None else start_date
    current_time = start_date.replace(hour=8, minute=0, second=0, microsecond=0)
    end_time = start_date.replace(hour=20, minute=0, second=0, microsecond=0)
    
    # Получаем все актуальные бронирования для этой аудитории
    bookings = load_bookings()
    existing_bookings = [
        (datetime.fromisoformat(b['start']).astimezone(TIMEZONE), 
         datetime.fromisoformat(b['end']).astimezone(TIMEZONE))
        for b in bookings 
        if b['audience'] == audience 
        and b['status'] == 'active'
        and datetime.fromisoformat(b['start']).date() == start_date.date()
    ]
    
    while current_time + timedelta(minutes=total_minutes) <= end_time:
        slot_end = current_time + timedelta(minutes=total_minutes)
        
        # Проверяем пересечение с существующими бронированиями
        is_available = True
        for existing_start, existing_end in existing_bookings:
            if not (slot_end <= existing_start or current_time >= existing_end):
                is_available = False
                break
                
        # Проверяем что слот еще не начался
        if is_available and current_time >= datetime.now(TIMEZONE):
            slots.append(current_time)
            
        current_time += timedelta(minutes=30)
    
    return slots



async def confirm_cancel_booking(update: Update, context: ContextTypes.DEFAULT_TYPE):  # Исправленный обработчик
    query = update.callback_query
    if query.data == "cancel_booking":
        await query.answer("ℹ️ Выберите бронирование из списка")
        return
    
    booking_id = query.data.split("_")[1]
    bookings = load_bookings()
    
    for booking in bookings:
        if booking['id'] == booking_id:
            booking['status'] = 'cancelled'
            save_bookings(bookings)
            await query.edit_message_text("✅ Бронирование успешно отменено")
            return
    
    await query.answer("❌ Бронирование не найдено")   


def main():
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    job_queue = application.job_queue
    job_queue.run_repeating(notify_users, interval=60, first=10)
    
    application.run_polling()

if __name__ == "__main__":
    main()