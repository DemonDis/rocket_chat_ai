import requests
import logging
from src.config import *
from src.prompts.rick_and_morty_prompt import get_rick_and_morty_prompt, RICK_AND_MORTY_RESPONSES
from src.prompts.george_carlin_prompt import get_george_carlin_prompt, GEORGE_CARLIN_RESPONSES
from src.prompts.get_quentin_tarantino_prompt import get_quentin_tarantino_prompt, TARANTINO_RESPONSES

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self, default_prompt='george_carlin'):
        logger.info(f"Инициализация LLM сервиса с промптом: {default_prompt}...")
        self.prompts = {
            'rick_and_morty': get_rick_and_morty_prompt,
            'george_carlin': get_george_carlin_prompt,
            'quentin_tarantino': get_quentin_tarantino_prompt
            # Добавьте другие промпты здесь
        }
        self.responses = {
            'rick_and_morty': RICK_AND_MORTY_RESPONSES,
            'george_carlin': GEORGE_CARLIN_RESPONSES,
            'quentin_tarantino': TARANTINO_RESPONSES,
        }
        self.current_prompt_name = None
        self.current_responses = None
        self.set_prompt(default_prompt)

    def set_prompt(self, prompt_name):
        if prompt_name in self.prompts:
            self.current_prompt_generator = self.prompts[prompt_name]
            self.current_prompt_name = prompt_name
            self.current_responses = self.responses[prompt_name]
            logger.info(f"Активный промпт установлен на: {prompt_name}")
        else:
            logger.warning(f"Промпт '{prompt_name}' не найден. Использование промпта по умолчанию ('rick_and_morty').")
            self.current_prompt_name = 'rick_and_morty'
            self.current_prompt_generator = self.prompts['rick_and_morty']
            self.current_responses = self.responses['rick_and_morty']

    def summarize_with_llm(self, messages_text, bot_username):
        """Суммаризация чата с использованием выбранного промпта"""
        try:
            logger.info("Начало суммаризации...")

            if not messages_text:
                return self.current_responses.get("empty_messages_text", "Ничего нет. Абсолютно.")

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
                return self.current_responses.get("only_bot_messages", "Только автоматические сообщения. Ничего интересного.")

            conversation = "\n".join(lines)
            if len(conversation) > 18000:
                conversation = conversation[-17500:] + "\n\n...а до этого была целая простыня бреда, поверь мне на слово."

            # Используем вынесенный промпт
            prompt = self.current_prompt_generator(conversation)

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
                return summary + self.current_responses.get("summary_suffix", "")

            elif response.status_code == 429:
                return self.current_responses.get("too_many_requests", "Слишком много запросов. Попробуйте позже.")
            else:
                return self.current_responses.get("api_error", "Произошла ошибка: код {status_code}.").format(status_code=response.status_code)

        except requests.exceptions.Timeout:
            return self.current_responses.get("timeout", "Превышено время ожидания ответа от LLM.")
        except Exception as e:
            logger.error(f"Ошибка в summarize_with_llm: {e}")
            return self.current_responses.get("generic_exception", "Произошла внутренняя ошибка.")
