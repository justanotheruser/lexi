# Lexi DevContainer

This devcontainer provides a complete development environment for the Lexi AI-powered language adventure bot.

## What's Included

- **Python 3.12** with all development tools
- **PostgreSQL 15** database with pre-configured schema
- **Redis 7** for caching and Celery broker
- **FastAPI** web server setup
- **VS Code extensions** for Python development

## Services

### App Service (Main Development Container)

- Python 3.12 with all dependencies
- FastAPI web server on port 8000
- All development tools (black, flake8, isort, pylint, pytest, mypy)

### Database Service (PostgreSQL)

- PostgreSQL 15 with Alpine Linux
- Pre-configured database `lexi_dev`
- User: `lexi`, Password: `lexi123`
- Port: 5432
- Automatic schema initialization

### Redis Service

- Redis 7 with Alpine Linux
- Used for caching and Celery broker
- Port: 6379

## Getting Started

1. **Open in DevContainer**: Use VS Code's "Reopen in Container" command
2. **Set Environment Variables**: Copy `env.example` to `.env` and fill in your API keys:
   ```bash
   cp env.example .env
   # Edit .env with your actual API keys
   ```
3. **Install Dependencies**: Dependencies are automatically installed when the container starts
4. **Start Development**: The container is ready for development!

## Environment Variables

Required environment variables (set in `.env`):

- `OPENAI_API_KEY`: Your OpenAI API key
- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token

## Database Schema

The database is automatically initialized with the following tables:

- `users`: Telegram user information
- `stories`: Completed story data
- `user_vocabulary_progress`: Vocabulary learning progress

## Development Commands

```bash
# Run FastAPI development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest

# Format code
black .
isort .

# Lint code
flake8
pylint app/

# Type checking
mypy app/
```

## Ports

- **8000**: FastAPI web server
- **5432**: PostgreSQL database
- **6379**: Redis cache/broker

## File Structure

```
.devcontainer/
├── devcontainer.json    # VS Code devcontainer configuration
├── docker-compose.yml   # Docker services definition
├── Dockerfile          # App container definition
├── init-db.sql        # Database initialization script
└── README.md          # This file
```

## Troubleshooting

1. **Container won't start**: Check that Docker and Docker Compose are installed
2. **Database connection issues**: Ensure the database service is running and ports are forwarded
3. **Missing dependencies**: Run `pip install -r requirements.txt` manually
4. **Environment variables**: Make sure `.env` file exists and contains required variables
