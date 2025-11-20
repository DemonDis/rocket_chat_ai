import logging

logger = logging.getLogger(__name__)

class MessageHandler:
    def __init__(self, chatbot, llm_service):
        self.chatbot = chatbot
        self.llm_service = llm_service
        self.current_prompt = self.llm_service.current_prompt_name # Store the current prompt for each user
        logger.info("Инициализация обработчика сообщений...")

    def process_direct_message(self, message):
        """Обработка личных сообщений"""
        try:
            text = message.get('msg', '').strip()
            username = message.get('_room_user', 'Unknown')
            message_id = message.get('_id')
            sender_username = message.get('username', 'Unknown')
            
            if (sender_username == self.chatbot.bot_username or 
                username == self.chatbot.bot_username or 
                not username or 
                username == 'Unknown' or
                message_id in self.chatbot.processed_messages):
                return
            
            if message_id:
                self.chatbot.processed_messages.add(message_id)
            
            logger.info(f"ЛС от {username}: {text}")
            
            if text.lower() in ['!help', '!помощь', 'help', 'помощь']:
                help_text = f"""🤖 **Бот суммаризации чатов**

**Доступные команды:**
• `help` - показать это сообщение
• `rooms` - список доступных комнат
• `summary <имя_комнаты>` - создать суммаризацию чата
• `summary <имя_комнаты> <количество_сообщений>` - суммаризация с указанием количества сообщений
• `prompt <имя_промпта>` - установить активный промпт (текущий: `{self.current_prompt}`)
• `list_prompts` - показать список доступных промптов

**Примеры:**
• `summary general` - суммаризация комнаты general (30 сообщений)
• `summary random 50` - суммаризация 50 сообщений из комнаты random
• `prompt rick_and_morty` - установить промпт "Рик и Морти"

*Примечание: суммаризация может занять некоторое время (до 2 минут)*"""
                
                if self.chatbot.send_direct_message(username, help_text):
                    logger.info(f"Помощь отправлена пользователю {username}")
                else:
                    logger.error(f"Не удалось отправить помощь пользователю {username}")
            
            elif text.lower() == 'rooms':
                rooms = self.chatbot.get_all_rooms()
                if not rooms:
                    self.chatbot.send_direct_message(username, "❌ Не найдено доступных комнат")
                    return
                
                rooms_list = "\n".join([f"• #{room.get('name')}" for room in rooms[:15]])
                response_text = f"📋 **Доступные комнаты ({len(rooms)}):**\n\n{rooms_list}\n\nИспользуйте: `summary имя_комнаты`"
                self.chatbot.send_direct_message(username, response_text)

            elif text.lower().startswith('prompt '):
                parts = text.split()
                if len(parts) < 2:
                    self.chatbot.send_direct_message(username, "❌ Укажите имя промпта. Например: `prompt rick_and_morty`")
                    return
                
                new_prompt_name = parts[1]
                if new_prompt_name in self.llm_service.prompts:
                    self.current_prompt = new_prompt_name
                    self.llm_service.set_prompt(new_prompt_name) # Set it globally for now, until per-user prompt is implemented
                    self.chatbot.send_direct_message(username, f"✅ Промпт успешно изменен на: `{new_prompt_name}`")
                    logger.info(f"Промпт изменен на {new_prompt_name} для пользователя {username}")
                else:
                    self.chatbot.send_direct_message(username, f"❌ Промпт `{new_prompt_name}` не найден. Доступные промпты: `{', '.join(self.llm_service.prompts.keys())}`")

            elif text.lower() == 'list_prompts':
                available_prompts = ", ".join(self.llm_service.prompts.keys())
                self.chatbot.send_direct_message(username, f"📋 **Доступные промпты:** `{available_prompts}`")
            
            elif text.lower().startswith('summary '):
                parts = text.split()
                if len(parts) < 2:
                    self.chatbot.send_direct_message(username, "❌ Укажите название комнаты. Например: `summary general`")
                    return
                
                room_name = parts[1]
                limit = 30
                if len(parts) > 2 and parts[2].isdigit():
                    limit = min(int(parts[2]), 100)
                
                self.chatbot.send_direct_message(username, f"🔄 Создаю суммаризацию для комнаты '{room_name}' (анализирую последние {limit} сообщений)...\n*Это может занять до 2 минут*")
                
                room = self.chatbot.get_room_by_name(room_name)
                if not room:
                    self.chatbot.send_direct_message(username, f"❌ Комната '{room_name}' не найдена. Используйте `rooms` для списка доступных комнат.")
                    return
                
                messages = self.chatbot.get_room_messages_for_summary(room['_id'], limit)
                
                if not messages:
                    self.chatbot.send_direct_message(username, f"❌ В комнате '{room_name}' нет сообщений для анализа")
                    return
                
                self.chatbot.send_direct_message(username, f"📊 Анализирую {len(messages)} сообщений...")
                
                summary = self.llm_service.summarize_with_llm(messages, self.chatbot.bot_username, prompt_name=self.current_prompt)
                result = f"📊 **Краткое содержание: #{room_name}**\n\n{summary}\n\n---\n*На основе анализа {len(messages)} сообщений*"
                
                if self.chatbot.send_direct_message(username, result):
                    logger.info(f"Суммаризация отправлена пользователю {username}")
                else:
                    logger.error(f"Не удалось отправить суммаризацию пользователю {username}")
            
            elif any(word in text.lower() for word in ['привет', 'hello', 'hi', 'start', 'начать']):
                welcome = f"Привет, {username}! 👋\n\nЯ бот для суммаризации чатов. Напишите `help` для списка команд."
                self.chatbot.send_direct_message(username, welcome)
            else:
                response = f"Не понимаю команду '{text}'. Напишите `help` для списка доступных команд."
                self.chatbot.send_direct_message(username, response)
                
        except Exception as e:
            logger.error(f"Ошибка обработки ЛС: {e}")
