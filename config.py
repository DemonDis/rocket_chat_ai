import os
from dotenv import load_dotenv

load_dotenv()

# Rocket.Chat конфигурация
ROCKETCHAT_URL = os.getenv('ROCKETCHAT_URL', 'http://192.168.91.162:80')
ROCKETCHAT_USER = os.getenv('ROCKETCHAT_USER')
ROCKETCHAT_PASSWORD = os.getenv('ROCKETCHAT_PASSWORD')
ROCKETCHAT_USER_ID = os.getenv('ROCKETCHAT_USER_ID')
ROCKETCHAT_AUTH_TOKEN = os.getenv('ROCKETCHAT_AUTH_TOKEN')

# LLM конфигурация
OPEN_AI_API_KEY = os.getenv('OPEN_AI_API_KEY')
OPEN_AI_BASE_URL = os.getenv('OPEN_AI_BASE_URL')
OPEN_AI_COMPLETIONS_PATHNAME = os.getenv('OPEN_AI_COMPLETIONS_PATHNAME')
LLM_NAME = os.getenv('LLM_NAME')

# Проверка обязательных переменных
def check_config():
    required = [
        'ROCKETCHAT_URL', 'ROCKETCHAT_USER', 'ROCKETCHAT_PASSWORD',
        'OPEN_AI_API_KEY', 'OPEN_AI_BASE_URL', 'LLM_NAME'
    ]
    
    missing = [var for var in required if not globals().get(var)]
    if missing:
        print(f"❌ Отсутствуют обязательные переменные: {missing}")
        return False
    return True

if __name__ == "__main__":
    check_config()