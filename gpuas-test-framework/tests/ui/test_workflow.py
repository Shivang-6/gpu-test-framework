import time
import pytest
from playwright.sync_api import expect
from core.reporting import TestReporter
from utils.logger import logger


@pytest.mark.ui
@pytest.mark.smoke
class TestUIWorkflows:
    """End-to-end UI workflow tests"""

    @pytest.fixture(autouse=True)
    def setup(self, page, api_client):
        self.page = page
        self.api_client = api_client
        self.test_instances = []

        yield

        for instance_id in self.test_instances:
            try:
                self.api_client.delete_instance(instance_id)
                logger.info(f"Cleaned up instance via API: {instance_id}")
            except Exception as exc:
                logger.warning(f"Failed to cleanup instance {instance_id}: {exc}")

    @pytest.mark.e2e
    def test_complete_gpu_provisioning_flow(self, login_page, dashboard_page):
        TestReporter.log_test_step("Complete GPU provisioning E2E test")

        login_page.navigate().login("test_user", "test_pass")
        login_page.expect_successful_login()

        TestReporter.attach_screenshot(self.page, "after_login")

        dashboard_page.navigate()
        initial_count = dashboard_page.get_instance_count()

        logger.info(f"Initial instance count: {initial_count}")

        instance_name = dashboard_page.open_create_instance_modal().create_gpu_instance(
            gpu_type="A100",
            count=2,
            region="us-east-1",
        )

        TestReporter.attach_screenshot(self.page, "instance_creation_submitted")

        instance_info = dashboard_page.wait_for_instance_creation(instance_name)

        assert instance_info is not None
        assert instance_info["gpu_type"] == "A100"
        assert instance_info["count"] == 2
        assert instance_info["region"] == "us-east-1"
        assert instance_info["status"].lower() == "active"

        TestReporter.attach_screenshot(self.page, "instance_created")

        final_count = dashboard_page.get_instance_count()
        assert final_count == initial_count + 1

        dashboard_page.view_instance_metrics(instance_name)

        TestReporter.attach_screenshot(self.page, "instance_metrics")

        expect(dashboard_page.metrics_chart).to_be_visible()

        logger.info(f"E2E test completed. Created instance: {instance_name}")

    @pytest.mark.ui
    def test_login_with_invalid_credentials(self, login_page):
        TestReporter.log_test_step("Test invalid login")

        login_page.navigate().login("invalid_user", "wrong_password")

        login_page.expect_error_message("Invalid username or password")

        TestReporter.attach_screenshot(self.page, "invalid_login_error")

        expect(self.page).to_have_url("/login")

        logger.info("Invalid login test passed")

    @pytest.mark.ui
    def test_create_multiple_instances(self, login_page, dashboard_page):
        TestReporter.log_test_step("Test multiple instance creation")

        login_page.navigate().login("test_user", "test_pass")
        login_page.expect_successful_login()

        dashboard_page.navigate()
        initial_count = dashboard_page.get_instance_count()

        instances_to_create = 2
        created_names = []

        for i in range(instances_to_create):
            instance_name = dashboard_page.open_create_instance_modal().create_gpu_instance(
                gpu_type="H100" if i % 2 == 0 else "V100",
                count=i + 1,
                region="eu-west-1",
                name=f"Multi-Test-{i}-{int(time.time())}",
            )
            created_names.append(instance_name)
            time.sleep(2)

        for name in created_names:
            dashboard_page.wait_for_instance_creation(name, timeout=90000)

        final_count = dashboard_page.get_instance_count()
        assert final_count == initial_count + instances_to_create

        for i, name in enumerate(created_names):
            instance = dashboard_page.get_instance_by_name(name)
            assert instance is not None
            assert instance["status"].lower() == "active"

            expected_gpu = "H100" if i % 2 == 0 else "V100"
            assert instance["gpu_type"] == expected_gpu
            assert instance["count"] == i + 1

        TestReporter.attach_screenshot(self.page, "multiple_instances_created")

        logger.info(f"Created {instances_to_create} instances: {created_names}")

    @pytest.mark.ui
    def test_instance_status_updates(self, login_page, dashboard_page):
        TestReporter.log_test_step("Test instance status updates")

        login_page.navigate().login("test_user", "test_pass")
        login_page.expect_successful_login()

        dashboard_page.navigate()

        instance_name = dashboard_page.open_create_instance_modal().create_gpu_instance(
            name=f"Status-Test-{int(time.time())}",
        )

        instance_info = dashboard_page.wait_for_instance_creation(instance_name)

        assert instance_info["status"].lower() in ["provisioning", "active"]

        self.page.reload()
        dashboard_page._wait_for_loading()

        for _ in range(10):
            instance_info = dashboard_page.get_instance_by_name(instance_name)
            if instance_info and instance_info["status"].lower() == "active":
                break
            time.sleep(3)
            self.page.reload()
            dashboard_page._wait_for_loading()

        assert instance_info["status"].lower() == "active"

        logger.info(f"Instance status correctly updated to active: {instance_name}")

    @pytest.mark.ui
    def test_logout_functionality(self, login_page, dashboard_page):
        TestReporter.log_test_step("Test logout")

        login_page.navigate().login("test_user", "test_pass")
        login_page.expect_successful_login()

        dashboard_page.navigate()
        expect(self.page).to_have_url("/dashboard")

        dashboard_page.logout()

        expect(self.page).to_have_url("/login")

        TestReporter.attach_screenshot(self.page, "after_logout")

        logger.info("Logout test passed")
