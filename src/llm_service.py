import requests
import logging
from src.config import *
from src.prompts.rick_and_morty_prompt import get_rick_and_morty_prompt, RICK_AND_MORTY_RESPONSES, RICK_AND_MORTY_SETTINGS
from src.prompts.george_carlin_prompt import get_george_carlin_prompt, GEORGE_CARLIN_RESPONSES, GEORGE_CARLIN_SETTINGS
from src.prompts.get_quentin_tarantino_prompt import get_quentin_tarantino_prompt, TARANTINO_RESPONSES, TARANTINO_SETTINGS
from src.prompts.get_neutral_professional_prompt import get_neutral_professional_prompt, NEUTRAL_RESPONSES, PROF_SETTINGS

# Настройка логирования для данного модуля
logger = logging.getLogger(__name__)

# Класс для взаимодействия с Large Language Models (LLM)
class LLMService:
    def __init__(self, default_prompt='prof'):
        """
        Инициализирует LLMService, загружает доступные промпты и устанавливает промпт по умолчанию.
        
        :param default_prompt: Имя промпта по умолчанию.
        """
        logger.info(f"Инициализация LLM сервиса с промптом: {default_prompt}...")
        # Словарь функций, генерирующих промпты
        self.prompts = {
            'rick_and_morty': get_rick_and_morty_prompt,
            'george_carlin': get_george_carlin_prompt,
            'quentin_tarantino': get_quentin_tarantino_prompt,
            'prof': get_neutral_professional_prompt
            # Добавьте другие промпты здесь
        }
        # Словарь предварительно заданных ответов для разных промптов
        self.responses = {
            'rick_and_morty': RICK_AND_MORTY_RESPONSES,
            'george_carlin': GEORGE_CARLIN_RESPONSES,
            'quentin_tarantino': TARANTINO_RESPONSES,
            'prof': NEUTRAL_RESPONSES
        }
        # Словарь настроек для разных промптов (например, temperature)
        self.settings = {
            'rick_and_morty': RICK_AND_MORTY_SETTINGS,
            'george_carlin': GEORGE_CARLIN_SETTINGS,
            'quentin_tarantino': TARANTINO_SETTINGS,
            'prof': PROF_SETTINGS
        }
        self.current_prompt_name = None # Текущее имя активного промпта
        self.current_responses = None # Текущие предварительно заданные ответы
        self.current_settings = None # Текущие настройки промпта
        self.set_prompt(default_prompt) # Установка промпта по умолчанию

    def set_prompt(self, prompt_name):
        """
        Устанавливает активный промпт, ответы и настройки на основе его имени.
        
        :param prompt_name: Имя промпта, который нужно установить.
        :return: True, если промпт успешно установлен, False в противном случае.
        """
        if prompt_name in self.prompts: # Проверяем, существует ли промпт с таким именем
            self.current_prompt_generator = self.prompts[prompt_name] # Устанавливаем функцию-генератор промпта
            self.current_prompt_name = prompt_name # Обновляем имя активного промпта
            self.current_responses = self.responses[prompt_name] # Обновляем текущие ответы
            self.current_settings = self.settings[prompt_name] # Обновляем текущие настройки
            logger.info(f"Активный промпт установлен на: {prompt_name}")
            return True
        else:
            logger.warning(f"Промпт '{prompt_name}' не найден. Использование промпта по умолчанию ('prof').")
            return False

    def summarize_with_llm(self, messages_text, bot_username, prompt_name=None):
        """
        Суммаризирует сообщения чата с использованием выбранной LLM и промпта.
        
        :param messages_text: Список сообщений для суммаризации.
        :param bot_username: Имя пользователя бота (для исключения его сообщений).
        :param prompt_name: Имя промпта, который нужно использовать для суммаризации (если отличается от текущего).
        :return: Суммаризированный текст или сообщение об ошибке.
        """
        try:
            # Если указан другой промпт, пытаемся его установить
            if prompt_name and prompt_name != self.current_prompt_name:
                if not self.set_prompt(prompt_name):
                    # Откат к текущему промпту, если новый не найден
                    logger.warning(f"Не удалось установить промпт '{prompt_name}'. Использование текущего промпта '{self.current_prompt_name}'.")

            logger.info(f"Начало суммаризации с промптом '{self.current_prompt_name}'...")

            if not messages_text:
                return self.current_responses.get("empty_messages_text", "Ничего нет. Абсолютно.") # Ответ, если нет сообщений

            participants = set() # Множество участников беседы
            lines = [] # Список обработанных строк сообщений

            # Обработка сообщений: собираем текст и участников
            for msg in reversed(messages_text): # Обрабатываем сообщения в обратном порядке (от старых к новым)
                username = msg.get('username') or msg.get('u', {}).get('username') # Извлекаем имя пользователя
                if not username or username == bot_username: # Игнорируем сообщения от бота
                    continue

                participants.add(username) # Добавляем участника
                text = msg.get('msg', '').strip() # Извлекаем текст сообщения
                if text:
                    lines.append(f"@{username}: {text}") # Формируем строку "Пользователь: Текст"

            if not lines:
                return self.current_responses.get("only_bot_messages", "Только автоматические сообщения. Ничего интересного.") # Ответ, если остались только сообщения бота

            conversation = "\n".join(lines) # Объединяем все строки в одну беседу
            # Обрезаем беседу, если она слишком длинная, чтобы избежать превышения лимитов токенов
            if len(conversation) > 18000:
                conversation = conversation[-17500:] + "\n\n...а до этого была целая простыня бреда, поверь мне на слово."

            # Используем вынесенный промпт для генерации запроса к LLM
            prompt = self.current_prompt_generator(conversation)

            # Параметры HTTP-запроса к API LLM
            url = f"{OPEN_AI_BASE_URL}{OPEN_AI_COMPLETIONS_PATHNAME}"
            headers = {
                "Authorization": f"Bearer {OPEN_AI_API_KEY}",
                "Content-Type": "application/json"
            }

            data = {
                "model": LLM_NAME, # Используемая модель LLM
                "messages": [{"role": "user", "content": prompt}], # Сообщения для модели (наш промпт)
                "max_tokens": MAX_TOKENS, # Максимальное количество токенов в ответе
                "temperature": self.current_settings.get("temperature", TEMPERATURE) # Температура генерации (креативность)
            }

            response = requests.post(url, headers=headers, json=data, timeout=180) # Отправляем запрос

            # Обработка ответа от API LLM
            if response.status_code == 200:
                summary = response.json()['choices'][0]['message']['content'].strip() # Извлекаем суммаризацию
                return summary + self.current_responses.get("summary_suffix", "") # Добавляем суффикс, если есть

            elif response.status_code == 429: # Если превышен лимит запросов
                return self.current_responses.get("too_many_requests", "Слишком много запросов. Попробуйте позже.")
            else: # Другие ошибки API
                return self.current_responses.get("api_error", "Произошла ошибка: код {status_code}.").format(status_code=response.status_code)

        except requests.exceptions.Timeout: # Обработка исключения таймаута
            return self.current_responses.get("timeout", "Превышено время ожидания ответа от LLM.")
        except Exception as e: # Общая обработка других исключений
            logger.error(f"Ошибка в summarize_with_llm: {e}")
            return self.current_responses.get("generic_exception", "Произошла внутренняя ошибка.")
