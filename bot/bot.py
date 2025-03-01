
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Токен вашего бота
TOKEN = '7625773300:AAHdvynF6MFxCZFzZNKxbZQs33txG_dPJz4'

# Обработчик команды /start
def start(update: Update, context: CallbackContext):
    update.message.reply_text('Привет! Я твой бот. Как дела?')

# Обработчик текстовых сообщений
def echo(update: Update, context: CallbackContext):
    user_text = update.message.text
    update.message.reply_text(f'Вы написали: {user_text}')

def main():
    # Создаем Updater и передаем ему токен
    updater = Updater(TOKEN)

    # Получаем диспетчер для регистрации обработчиков
    dp = updater.dispatcher

    # Регистрируем обработчик команды /start
    dp.add_handler(CommandHandler("start", start))

    # Регистрируем обработчик текстовых сообщений
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Запускаем бота
    updater.start_polling()

    # Работаем до тех пор, пока не нажмем Ctrl+C
    updater.idle()

if __name__ == '__main__':
    main()