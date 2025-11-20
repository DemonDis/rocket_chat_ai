# Установка

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

## Запуск проекта

### Запуск MongoDB с помощью Docker
```bash
docker run -d --name db -p 27017:27017 -v mongo_data:/data/db mongo:5.0
```

### Запуск Rocket.Chat с помощью Docker
```bash
docker run -d --name rocketchat -p 80:3000 --link db --env ROOT_URL=http://localhost --env MONGO_URL=mongodb://db:27017/rocketchat --env MONGO_OPLOG_URL=mongodb://db:27017/local rocket.chat


curl -X GET http://localhost/api/v1/im.list ^  -H "X-User-Id: <ROCKETCHAT_USER_ID>" ^  -H "X-Auth-Token: <ROCKETCHAT_AUTH_TOKEN>"