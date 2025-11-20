import json
import time
import requests
import logging
import pickle
import os
from rocketchat_API.rocketchat import RocketChat
from src.config import *

logger = logging.getLogger(__name__)

class RocketChatBot:
    def __init__(self):
        try:
            logger.info("Инициализация бота Rocket.Chat...")
            
            self.rocket = RocketChat(
                user=ROCKETCHAT_USER,
                password=ROCKETCHAT_PASSWORD,
                server_url=ROCKETCHAT_URL,
                timeout=30
            )
            
            self.base_url = ROCKETCHAT_URL
            self.processed_messages_file = 'data/processed_messages.pkl'
            self.processed_messages = self.load_processed_messages()
            self.bot_username = None
            
            self.test_connection()
            logger.info("Бот Rocket.Chat успешно инициализирован")
            logger.info(f"Загружено {len(self.processed_messages)} обработанных сообщений из файла")
            
        except Exception as e:
            logger.error(f"Ошибка инициализации Rocket.Chat бота: {e}")
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
            
            channels_response = self.rocket.channels_list()
            channels_data = channels_response.json()
            
            if channels_data.get('success'):
                rooms.extend(channels_data.get('channels', []))
            
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
                    
                    if not room_user:
                        room_info = self.rocket.rooms_info(room_id=room_id).json()
                        if room_info.get('success'):
                            room_data = room_info.get('room', {})
                            if room_data.get('t') == 'd':
                                usernames = room_data.get('usernames', [])
                                room_user = next((u for u in usernames if u != self.bot_username), 'Unknown')
                    
                    messages_response = self.rocket.im_history(room_id, count=20)
                    messages_data = messages_response.json()
                    
                    if messages_data.get('success'):
                        messages = messages_data.get('messages', [])
                        
                        for msg in messages:
                            message_id = msg.get('_id')
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

    def clear_processed_messages(self):
        """Очистить историю обработанных сообщений (чтобы не рос бесконечно)"""
        if len(self.processed_messages) > 1000:
            self.processed_messages = set(list(self.processed_messages)[-500:])
            logger.info("Очищена история обработанных сообщений")
