import requests
import os
from dotenv import load_dotenv

load_dotenv()

def test_connection():
    base_url = os.getenv('ROCKETCHAT_URL', '')
    user_id = os.getenv('ROCKETCHAT_USER_ID')
    auth_token = os.getenv('ROCKETCHAT_AUTH_TOKEN')
    
    print("🔍 Тестирование подключения к Rocket.Chat")
    print("=" * 50)
    
    # 1. Проверка базового подключения
    print("1. Проверка доступности Rocket.Chat...")
    try:
        response = requests.get(f"{base_url}/api/info", timeout=10)
        if response.status_code == 200:
            info = response.json()
            print(f"✅ Rocket.Chat доступен")
            print(f"   Версия: {info.get('info', {}).get('version', 'Unknown')}")
        else:
            print(f"❌ Ошибка HTTP: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False
    
    # 2. Проверка аутентификации
    print("\n2. Проверка аутентификации...")
    headers = {
        'X-User-Id': user_id,
        'X-Auth-Token': auth_token,
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(f"{base_url}/api/v1/me", headers=headers, timeout=10)
        if response.status_code == 200:
            user_info = response.json()
            if user_info.get('success'):
                print(f"✅ Аутентификация успешна")
                print(f"   Пользователь: {user_info['username']}")
                print(f"   Email: {user_info.get('emails', [{}])[0].get('address', 'N/A')}")
            else:
                print(f"❌ Ошибка аутентификации: {user_info}")
                return False
        else:
            print(f"❌ Ошибка HTTP при аутентификации: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка при аутентификации: {e}")
        return False
    
    # 3. Проверка получения списка комнат
    print("\n3. Проверка получения списка комнат...")
    try:
        response = requests.get(f"{base_url}/api/v1/channels.list", headers=headers, timeout=10)
        if response.status_code == 200:
            channels = response.json()
            if channels.get('success'):
                print(f"✅ Получено комнат: {len(channels.get('channels', []))}")
                for channel in channels.get('channels', [])[:3]:  # Показать первые 3
                    print(f"   - {channel['name']}")
            else:
                print(f"❌ Ошибка при получении комнат: {channels}")
        else:
            print(f"❌ Ошибка HTTP при получении комнат: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка при получении комнат: {e}")
    
    return True

if __name__ == "__main__":
    test_connection()