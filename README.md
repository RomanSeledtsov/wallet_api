# 💰 Wallet API

REST API для управления виртуальными кошельками: пополнение, снятие и проверка баланса.

## 🚀 Технологии

- Python 3.12
- FastAPI
- PostgreSQL - использовал ORM'ку, 
- SQLAlchemy + Alembic
- Docker + Docker Compose
- Pytest

## 📦 Установка и запуск

```bash
git clone https://github.com/RomanSeledtsov/wallet_api.git
cd wallet_api 

но думаю вы и так знаете 😏

# Собрать и запустить контейнеры
docker-compose up --build


Эндпоинты покрыты тестами 

| Метод  | URL                                      | Описание                                   |
| ------ | ---------------------------------------- | ------------------------------------------ |
| `POST` | `/api/v1/wallets/`                       | Создать кошелёк                            |
| `GET`  | `/api/v1/wallets/{wallet_id}`            | Получить баланс кошелька                   |
| `POST` | `/api/v1/wallets/{wallet_id}/operations` | Провести операцию `DEPOSIT` или `WITHDRAW` |
