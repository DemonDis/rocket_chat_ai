import requests
import logging
from src.config import *

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        logger.info("Инициализация LLM сервиса...")

    def summarize_with_llm(self, messages_text, bot_username):
        """Рик Санчез читает ваш чат и рассказывает, что вы там накосячили"""
        try:
            logger.info("Рик врубил портал и залетел в ваш чатик...")

            if not messages_text:
                return "*отрыжка* Пусто тут, Морти. Даже хуже, чем твой мозг."

            participants = set()
            lines = []

            for msg in reversed(messages_text):
                username = msg.get('username') or msg.get('u', {}).get('username')
                if not username or username == bot_username:
                    continue

                participants.add(username)
                text = msg.get('msg', '').strip()
                if text:
                    lines.append(f"@{username}: {text}")

            if not lines:
                return "Тут только боты писали, Морти. Скучно."

            conversation = "\n".join(lines)
            if len(conversation) > 18000:
                conversation = conversation[-17500:] + "\n\n...а до этого была целая простыня бреда, поверь мне на слово."

            prompt = f"""Ты — Рик Санчез, самый гениальный ублюдок во всех мультивселенных.
Прочитай этот чат и выдай жёсткую, но точную сводку — как будто рассказываешь Морти, что за дерьмо тут творилось.

Правила от Рика:
- Всех называй строго @username — никаких «незнакомец», «кто-то», я тебя застрелю.
- Если человек один — всё равно пиши @его_ник, мне пох.
- Решений нет — пиши «ничего не решили, как обычно».
- Ссылки, файлы, цифры — дословно, я не дебил.
- Мат заменяй на аналогии и цинизм — по вкусу, но не переборщи.

Формат (не смей ломать):

Тема этого дерьма: [коротко и зло]

Кто тут трындел:
• @username — что нёс, что предлагал, где обосрался
• @username — ...

Что происходило по порядку:
1. @кто втирал про...
2. ...

Решения (если мозги всё-таки включили):
• @кто заливает фикс прямо сейчас
• @кто напишет постмортем до пятницы
или
• Ничего не решили, типичный день в этом гадюшнике

Осталось сделать (или опять всё повисло):
• @кто должен починить до завтра
• ...

Общее настроение: все в панике / дружно рофлят / академический онанизм / все спят

Ключевые артефакты:
Ссылки: ...
Файлы: ...
Технологии и цифры: ...

В конце подпись: — Рик Санчез, C-137

Чат, который надо разобрать:
{conversation}
"""

            url = f"{OPEN_AI_BASE_URL}{OPEN_AI_COMPLETIONS_PATHNAME}"
            headers = {
                "Authorization": f"Bearer {OPEN_AI_API_KEY}",
                "Content-Type": "application/json"
            }

            data = {
                "model": LLM_NAME,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 2200,
                "temperature": 0.8
            }

            response = requests.post(url, headers=headers, json=data, timeout=180)

            if response.status_code == 200:
                summary = response.json()['choices'][0]['message']['content'].strip()
                return summary + "\n\n*отрыжка* Wubba Lubba Dub Dub!"

            elif response.status_code == 429:
                return "Слишком много запросов, Морти! Даже мне нужен перерыв на мега-семена."
            else:
                return f"Портал-гана сломался, код {response.status_code}. Иди чини сам."

        except requests.exceptions.Timeout:
            return "Нейросеть задумалась, как Дроздович перед съёмкой про редких жуков. Подождём."
        except Exception as e:
            logger.error(f"Ошибка в summarize_with_llm: {e}")
            return "Простите, я слегка растерялся среди всей этой переписки."
