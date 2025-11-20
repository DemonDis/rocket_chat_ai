# Rocket.Chat AI Бот

Этот проект представляет собой реализацию AI-бота для Rocket.Chat, предназначенного для автоматизации взаимодействий и предоставления интеллектуальных ответов на платформе Rocket.Chat. Бот использует различные библиотеки Python для своей функциональности.

## Версии Программного Обеспечения

В проекте используются следующие программы и их версии:

*   **Python**: 3.9+
*   **pip**: 23.x (или последняя)
*   **Docker**: 24.x (или последняя)

## Установка

1.  **Клонируйте репозиторий (если вы еще этого не сделали):**
    ```bash
    git clone https://github.com/DemonDis/rocket_chat_ai.git
    cd rocket_chat_ai
    ```

2.  **Создайте виртуальное окружение (рекомендуется):**
    ```bash
    python -m venv venv
    ```

3.  **Активируйте виртуальное окружение:**
    ```bash
    .\venv\Scripts\activate
    ```

4.  **Установите необходимые пакеты:**
    ```bash
    pip install -r requirements.txt
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
│       └── rick_and_morty_prompt.py # Промпт в стиле Рика и Морти (используется по умолчанию).
├── data/                    # Каталог для хранения персистентных данных, например, processed_messages.pkl.
├── logs/                    # Каталог для хранения логов, например, bot.log.
├── main.py                  # Главный исполняемый файл бота.
├── README.md
├── requirements.txt
└── ... (другие файлы проекта)
```

## Запуск проекта

### Запуск MongoDB с помощью Docker
```bash
docker run -d --name db -p 27017:27017 -v mongo_data:/data/db mongo:5.0
```

### Запуск Rocket.Chat с помощью Docker
```bash
docker run -d --name rocketchat -p 80:3000 --link db --env ROOT_URL=http://localhost --env MONGO_URL=mongodb://db:27017/rocketchat --env MONGO_OPLOG_URL=mongodb://db:27017/local rocket.chat
```

### Проверка с помощью CURL
```bash
curl -X GET http://localhost/api/v1/im.list ^  -H "X-User-Id: <ROCKETCHAT_USER_ID>" ^  -H "X-Auth-Token: <ROCKETCHAT_AUTH_TOKEN>"
```
