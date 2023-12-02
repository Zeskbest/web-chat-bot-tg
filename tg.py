from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

from config import Config
from db import get_person


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    person = get_person(update.effective_user.id, update.effective_chat.id)
    await update.message.reply_text(
        f'Hello {update.effective_user.first_name}, '
        f'your text: {update.message.text}, '
        f'your id: {person.id}'
    )


def run_tg_bot():
    app = ApplicationBuilder().token(Config.tg_token).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.run_polling()


if __name__ == '__main__':
    run_tg_bot()
