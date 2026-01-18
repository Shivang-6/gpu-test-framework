import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    # Base URLs
    BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
    UI_URL = os.getenv("UI_URL", "http://localhost:3000")

    # Test Configuration
    TEST_TIMEOUT = int(os.getenv("TEST_TIMEOUT", 30))
    WAIT_TIMEOUT = int(os.getenv("WAIT_TIMEOUT", 10))

    # Auth Configuration
    TEST_USER = os.getenv("TEST_USER", "test_user")
    TEST_PASSWORD = os.getenv("TEST_PASSWORD", "test_pass")

    # Reporting
    REPORT_DIR = Path("reports")
    SCREENSHOT_DIR = REPORT_DIR / "screenshots"
    LOG_DIR = REPORT_DIR / "logs"

    # Performance
    LOAD_TEST_USERS = int(os.getenv("LOAD_TEST_USERS", 10))
    LOAD_TEST_DURATION = os.getenv("LOAD_TEST_DURATION", "30s")

    def __init__(self):
        # Create directories if they don't exist
        self.REPORT_DIR.mkdir(exist_ok=True)
        self.SCREENSHOT_DIR.mkdir(exist_ok=True)
        self.LOG_DIR.mkdir(exist_ok=True)


auth_settings = Settings()
settings = auth_settings
