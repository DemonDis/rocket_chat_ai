import json
import time
import requests
import logging
import pickle
import os
from rocketchat_API.rocketchat import RocketChat
from config import *

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DebugSummaryBot:
    def __init__(self):
        try:
            logger.info("Инициализация бота...")
            
            self.rocket = RocketChat(
                user=ROCKETCHAT_USER,
                password=ROCKETCHAT_PASSWORD,
                server_url=ROCKETCHAT_URL,
                timeout=30
            )
            
            self.base_url = ROCKETCHAT_URL
            self.processed_messages_file = 'processed_messages.pkl'
            self.processed_messages = self.load_processed_messages()
            self.bot_username = None
            
            self.test_connection()
            logger.info("Бот успешно инициализирован")
            logger.info(f"Загружено {len(self.processed_messages)} обработанных сообщений из файла")
            
        except Exception as e:
            logger.error(f"Ошибка инициализации: {e}")
            raise

    def load_processed_messages(self):
        """Загрузить обработанные сообщения из файла"""
        try:
            if os.path.exists(self.processed_messages_file):
                with open(self.processed_messages_file, 'rb') as f:
                    return pickle.load(f)
            return set()
        except Exception as e:
            logger.error(f"Ошибка загрузки обработанных сообщений: {e}")
            return set()

    def save_processed_messages(self):
        """Сохранить обработанные сообщения в файл"""
        try:
            with open(self.processed_messages_file, 'wb') as f:
                pickle.dump(self.processed_messages, f)
            logger.debug("Сохранены обработанные сообщения")
        except Exception as e:
            logger.error(f"Ошибка сохранения обработанных сообщений: {e}")

    def test_connection(self):
        """Проверка подключения к Rocket.Chat"""
        me = self.rocket.me().json()
        if me.get('success'):
            self.bot_username = me.get('username', 'Unknown')
            logger.info(f"Подключение установлено как: {self.bot_username}")
        else:
            raise Exception(f"Ошибка аутентификации: {me}")

    def send_message(self, room_id, text):
        """Отправить сообщение в комнату"""
        try:
            logger.debug(f"Отправка сообщения в room_id: {room_id}")
            
            response = self.rocket.chat_post_message(text, room_id=room_id)
            response_data = response.json()
            
            if response_data.get('success', False):
                message_id = response_data.get('message', {}).get('_id')
                if message_id:
                    self.processed_messages.add(message_id)
                logger.info("Сообщение успешно отправлено")
                return True
            else:
                logger.error(f"Ошибка отправки: {response_data}")
                return False
                
        except Exception as e:
            logger.error(f"Исключение при отправке: {e}")
            return False

    def send_direct_message(self, username, text):
        """Отправить личное сообщение пользователю"""
        try:
            logger.info(f"Отправка ЛС пользователю: {username}")
            
            # Создаем или получаем личную комнату
            response = self.rocket.im_create(username)
            response_data = response.json()
            
            if response_data.get('success'):
                room_id = response_data.get('room', {}).get('_id')
                if room_id:
                    return self.send_message(room_id, text)
                else:
                    logger.error("Не найден room_id в ответе")
            else:
                logger.error(f"Ошибка создания личной комнаты: {response_data}")
            
            return False
            
        except Exception as e:
            logger.error(f"Исключение при отправке ЛС: {e}")
            return False

    def get_all_rooms(self):
        """Получить список всех доступных комнат"""
        try:
            logger.debug("Получение списка комнат...")
            rooms = []
            
            # Публичные каналы
            channels_response = self.rocket.channels_list()
            channels_data = channels_response.json()
            
            if channels_data.get('success'):
                rooms.extend(channels_data.get('channels', []))
            
            # Приватные группы
            groups_response = self.rocket.groups_list()
            groups_data = groups_response.json()
            
            if groups_data.get('success'):
                rooms.extend(groups_data.get('groups', []))
            
            logger.info(f"Найдено комнат: {len(rooms)}")
            return rooms
            
        except Exception as e:
            logger.error(f"Ошибка получения комнат: {e}")
            return []

    def get_room_by_name(self, room_name):
        """Найти комнату по имени"""
        rooms = self.get_all_rooms()
        for room in rooms:
            if room.get('name', '').lower() == room_name.lower():
                logger.info(f"Найдена комната: {room.get('name')}")
                return room
        logger.warning(f"Комната '{room_name}' не найдена")
        return None

    def get_room_messages_for_summary(self, room_id, limit=50):
        """Получить сообщения для суммаризации"""
        try:
            logger.debug(f"Получение сообщений из комнаты {room_id}")
            response = self.rocket.channels_history(room_id, count=limit)
            response_data = response.json()
            
            if response_data.get('success'):
                messages = response_data.get('messages', [])
                # Исключаем сообщения бота и системные сообщения
                text_messages = [
                    msg for msg in messages 
                    if (msg.get('msg') and 
                        not msg.get('t') and 
                        msg.get('username') != self.bot_username)
                ]
                logger.info(f"Получено сообщений для анализа: {len(text_messages)}")
                return text_messages
            else:
                logger.error(f"Ошибка получения сообщений: {response_data}")
            return []
        except Exception as e:
            logger.error(f"Исключение при получении сообщений: {e}")
            return []


    def summarize_with_llm(self, messages_text):
        """Рик Санчез читает ваш чат и рассказывает, что вы там накосячили"""
        try:
            logger.info("Рик врубил портал и залетел в ваш чатик...")

            if not messages_text:
                return "*отрыжка* Пусто тут, Морти. Даже хуже, чем твой мозг."

            participants = set()
            lines = []

            for msg in reversed(messages_text):
                username = msg.get('username') or msg.get('u', {}).get('username')
                if not username or username == self.bot_username:
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
                "temperature": 0.8   # Рик должен быть слегка пьян и креативен
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



    def get_direct_messages(self):
        """Получить личные сообщения к боту (только новые)"""
        try:
            logger.debug("Проверка личных сообщений...")
            im_list_response = self.rocket.im_list()
            im_list_data = im_list_response.json()
            
            if im_list_data.get('success'):
                direct_rooms = im_list_data.get('ims', [])
                
                all_messages = []
                for room in direct_rooms:
                    room_id = room.get('_id')
                    room_user = room.get('username')
                    
                    # Получаем информацию о пользователе для этой комнаты
                    if not room_user:
                        # Если username не указан, получаем информацию о комнате
                        room_info = self.rocket.rooms_info(room_id=room_id).json()
                        if room_info.get('success'):
                            room_data = room_info.get('room', {})
                            # Для личных сообщений ищем username другого участника
                            if room_data.get('t') == 'd':
                                usernames = room_data.get('usernames', [])
                                # Исключаем самого бота
                                room_user = next((u for u in usernames if u != self.bot_username), 'Unknown')
                    
                    # Получаем только последние 20 сообщений для проверки новых
                    messages_response = self.rocket.im_history(room_id, count=20)
                    messages_data = messages_response.json()
                    
                    if messages_data.get('success'):
                        messages = messages_data.get('messages', [])
                        
                        for msg in messages:
                            message_id = msg.get('_id')
                            # Игнорируем сообщения бота и уже обработанные сообщения
                            if (message_id not in self.processed_messages and 
                                msg.get('username') != self.bot_username):
                                msg['_room_id'] = room_id
                                msg['_room_user'] = room_user or msg.get('username', 'Unknown')
                                all_messages.append(msg)
                
                if all_messages:
                    logger.info(f"Обнаружено новых ЛС: {len(all_messages)}")
                return all_messages
                
            return []
            
        except Exception as e:
            logger.error(f"Ошибка получения ЛС: {e}")
            return []

    def process_direct_message(self, message):
        """Обработка личных сообщений"""
        try:
            text = message.get('msg', '').strip()
            username = message.get('_room_user', 'Unknown')
            message_id = message.get('_id')
            sender_username = message.get('username', 'Unknown')
            
            # Пропускаем сообщения от бота и уже обработанные
            if (sender_username == self.bot_username or 
                username == self.bot_username or 
                not username or 
                username == 'Unknown' or
                message_id in self.processed_messages):
                return
            
            if message_id:
                self.processed_messages.add(message_id)
            
            logger.info(f"ЛС от {username}: {text}")
            
            # Команда помощи
            if text.lower() in ['!help', '!помощь', 'help', 'помощь']:
                help_text = """🤖 **Бот суммаризации чатов**

**Доступные команды:**
• `help` - показать это сообщение
• `rooms` - список доступных комнат
• `summary <имя_комнаты>` - создать суммаризацию чата
• `summary <имя_комнаты> <количество_сообщений>` - суммаризация с указанием количества сообщений

**Примеры:**
• `summary general` - суммаризация комнаты general (30 сообщений)
• `summary random 50` - суммаризация 50 сообщений из комнаты random

*Примечание: суммаризация может занять некоторое время (до 2 минут)*"""
                
                if self.send_direct_message(username, help_text):
                    logger.info(f"Помощь отправлена пользователю {username}")
                else:
                    logger.error(f"Не удалось отправить помощь пользователю {username}")
            
            # Список комнат
            elif text.lower() == 'rooms':
                rooms = self.get_all_rooms()
                if not rooms:
                    self.send_direct_message(username, "❌ Не найдено доступных комнат")
                    return
                
                rooms_list = "\n".join([f"• #{room.get('name')}" for room in rooms[:15]])
                response_text = f"📋 **Доступные комнаты ({len(rooms)}):**\n\n{rooms_list}\n\nИспользуйте: `summary имя_комнаты`"
                self.send_direct_message(username, response_text)
            
            # Суммаризация
            elif text.lower().startswith('summary '):
                parts = text.split()
                if len(parts) < 2:
                    self.send_direct_message(username, "❌ Укажите название комнаты. Например: `summary general`")
                    return
                
                room_name = parts[1]
                limit = 30
                if len(parts) > 2 and parts[2].isdigit():
                    limit = min(int(parts[2]), 100)  # Максимум 100 сообщений
                
                self.send_direct_message(username, f"🔄 Создаю суммаризацию для комнаты '{room_name}' (анализирую последние {limit} сообщений)...\n*Это может занять до 2 минут*")
                
                room = self.get_room_by_name(room_name)
                if not room:
                    self.send_direct_message(username, f"❌ Комната '{room_name}' не найдена. Используйте `rooms` для списка доступных комнат.")
                    return
                
                messages = self.get_room_messages_for_summary(room['_id'], limit)
                
                if not messages:
                    self.send_direct_message(username, f"❌ В комнате '{room_name}' нет сообщений для анализа")
                    return
                
                # Отправляем уведомление о начале обработки
                self.send_direct_message(username, f"📊 Анализирую {len(messages)} сообщений...")
                
                summary = self.summarize_with_llm(messages)
                result = f"📊 **Краткое содержание: #{room_name}**\n\n{summary}\n\n---\n*На основе анализа {len(messages)} сообщений*"
                
                if self.send_direct_message(username, result):
                    logger.info(f"Суммаризация отправлена пользователю {username}")
                else:
                    logger.error(f"Не удалось отправить суммаризацию пользователю {username}")
            
            # Приветствие
            elif any(word in text.lower() for word in ['привет', 'hello', 'hi', 'start', 'начать']):
                welcome = f"Привет, {username}! 👋\n\nЯ бот для суммаризации чатов. Напишите `help` для списка команд."
                self.send_direct_message(username, welcome)
            else:
                # Ответ на неизвестные сообщения
                response = f"Не понимаю команду '{text}'. Напишите `help` для списка доступных команд."
                self.send_direct_message(username, response)
                
        except Exception as e:
            logger.error(f"Ошибка обработки ЛС: {e}")

    def clear_processed_messages(self):
        """Очистить историю обработанных сообщений (чтобы не рос бесконечно)"""
        if len(self.processed_messages) > 1000:
            # Оставляем только последние 500 сообщений
            self.processed_messages = set(list(self.processed_messages)[-500:])
            logger.info("Очищена история обработанных сообщений")

    def listen_for_messages(self):
        """Основной цикл прослушивания"""
        logger.info("Запуск прослушивания сообщений...")
        logger.info("Отправьте боту личное сообщение 'help' для теста")
        
        while True:
            try:
                # Проверяем личные сообщения
                direct_messages = self.get_direct_messages()
                for message in direct_messages:
                    self.process_direct_message(message)
                
                # Периодически очищаем историю и сохраняем в файл
                self.clear_processed_messages()
                self.save_processed_messages()
                
                time.sleep(3)
                
            except KeyboardInterrupt:
                logger.info("Остановка бота...")
                # Сохраняем состояние при выходе
                self.save_processed_messages()
                break
            except Exception as e:
                logger.error(f"Ошибка в основном цикле: {e}")
                time.sleep(5)

def main():
    try:
        bot = DebugSummaryBot()
        bot.listen_for_messages()
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")

if __name__ == "__main__":
    main()
