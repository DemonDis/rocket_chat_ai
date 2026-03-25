---
name: rocket-chat-dev
description: Разработка Rocket.Chat AI Бота - отладка, тестирование, добавление фич
---

## Разработка

### Запуск в режиме разработки
```bash
python main.py
```

### Тест подключения к Rocket.Chat
```bash
python src/test_connection.py
```

### Структура проекта
- `src/chatbot.py` - Подключение к Rocket.Chat, отправка/получение сообщений
- `src/llm_service.py` - Интеграция с OpenAI API, промпты для LLM
- `src/message_handler.py` - Обработка сообщений, выполнение команд
- `src/config.py` - Переменные окружения
- `src/prompts/` - Промпты для AI персон (Rick&Morty, Carlin, Tarantino, Professional)
- `main.py` - Точка входа с циклом опроса сообщений

### Добавление новой персоны
1. Создай новый файл в `src/prompts/` типа `new_persona_prompt.py`
2. Верни dict с `name`, `description`, `system_prompt`
3. Импортируй в `message_handler.py`

### Добавление новой команды
Редактируй `src/message_handler.py` - найди метод `process_direct_message` и добавь обработчик команды

### Основные файлы для修改
- `src/config.py` - Добавление новых env переменных
- `src/llm_service.py` - Изменение поведения LLM
- `src/message_handler.py` - Логика обработки сообщений
