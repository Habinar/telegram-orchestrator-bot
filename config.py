import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8209802088:AAGNMKwwhLBC7HICuz9wQQ6QhXhdm5BOePk")

# Bhindi API
BHINDI_API_KEY = os.getenv("BHINDI_API_KEY", "")  # Will be set via Railway env vars
BHINDI_API_URL = "https://api.bhindi.io/v1"

# Validation Settings
VALIDATION_MODE = "RIGOROUS"
MAX_RETRIES = 3
TRANSPARENCY_LEVEL = "STANDARD"

# Agent Configuration
AGENT_TIMEOUT = 60  # seconds
VALIDATION_TIMEOUT = 30  # seconds

# User Timezone
USER_TIMEZONE = "Europe/Kiev"