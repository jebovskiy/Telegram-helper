from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
import database as db
import plan_engine as pe
import ai_helper as ai
from scheduler import set_user

WAITING_SURVEY = 1
WAITING_AI_CHAT = 2
WAITING_SALES_ADVICE = 3
WAITING_WRITE_MSG = 4


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    set_user(user_id)
    db.save_user(user_id, user.username, user.first_name)
    db.init_db()

    reply_keyboard = [
        [KeyboardButton("📋 План дня"), KeyboardButton("📊 Статистика")],
        [KeyboardButton("📝 Итоги дня"), KeyboardButton("🤖 ИИ-помощник")],
        [KeyboardButton("💼 Совет по продажам"), KeyboardButton("✉️ Написать клиенту")],
    ]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Привет! Я твой помощник по продажам.\n\n"
        "Нажми на кнопку внизу или используй команды:\n"
        "/plan — план на сегодня\n"
        "/stats — статистика\n"
        "/survey — записать итоги дня\n"
        "/ai — чат с ИИ\n"
        "/sales — совет по продажам\n"
        "/write — написать сообщение клиенту\n"
        "/help — помощь",
        reply_markup=reply_markup,
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Команды:\n\n"
        "/plan — показать план на сегодня\n"
        "/stats — статистика и прогресс\n"
        "/survey — записать итоги дня\n"
        "/ai — чат с ИИ-помощником\n"
        "/sales — совет по продажам\n"
        "/write — написать сообщение клиенту\n"
        "/help — это сообщение"
    )


async def plan_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    msg = pe.build_daily_message(user_id)
    await update.message.reply_text(msg)


async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    msg = pe.build_stats_message(user_id)
    await update.message.reply_text(msg)


async def ai_chat_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Задай вопрос ИИ-помощнику.\n"
        "Он поможет с продажами, напишет сообщение или ответит на любой вопрос.\n\n"
        "Просто напиши сообщение:"
    )
    return WAITING_AI_CHAT


async def ai_chat_receive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.strip()

    await update.message.reply_text("Думаю...")

    response = ai.chat(user_message)
    await update.message.reply_text(response)
    return ConversationHandler.END


async def sales_advice_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Опиши ситуацию:\n"
        "- Что написал клиент?\n"
        "- Какой вопрос?\n"
        "- На каком этапе диалог?\n\n"
        "И я дам совет."
    )
    return WAITING_SALES_ADVICE


async def sales_advice_receive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    situation = update.message.text.strip()

    await update.message.reply_text("Анализирую...")

    response = ai.sales_advice(situation)
    await update.message.reply_text(response)
    return ConversationHandler.END


async def write_message_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Напиши:\n"
        "1. Какое сообщение нужно (знакомство, follow-up, коммерческое предложение)\n"
        "2. Контекст (если есть)\n\n"
        "Пример: 'Первое сообщение для стартапа, который ищет разработчика Telegram Mini App'"
    )
    return WAITING_WRITE_MSG


async def write_message_receive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    await update.message.reply_text("Пишу сообщение...")

    response = ai.write_message(text)
    await update.message.reply_text(response)
    return ConversationHandler.END


async def survey_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = pe.build_evening_survey()
    await update.message.reply_text(msg)
    return WAITING_SURVEY


async def survey_receive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    try:
        parts = [x.strip() for x in text.split(",")]
        contacts = int(parts[0]) if len(parts) > 0 else 0
        messages = int(parts[1]) if len(parts) > 1 else 0
        responses = int(parts[2]) if len(parts) > 2 else 0
        calls = int(parts[3]) if len(parts) > 3 else 0
        money = float(parts[4]) if len(parts) > 4 else 0.0
    except (ValueError, IndexError):
        await update.message.reply_text(
            "Не удалось распознать ответ. Попробуй ещё раз.\n"
            "Формат: 30, 15, 3, 1, 0"
        )
        return WAITING_SURVEY

    from datetime import date
    today = date.today()
    db.save_daily_log(user_id, today, contacts, messages, responses, calls, money)

    reason, focus = pe.analyze_evening_survey(
        user_id, contacts, messages, responses, calls, money
    )

    response = "Итоги записаны!\n\n"

    if reason:
        response += f"Завтра: {focus}"
    else:
        response += "Всё идёт по плану. Завтра продолжаем!"

    response += f"\n\n{pe.build_stats_message(user_id)}"

    await update.message.reply_text(response)
    return ConversationHandler.END


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id

    if query.data == "plan_today":
        msg = pe.build_daily_message(user_id)
        await query.edit_message_text(msg)

    elif query.data == "stats":
        msg = pe.build_stats_message(user_id)
        await query.edit_message_text(msg)

    elif query.data == "survey":
        msg = pe.build_evening_survey()
        await query.edit_message_text(msg)
        context.user_data["awaiting_survey"] = True


async def handle_survey_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("awaiting_survey"):
        return

    user_id = update.effective_user.id
    text = update.message.text.strip()

    try:
        parts = [x.strip() for x in text.split(",")]
        contacts = int(parts[0]) if len(parts) > 0 else 0
        messages = int(parts[1]) if len(parts) > 1 else 0
        responses = int(parts[2]) if len(parts) > 2 else 0
        calls = int(parts[3]) if len(parts) > 3 else 0
        money = float(parts[4]) if len(parts) > 4 else 0.0
    except (ValueError, IndexError):
        await update.message.reply_text(
            "Не удалось распознать ответ. Формат: 30, 15, 3, 1, 0"
        )
        return

    from datetime import date
    today = date.today()
    db.save_daily_log(user_id, today, contacts, messages, responses, calls, money)

    reason, focus = pe.analyze_evening_survey(
        user_id, contacts, messages, responses, calls, money
    )

    response = "Итоги записаны!\n\n"
    if reason:
        response += f"Завтра: {focus}"
    else:
        response += "Всё идёт по плану. Завтра продолжаем!"

    response += f"\n\n{pe.build_stats_message(user_id)}"

    context.user_data["awaiting_survey"] = False
    await update.message.reply_text(response)


async def handle_reply_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    if context.user_data.get("awaiting_survey"):
        await handle_survey_text(update, context)
        return

    if text == "📋 План дня":
        msg = pe.build_daily_message(user_id)
        await update.message.reply_text(msg)
    elif text == "📊 Статистика":
        msg = pe.build_stats_message(user_id)
        await update.message.reply_text(msg)
    elif text == "📝 Итоги дня":
        msg = pe.build_evening_survey()
        await update.message.reply_text(msg)
        context.user_data["awaiting_survey"] = True
    elif text == "🤖 ИИ-помощник":
        await update.message.reply_text("Задай вопрос ИИ-помощнику:\n\nПросто напиши сообщение:")
        context.user_data["awaiting_ai_chat"] = True
    elif text == "💼 Совет по продажам":
        await update.message.reply_text("Опиши ситуацию с клиентом:")
        context.user_data["awaiting_sales_advice"] = True
    elif text == "✉️ Написать клиенту":
        await update.message.reply_text("Напиши, какое сообщение нужно:")
        context.user_data["awaiting_write_msg"] = True
    elif context.user_data.get("awaiting_ai_chat"):
        await update.message.reply_text("Думаю...")
        response = ai.chat(text)
        await update.message.reply_text(response)
        context.user_data["awaiting_ai_chat"] = False
    elif context.user_data.get("awaiting_sales_advice"):
        await update.message.reply_text("Анализирую...")
        response = ai.sales_advice(text)
        await update.message.reply_text(response)
        context.user_data["awaiting_sales_advice"] = False
    elif context.user_data.get("awaiting_write_msg"):
        await update.message.reply_text("Пишу сообщение...")
        response = ai.write_message(text)
        await update.message.reply_text(response)
        context.user_data["awaiting_write_msg"] = False


def get_handlers():
    survey_conv = ConversationHandler(
        entry_points=[CommandHandler("survey", survey_start)],
        states={
            WAITING_SURVEY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, survey_receive)
            ],
        },
        fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)],
    )

    ai_chat_conv = ConversationHandler(
        entry_points=[CommandHandler("ai", ai_chat_start)],
        states={
            WAITING_AI_CHAT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, ai_chat_receive)
            ],
        },
        fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)],
    )

    sales_conv = ConversationHandler(
        entry_points=[CommandHandler("sales", sales_advice_start)],
        states={
            WAITING_SALES_ADVICE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, sales_advice_receive)
            ],
        },
        fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)],
    )

    write_conv = ConversationHandler(
        entry_points=[CommandHandler("write", write_message_start)],
        states={
            WAITING_WRITE_MSG: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, write_message_receive)
            ],
        },
        fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)],
    )

    return [
        CommandHandler("start", start),
        CommandHandler("help", help_cmd),
        CommandHandler("plan", plan_cmd),
        CommandHandler("stats", stats_cmd),
        survey_conv,
        ai_chat_conv,
        sales_conv,
        write_conv,
        CallbackQueryHandler(button_callback),
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_reply_keyboard),
    ]
