import requests
import logging
from src.config import *
from src.prompts.rick_and_morty_prompt import get_rick_and_morty_prompt, RICK_AND_MORTY_RESPONSES, RICK_AND_MORTY_SETTINGS
from src.prompts.george_carlin_prompt import get_george_carlin_prompt, GEORGE_CARLIN_RESPONSES, GEORGE_CARLIN_SETTINGS
from src.prompts.get_quentin_tarantino_prompt import get_quentin_tarantino_prompt, TARANTINO_RESPONSES, TARANTINO_SETTINGS
from src.prompts.get_neutral_professional_prompt import get_neutral_professional_prompt, NEUTRAL_RESPONSES, PROF_SETTINGS

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self, default_prompt='prof'):
        logger.info(f"Инициализация LLM сервиса с промптом: {default_prompt}...")
        self.prompts = {
            'rick_and_morty': get_rick_and_morty_prompt,
            'george_carlin': get_george_carlin_prompt,
            'quentin_tarantino': get_quentin_tarantino_prompt,
            'prof': get_neutral_professional_prompt
            # Добавьте другие промпты здесь
        }
        self.responses = {
            'rick_and_morty': RICK_AND_MORTY_RESPONSES,
            'george_carlin': GEORGE_CARLIN_RESPONSES,
            'quentin_tarantino': TARANTINO_RESPONSES,
            'prof': NEUTRAL_RESPONSES
        }
        self.settings = {
            'rick_and_morty': RICK_AND_MORTY_SETTINGS,
            'george_carlin': GEORGE_CARLIN_SETTINGS,
            'quentin_tarantino': TARANTINO_SETTINGS,
            'prof': PROF_SETTINGS
        }
        self.current_prompt_name = None
        self.current_responses = None
        self.current_settings = None
        self.set_prompt(default_prompt)

    def set_prompt(self, prompt_name):
        if prompt_name in self.prompts:
            self.current_prompt_generator = self.prompts[prompt_name]
            self.current_prompt_name = prompt_name
            self.current_responses = self.responses[prompt_name]
            self.current_settings = self.settings[prompt_name]
            logger.info(f"Активный промпт установлен на: {prompt_name}")
            return True
        else:
            logger.warning(f"Промпт '{prompt_name}' не найден. Использование промпта по умолчанию ('prof').")
            return False

    def summarize_with_llm(self, messages_text, bot_username, prompt_name=None):
        """Суммаризация чата с использованием выбранного промпта"""
        try:
            if prompt_name and prompt_name != self.current_prompt_name:
                if not self.set_prompt(prompt_name):
                    # Fallback to current prompt if new prompt not found
                    logger.warning(f"Не удалось установить промпт '{prompt_name}'. Использование текущего промпта '{self.current_prompt_name}'.")

            logger.info(f"Начало суммаризации с промптом '{self.current_prompt_name}'...")

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
                "max_tokens": MAX_TOKENS,
                "temperature": self.current_settings.get("temperature", TEMPERATURE)
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
