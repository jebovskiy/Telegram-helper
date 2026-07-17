from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from config import DAILY_TASKS, WEEKEND_TASKS, EVENING_SURVEY_TIME, TIMEZONE
import plan_engine as pe
import asyncio
import database as db


scheduler = BackgroundScheduler(timezone=TIMEZONE)
REGISTERED_USER_ID = None
BOT_APPLICATION = None


def set_user(user_id: int):
    global REGISTERED_USER_ID
    REGISTERED_USER_ID = user_id


def restore_user():
    global REGISTERED_USER_ID
    user_id = db.get_registered_user()
    if user_id:
        REGISTERED_USER_ID = user_id


def set_application(application):
    global BOT_APPLICATION
    BOT_APPLICATION = application


def _run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(coro)
    finally:
        loop.close()


def send_morning_reminder():
    if REGISTERED_USER_ID is None or BOT_APPLICATION is None:
        return

    user_id = REGISTERED_USER_ID
    msg = pe.build_daily_message(user_id)
    _run_async(BOT_APPLICATION.bot.send_message(chat_id=user_id, text=msg))


def send_evening_survey():
    if REGISTERED_USER_ID is None or BOT_APPLICATION is None:
        return

    user_id = REGISTERED_USER_ID
    msg = pe.build_evening_survey()
    _run_async(BOT_APPLICATION.bot.send_message(chat_id=user_id, text=msg))


def setup_scheduler():
    for task in DAILY_TASKS:
        hour, minute = map(int, task["time"].split(":"))
        scheduler.add_job(
            send_morning_reminder,
            CronTrigger(hour=hour, minute=minute, day_of_week="mon-fri",
                        timezone=TIMEZONE),
            id=f"morning_{task['time']}",
        )

    for task in WEEKEND_TASKS:
        hour, minute = map(int, task["time"].split(":"))
        scheduler.add_job(
            send_morning_reminder,
            CronTrigger(hour=hour, minute=minute, day_of_week="sat,sun",
                        timezone=TIMEZONE),
            id=f"weekend_{task['time']}",
        )

    hour, minute = map(int, EVENING_SURVEY_TIME.split(":"))
    scheduler.add_job(
        send_evening_survey,
        CronTrigger(hour=hour, minute=minute, timezone=TIMEZONE),
        id="evening_survey",
    )


def start_scheduler():
    setup_scheduler()
    scheduler.start()


def stop_scheduler():
    scheduler.shutdown()
