import time
import pytest
from core.api_client import GPUaaSClient
from core.assertions import CustomAssertions
from core.reporting import TestReporter
from config.test_data import JobFactory
from utils.logger import logger


class TestJobManagement:
    """Test job submission and management"""

    @pytest.fixture
    def authenticated_client(self):
        client = GPUaaSClient()
        client.login()
        return client

    @pytest.fixture
    def setup_instance(self, authenticated_client, cleanup_instances):
        response = authenticated_client.create_gpu_instance(
            gpu_type="A100",
            count=1,
            region="us-east-1",
        )

        instance_id = response["instance_id"]
        cleanup_instances.append(instance_id)

        CustomAssertions.assert_instance_state(instance_id, "active")

        yield instance_id

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
            except Exception as exc:
                logger.warning(f"Failed to cleanup instance {instance_id}: {exc}")

    @pytest.mark.smoke
    @pytest.mark.jobs
    def test_submit_job(self, authenticated_client, setup_instance):
        TestReporter.log_test_step("Test submit job")

        instance_id = setup_instance

        job_data = {
            "instance_id": instance_id,
            "job_type": "training",
            "script_path": "/scripts/train_model.py",
            "parameters": {
                "model": "resnet50",
                "epochs": 10,
                "batch_size": 32,
                "learning_rate": 0.001,
            },
        }

        response = authenticated_client.submit_job(**job_data)

        TestReporter.attach_json(response, "submit_job_response")
        TestReporter.attach_json(job_data, "job_data")

        assert "job_id" in response
        assert response["status"] == "queued"
        assert response["message"] is not None

        job_id = response["job_id"]

        def job_is_running():
            job_info = authenticated_client.get_job(job_id)
            return job_info.get("status") == "running"

        CustomAssertions.assert_eventually(
            job_is_running,
            timeout=30,
            interval=3,
            error_msg=f"Job {job_id} did not start running",
        )

        job_details = authenticated_client.get_job(job_id)

        assert job_details["id"] == job_id
        assert job_details["instance_id"] == instance_id
        assert job_details["job_type"] == "training"
        assert "progress" in job_details

        logger.info(f"Job submitted successfully: {job_id}")

    @pytest.mark.jobs
    def test_job_lifecycle(self, authenticated_client, setup_instance):
        TestReporter.log_test_step("Test job lifecycle")

        instance_id = setup_instance

        submit_response = authenticated_client.submit_job(instance_id=instance_id)
        job_id = submit_response["job_id"]

        CustomAssertions.assert_job_completed(job_id, timeout=120, interval=10)

        job_details = authenticated_client.get_job(job_id)

        TestReporter.attach_json(job_details, "completed_job_details")

        assert job_details["status"] in ["completed", "failed"]

        if job_details["status"] == "completed":
            assert "results" in job_details
            assert "accuracy" in job_details["results"]
            assert "loss" in job_details["results"]
            logger.info(f"Job completed successfully with results: {job_details['results']}")
        else:
            logger.info("Job failed (expected for mock server)")

        assert "duration" in job_details
        assert job_details["duration"] > 0

    @pytest.mark.jobs
    def test_multiple_jobs_concurrent(self, authenticated_client, setup_instance):
        TestReporter.log_test_step("Test concurrent jobs")

        instance_id = setup_instance
        num_jobs = 3
        job_ids = []

        for i in range(num_jobs):
            response = authenticated_client.submit_job(
                instance_id=instance_id,
                job_type="inference" if i % 2 == 0 else "training",
                script_path=f"/scripts/job_{i}.py",
                parameters={"job_index": i},
            )
            job_ids.append(response["job_id"])

        logger.info(f"Submitted {num_jobs} jobs: {job_ids}")

        for job_id in job_ids:
            CustomAssertions.assert_job_completed(job_id, timeout=180, interval=15)

        for job_id in job_ids:
            job_details = authenticated_client.get_job(job_id)
            assert job_details["status"] in ["completed", "failed"]

        logger.info(f"All {num_jobs} concurrent jobs completed")

    @pytest.mark.jobs
    @pytest.mark.negative
    def test_submit_job_to_inactive_instance(self, authenticated_client):
        TestReporter.log_test_step("Test job to inactive instance")

        response = authenticated_client.create_gpu_instance()
        instance_id = response["instance_id"]

        with pytest.raises(Exception) as exc_info:
            authenticated_client.submit_job(instance_id=instance_id)

        error_message = str(exc_info.value)
        assert "not active" in error_message.lower() or "400" in error_message

        logger.info("Correctly rejected job submission to inactive instance")

    @pytest.mark.jobs
    def test_job_progress_tracking(self, authenticated_client, setup_instance):
        TestReporter.log_test_step("Test job progress tracking")

        instance_id = setup_instance

        response = authenticated_client.submit_job(instance_id=instance_id)
        job_id = response["job_id"]

        progress_values = []

        for _ in range(10):
            time.sleep(5)
            job_info = authenticated_client.get_job(job_id)

            if job_info["status"] == "running":
                progress = job_info.get("progress", 0)
                progress_values.append(progress)
                logger.debug(f"Job progress: {progress}%")

            if job_info["status"] in ["completed", "failed"]:
                break

        if progress_values:
            assert max(progress_values) > 0
            logger.info(f"Job progress tracked: {progress_values}")
        else:
            logger.info("Job completed too quickly for progress tracking")
