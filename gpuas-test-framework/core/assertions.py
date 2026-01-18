import time
from typing import Callable, Any
from utils.logger import logger


class CustomAssertions:
    """Custom assertions for GPUaaS testing"""

    @staticmethod
    def assert_eventually(
        condition_func: Callable[[], bool],
        timeout: int = 30,
        interval: int = 2,
        error_msg: str = "Condition not met within timeout"
    ) -> bool:
        """
        Assert that a condition becomes true within a timeout period.
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                if condition_func():
                    logger.debug(f"Condition met after {time.time() - start_time:.1f}s")
                    return True
            except Exception as exc:
                logger.debug(f"Condition check raised exception: {exc}")

            time.sleep(interval)

        logger.error(f"{error_msg} (timeout: {timeout}s)")
        raise AssertionError(error_msg)

    @staticmethod
    def assert_api_response(
        response: dict,
        expected_status: str = None,
        expected_fields: list = None,
        error_msg: str = "API response validation failed"
    ):
        """Assert API response contains expected data."""
        if not response:
            raise AssertionError(f"{error_msg}: Response is empty")

        if expected_status and response.get("status") != expected_status:
            raise AssertionError(
                f"{error_msg}: Expected status '{expected_status}', got '{response.get('status')}'"
            )

        if expected_fields:
            missing_fields = [field for field in expected_fields if field not in response]
            if missing_fields:
                raise AssertionError(
                    f"{error_msg}: Missing fields in response: {missing_fields}"
                )

    @staticmethod
    def assert_instance_state(
        instance: dict,
        expected_state: str,
        timeout: int = 60,
        interval: int = 5
    ):
        """Assert GPU instance reaches expected state."""
        if isinstance(instance, str):
            from core.api_client import GPUaaSClient

            client = GPUaaSClient()

            def check_state():
                instance_data = client.get_instance(instance)
                return instance_data.get("status") == expected_state

            CustomAssertions.assert_eventually(
                check_state,
                timeout=timeout,
                interval=interval,
                error_msg=f"Instance {instance} did not reach state '{expected_state}'"
            )
        else:
            if instance.get("status") != expected_state:
                raise AssertionError(
                    f"Instance state is '{instance.get('status')}', expected '{expected_state}'"
                )

    @staticmethod
    def assert_job_completed(
        job: dict or str,
        timeout: int = 300,
        interval: int = 10
    ):
        """Assert job reaches completed or failed state."""
        if isinstance(job, str):
            from core.api_client import GPUaaSClient

            client = GPUaaSClient()

            def check_job():
                job_data = client.get_job(job)
                status = job_data.get("status")
                return status in ["completed", "failed"]

            CustomAssertions.assert_eventually(
                check_job,
                timeout=timeout,
                interval=interval,
                error_msg=f"Job {job} did not complete within timeout"
            )
        else:
            status = job.get("status")
            if status not in ["completed", "failed"]:
                raise AssertionError(
                    f"Job status is '{status}', expected 'completed' or 'failed'"
                )

    @staticmethod
    def assert_metrics_present(metrics_response: dict, min_count: int = 1):
        """Assert metrics response contains expected data."""
        if not metrics_response:
            raise AssertionError("Metrics response is empty")

        count = metrics_response.get("count", 0)
        metrics = metrics_response.get("metrics", [])

        if count < min_count:
            raise AssertionError(f"Expected at least {min_count} metrics, got {count}")

        if len(metrics) < min_count:
            raise AssertionError(
                f"Expected at least {min_count} metric entries, got {len(metrics)}"
            )

        required_fields = ["timestamp", "gpu_utilization", "memory_used_mb"]
        for metric in metrics[:min_count]:
            missing = [field for field in required_fields if field not in metric]
            if missing:
                raise AssertionError(
                    f"Metric missing required fields: {missing}. Metric: {metric}"
                )
