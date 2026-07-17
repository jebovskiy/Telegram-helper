import asyncio
import logging
import threading
import os
from flask import Flask
from telegram.ext import ApplicationBuilder
from config import BOT_TOKEN
from handlers import get_handlers
from scheduler import start_scheduler, stop_scheduler, set_application, restore_user
import database as db

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.route("/")
def health():
    return "Bot is running", 200


@app.route("/health")
def health_check():
    return {"status": "ok"}, 200


async def post_init(application):
    db.init_db()
    restore_user()
    logger.info("Database initialized, user restored")


async def post_shutdown(application):
    stop_scheduler()
    logger.info("Scheduler stopped")


def run_bot():
    bot_app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )

    for handler in get_handlers():
        bot_app.add_handler(handler)

    set_application(bot_app)
    start_scheduler()
    logger.info("Bot starting...")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(
            bot_app.run_polling(allowed_updates=["message", "callback_query"])
        )
    finally:
        loop.close()


def main():
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()

    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Starting web server on port {port}")
    app.run(host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
