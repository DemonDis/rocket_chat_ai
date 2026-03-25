---
name: rocket-chat-deploy
description: Деплой и эксплуатация Rocket.Chat AI Бота
---

## Docker Деплой

### Сборка и запуск
```bash
docker compose up --build
```

### Запуск в фоне
```bash
docker compose up --build -d
```

### Остановка контейнеров
```bash
docker compose down
```

### Просмотр логов
```bash
docker compose logs -f
```

## Конфигурация (.env)

Обязательные переменные:
- `ROCKETCHAT_URL` - URL сервера Rocket.Chat
- `ROCKETCHAT_USER` - Имя пользователя бота
- `ROCKETCHAT_PASSWORD` - Пароль бота
- `ROCKETCHAT_USER_ID` - ID пользователя бота
- `ROCKETCHAT_AUTH_TOKEN` - Токен авторизации
- `OPEN_AI_API_KEY` - API ключ OpenAI
- `OPEN_AI_BASE_URL` - Базовый URL API
- `LLM_NAME` - Имя модели (напр. gpt-4)

Опционально:
- `MAX_TOKENS` - По умолчанию: 2200
- `TEMPERATURE` - По умолчанию: 0.8

## Проверка работоспособности
Отправь боту личное сообщение "help" для проверки
