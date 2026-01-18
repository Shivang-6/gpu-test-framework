import time
import pytest
from typing import Dict, Any
from config.settings import settings
from utils.logger import logger


class BaseTest:
    """Base test class with common utilities"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Setup and teardown for each test"""
        self.test_start_time = time.time()
        self.test_name = None

        logger.info("Starting test setup")
        yield

        duration = time.time() - self.test_start_time
        logger.info(f"Test completed in {duration:.2f} seconds")

    def log_step(self, step: str, details: Dict = None):
        """Log a test step with details"""
        logger.info(f"STEP: {step}")
        if details:
            logger.debug(f"Details: {details}")

    def assert_with_retry(self, condition_func, timeout=30, interval=2, error_msg=""):
        """Assert with retry for eventual consistency"""
        start_time = time.time()
        last_error = None

        while time.time() - start_time < timeout:
            try:
                result = condition_func()
                if result:
                    return result
            except AssertionError as exc:
                last_error = exc

            time.sleep(interval)

        if last_error:
            raise AssertionError(f"{error_msg}. Last error: {last_error}")
        raise AssertionError(f"{error_msg}. Condition not met after {timeout} seconds")

    def generate_test_id(self, prefix="test"):
        """Generate unique test ID"""
        return f"{prefix}_{int(time.time())}_{id(self)}"
