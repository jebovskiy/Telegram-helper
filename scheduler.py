from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import DAILY_TASKS, WEEKEND_TASKS, EVENING_SURVEY_TIME
import plan_engine as pe


scheduler = AsyncIOScheduler()
REGISTERED_USER_ID = None
BOT_APPLICATION = None


def set_user(user_id: int):
    global REGISTERED_USER_ID
    REGISTERED_USER_ID = user_id


def set_application(application):
    global BOT_APPLICATION
    BOT_APPLICATION = application


async def send_morning_reminder():
    if REGISTERED_USER_ID is None or BOT_APPLICATION is None:
        return

    user_id = REGISTERED_USER_ID
    msg = pe.build_daily_message(user_id)
    await BOT_APPLICATION.bot.send_message(chat_id=user_id, text=msg)


async def send_evening_survey():
    if REGISTERED_USER_ID is None or BOT_APPLICATION is None:
        return

    user_id = REGISTERED_USER_ID
    msg = pe.build_evening_survey()
    await BOT_APPLICATION.bot.send_message(chat_id=user_id, text=msg)


def setup_scheduler():
    for task in DAILY_TASKS:
        hour, minute = map(int, task["time"].split(":"))
        scheduler.add_job(
            send_morning_reminder,
            "cron",
            hour=hour,
            minute=minute,
            day_of_week="mon-fri",
            id=f"morning_{task['time']}",
        )

    for task in WEEKEND_TASKS:
        hour, minute = map(int, task["time"].split(":"))
        scheduler.add_job(
            send_morning_reminder,
            "cron",
            hour=hour,
            minute=minute,
            day_of_week="sat,sun",
            id=f"weekend_{task['time']}",
        )

    hour, minute = map(int, EVENING_SURVEY_TIME.split(":"))
    scheduler.add_job(
        send_evening_survey,
        "cron",
        hour=hour,
        minute=minute,
        id="evening_survey",
    )


def start_scheduler():
    setup_scheduler()
    scheduler.start()


def stop_scheduler():
    scheduler.shutdown()
