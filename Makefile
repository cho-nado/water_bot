# Makefile

# Собрать образы
.PHONY: build
build:
	docker compose build

# Запустить все сервисы в фоне
.PHONY: up
up:
	docker compose up -d

# Остановить и удалить контейнеры
.PHONY: down
down:
	docker compose down

# Смотреть логи бота
.PHONY: logs
logs:
	docker compose logs -f bot

# Перезапустить сервис бота (падение + поднятие)
.PHONY: restart
restart: down up

# Устанавливаем cron‑задачу на ежедневный бэкап в 02:00
.PHONY: install-cron
install-cron:
	@echo "Installing daily backup cron job at 02:00…"
	@CRON_LINE="0 2 * * * cd $(shell pwd) && ./scripts/backup.sh >> $(shell pwd)/scripts/backup.log 2>&1"
	@(crontab -l 2>/dev/null; echo "$$CRON_LINE") | crontab -
	@echo "Done. Cron:"
	@crontab -l | grep backup.sh