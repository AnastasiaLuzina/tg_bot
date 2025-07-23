from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)
from datetime import datetime, timedelta
import json
import uuid
import pytz

TIMEZONE = pytz.timezone('Asia/Vladivostok')
TOKEN = "7553938465:AAFU2CoR2ABTOcj4injsZjzOclImjv3DV3w"
BOOKINGS_FILE = "bookings.json"



def load_bookings():
    try:
        with open(BOOKINGS_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []




def save_bookings(bookings):
    with open(BOOKINGS_FILE, 'w') as f:
        json.dump(bookings, f, indent=4)



def generate_calendar(start_date: datetime):
    calendar = []
    current_date = start_date.replace(
        hour=0, minute=0, second=0, microsecond=0
    ).astimezone(TIMEZONE)
    
    for _ in range(7):
        if current_date.weekday() < 5:  # Только пн-пт
            date_str = current_date.strftime("%d.%m (%a)")
            callback_data = f"date_{current_date.strftime('%Y-%m-%d')}"
            calendar.append([InlineKeyboardButton(date_str, callback_data=callback_data)])
        current_date += timedelta(days=1)
    
    return InlineKeyboardMarkup(calendar)

def generate_time_slots(selected_date: datetime):
    try:
        selected_date = TIMEZONE.localize(selected_date)
    except:
        selected_date = selected_date.astimezone(TIMEZONE)
        
    current_time = selected_date.replace(hour=8, minute=0)
    end_time = selected_date.replace(hour=20, minute=0)
    
    # Проверка существующих бронирований
    bookings = load_bookings()
    existing_bookings = [
        (
            datetime.fromisoformat(b['start']).astimezone(TIMEZONE),
            datetime.fromisoformat(b['end']).astimezone(TIMEZONE)
        )
        for b in bookings
        if b['status'] == 'active'
        and datetime.fromisoformat(b['start']).date() == selected_date.date()
    ]
    
    slots = []
    while current_time <= end_time - timedelta(minutes=30):
        slot_end = current_time + timedelta(minutes=30)
        
        # Проверка доступности слота
        available = True
        for exist_start, exist_end in existing_bookings:
            if current_time < exist_end and slot_end > exist_start:
                available = False
                break
                
        # Проверка что время еще не прошло
        if available and current_time >= datetime.now(TIMEZONE):
            slots.append(current_time)
            
        current_time += timedelta(minutes=30)
    
    return slots

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = generate_calendar(datetime.now(TIMEZONE))
    await update.message.reply_text(
        "🗓 Выберите дату бронирования:",
        reply_markup=keyboard
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data.startswith("date_"):
        selected_date = datetime.strptime(
            data.split("_")[1], "%Y-%m-%d"
        ).replace(tzinfo=TIMEZONE)
        
        # Сохраняем дату в контексте
        context.user_data['selected_date'] = selected_date
        await show_time_slots(query, context)
        
    elif data.startswith("time_"):
        selected_time = datetime.fromisoformat(
            data.split("_")[1]
        ).astimezone(TIMEZONE)
        await create_booking(query, selected_time)

async def show_time_slots(query, context):
    selected_date = context.user_data['selected_date']
    time_slots = generate_time_slots(selected_date)
    
    if not time_slots:
        await query.edit_message_text("❌ Нет доступных слотов на эту дату")
        return
    
    # Создаем кнопки по 4 в ряд
    buttons = [
        InlineKeyboardButton(
            slot.strftime("%H:%M"), 
            callback_data=f"time_{slot.isoformat()}"
        )
        for slot in time_slots
    ]
    keyboard = [buttons[i:i+4] for i in range(0, len(buttons), 4)]
    
    await query.edit_message_text(
        "🕒 Выберите время начала:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def create_booking(query, start_time):
    user_id = query.from_user.id
    end_time = start_time + timedelta(minutes=30)
    
    new_booking = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "start": start_time.isoformat(),
        "end": end_time.isoformat(),
        "status": "active"
    }
    
    # Сохраняем бронирование
    bookings = load_bookings()
    bookings.append(new_booking)
    save_bookings(bookings)
    
    await query.edit_message_text(
        f"✅ Бронирование оформлено!\n"
        f"📅 Дата: {start_time.strftime('%d.%m.%Y')}\n"
        f"⏰ Время: {start_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')}\n"
        f"🆔 ID: {new_booking['id']}"
    )

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_callback))
    application.run_polling()

if __name__ == "__main__":
    main()