#!/bin/bash
set -e

echo "Starting containers..."
docker compose up -d mongo

echo "Waiting for MongoDB to be ready..."
until docker exec rocketchat-mongo mongosh --quiet --eval "rs.status()" &>/dev/null; do
  sleep 2
done

echo "Initializing replica set..."
docker exec rocketchat-mongo mongosh --eval "rs.initiate({_id: 'rs0', members: [{_id: 0, host: 'localhost:27017'}]})"

echo "Starting Rocket.Chat..."
docker compose up -d rocketchat

echo ""
echo "Rocket.Chat will be available at: http://localhost:3000"
echo "Login: admin / admin_password"
