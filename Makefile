.PHONY: help build up down logs shell migrate createsuperuser

help:
	@echo "Comandos disponíveis:"
	@echo "  make build              - Constrói as imagens Docker"
	@echo "  make up                 - Inicia os containers"
	@echo "  make down               - Para os containers"
	@echo "  make logs               - Mostra os logs da aplicação"
	@echo "  make shell              - Abre o shell do Django"
	@echo "  make migrate            - Executa as migrações do banco de dados"
	@echo "  make createsuperuser    - Cria um super usuário"

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f web

shell:
	docker-compose exec web python manage.py shell

migrate:
	docker-compose exec web python manage.py migrate

createsuperuser:
	docker-compose exec web python manage.py createsuperuser

collectstatic:
	docker-compose exec web python manage.py collectstatic --noinput

restart:
	docker-compose restart web
