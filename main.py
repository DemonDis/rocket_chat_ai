import time
import logging
from src.chatbot import RocketChatBot
from src.llm_service import LLMService
from src.message_handler import MessageHandler
from src.config import * # Add this import statement

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('src/logs/bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    try:
        logger.info("Запуск бота...")
        
        chatbot = RocketChatBot()
        # По умолчанию используется промпт Рика и Морти.
        # Для использования промпта Джорджа Карлина, измените на:
        # llm_service = LLMService(default_prompt='george_carlin')
        llm_service = LLMService()
        message_handler = MessageHandler(chatbot, llm_service)

        logger.info("Запуск прослушивания сообщений...")
        logger.info("Отправьте боту личное сообщение 'help' для теста")
        
        while True:
            try:
                direct_messages = chatbot.get_direct_messages()
                for message in direct_messages:
                    message_handler.process_direct_message(message)
                
                chatbot.clear_processed_messages()
                chatbot.save_processed_messages()
                
                time.sleep(3)
                
            except KeyboardInterrupt:
                logger.info("Остановка бота...")
                chatbot.save_processed_messages()
                break
            except Exception as e:
                logger.error(f"Ошибка в основном цикле: {e}")
                time.sleep(5)
                
    except Exception as e:
        logger.error(f"Критическая ошибка при запуске: {e}")

if __name__ == "__main__":
    main()
