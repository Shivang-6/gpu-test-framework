import json
from typing import Dict, Any, Optional

import requests
from config.settings import settings
from utils.logger import logger


class APIError(Exception):
    """Custom exception for API errors"""


class GPUaaSClient:
    """Client for interacting with GPUaaS API"""

    def __init__(self, base_url: str = None):
        self.base_url = base_url or settings.BASE_URL
        self.session = requests.Session()
        self.token = None
        self.user_id = None

        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })

    def login(self, username: str = None, password: str = None) -> Dict:
        """Authenticate with the platform"""
        username = username or settings.TEST_USER
        password = password or settings.TEST_PASSWORD

        url = f"{self.base_url}/api/v1/auth/login"
        payload = {"username": username, "password": password}

        logger.info(f"Logging in as {username}")

        try:
            response = self.session.post(url, json=payload)
            response.raise_for_status()

            data = response.json()
            self.token = data["access_token"]
            self.user_id = data["user_id"]

            self.session.headers.update({
                "Authorization": f"Bearer {self.token}"
            })

            logger.info(f"Login successful. User ID: {self.user_id}")
            return data

        except requests.exceptions.RequestException as exc:
            logger.error(f"Login failed: {exc}")
            raise APIError(f"Authentication failed: {exc}") from exc

    def verify_token(self) -> bool:
        """Verify the current authentication token"""
        if not self.token:
            return False

        url = f"{self.base_url}/api/v1/auth/verify"
        params = {"token": self.token}

        try:
            response = self.session.get(url, params=params)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def create_gpu_instance(self, **kwargs) -> Dict:
        """Create a new GPU instance"""
        url = f"{self.base_url}/api/v1/gpu/instances"

        data = {
            "gpu_type": "A100",
            "count": 1,
            "region": "us-east-1",
            **kwargs
        }

        logger.info(f"Creating GPU instance: {data}")

        try:
            response = self.session.post(url, json=data)
            response.raise_for_status()

            result = response.json()
            logger.info(f"Instance creation initiated: {result.get('instance_id')}")
            return result

        except requests.exceptions.RequestException as exc:
            logger.error(f"Failed to create instance: {exc}")
            if 'response' in locals() and response is not None and response.status_code == 400:
                error_detail = response.json().get('detail', str(exc))
                raise APIError(f"Bad request: {error_detail}") from exc
            raise APIError(f"Instance creation failed: {exc}") from exc

    def get_instance(self, instance_id: str) -> Dict:
        """Get details of a specific GPU instance"""
        url = f"{self.base_url}/api/v1/gpu/instances/{instance_id}"

        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as exc:
            logger.error(f"Failed to get instance {instance_id}: {exc}")
            raise APIError(f"Failed to get instance: {exc}") from exc

    def list_instances(self, **filters) -> Dict:
        """List all GPU instances with optional filters"""
        url = f"{self.base_url}/api/v1/gpu/instances"

        try:
            response = self.session.get(url, params=filters)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as exc:
            logger.error(f"Failed to list instances: {exc}")
            raise APIError(f"Failed to list instances: {exc}") from exc

    def submit_job(self, instance_id: str, **kwargs) -> Dict:
        """Submit a job to a GPU instance"""
        url = f"{self.base_url}/api/v1/jobs"

        data = {
            "instance_id": instance_id,
            "job_type": "training",
            "script_path": "/scripts/train.py",
            "parameters": {"epochs": 10, "batch_size": 32},
            **kwargs
        }

        logger.info(f"Submitting job to instance {instance_id}")

        try:
            response = self.session.post(url, json=data)
            response.raise_for_status()

            result = response.json()
            logger.info(f"Job submitted: {result.get('job_id')}")
            return result

        except requests.exceptions.RequestException as exc:
            logger.error(f"Failed to submit job: {exc}")
            raise APIError(f"Job submission failed: {exc}") from exc

    def get_job(self, job_id: str) -> Dict:
        """Get job status and details"""
        url = f"{self.base_url}/api/v1/jobs/{job_id}"

        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as exc:
            logger.error(f"Failed to get job {job_id}: {exc}")
            raise APIError(f"Failed to get job: {exc}") from exc

    def get_metrics(self, **filters) -> Dict:
        """Get metrics data"""
        url = f"{self.base_url}/api/v1/metrics"

        try:
            response = self.session.get(url, params=filters)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as exc:
            logger.error(f"Failed to get metrics: {exc}")
            raise APIError(f"Failed to get metrics: {exc}") from exc

    def delete_instance(self, instance_id: str) -> Dict:
        """Delete/terminate a GPU instance"""
        url = f"{self.base_url}/api/v1/gpu/instances/{instance_id}"

        logger.info(f"Deleting instance {instance_id}")

        try:
            response = self.session.delete(url)
            response.raise_for_status()

            result = response.json()
            logger.info(f"Instance deletion initiated: {result}")
            return result

        except requests.exceptions.RequestException as exc:
            logger.error(f"Failed to delete instance: {exc}")
            raise APIError(f"Instance deletion failed: {exc}") from exc

    def health_check(self) -> Dict:
        """Check API health"""
        url = f"{self.base_url}/health"

        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as exc:
            logger.error(f"Health check failed: {exc}")
            raise APIError(f"Health check failed: {exc}") from exc
