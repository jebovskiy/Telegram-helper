from datetime import date, timedelta
from config import DEADLINE, DAILY_TASKS, WEEKEND_TASKS, WEEKDAYS_RU
import database as db


def days_until_deadline():
    today = date.today()
    delta = (DEADLINE - today).days
    return max(delta, 0)


def is_weekend(d: date = None):
    if d is None:
        d = date.today()
    return d.weekday() >= 5


def get_tasks_for_day(d: date = None):
    if d is None:
        d = date.today()
    if is_weekend(d):
        return WEEKEND_TASKS
    return DAILY_TASKS


def build_daily_message(user_id: int, d: date = None):
    if d is None:
        d = date.today()

    days_left = days_until_deadline()
    weekday = WEEKDAYS_RU[d.weekday()]
    tasks = get_tasks_for_day(d)

    adjustment = db.get_adjustment(user_id, d)
    focus_note = ""
    if adjustment:
        focus_note = f"\n\nСфокусируйся на: {adjustment['focus_area']}\nПричина: {adjustment['reason']}"

    total_earned = db.get_total_earned(user_id)

    if is_weekend(d):
        header = f"Сегодня {weekday} (облегчённый режим)\nДней до дедлайна: {days_left}"
    else:
        header = f"Сегодня {weekday}\nДней до дедлайна: {days_left}\nЗаработано: €{total_earned:.0f}"

    task_lines = []
    for t in tasks:
        task_lines.append(f"⏰ {t['time']} — {t['task']}\n{t['description']}")

    tasks_text = "\n\n".join(task_lines)

    return f"Доброе утро!\n\n{header}{focus_note}\n\nПлан на сегодня:\n\n{tasks_text}"


def analyze_evening_survey(user_id: int, contacts: int, messages: int,
                           responses: int, calls: int, money: float):
    today = date.today()
    yesterday = today - timedelta(days=1)

    prev_log = db.get_daily_log(user_id, yesterday)
    adjustment_reason = ""
    focus_area = ""

    if contacts < 30:
        adjustment_reason = "Мало новых контактов"
        focus_area = "Утром усилить поиск клиентов — найти 50+ контактов"
    elif messages < 20:
        adjustment_reason = "Мало сообщений"
        focus_area = "Уделить больше времени персональным сообщениям"
    elif responses == 0 and messages > 10:
        adjustment_reason = "Нет ответов при активных рассылках"
        focus_area = "Пересмотреть шаблоны сообщений, попробовать другой подход"
    elif calls == 0 and contacts > 20:
        adjustment_reason = "Нет созвонов"
        focus_area = "Сфокусироваться на follow-up с теми, кто ответил"

    if money > 0:
        adjustment_reason = "Хороший день!"
        focus_area = "Продолжать в том же духе, закрывать текущие сделки"

    if adjustment_reason:
        db.save_adjustment(user_id, today, adjustment_reason, focus_area)

    return adjustment_reason, focus_area


def build_evening_survey():
    return (
        "Время подвести итоги дня!\n\n"
        "Ответь на вопросы (просто отправь числа через запятую):\n\n"
        "1. Сколько новых контактов нашёл?\n"
        "2. Сколько сообщений отправил?\n"
        "3. Сколько ответов получил?\n"
        "4. Сколько созвонов назначил?\n"
        "5. Сколько заработал (в €)?\n\n"
        "Формат: 30, 15, 3, 1, 0\n"
        "Или напиши подробнее, если хочешь."
    )


def build_stats_message(user_id: int):
    days_left = days_until_deadline()
    total_earned = db.get_total_earned(user_id)
    stats = db.get_total_stats(user_id)

    progress_pct = (total_earned / 3000) * 100 if total_earned > 0 else 0
    daily_target = 3000 / max(days_left, 1)

    msg = (
        "📊 Статистика\n\n"
        f"Дней до 21 августа: {days_left}\n"
        f"Заработано: €{total_earned:.0f} из €3000\n"
        f"Прогресс: {progress_pct:.1f}%\n"
        f"Нужно в день: €{daily_target:.0f}\n\n"
        f"Всего контактов: {stats.get('total_contacts', 0)}\n"
        f"Всего сообщений: {stats.get('total_messages', 0)}\n"
        f"Всего ответов: {stats.get('total_responses', 0)}\n"
        f"Всего созвонов: {stats.get('total_calls', 0)}\n"
        f"Дней с активностью: {stats.get('days_logged', 0)}"
    )

    return msg


def build_plan_message(user_id: int):
    days_left = days_until_deadline()

    if days_left > 21:
        phase = "Этап 1: Портфолио"
        focus = "Оформить кейсы StudyAI и Master.by"
    elif days_left > 14:
        phase = "Этап 2: Площадки"
        focus = "Upwork, Fiverr, LinkedIn, шаблоны откликов"
    else:
        phase = "Этап 3: Активные продажи"
        focus = "50-100 касаний в день"

    msg = (
        f"📋 Текущий план\n\n"
        f"Фаза: {phase}\n"
        f"Фокус: {focus}\n"
        f"Дней до дедлайна: {days_left}\n\n"
        "Еженедельные цели:\n"
        "• 250-500 касаний\n"
        "• 5-10 созвонов\n"
        "• 2-5 коммерческих предложений\n"
        "• 1-3 оплаченных заказа"
    )

    return msg
