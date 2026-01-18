import time
import json
from locust import HttpUser, task, between, events
from locust.runners import MasterRunner, WorkerRunner
from utils.logger import logger


@events.init.add_listener
def on_locust_init(environment, **kwargs):
    if isinstance(environment.runner, MasterRunner):
        logger.info("Initializing master node for performance tests")
    elif isinstance(environment.runner, WorkerRunner):
        logger.info("Initializing worker node for performance tests")
    else:
        logger.info("Initializing standalone node for performance tests")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    logger.info("Performance test starting...")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    logger.info("Performance test completed")


class GPUaaSUser(HttpUser):
    """Simulated user for GPUaaS performance testing."""

    wait_time = between(1, 3)

    auth_token = None
    user_id = None
    instances = []
    jobs = []

    def on_start(self):
        self.login()

    def login(self):
        try:
            response = self.client.post("/api/v1/auth/login", json={
                "username": "test_user",
                "password": "test_pass",
            })

            if response.status_code == 200:
                data = response.json()
                self.auth_token = data["access_token"]
                self.user_id = data["user_id"]

                self.client.headers.update({
                    "Authorization": f"Bearer {self.auth_token}",
                })

                logger.debug(f"User logged in: {self.user_id}")
                return True
            logger.error(f"Login failed: {response.status_code}")
            return False

        except Exception as exc:
            logger.error(f"Login exception: {exc}")
            return False

    @task(5)
    def check_platform_health(self):
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    response.success()
                else:
                    response.failure(f"Health check failed: {data}")
            else:
                response.failure(f"Health check HTTP error: {response.status_code}")

    @task(3)
    def list_gpu_instances(self):
        with self.client.get("/api/v1/gpu/instances", catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if "instances" in data:
                    response.success()
                else:
                    response.failure("Invalid response format")
            else:
                response.failure(f"List instances failed: {response.status_code}")

    @task(2)
    def view_instance_details(self):
        if not self.instances:
            self.create_gpu_instance()
            time.sleep(5)

        if self.instances:
            instance_id = self.instances[0]
            with self.client.get(f"/api/v1/gpu/instances/{instance_id}", catch_response=True) as response:
                if response.status_code == 200:
                    data = response.json()
                    if "id" in data and data["id"] == instance_id:
                        response.success()
                    else:
                        response.failure("Instance details mismatch")
                else:
                    response.failure(f"Get instance failed: {response.status_code}")

    @task(1)
    def create_gpu_instance(self):
        gpu_types = ["A100", "H100", "V100"]
        gpu_type = self.environment.runner.weighted_choice(gpu_types)

        payload = {
            "gpu_type": gpu_type,
            "count": 1,
            "region": "us-east-1",
            "instance_name": f"load-test-{int(time.time())}",
        }

        with self.client.post("/api/v1/gpu/instances", json=payload, catch_response=True) as response:
            if response.status_code == 202:
                data = response.json()
                instance_id = data.get("instance_id")
                if instance_id:
                    self.instances.append(instance_id)
                    if len(self.instances) > 5:
                        self.instances.pop(0)
                    response.success()
                    logger.debug(f"Instance created: {instance_id}")
                else:
                    response.failure("No instance_id in response")
            else:
                response.failure(f"Create instance failed: {response.status_code}")

    @task(1)
    def submit_job(self):
        if not self.instances:
            return

        instance_id = self.instances[0]

        payload = {
            "instance_id": instance_id,
            "job_type": "training",
            "script_path": "/scripts/load_test.py",
            "parameters": {
                "epochs": 5,
                "batch_size": 16,
                "test_run": True,
            },
        }

        with self.client.post("/api/v1/jobs", json=payload, catch_response=True) as response:
            if response.status_code == 201:
                data = response.json()
                job_id = data.get("job_id")
                if job_id:
                    self.jobs.append(job_id)
                    if len(self.jobs) > 10:
                        self.jobs.pop(0)
                    response.success()
                    logger.debug(f"Job submitted: {job_id}")
                else:
                    response.failure("No job_id in response")
            else:
                response.failure(f"Submit job failed: {response.status_code}")

    @task(2)
    def check_job_status(self):
        if not self.jobs:
            return

        job_id = self.jobs[0]

        with self.client.get(f"/api/v1/jobs/{job_id}", catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("id") == job_id:
                    response.success()
                else:
                    response.failure("Job ID mismatch")
            else:
                response.failure(f"Check job failed: {response.status_code}")

    @task(1)
    def get_metrics(self):
        with self.client.get("/api/v1/metrics", params={"minutes": 15}, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if "metrics" in data:
                    response.success()
                else:
                    response.failure("No metrics in response")
            else:
                response.failure(f"Get metrics failed: {response.status_code}")

    @task(1)
    def simulate_user_workflow(self):
        self.client.get("/api/v1/gpu/instances")

        create_response = self.client.post("/api/v1/gpu/instances", json={
            "gpu_type": "A100",
            "count": 1,
            "region": "us-east-1",
        })

        if create_response.status_code == 202:
            instance_id = create_response.json().get("instance_id")

            time.sleep(2)

            self.client.get(f"/api/v1/gpu/instances/{instance_id}")

            self.client.post("/api/v1/jobs", json={
                "instance_id": instance_id,
                "job_type": "inference",
                "script_path": "/scripts/workflow_test.py",
            })

            self.client.delete(f"/api/v1/gpu/instances/{instance_id}")


class HeavyUser(GPUaaSUser):
    wait_time = between(0.5, 1.5)
    weight = 3


class APIOnlyUser(HttpUser):
    wait_time = between(0.1, 0.5)

    @task(10)
    def rapid_api_calls(self):
        endpoints = [
            "/health",
            "/api/v1/gpu/instances",
            "/api/v1/metrics?minutes=5",
        ]

        for endpoint in endpoints:
            self.client.get(endpoint)
