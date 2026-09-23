# Instruções de Configuração - Django + Docker + MySQL

## Pré-requisitos
- Docker
- Docker Compose

## Como começar

### 1. Clone ou navegue até o diretório do projeto
```bash
cd c:\Users\onildo\Documents\project-promo-groups
```

### 2. Configure as variáveis de ambiente
Copie o arquivo `.env.example` para `.env` (já foi feito):
```bash
cp .env.example .env
```

### 3. Construa as imagens Docker
```bash
docker-compose build
```

### 4. Inicie os containers
```bash
docker-compose up -d
```

As migrações serão executadas automaticamente ao iniciar.

### 5. Crie um superusuário (administrador)
```bash
docker-compose exec web python manage.py createsuperuser
```

### 6. Acesse a aplicação
- **Aplicação**: http://localhost:8000
- **Painel Admin**: http://localhost:8000/admin

## Comandos úteis

### Ver logs da aplicação
```bash
docker-compose logs -f web
```

### Acessar o shell do Django
```bash
docker-compose exec web python manage.py shell
```

### Executar migrações
```bash
docker-compose exec web python manage.py migrate
```

### Coletar arquivos estáticos
```bash
docker-compose exec web python manage.py collectstatic --noinput
```

### Parar os containers
```bash
docker-compose down
```

### Reiniciar apenas a aplicação Django
```bash
docker-compose restart web
```

## Estrutura do Projeto

```
project-promo-groups/
├── config/                 # Configurações do Django
│   ├── __init__.py
│   ├── settings.py        # Configurações principais
│   ├── urls.py            # URLs da aplicação
│   ├── wsgi.py            # WSGI para produção
│   └── asgi.py            # ASGI para WebSockets
├── manage.py              # Script de gerenciamento do Django
├── requirements.txt       # Dependências Python
├── Dockerfile             # Imagem Docker
├── docker-compose.yml     # Configuração dos containers
├── .env                   # Variáveis de ambiente
├── .env.example           # Exemplo de variáveis
├── .gitignore             # Arquivos ignorados pelo Git
└── Makefile               # Atalhos de comandos (opcional)
```

## Criar novos apps Django

Quando precisar criar um novo app:
```bash
docker-compose exec web python manage.py startapp nome_do_app
```

Não esqueça de adicionar o app em `INSTALLED_APPS` no `config/settings.py`

## Banco de dados

- **Host**: db (dentro da rede Docker) ou localhost (da máquina host)
- **Porta**: 3306
- **Database**: django_db
- **Usuário**: django_user
- **Senha**: django_password
- **Root Password**: root

Você pode conectar com qualquer cliente MySQL/MariaDB ao `localhost:3306`

## Variáveis de Ambiente

As variáveis de ambiente podem ser modificadas no arquivo `.env`:

- `DEBUG`: True/False (modo debug)
- `SECRET_KEY`: Chave secreta do Django
- `MYSQL_DATABASE`: Nome do banco de dados
- `MYSQL_USER`: Usuário do MySQL
- `MYSQL_PASSWORD`: Senha do MySQL
- `MYSQL_ROOT_PASSWORD`: Senha do root

## Troubleshooting

### Port 3306 already in use
```bash
docker-compose down
```

Então inicie novamente:
```bash
docker-compose up -d
```

### Erro de conexão com o banco de dados
Aguarde alguns segundos para o MySQL inicializar. O docker-compose tem um healthcheck configurado.

### Limpar volumes do MySQL
```bash
docker-compose down -v
```

## Próximas etapas

1. Crie seus apps Django
2. Defina seus modelos em `models.py`
3. Crie as migrações: `docker-compose exec web python manage.py makemigrations`
4. Aplique as migrações: `docker-compose exec web python manage.py migrate`
5. Comece a desenvolver!
