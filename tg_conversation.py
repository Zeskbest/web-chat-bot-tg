#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
import asyncio

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

READY, ASKED = range(2)

ADMINS = {143185162}

queue_to_ask = asyncio.Queue(maxsize=1)
queue_answered = asyncio.Queue(maxsize=1)


class Question:
    def __init__(self, img: bytes, text: str, reply_keys: list[str]):
        self.img = img
        self.text = text
        self.reply_keys = reply_keys

        self.answer = None
        self.future = asyncio.Future()

    async def get_answer(self):
        await self.future
        return self.answer

    def set_answer(self, answer):
        assert answer in self.reply_keys
        self.answer = answer
        self.future.set_result(1)
        # pass


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and tells the user is going to recapture."""
    user = update.message.from_user
    if user.id not in ADMINS:
        return -1
    reply_keyboard = [["OK", "cancel"]]
    await update.message.reply_text(
        text="Hi! Now you're ready to handle recapcha!",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Acknowledged"
        ),
    )

    return READY


async def ready(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected gender and asks for a photo."""
    user = update.message.from_user
    if user not in ADMINS:
        pass
    try:
        question: Question = queue_to_ask.get_nowait()
    except asyncio.QueueEmpty:
        await update.message.reply_text(
            text=f"Nothing to do.",
            reply_markup=ReplyKeyboardRemove(),
        )
        return READY
    else:
        await update.message.reply_photo(
            photo=question.img,
            caption=f"Question: {question.text}",
            reply_markup=ReplyKeyboardMarkup(
                [question.reply_keys], one_time_keyboard=True, input_field_placeholder="Acknowledged"
            ),
        )
        queue_answered.put_nowait(question)
        return ASKED


async def asked(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected gender and asks for a photo."""
    user = update.message.from_user
    if user not in ADMINS:
        return -1
    question: Question = queue_to_ask.get_nowait()
    question.set_answer(update.message.text)
    queue_answered.put_nowait(question)
    await update.message.reply_text(
        text=f"Ok",
        reply_markup=ReplyKeyboardRemove(),
    )
    return READY


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    await update.message.reply_text(
        "Bye!", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def get_recapcha_handler():
    return ConversationHandler(
        entry_points=[CommandHandler("start_interactive", start)],
        states={
            READY: [MessageHandler(filters.Regex("."), ready)],
            ASKED: [MessageHandler(filters.Regex("."), asked)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
