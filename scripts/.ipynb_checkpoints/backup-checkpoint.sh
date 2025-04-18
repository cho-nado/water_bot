#!/usr/bin/env bash
set -euo pipefail

# находим корень проекта (где лежит docker-compose.yml и .env)
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_DIR="${ROOT_DIR}/backups"
mkdir -p "$BACKUP_DIR"

# загружаем переменные из .env
# (тут важно, что .env лежит в корне проекта)
set -a
source "${ROOT_DIR}/.env"
set +a

TIMESTAMP=$(date +"%Y-%m-%d")
FILENAME="${DB_NAME}_${TIMESTAMP}.sql"

# Делаем дамп через docker exec в контейнер db
CONTAINER_ID=$(docker-compose -f "${ROOT_DIR}/docker-compose.yml" ps -q db)
docker exec -i "$CONTAINER_ID" \
    pg_dump -U "${DB_USER}" "${DB_NAME}" \
    > "${BACKUP_DIR}/${FILENAME}"

# Удаляем дампы старше 7 дней (храним 7 последних)
find "$BACKUP_DIR" -type f -name "*.sql" -mtime +7 -delete
