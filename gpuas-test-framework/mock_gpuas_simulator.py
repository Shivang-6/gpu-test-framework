"""
Mock GPUaaS Platform Server
Simulates key GPU-as-a-Service functionality for testing
"""
import asyncio
import logging
import random
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import BackgroundTasks, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LoginRequest(BaseModel):
    username: str
    password: str


class GPUInstanceRequest(BaseModel):
    gpu_type: str = Field(default="A100", regex="^(A100|H100|V100|RTX4090)$")
    count: int = Field(default=1, ge=1, le=8)
    region: str = Field(default="us-east-1")
    instance_name: Optional[str] = None


class JobRequest(BaseModel):
    instance_id: str
    job_type: str = Field(default="training", regex="^(training|inference|fine-tuning)$")
    script_path: str
    parameters: Dict = Field(default_factory=dict)


class MetricsRequest(BaseModel):
    start_time: datetime
    end_time: datetime
    metric_type: str = Field(regex="^(gpu_utilization|memory_usage|power_draw)$")


app = FastAPI(
    title="Mock GPUaaS Platform API",
    description="Mock server simulating GPU-as-a-Service functionality",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class MockDatabase:
    def __init__(self):
        self.users = {
            "test_user": {
                "password": "test_pass",
                "user_id": "usr_001",
                "token": "mock_token_test_user",
                "plan": "premium",
                "gpu_quota": 16,
            }
        }
        self.instances: Dict[str, dict] = {}
        self.jobs: Dict[str, dict] = {}
        self.metrics: List[dict] = []
        self.billing_records: List[dict] = []

        self._initialize_mock_data()

    def _initialize_mock_data(self):
        for i in range(3):
            instance_id = f"inst_{1000 + i}"
            self.instances[instance_id] = {
                "id": instance_id,
                "user_id": "usr_001",
                "gpu_type": random.choice(["A100", "H100", "V100"]),
                "count": random.randint(1, 4),
                "status": "active",
                "region": random.choice(["us-east-1", "eu-west-1"]),
                "created_at": time.time() - random.randint(3600, 86400),
                "ip_address": f"10.0.{random.randint(1,255)}.{random.randint(1,255)}",
                "hourly_rate": random.uniform(2.5, 8.5),
            }

            for j in range(random.randint(1, 3)):
                job_id = f"job_{10000 + i * 3 + j}"
                self.jobs[job_id] = {
                    "id": job_id,
                    "instance_id": instance_id,
                    "user_id": "usr_001",
                    "job_type": random.choice(["training", "inference"]),
                    "status": random.choice(["completed", "running", "failed"]),
                    "submitted_at": time.time() - random.randint(600, 7200),
                    "duration": random.randint(300, 3600),
                    "gpu_utilization": random.uniform(30, 95),
                }

    def generate_metrics(self, instance_id: str):
        return {
            "timestamp": datetime.now().isoformat(),
            "instance_id": instance_id,
            "gpu_utilization": random.uniform(10, 99),
            "memory_used_mb": random.randint(1024, 4096),
            "memory_total_mb": 4096,
            "power_draw_w": random.uniform(250, 400),
            "temperature_c": random.uniform(40, 85),
        }


db = MockDatabase()


async def simulate_provisioning(instance_id: str):
    await asyncio.sleep(random.uniform(3, 8))
    if instance_id in db.instances:
        db.instances[instance_id]["status"] = "active"
        logger.info(f"Instance {instance_id} provisioned successfully")


async def simulate_job_execution(job_id: str):
    job = db.jobs.get(job_id)
    if not job:
        return

    states = ["queued", "initializing", "running", "completing"]

    for state in states:
        job["status"] = state
        await asyncio.sleep(random.uniform(2, 5))

    job["status"] = "completed" if random.random() > 0.1 else "failed"
    job["completed_at"] = time.time()

    if job["status"] == "completed":
        job["results"] = {
            "accuracy": random.uniform(0.85, 0.99),
            "loss": random.uniform(0.01, 0.2),
            "training_time": random.randint(300, 1800),
        }

    logger.info(f"Job {job_id} finished with status: {job['status']}")


@app.post("/api/v1/auth/login", status_code=status.HTTP_200_OK)
async def login(credentials: LoginRequest):
    user = db.users.get(credentials.username)

    if not user or user["password"] != credentials.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    logger.info(f"User {credentials.username} logged in")
    return {
        "access_token": user["token"],
        "token_type": "bearer",
        "user_id": user["user_id"],
        "plan": user["plan"],
        "gpu_quota": user["gpu_quota"],
    }


@app.get("/api/v1/auth/verify")
async def verify_token(token: str):
    for user in db.users.values():
        if user["token"] == token:
            return {"valid": True, "user_id": user["user_id"]}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token",
    )


@app.post("/api/v1/gpu/instances", status_code=status.HTTP_202_ACCEPTED)
async def create_gpu_instance(
    request: GPUInstanceRequest,
    background_tasks: BackgroundTasks,
    token: str = "mock_token_test_user",
):
    auth_result = await verify_token(token)
    user_id = auth_result["user_id"]

    user_instances = [i for i in db.instances.values() if i["user_id"] == user_id]
    total_gpus = sum(i["count"] for i in user_instances)

    if total_gpus + request.count > db.users[user_id]["gpu_quota"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Exceeds GPU quota. Available: {db.users[user_id]['gpu_quota'] - total_gpus}",
        )

    instance_id = f"inst_{uuid.uuid4().hex[:8]}"

    db.instances[instance_id] = {
        "id": instance_id,
        "user_id": user_id,
        "gpu_type": request.gpu_type,
        "count": request.count,
        "status": "provisioning",
        "region": request.region,
        "instance_name": request.instance_name or f"{request.gpu_type}-instance",
        "created_at": time.time(),
        "ip_address": None,
        "hourly_rate": 3.50 if request.gpu_type == "A100" else 4.50,
    }

    background_tasks.add_task(simulate_provisioning, instance_id)

    logger.info(f"Creating GPU instance {instance_id}: {request.gpu_type} x{request.count}")

    return {
        "instance_id": instance_id,
        "status": "provisioning",
        "message": "Instance is being provisioned",
        "estimated_completion": "30 seconds",
    }


@app.get("/api/v1/gpu/instances")
async def list_instances(
    token: str = "mock_token_test_user",
    status_filter: Optional[str] = None,
    region: Optional[str] = None,
):
    auth_result = await verify_token(token)
    user_id = auth_result["user_id"]

    instances = [i for i in db.instances.values() if i["user_id"] == user_id]

    if status_filter:
        instances = [i for i in instances if i["status"] == status_filter]
    if region:
        instances = [i for i in instances if i["region"] == region]

    return {
        "count": len(instances),
        "instances": instances,
        "total_gpus": sum(i["count"] for i in instances),
    }


@app.get("/api/v1/gpu/instances/{instance_id}")
async def get_instance(instance_id: str, token: str = "mock_token_test_user"):
    auth_result = await verify_token(token)
    user_id = auth_result["user_id"]

    instance = db.instances.get(instance_id)

    if not instance or instance["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instance not found or access denied",
        )

    metrics = db.generate_metrics(instance_id)

    return {
        **instance,
        "current_metrics": metrics,
        "uptime": time.time() - instance["created_at"] if instance["created_at"] else 0,
    }


@app.post("/api/v1/jobs", status_code=status.HTTP_201_CREATED)
async def submit_job(
    request: JobRequest,
    background_tasks: BackgroundTasks,
    token: str = "mock_token_test_user",
):
    auth_result = await verify_token(token)
    user_id = auth_result["user_id"]

    instance = db.instances.get(request.instance_id)
    if not instance or instance["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instance not found or access denied",
        )

    if instance["status"] != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Instance is not active. Current status: {instance['status']}",
        )

    job_id = f"job_{uuid.uuid4().hex[:8]}"

    db.jobs[job_id] = {
        "id": job_id,
        "instance_id": request.instance_id,
        "user_id": user_id,
        "job_type": request.job_type,
        "script_path": request.script_path,
        "parameters": request.parameters,
        "status": "queued",
        "submitted_at": time.time(),
        "duration": 0,
        "gpu_utilization": 0,
        "progress": 0,
    }

    background_tasks.add_task(simulate_job_execution, job_id)

    logger.info(f"Job {job_id} submitted to instance {request.instance_id}")

    return {
        "job_id": job_id,
        "status": "queued",
        "message": "Job submitted successfully",
        "estimated_start": "10 seconds",
    }


@app.get("/api/v1/jobs/{job_id}")
async def get_job(job_id: str, token: str = "mock_token_test_user"):
    auth_result = await verify_token(token)
    user_id = auth_result["user_id"]

    job = db.jobs.get(job_id)

    if not job or job["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found or access denied",
        )

    if job["status"] == "running":
        elapsed = time.time() - job["submitted_at"]
        job["progress"] = min(95, (elapsed / 30) * 100)

    return job


@app.get("/api/v1/metrics")
async def get_metrics(
    instance_id: Optional[str] = None,
    metric_type: Optional[str] = None,
    minutes: int = 30,
):
    metrics = []
    target_instances = [instance_id] if instance_id else list(db.instances.keys())

    for inst_id in target_instances:
        if inst_id in db.instances:
            for _ in range(10):
                metric = db.generate_metrics(inst_id)
                if metric_type and metric_type not in metric:
                    continue
                metrics.append(metric)
                db.metrics.append(metric)

    return {
        "count": len(metrics),
        "metrics": metrics[-100:],
        "time_range": f"last {minutes} minutes",
    }


@app.delete("/api/v1/gpu/instances/{instance_id}")
async def delete_instance(
    instance_id: str,
    token: str = "mock_token_test_user",
):
    auth_result = await verify_token(token)
    user_id = auth_result["user_id"]

    instance = db.instances.get(instance_id)

    if not instance or instance["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instance not found or access denied",
        )

    running_jobs = [
        j for j in db.jobs.values()
        if j["instance_id"] == instance_id and j["status"] in ["running", "queued"]
    ]

    if running_jobs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete instance with running jobs. Stop jobs first.",
        )

    instance["status"] = "terminating"

    await asyncio.sleep(2)

    del db.instances[instance_id]

    logger.info(f"Instance {instance_id} terminated")

    return {
        "message": "Instance terminated successfully",
        "instance_id": instance_id,
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "mock-gpuas-server",
        "version": "1.0.0",
        "statistics": {
            "users": len(db.users),
            "instances": len(db.instances),
            "jobs": len(db.jobs),
            "metrics": len(db.metrics),
        },
    }


@app.get("/")
async def root():
    return {
        "message": "Mock GPUaaS Platform API",
        "version": "1.0.0",
        "documentation": "/docs",
        "endpoints": {
            "auth": ["POST /api/v1/auth/login", "GET /api/v1/auth/verify"],
            "instances": [
                "POST /api/v1/gpu/instances",
                "GET /api/v1/gpu/instances",
                "GET /api/v1/gpu/instances/{id}",
                "DELETE /api/v1/gpu/instances/{id}",
            ],
            "jobs": ["POST /api/v1/jobs", "GET /api/v1/jobs/{id}"],
            "metrics": ["GET /api/v1/metrics"],
            "health": ["GET /health"],
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
