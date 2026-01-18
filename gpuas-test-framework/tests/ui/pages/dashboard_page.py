import time
from playwright.sync_api import Page, expect
from core.reporting import TestReporter
from utils.logger import logger


class DashboardPage:
    """Page Object for Dashboard page"""

    def __init__(self, page: Page):
        self.page = page
        self.welcome_message = page.locator(".welcome-message")
        self.gpu_instances_section = page.locator("#gpu-instances")
        self.create_instance_button = page.locator("button#create-instance")
        self.instance_table = page.locator("table.instances")
        self.instance_rows = page.locator("table.instances tbody tr")
        self.jobs_section = page.locator("#jobs-section")
        self.metrics_chart = page.locator("#metrics-chart")
        self.logout_button = page.locator("button#logout")

        self.instance_modal = page.locator("#create-instance-modal")
        self.gpu_type_select = page.locator("select#gpu-type")
        self.gpu_count_input = page.locator("input#gpu-count")
        self.region_select = page.locator("select#region")
        self.instance_name_input = page.locator("input#instance-name")
        self.submit_instance_button = page.locator("button#submit-instance")
        self.cancel_button = page.locator("button#cancel-instance")

    def navigate(self):
        self.page.goto("/dashboard")
        self._wait_for_loading()
        logger.info("Navigated to dashboard")
        return self

    def _wait_for_loading(self, timeout: int = 10000):
        expect(self.welcome_message).to_be_visible(timeout=timeout)
        expect(self.gpu_instances_section).to_be_visible(timeout=timeout)

    def get_welcome_text(self) -> str:
        return self.welcome_message.text_content()

    def get_instance_count(self) -> int:
        return self.instance_rows.count()

    def open_create_instance_modal(self):
        TestReporter.log_test_step("Open create instance modal")

        self.create_instance_button.click()
        expect(self.instance_modal).to_be_visible()

        logger.info("Create instance modal opened")
        return self

    def create_gpu_instance(self, **kwargs):
        TestReporter.log_test_step("Create GPU instance via UI")

        config = {
            "gpu_type": "A100",
            "count": 1,
            "region": "us-east-1",
            "name": f"Test-Instance-{int(time.time())}",
            **kwargs,
        }

        self.gpu_type_select.select_option(config["gpu_type"])
        self.gpu_count_input.fill(str(config["count"]))
        self.region_select.select_option(config["region"])
        self.instance_name_input.fill(config["name"])

        TestReporter.attach_text(str(config), "ui_instance_config")

        self.submit_instance_button.click()

        expect(self.instance_modal).to_be_hidden()

        logger.info(f"UI instance creation submitted: {config}")
        return config["name"]

    def wait_for_instance_creation(self, instance_name: str, timeout: int = 60000):
        TestReporter.log_test_step(f"Wait for instance {instance_name}")

        start_time = time.time()
        while time.time() - start_time < timeout / 1000:
            instances = self.get_instance_details()
            for instance in instances:
                if instance_name in instance.get("name", ""):
                    logger.info(f"Instance found: {instance_name}")
                    return instance

            time.sleep(2)
            self.page.reload()
            self._wait_for_loading()

        raise TimeoutError(f"Instance {instance_name} not found within {timeout}ms")

    def get_instance_details(self) -> list:
        instances = []

        for i in range(self.instance_rows.count()):
            row = self.instance_rows.nth(i)
            instance = {
                "name": row.locator("td.name").text_content(),
                "gpu_type": row.locator("td.gpu-type").text_content(),
                "count": int(row.locator("td.count").text_content()),
                "status": row.locator("td.status").text_content(),
                "region": row.locator("td.region").text_content(),
            }
            instances.append(instance)

        return instances

    def get_instance_by_name(self, name: str):
        instances = self.get_instance_details()
        for instance in instances:
            if name in instance["name"]:
                return instance
        return None

    def view_instance_metrics(self, instance_name: str):
        TestReporter.log_test_step(f"View metrics for {instance_name}")

        for i in range(self.instance_rows.count()):
            row = self.instance_rows.nth(i)
            if instance_name in row.locator("td.name").text_content():
                row.locator("button.metrics").click()
                break

        expect(self.metrics_chart).to_be_visible()

        logger.info(f"Metrics opened for instance: {instance_name}")
        return self

    def logout(self):
        self.logout_button.click()
        logger.info("Logged out from dashboard")
        return self
