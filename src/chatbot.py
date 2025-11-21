import logging
import pickle # Импорт модуля для сериализации и десериализации объектов Python (сохранение/загрузка состояния)
import os
from rocketchat_API.rocketchat import RocketChat
from src.config import *

# Настройка логирования для данного модуля
logger = logging.getLogger(__name__)

# Класс для взаимодействия с Rocket.Chat в качестве бота
class RocketChatBot:
    def __init__(self):
        """
        Конструктор класса RocketChatBot.
        Инициализирует подключение к Rocket.Chat и загружает историю обработанных сообщений.
        """
        try:
            logger.info("Инициализация бота Rocket.Chat...")
            
            # Инициализация объекта RocketChat с учетными данными из конфига
            self.rocket = RocketChat(
                user=ROCKETCHAT_USER, # Имя пользователя бота
                password=ROCKETCHAT_PASSWORD, # Пароль пользователя бота
                server_url=ROCKETCHAT_URL, # URL-адрес сервера Rocket.Chat
                timeout=30 # Таймаут для запросов
            )
            
            self.base_url = ROCKETCHAT_URL # Базовый URL сервера Rocket.Chat
            self.processed_messages_file = 'src/data/processed_messages.pkl' # Путь к файлу для хранения ID обработанных сообщений
            self.processed_messages = self.load_processed_messages() # Загрузка ранее обработанных сообщений
            self.bot_username = None # Имя пользователя бота, будет установлено после успешного подключения
            
            self.test_connection() # Проверка подключения к Rocket.Chat
            logger.info("Бот Rocket.Chat успешно инициализирован")
            logger.info(f"Загружено {len(self.processed_messages)} обработанных сообщений из файла")
            
        except Exception as e:
            logger.error(f"Ошибка инициализации Rocket.Chat бота: {e}")
            raise # Перевыброс исключения при ошибке инициализации

    def load_processed_messages(self):
        """
        Загружает ID обработанных сообщений из файла.
        Возвращает множество (set) с ID сообщений.
        """
        try:
            if os.path.exists(self.processed_messages_file): # Проверяем, существует ли файл
                with open(self.processed_messages_file, 'rb') as f: # Открываем файл в бинарном режиме для чтения
                    return pickle.load(f) # Десериализуем и возвращаем данные
            return set() # Если файл не существует, возвращаем пустое множество
        except Exception as e:
            logger.error(f"Ошибка загрузки обработанных сообщений: {e}")
            return set() # В случае ошибки возвращаем пустое множество

    def save_processed_messages(self):
        """
        Сохраняет ID обработанных сообщений в файл.
        """
        try:
            with open(self.processed_messages_file, 'wb') as f: # Открываем файл в бинарном режиме для записи
                pickle.dump(self.processed_messages, f) # Сериализуем и сохраняем данные
            logger.debug("Сохранены обработанные сообщения")
        except Exception as e:
            logger.error(f"Ошибка сохранения обработанных сообщений: {e}")

    def test_connection(self):
        """
        Проверяет подключение к Rocket.Chat и получает информацию о боте.
        Устанавливает self.bot_username.
        Вызывает исключение при ошибке аутентификации.
        """
        me = self.rocket.me().json() # Получаем информацию о текущем пользователе (боте)
        if me.get('success'): # Если запрос успешен
            self.bot_username = me.get('username', 'Unknown') # Получаем имя пользователя бота
            logger.info(f"Подключение установлено как: {self.bot_username}")
        else:
            raise Exception(f"Ошибка аутентификации: {me}") # Выбрасываем исключение при неудачной аутентификации

    def send_message(self, room_id, text):
        """
        Отправляет текстовое сообщение в указанную комнату.
        
        :param room_id: ID комнаты, куда нужно отправить сообщение.
        :param text: Текст сообщения.
        :return: True, если сообщение отправлено успешно, иначе False.
        """
        try:
            logger.debug(f"Отправка сообщения в room_id: {room_id}")
            
            response = self.rocket.chat_post_message(text, room_id=room_id) # Отправляем сообщение
            response_data = response.json() # Парсим ответ сервера
            
            if response_data.get('success', False): # Если сообщение успешно отправлено
                message_id = response_data.get('message', {}).get('_id') # Получаем ID отправленного сообщения
                if message_id:
                    self.processed_messages.add(message_id) # Добавляем ID в список обработанных сообщений
                logger.info("Сообщение успешно отправлено")
                return True
            else:
                logger.error(f"Ошибка отправки: {response_data}") # Логируем ошибку
                return False
                
        except Exception as e:
            logger.error(f"Исключение при отправке: {e}")
            return False

    def send_direct_message(self, username, text):
        """
        Отправляет личное сообщение указанному пользователю.
        
        :param username: Имя пользователя, которому нужно отправить ЛС.
        :param text: Текст сообщения.
        :return: True, если ЛС отправлено успешно, иначе False.
        """
        try:
            logger.info(f"Отправка ЛС пользователю: {username}")
            
            response = self.rocket.im_create(username) # Создаем или получаем личную беседу с пользователем
            response_data = response.json() # Парсим ответ сервера
            
            if response_data.get('success'):
                room_id = response_data.get('room', {}).get('_id') # Получаем ID комнаты личной беседы
                if room_id:
                    return self.send_message(room_id, text) # Отправляем сообщение в эту комнату
                else:
                    logger.error("Не найден room_id в ответе")
            else:
                logger.error(f"Ошибка создания личной комнаты: {response_data}")
            
            return False
            
        except Exception as e:
            logger.error(f"Исключение при отправке ЛС: {e}")
            return False

    def get_all_rooms(self):
        """
        Получает список всех доступных комнат (каналов и групп).
        
        :return: Список словарей, представляющих комнаты.
        """
        try:
            logger.debug("Получение списка комнат...")
            rooms = []
            
            channels_response = self.rocket.channels_list() # Получаем список публичных каналов
            channels_data = channels_response.json()
            
            if channels_data.get('success'):
                rooms.extend(channels_data.get('channels', [])) # Добавляем каналы в общий список
            
            groups_response = self.rocket.groups_list() # Получаем список приватных групп
            groups_data = groups_response.json()
            
            if groups_data.get('success'):
                rooms.extend(groups_data.get('groups', [])) # Добавляем группы в общий список
            
            logger.info(f"Найдено комнат: {len(rooms)}")
            return rooms
            
        except Exception as e:
            logger.error(f"Ошибка получения комнат: {e}")
            return []

    def get_room_by_name(self, room_name):
        """
        Находит комнату по её имени.
        
        :param room_name: Имя комнаты для поиска.
        :return: Словарь, представляющий комнату, если найдена, иначе None.
        """
        rooms = self.get_all_rooms() # Получаем все комнаты
        for room in rooms:
            if room.get('name', '').lower() == room_name.lower(): # Сравниваем имена без учета регистра
                logger.info(f"Найдена комната: {room.get('name')}")
                return room
        logger.warning(f"Комната '{room_name}' не найдена")
        return None

    def get_room_messages_for_summary(self, room_id, limit=50):
        """
        Получает сообщения из указанной комнаты для дальнейшего суммаризации.
        Исключает сообщения, отправленные самим ботом, и системные сообщения.
        
        :param room_id: ID комнаты.
        :param limit: Максимальное количество сообщений для получения.
        :return: Список текстовых сообщений.
        """
        try:
            logger.debug(f"Получение сообщений из комнаты {room_id}")
            response = self.rocket.channels_history(room_id, count=limit) # Получаем историю сообщений канала
            response_data = response.json()
            
            if response_data.get('success'):
                messages = response_data.get('messages', [])
                text_messages = [
                    msg for msg in messages 
                    if (msg.get('msg') and # Проверяем наличие текста сообщения
                        not msg.get('t') and # Исключаем системные сообщения (t - type)
                        msg.get('username') != self.bot_username) # Исключаем сообщения от самого бота
                ]
                logger.info(f"Получено сообщений для анализа: {len(text_messages)}")
                return text_messages
            else:
                logger.error(f"Ошибка получения сообщений: {response_data}")
            return []
        except Exception as e:
            logger.error(f"Исключение при получении сообщений: {e}")
            return []
            
    def get_direct_messages(self):
        """
        Получает новые личные сообщения, адресованные боту.
        Фильтрует уже обработанные сообщения.
        
        :return: Список новых личных сообщений.
        """
        try:
            logger.debug("Проверка личных сообщений...")
            im_list_response = self.rocket.im_list() # Получаем список личных бесед
            im_list_data = im_list_response.json()
            
            if im_list_data.get('success'):
                direct_rooms = im_list_data.get('ims', []) # Список личных комнат
                
                all_messages = []
                for room in direct_rooms:
                    room_id = room.get('_id')
                    room_user = room.get('username') # Имя пользователя в ЛС, если доступно
                    
                    # Если имя пользователя не найдено напрямую в IM_list, пытаемся получить его из информации о комнате
                    if not room_user:
                        room_info = self.rocket.rooms_info(room_id=room_id).json()
                        if room_info.get('success'):
                            room_data = room_info.get('room', {})
                            if room_data.get('t') == 'd': # Если это личная беседа (direct)
                                usernames = room_data.get('usernames', [])
                                # Находим имя пользователя, которое не является именем бота
                                room_user = next((u for u in usernames if u != self.bot_username), 'Unknown')
                    
                    messages_response = self.rocket.im_history(room_id, count=20) # Получаем историю сообщений из личной беседы
                    messages_data = messages_response.json()
                    
                    if messages_data.get('success'):
                        messages = messages_data.get('messages', [])
                        
                        for msg in messages:
                            message_id = msg.get('_id')
                            # Если сообщение не было обработано ранее и не отправлено самим ботом
                            if (message_id not in self.processed_messages and 
                                msg.get('username') != self.bot_username):
                                msg['_room_id'] = room_id # Добавляем ID комнаты к сообщению
                                msg['_room_user'] = room_user or msg.get('username', 'Unknown') # Добавляем имя пользователя к сообщению
                                all_messages.append(msg) # Добавляем сообщение в список
                
                if all_messages:
                    logger.info(f"Обнаружено новых ЛС: {len(all_messages)}")
                return all_messages
                
            return []
            
        except Exception as e:
            logger.error(f"Ошибка получения ЛС: {e}")
            return []

    def clear_processed_messages(self):
        """
        Очищает историю обработанных сообщений, оставляя только последние 500.
        Это предотвращает бесконечный рост размера списка processed_messages.
        """
        if len(self.processed_messages) > 1000: # Если количество обработанных сообщений превышает 1000
            self.processed_messages = set(list(self.processed_messages)[-500:]) # Оставляем только последние 500
            logger.info("Очищена история обработанных сообщений")
