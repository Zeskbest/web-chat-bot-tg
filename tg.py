from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

from config import Config


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}, your text: {update.message.text}')


def run_tg_bot():
    app = ApplicationBuilder().token(Config.tg_token).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.run_polling()


if __name__ == '__main__':
    run_tg_bot()
