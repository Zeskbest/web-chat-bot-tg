from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

from config import Config
from db import get_person, sess
from tg_conversation import get_recapcha_handler, Question, queue_to_ask
from web_chat_bot import WebChatBot


async def ask_human(img, text, options):
    q = Question(img, text, options)
    queue_to_ask.put_nowait(q)
    return await q.get_answer()


def run_tg_bot():
    chat_bot = WebChatBot(ask_human)

    async def post_init(app_):
        await chat_bot.init()

    async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        person = get_person(update.effective_user.id, update.effective_chat.id)
        resp, person.web_chat_id = chat_bot.ask(update.message.text, person.web_chat_id)
        sess.flush([person])
        sess.commit()
        await update.message.reply_text(
            resp,
            reply_to_message_id=update.message.id,
        )

    app = ApplicationBuilder().token(Config.tg_token).post_init(post_init).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.add_handler(get_recapcha_handler())

    app.run_polling()


if __name__ == '__main__':
    (run_tg_bot())
