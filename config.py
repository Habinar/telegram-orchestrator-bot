import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8209802088:AAGNMKwwhLBC7HICuz9wQQ6QhXhdm5BOePk")

# OpenAI API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")

# Validation Settings
VALIDATION_MODE = "RIGOROUS"
MAX_RETRIES = 3
TRANSPARENCY_LEVEL = "STANDARD"

# Agent Configuration
AGENT_TIMEOUT = 60  # seconds
VALIDATION_TIMEOUT = 30  # seconds

# User Timezone
USER_TIMEZONE = "Europe/Kiev"