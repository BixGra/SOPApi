echo "docker build . -t sopapi"

docker build . -t sopapi

echo "docker compose up -d --remove-orphans"

docker compose up -d --remove-orphans

echo "system prune -a"

docker system prune -a