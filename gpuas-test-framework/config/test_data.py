import factory
from factory import Faker


class GPUInstanceFactory(factory.Factory):
    """Factory for creating GPU instance test data"""

    class Meta:
        model = dict

    gpu_type = Faker("random_element", elements=["A100", "H100", "V100", "RTX4090"])
    count = Faker("random_int", min=1, max=8)
    region = Faker("random_element", elements=["us-east-1", "eu-west-1", "ap-south-1"])

    @classmethod
    def create_training_instance(cls):
        """Create instance optimized for training workloads"""
        return cls.build(gpu_type="A100", count=4, region="us-east-1")

    @classmethod
    def create_inference_instance(cls):
        """Create instance optimized for inference workloads"""
        return cls.build(gpu_type="H100", count=2, region="ap-south-1")


class JobFactory(factory.Factory):
    """Factory for creating job test data"""

    class Meta:
        model = dict

    job_type = Faker("random_element", elements=["training", "inference", "fine-tuning"])
    duration = Faker("random_int", min=300, max=3600)  # 5 min to 1 hour
    dataset_size = Faker("random_int", min=100, max=10000)  # MB

    @classmethod
    def create_long_running_job(cls):
        """Create a long-running training job"""
        return cls.build(job_type="training", duration=7200, dataset_size=5000)
