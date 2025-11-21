import time
import logging
from src.chatbot import RocketChatBot
from src.llm_service import LLMService
from src.message_handler import MessageHandler
from src.config import *

# Настройка логирования
logging.basicConfig(
    level=logging.INFO, # Уровень логирования: INFO и выше
    format='%(asctime)s - %(levelname)s - %(message)s', # Формат сообщений в логе
    handlers=[
        logging.FileHandler('src/logs/bot.log', encoding='utf-8'), # Запись логов в файл
        logging.StreamHandler() # Вывод логов в консоль
    ]
)
logger = logging.getLogger(__name__) # Получение логгера для текущего модуля

def main():
    """
    Главная функция для запуска бота Rocket.Chat.
    Инициализирует бота, сервис LLM и обработчик сообщений,
    затем входит в бесконечный цикл для обработки личных сообщений.
    """
    try:
        logger.info("Запуск бота...")
        
        chatbot = RocketChatBot() # Создание экземпляра бота Rocket.Chat
        llm_service = LLMService() # Создание экземпляра сервиса LLM
        message_handler = MessageHandler(chatbot, llm_service) # Создание экземпляра обработчика сообщений

        logger.info("Запуск прослушивания сообщений...")
        logger.info("Отправьте боту личное сообщение 'help' для теста")
        
        while True: # Бесконечный цикл для постоянной работы бота
            try:
                direct_messages = chatbot.get_direct_messages() # Получение новых личных сообщений
                for message in direct_messages:
                    message_handler.process_direct_message(message) # Обработка каждого личного сообщения
                
                chatbot.clear_processed_messages() # Очистка списка обработанных сообщений (чтобы не рос бесконечно)
                chatbot.save_processed_messages() # Сохранение списка обработанных сообщений в файл
                
                time.sleep(3) # Задержка перед следующей проверкой сообщений
                
            except KeyboardInterrupt: # Обработка прерывания программы (например, Ctrl+C)
                logger.info("Остановка бота...")
                chatbot.save_processed_messages() # Сохранение обработанных сообщений перед выходом
                break # Выход из бесконечного цикла
            except Exception as e: # Обработка любых других ошибок в основном цикле
                logger.error(f"Ошибка в основном цикле: {e}")
                time.sleep(5) # Пауза перед повторной попыткой
                
    except Exception as e: # Обработка критических ошибок при запуске бота
        logger.error(f"Критическая ошибка при запуске: {e}")

if __name__ == "__main__":
    main() # Запуск главной функции при выполнении скрипта напрямую
