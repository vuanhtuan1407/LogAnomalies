# Default scale values (can be overridden via CLI)
KAFKA_SCALE ?= 1
FLUENTBIT_SCALE ?= 1  # DO NOT scale if only have 1 .log file

# Start environment normally (with scale)
up:
	docker compose up -d \
		--build \
		--scale kafka=$(KAFKA_SCALE) \
		--scale fluentbit=$(FLUENTBIT_SCALE) \
		--remove-orphans

# Start and force recreate (with scale)
up-force:
	docker compose up -d --force-recreate \
		--build \
		--scale kafka=$(KAFKA_SCALE) \
		--scale fluentbit=$(FLUENTBIT_SCALE) \
		--remove-orphans

# Stop and remove services + volumes
down:
	docker compose down -v --remove-orphans

# Clean all Docker resources
clean:
	docker compose down -v --remove-orphans
	docker image prune -a -f
	docker volume prune -f
	docker network prune -f
	docker builder prune -a -f

# Full reset
reset: clean up
