markdown
# Universal Parser

Универсальный веб-парсер с визуальным интерфейсом. Позволяет анализировать страницы, выделять повторяющиеся блоки, настраивать поля и запускать сбор данных с пагинацией. Результаты можно экспортировать в JSON или Excel.

## Технологии

- **Backend**: Python + FastAPI, PostgreSQL, Redis, Playwright, SQLAlchemy
- **Frontend**: React + TypeScript, Tailwind CSS, Vite

## Требования

- Python 3.12+
- Node.js 18+
- PostgreSQL (14+)
- Redis (7+)
- (Опционально) Docker и Docker Compose

## Быстрый старт

### 1. Клонирование репозитория

```bash
git clone <url>
cd UniversalParser
```
### 2. Настройка базы данных и Redis
Вариант А: Через Docker (рекомендуется)
Создайте файл docker-compose.yml в корне проекта:

```yaml
version: '3'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: parser_user
      POSTGRES_PASSWORD: parser_pass
      POSTGRES_DB: parser_db
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
  redis:
    image: redis:7
    ports:
      - "6379:6379"

volumes:
  pgdata:
```  
Запустите:

```bash
docker-compose up -d
```
#### Вариант Б: Локальная установка
1. Установите PostgreSQL и создайте базу данных:

```sql
CREATE DATABASE parser_db;
CREATE USER parser_user WITH PASSWORD 'parser_pass';
GRANT ALL PRIVILEGES ON DATABASE parser_db TO parser_user;
```
#### Установите Redis (стандартный порт 6379).

3. Бэкенд
#### Перейдите в папку parser_app:

```bash
cd parser_app
```
#### Создайте и активируйте виртуальное окружение:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```
#### Установите зависимости:

```bash
pip install -r requirements.txt
```

#### Установите браузеры Playwright:

```bash
playwright install chromium
```
#### Создайте файл .env на основе .env.example:

```env
DATABASE_URL=postgresql+asyncpg://parser_user:parser_pass@localhost/parser_db
REDIS_URL=redis://localhost:6379/0
```
### Запустите сервер:

```bash
uvicorn main:app --reload
```
### API будет доступно по адресу http://localhost:8000. 
### Документация Swagger: http://localhost:8000/docs.

### 4. Фронтенд
#### Откройте новый терминал в папке frontend:

```bash
cd frontend
npm install
npm run dev
```
#### Приложение откроется по адресу http://localhost:5173.

## Использование
### На главной странице введите URL страницы для анализа (например, http://books.toscrape.com/catalogue/page-1.html).

### Дождитесь завершения анализа – появятся кандидаты (повторяющиеся блоки). Выберите подходящий.

### Настройте поля: измените имена, при необходимости селекторы, отметьте нужные.

### Сохраните конфигурацию – она появится в списке.

### Запустите сбор данных по конфигурации, укажите стартовый URL и количество страниц (опционально).

### После завершения просмотрите результаты и скачайте в JSON или Excel.