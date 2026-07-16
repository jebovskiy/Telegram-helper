from openai import OpenAI
from config import NVIDIA_API_KEY, NVIDIA_BASE_URL, NVIDIA_MODEL

client = OpenAI(
    api_key=NVIDIA_API_KEY,
    base_url=NVIDIA_BASE_URL,
)

SYSTEM_PROMPT = """Ты — ИИ-помощник для фриланс-разработчика, который продаёт услуги по разработке Telegram Mini Apps, SaaS и AI-сервисов.

Твой клиент:
- Хочет заработать €3000+ до 21 августа
- Продаёт: Telegram Mini Apps (€500-1500), SaaS MVP (€1000-3000), Telegram Bots (€200-800), доработки (€50-500)
- Имеет кейсы: StudyAI (AI SaaS), Master.by (Telegram Mini App)
- Ищет клиентов на: Telegram, LinkedIn, Upwork

Ты помогаешь с:
1. Советами по продажам
2. Написанием сообщений клиентам
3. Ответами на возражения
4. Составлением коммерческих предложений
5. Любыми другими вопросами

Отвечай кратко и по делу на русском языке."""


def chat(user_message: str, history: list = None) -> str:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if history:
        messages.extend(history)

    messages.append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model=NVIDIA_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Ошибка: {str(e)}"


def sales_advice(situation: str) -> str:
    prompt = f"""Ситуация в продажах: {situation}

Дай конкретный совет:
- Что написать клиенту
- Как ответить на возражение
- Как правильно сформулировать предложение"""

    return chat(prompt)


def write_message(purpose: str, context: str = "") -> str:
    prompt = f"""Напиши сообщение для клиента.

Цель: {purpose}
{f'Контекст: {context}' if context else ''}

Сообщение должно быть:
- Персонализированным
- Кратким
- С чётким call-to-action"""

    return chat(prompt)
