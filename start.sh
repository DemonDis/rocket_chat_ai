#!/bin/bash
set -e

echo "=== 1. Остановка и удаление старых контейнеров ==="
docker compose down -v

echo ""
echo "=== 2. Запуск MongoDB ==="
docker compose up -d mongo

echo ""
echo "=== 3. Ожидание готовности MongoDB ==="
until docker exec rocketchat-mongo mongosh --quiet --eval "db.adminCommand({ping:1})" &>/dev/null; do
  echo "    Ждём MongoDB..."
  sleep 2
done
echo "    MongoDB готова"

echo ""
echo "=== 4. Инициализация replica set (с хостом 'mongo:27017'!) ==="
docker exec rocketchat-mongo mongosh --quiet --eval "
  rs.initiate({
    _id: 'rs0',
    members: [{ _id: 0, host: 'mongo:27017' }]
  })
"
sleep 3

echo ""
echo "=== 5. Проверка replica set ==="
docker exec rocketchat-mongo mongosh --quiet --eval "
  const status = rs.status();
  print('Replica set: ' + (status.ok ? 'OK' : 'ERROR'));
  status.members.forEach(function(m) {
    print('  ' + m.name + ' - ' + m.stateStr);
  });
"

echo ""
echo "=== 6. Запуск Rocket.Chat ==="
docker compose up -d rocketchat

echo ""
echo "=== Ждём запуска Rocket.Chat (30 сек) ==="
sleep 30

echo ""
echo "=== Проверка логов ==="
docker logs rocketchat --tail 10

echo ""
echo "=========================================="
echo "Готово! Откройте: http://localhost:3000"
echo "Логин: admin"
echo "Пароль: admin_password"
echo "=========================================="
