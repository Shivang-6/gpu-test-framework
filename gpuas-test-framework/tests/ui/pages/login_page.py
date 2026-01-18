from playwright.sync_api import Page, expect
from core.reporting import TestReporter
from utils.logger import logger


class LoginPage:
    """Page Object for Login page"""

    def __init__(self, page: Page):
        self.page = page
        self.username_input = page.locator("input[name='username']")
        self.password_input = page.locator("input[name='password']")
        self.login_button = page.locator("button[type='submit']")
        self.error_message = page.locator(".error-message")
        self.forgot_password_link = page.locator("a[href='/forgot-password']")

    def navigate(self):
        self.page.goto("/login")
        logger.info("Navigated to login page")
        return self

    def login(self, username: str, password: str):
        TestReporter.log_test_step(f"Login as {username}")

        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_button.click()

        logger.info(f"Login attempted for user: {username}")
        return self

    def expect_successful_login(self):
        expect(self.page).to_have_url("/dashboard")
        logger.info("Login successful - redirected to dashboard")

    def expect_error_message(self, message: str = None):
        expect(self.error_message).to_be_visible()
        if message:
            expect(self.error_message).to_contain_text(message)
        logger.info(f"Login error displayed: {message or 'generic error'}")

    def click_forgot_password(self):
        self.forgot_password_link.click()
        logger.info("Clicked forgot password link")
        return self
