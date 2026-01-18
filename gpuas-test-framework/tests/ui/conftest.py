import pytest
import allure
from playwright.sync_api import Page, BrowserContext
from core.reporting import TestReporter
from utils.logger import logger


@pytest.fixture(scope="function")
def page(context: BrowserContext):
    page = context.new_page()
    page.set_default_timeout(30000)
    page.set_viewport_size({"width": 1920, "height": 1080})

    yield page

    if hasattr(pytest, "test_failed") and pytest.test_failed:
        TestReporter.attach_screenshot(page, "test_failure")

    page.close()


@pytest.fixture(scope="function")
def context(browser):
    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        record_video_dir="reports/videos/",
        record_har_path="reports/har/",
    )

    context.tracing.start(screenshots=True, snapshots=True, sources=True)

    yield context

    trace_path = "reports/trace.zip"
    context.tracing.stop(path=trace_path)

    try:
        allure.attach.file(
            trace_path,
            name="playwright_trace",
            attachment_type=allure.attachment_type.ZIP,
        )
    except Exception as exc:
        logger.error(f"Failed to attach trace: {exc}")

    context.close()


@pytest.fixture(scope="function")
def login_page(page):
    from .pages.login_page import LoginPage

    return LoginPage(page)


@pytest.fixture(scope="function")
def dashboard_page(page):
    from .pages.dashboard_page import DashboardPage

    return DashboardPage(page)


@pytest.fixture(scope="session")
def api_client():
    from core.api_client import GPUaaSClient

    client = GPUaaSClient()
    client.login()
    return client


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call" and rep.failed:
        pytest.test_failed = True
    else:
        pytest.test_failed = False
