# Rocket.Chat AI Бот

Этот проект представляет собой реализацию AI-бота для Rocket.Chat, предназначенного для автоматизации взаимодействий и предоставления интеллектуальных ответов на платформе Rocket.Chat. Бот использует различные библиотеки Python для своей функциональности.

## Версии Программного Обеспечения

В проекте используются следующие программы и их версии:

*   **Python**: 3.9+
*   **pip**: 23.x (или последняя)
*   **Docker**: 24.x (или последняя)

## Запуск проекта

- Для запуска приложения используйте следующую команду в корневой директории проекта: 
```bash
docker compose up --build
```

- Если вы хотите запустить его в фоновом режиме: 
```bash
docker compose up --build -d
```

-Для остановки контейнеров: 
```bash
docker compose down
```

## Структура Проекта
```
.
├── src/
│   ├── __init__.py
│   ├── chatbot.py           # Управление подключением к Rocket.Chat, отправкой/получением сообщений.
│   ├── config.py            # Конфигурационные переменные.
│   ├── llm_service.py       # Взаимодействие с Large Language Model для суммаризации.
│   ├── message_handler.py   # Обработка входящих сообщений и выполнение команд.
│   └── prompts/             # Каталог для хранения различных вариантов промптов.
│       ├── rick_and_morty_prompt.py # Промпт в стиле Рика и Морти.
│       └── george_carlin_prompt.py  # Промпт в стиле Джорджа Карлина.
├── data/                    # Каталог для хранения персистентных данных, например, processed_messages.pkl.
├── logs/                    # Каталог для хранения логов, например, bot.log.
├── main.py                  # Главный исполняемый файл бота.
├── README.md
├── requirements.txt
└── ... (другие файлы проекта)
```


## Запуск Бота
- Создайте .env в корне проекта
```
ROCKETCHAT_URL=http://host.docker.internal:80
ROCKETCHAT_USER=BOT
ROCKETCHAT_PASSWORD=
ROCKETCHAT_USER_ID=
ROCKETCHAT_AUTH_TOKEN=

OPEN_AI_API_KEY=
OPEN_AI_BASE_URL=
OPEN_AI_COMPLETIONS_PATHNAME=/v1/chat/completions
LLM_NAME=

MAX_TOKENS=2200
TEMPERATURE=0.8
```

1.  **Клонируйте репозиторий (если вы еще этого не сделали):**
```bash
git clone https://github.com/DemonDis/rocket_chat_ai.git
cd rocket_chat_ai
```

2.  **Создайте виртуальное окружение (рекомендуется):**
```bash
python -m venv .venv
```

3.  **Активируйте виртуальное окружение:**
```bash
. .\venv\Scripts\activate
# для Linux
source .venv/bin/activate 
```

4.  **Установите необходимые пакеты:**
```bash
pip install -r requirements.txt
```