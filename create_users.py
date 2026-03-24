import requests
import json
import logging
from src.config import (
    ROCKETCHAT_URL,
    ROCKETCHAT_USER,
    ROCKETCHAT_PASSWORD,
    ROCKETCHAT_USER_ID,
    ROCKETCHAT_AUTH_TOKEN,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class RocketChatUserManager:
    def __init__(self):
        self.url = ROCKETCHAT_URL.rstrip("/")
        self.headers = {
            "X-User-Id": ROCKETCHAT_USER_ID,
            "X-Auth-Token": ROCKETCHAT_AUTH_TOKEN,
            "Content-Type": "application/json",
        }
        self._login()

    def _login(self):
        resp = requests.post(
            f"{self.url}/api/v1/login",
            json={"user": ROCKETCHAT_USER, "password": ROCKETCHAT_PASSWORD},
        )
        data = resp.json()
        if data.get("status") == "success":
            self.headers["X-User-Id"] = data["data"]["userId"]
            self.headers["X-Auth-Token"] = data["data"]["authToken"]
            logger.info("Авторизация успешна")
        else:
            raise Exception(f"Ошибка авторизации: {data}")

    def user_exists(self, username=None, email=None):
        if username:
            resp = requests.get(
                f"{self.url}/api/v1/users.info",
                headers=self.headers,
                params={"username": username},
            )
            if resp.json().get("user"):
                return True

        if email:
            resp = requests.post(
                f"{self.url}/api/v1/users.list",
                headers=self.headers,
                json={"query": json.dumps({"emails.address": email})},
            )
            if resp.json().get("count", 0) > 0:
                return True

        return False

    def create_user(self, username, email, name, password, roles=None):
        data = {
            "username": username,
            "email": email,
            "name": name,
            "password": password,
            "joinDefaultChannels": False,
        }
        if roles:
            data["roles"] = roles

        resp = requests.post(
            f"{self.url}/api/v1/users.create", headers=self.headers, json=data
        )
        return resp.json()

    def create_users_from_file(self, filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            users = json.load(f)

        results = {"created": [], "skipped": [], "failed": []}

        for user in users:
            username = user.get("username")
            email = user.get("email")
            name = user.get("name", username)
            password = user.get("password", "ChangeMe123!")
            roles = user.get("roles")

            if self.user_exists(username=username, email=email):
                logger.info(f"Пропущен (уже существует): {username} ({email})")
                results["skipped"].append({"username": username, "email": email})
                continue

            try:
                result = self.create_user(username, email, name, password, roles)
                if result.get("user"):
                    logger.info(f"Создан: {username}")
                    results["created"].append({"username": username, "email": email})
                else:
                    logger.error(f"Ошибка создания {username}: {result}")
                    results["failed"].append(
                        {"username": username, "error": result.get("error")}
                    )
            except Exception as e:
                logger.error(f"Ошибка: {username} - {e}")
                results["failed"].append({"username": username, "error": str(e)})

        return results


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Использование: python create_users.py <файл_с_пользователями.json>")
        print("Пример JSON файла:")
        print(
            json.dumps(
                [
                    {
                        "username": "user1",
                        "email": "user1@test.com",
                        "name": "User One",
                        "password": "Pass123",
                    },
                    {
                        "username": "user2",
                        "email": "user2@test.com",
                        "name": "User Two",
                        "roles": ["bot"],
                    },
                ],
                indent=2,
            )
        )
        sys.exit(1)

    manager = RocketChatUserManager()
    results = manager.create_users_from_file(sys.argv[1])

    print("\n=== Результаты ===")
    print(f"Создано: {len(results['created'])}")
    print(f"Пропущено: {len(results['skipped'])}")
    print(f"Ошибки: {len(results['failed'])}")
