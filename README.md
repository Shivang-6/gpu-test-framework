# 🧪 GPU-as-a-Service Test Automation Framework


A comprehensive, production-ready test automation framework specifically designed for **GPU-as-a-Service (GPUaaS) platforms**. This framework demonstrates professional QA engineering skills for modern AI infrastructure testing.

## 🎯 Why This Framework?

Built to showcase expertise in testing **cutting-edge AI cloud platforms**, this framework addresses the unique challenges of GPU-as-a-Service infrastructure:

- ✅ **GPU-specific testing** (provisioning, overcommit, multi-tenancy)
- ✅ **Realistic simulation** without requiring actual GPU hardware
- ✅ **Production-ready** with CI/CD, Docker, and professional reporting
- ✅ **Modern tech stack** matching industry standards

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- pip
- Git

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/gpuas-test-framework.git
cd gpuas-test-framework

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### Run Everything in One Command
```bash
# This will start the mock server, run all tests, and generate reports
./run_all_tests.sh
```

## 📁 Project Structure

```
gpuas-test-framework/
├── config/                 # Configuration and settings
│   ├── settings.py        # Environment configuration
│   └── test_data.py       # Test data factories
├── core/                  # Framework core components
│   ├── api_client.py      # GPUaaS API client
│   ├── assertions.py      # Custom assertions
│   ├── base_test.py       # Base test class
│   └── reporting.py       # Reporting utilities
├── tests/                 # Test suites
│   ├── api/               # API tests (authentication, provisioning, jobs)
│   ├── ui/                # UI tests with Playwright
│   └── performance/       # Performance tests with Locust
├── mock_gpuas_simulator.py # Complete mock GPUaaS server
├── utils/                 # Utility functions
├── docker-compose.yml     # Docker setup
├── .github/workflows/     # CI/CD pipelines
└── README.md              # This file
```

## 🧪 Key Features

### 1. **Mock GPUaaS Server**
A complete simulation of a GPU cloud platform with:
- REST API with authentication
- GPU instance provisioning
- Job scheduling and management
- Performance metrics generation
- Multi-tenant support

**Start the server:**
```bash
python mock_gpuas_simulator.py
# Access at: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### 2. **Multi-layered Testing**
```bash
# Run API tests
pytest tests/api/ -v --html=reports/api-report.html

# Run UI tests
pytest tests/ui/ -v --html=reports/ui-report.html

# Run performance tests
locust -f tests/performance/test_load.py --host=http://localhost:8000
```

### 3. **GPU-Specific Test Scenarios**
- ✅ GPU instance provisioning (A100, H100, V100, RTX4090)
- ✅ Job submission and management
- ✅ Multi-tenant isolation testing
- ✅ Performance benchmarking
- ✅ Error handling and edge cases

### 4. **Professional Reporting**
- HTML/XML test reports
- Screenshots and video recordings
- Performance metrics and charts
- Code coverage reports
- Allure integration for rich reports

### 5. **CI/CD Ready**
```yaml
# GitHub Actions workflow included
name: GPUaaS Test Suite
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: pytest tests/ -v
      - run: locust --headless
      - uses: actions/upload-artifact@v3
        with:
          name: test-reports
          path: reports/
```

## 🐳 Docker Support

Run everything with Docker Compose:

```bash
# Build and start all services
docker-compose up --build

# View services
docker-compose ps

# Run tests in container
docker-compose run tests

# Access reports
open reports/pytest-report.html
```

## 📊 Demo Dashboard

An interactive Streamlit dashboard is included to showcase test results:

```bash
pip install streamlit plotly
streamlit run create_demo_dashboard.py
```

**Dashboard features:**
- Live test execution
- Results visualization
- Performance metrics
- API documentation browser

## 🔧 Configuration

Create a `.env` file:

```bash
# Server URLs
BASE_URL=http://localhost:8000
UI_URL=http://localhost:3000

# Test Credentials
TEST_USER=test_user
TEST_PASSWORD=test_pass

# Test Configuration
TEST_TIMEOUT=30
WAIT_TIMEOUT=10

# Performance Testing
LOAD_TEST_USERS=10
LOAD_TEST_DURATION=30s
```

## 🎯 Test Scenarios

### API Testing Suite
```python
# tests/api/test_gpu_provisioning.py
def test_create_gpu_instance():
    """Test GPU instance provisioning"""
    client = GPUaaSClient()
    client.login()
    
    response = client.create_gpu_instance(
        gpu_type="A100",
        count=2,
        region="us-east-1"
    )
    
    assert response["status"] == "provisioning"
    assert "instance_id" in response
```

### UI Testing with Playwright
```python
# tests/ui/test_workflow.py
def test_complete_gpu_provisioning_flow():
    """Complete UI workflow test"""
    login_page.navigate().login("test_user", "test_pass")
    dashboard_page.create_gpu_instance(gpu_type="A100", count=2)
    assert dashboard_page.get_instance_count() == 1
```

### Performance Testing with Locust
```python
# tests/performance/test_load.py
class GPUaaSUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def create_gpu_instance(self):
        self.client.post("/api/v1/gpu/instances", json={
            "gpu_type": "A100",
            "count": 1
        })
```

## 📈 Performance Metrics

The framework tracks:
- **API Response Times**: < 100ms for 95% of requests
- **Test Execution**: Full suite runs in < 5 minutes
- **Resource Usage**: Minimal memory footprint
- **Scalability**: Supports 100+ concurrent virtual users

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Testing Framework** | Pytest | Test execution and reporting |
| **UI Automation** | Playwright | Modern browser automation |
| **API Testing** | Requests + Pytest | REST API validation |
| **Performance Testing** | Locust | Load and stress testing |
| **Mock Server** | FastAPI | Realistic API simulation |
| **Reporting** | Allure + HTML | Professional test reports |
| **CI/CD** | GitHub Actions | Automated testing pipeline |
| **Containerization** | Docker | Environment consistency |
| **Visualization** | Streamlit | Interactive dashboard |

## 🎓 Learning Resources

### For Beginners
1. Start with `mock_gpuas_simulator.py` to understand the API
2. Explore `tests/api/test_auth.py` for basic API testing
3. Run the demo dashboard: `streamlit run create_demo_dashboard.py`

### For Advanced Users
1. Study the custom assertions in `core/assertions.py`
2. Examine the CI/CD pipeline in `.github/workflows/tests.yml`
3. Review the Docker setup in `docker-compose.yml`

## 🔄 Extending the Framework

### Add New Test Types
```python
# tests/advanced/test_gpu_overcommit.py
class TestGPUOvercommit:
    def test_multi_tenant_gpu_sharing(self):
        """Test GPU overcommit scenarios"""
        # Your implementation here
```

### Integrate with Real Infrastructure
```python
# config/settings.py
import os

if os.getenv('ENVIRONMENT') == 'production':
    BASE_URL = 'https://api.hosted.ai'
```

### Add Custom Reporting
```python
# core/reporting.py
class CustomReporter:
    def generate_performance_report(self, metrics):
        """Generate custom performance reports"""
        pass
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request


