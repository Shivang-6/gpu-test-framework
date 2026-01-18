import time
import pytest
from core.api_client import GPUaaSClient, APIError
from core.assertions import CustomAssertions
from core.reporting import TestReporter
from config.test_data import GPUInstanceFactory
from utils.logger import logger


class TestGPUProvisioning:
    """Test GPU instance provisioning"""

    @pytest.fixture
    def authenticated_client(self):
        client = GPUaaSClient()
        client.login()
        return client

    @pytest.fixture
    def cleanup_instances(self, authenticated_client):
        created_instances = []
        yield created_instances

        for instance_id in created_instances:
            try:
                instance = authenticated_client.get_instance(instance_id)
                if instance.get("status") in ["active", "provisioning"]:
                    authenticated_client.delete_instance(instance_id)
                    logger.info(f"Cleaned up instance: {instance_id}")
                    time.sleep(2)
            except APIError as exc:
                logger.warning(f"Failed to cleanup instance {instance_id}: {exc}")

    @pytest.mark.smoke
    @pytest.mark.provisioning
    def test_create_gpu_instance(self, authenticated_client, cleanup_instances):
        TestReporter.log_test_step("Test create GPU instance")

        test_data = GPUInstanceFactory.create_training_instance()

        response = authenticated_client.create_gpu_instance(**test_data)

        TestReporter.attach_json(response, "create_instance_response")
        TestReporter.attach_json(test_data, "test_data")

        assert "instance_id" in response
        assert response["status"] == "provisioning"
        assert response["message"] is not None

        instance_id = response["instance_id"]
        cleanup_instances.append(instance_id)

        CustomAssertions.assert_instance_state(
            instance_id,
            expected_state="active",
            timeout=60,
            interval=5,
        )

        instance_details = authenticated_client.get_instance(instance_id)

        assert instance_details["id"] == instance_id
        assert instance_details["gpu_type"] == test_data["gpu_type"]
        assert instance_details["count"] == test_data["count"]
        assert instance_details["status"] == "active"

        logger.info(f"GPU instance created successfully: {instance_id}")

    @pytest.mark.provisioning
    def test_create_multiple_gpu_types(self, authenticated_client, cleanup_instances):
        TestReporter.log_test_step("Test multiple GPU types")

        gpu_types = ["A100", "H100", "V100", "RTX4090"]
        created_instances = []

        for gpu_type in gpu_types:
            response = authenticated_client.create_gpu_instance(
                gpu_type=gpu_type,
                count=1,
                region="us-east-1",
            )

            assert response["status"] == "provisioning"
            instance_id = response["instance_id"]
            created_instances.append(instance_id)
            cleanup_instances.append(instance_id)

            CustomAssertions.assert_instance_state(
                instance_id,
                expected_state="active",
                timeout=45,
                interval=3,
            )

            instance = authenticated_client.get_instance(instance_id)
            assert instance["gpu_type"] == gpu_type

            logger.info(f"Successfully created {gpu_type} instance")

        logger.info(f"Created instances of all GPU types: {created_instances}")

    @pytest.mark.provisioning
    @pytest.mark.negative
    def test_create_instance_invalid_gpu_type(self, authenticated_client):
        TestReporter.log_test_step("Test invalid GPU type")

        with pytest.raises(APIError) as exc_info:
            authenticated_client.create_gpu_instance(
                gpu_type="INVALID_GPU",
                count=1,
            )

        error_message = str(exc_info.value)
        assert "Bad request" in error_message or "400" in error_message

        logger.info("Invalid GPU type correctly rejected")

    @pytest.mark.provisioning
    def test_list_instances(self, authenticated_client, cleanup_instances):
        TestReporter.log_test_step("Test list instances")

        create_response = authenticated_client.create_gpu_instance(
            gpu_type="A100",
            count=2,
            region="eu-west-1",
        )

        instance_id = create_response["instance_id"]
        cleanup_instances.append(instance_id)

        CustomAssertions.assert_instance_state(instance_id, "active")

        list_response = authenticated_client.list_instances()

        TestReporter.attach_json(list_response, "list_instances_response")

        assert "count" in list_response
        assert "instances" in list_response
        assert isinstance(list_response["instances"], list)

        found = False
        for instance in list_response["instances"]:
            if instance["id"] == instance_id:
                found = True
                assert instance["gpu_type"] == "A100"
                assert instance["count"] == 2
                assert instance["region"] == "eu-west-1"
                break

        assert found, f"Instance {instance_id} not found in list"

        logger.info(f"List instances successful. Found {list_response['count']} instances")

    @pytest.mark.provisioning
    def test_instance_metrics(self, authenticated_client, cleanup_instances):
        TestReporter.log_test_step("Test instance metrics")

        create_response = authenticated_client.create_gpu_instance()
        instance_id = create_response["instance_id"]
        cleanup_instances.append(instance_id)

        CustomAssertions.assert_instance_state(instance_id, "active")

        instance_details = authenticated_client.get_instance(instance_id)

        assert "current_metrics" in instance_details
        metrics = instance_details["current_metrics"]

        required_metrics = [
            "gpu_utilization",
            "memory_used_mb",
            "memory_total_mb",
            "power_draw_w",
            "temperature_c",
        ]

        for metric in required_metrics:
            assert metric in metrics, f"Missing metric: {metric}"
            assert isinstance(metrics[metric], (int, float)), f"Metric {metric} should be numeric"

        metrics_response = authenticated_client.get_metrics(instance_id=instance_id)
        CustomAssertions.assert_metrics_present(metrics_response, min_count=1)

        logger.info(f"Metrics test passed for instance {instance_id}")

    @pytest.mark.provisioning
    def test_delete_instance(self, authenticated_client):
        TestReporter.log_test_step("Test delete instance")

        create_response = authenticated_client.create_gpu_instance()
        instance_id = create_response["instance_id"]

        CustomAssertions.assert_instance_state(instance_id, "active")

        delete_response = authenticated_client.delete_instance(instance_id)

        TestReporter.attach_json(delete_response, "delete_response")

        assert delete_response["message"] is not None
        assert "Instance terminated successfully" in delete_response["message"]

        time.sleep(3)

        with pytest.raises(APIError) as exc_info:
            authenticated_client.get_instance(instance_id)

        assert "404" in str(exc_info.value) or "not found" in str(exc_info.value).lower()

        logger.info(f"Instance {instance_id} successfully deleted")
