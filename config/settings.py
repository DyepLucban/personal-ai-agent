from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Database configuration
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")  
DB_USER = os.getenv("POSTGRES_USER", "user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password") 
DB_NAME = os.getenv("POSTGRES_DB", "mydatabase")

# Telegram Bot Configuration
TELEGRAM_API_URL = os.getenv("TELEGRAM_API_URL")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_WEBHOOK_SECRET = os.getenv("TELEGRAM_WEBHOOK_SECRET")

# Docker Runner Model Configuration
RUNNER_MODEL_BASE_URL = os.getenv("RUNNER_MODEL_BASE_URL")
RUNNER_MODEL = os.getenv("RUNNER_MODEL")

# --- GitHub Credentials ---
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# --- Google API Credentials
GOOGLE_TOKEN_URI = os.getenv("GOOGLE_TOKEN_URI")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_SCOPE = os.getenv("GOOGLE_SCOPE")
GOOGLE_REFRESH_TOKEN = os.getenv("GOOGLE_REFRESH_TOKEN")

# --- Telegram Bot Credentials
TELEGRAM_API_URL = os.getenv("TELEGRAM_API_URL")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
