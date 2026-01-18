# GPUaaS Test Automation Framework

A comprehensive test automation framework for GPU-as-a-Service (GPUaaS) platforms, built to demonstrate QA engineering skills for modern AI infrastructure.

## 🚀 Features

- **Multi-layered Testing**: API, UI, and Performance tests
- **Mock GPUaaS Server**: Complete simulation of GPU cloud platform
- **Modern Test Stack**: Playwright, Pytest, Locust, Allure
- **CI/CD Ready**: GitHub Actions with comprehensive reporting
- **Production-like Architecture**: Page Object Model, custom assertions, test factories
- **Professional Reporting**: HTML reports, screenshots, videos, traces

## 📋 Prerequisites

- Python 3.9+
- Node.js (for Playwright)
- Git

## 🛠️ Installation

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

## 🏃‍♂️ Quick Start

### 1. Start the Mock GPUaaS Server
```bash
python mock_gpuas_simulator.py
# Server runs at http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### 2. Run API Tests
```bash
pytest tests/api/ -v
```

### 3. Run UI Tests
```bash
pytest tests/ui/ -v
```

### 4. Run Performance Tests
```bash
locust -f tests/performance/test_load.py --host=http://localhost:8000
```

## 🗂️ Project Structure

```
gpuas-test-framework/
├── config/              # Configuration and test data
├── core/               # Core framework components
│   ├── api_client.py   # API client for GPUaaS
│   ├── assertions.py   # Custom assertions
│   ├── base_test.py    # Base test class
│   └── reporting.py    # Test reporting utilities
├── tests/
│   ├── api/           # API test suite
│   ├── ui/            # UI test suite (Playwright)
│   └── performance/   # Performance tests (Locust)
├── mock_gpuas_simulator.py  # Mock server
├── requirements.txt   # Python dependencies
├── pytest.ini        # Pytest configuration
├── docker-compose.yml # Docker setup
└── README.md         # This file
```

## 🧪 Test Scenarios Covered

### API Tests
- Authentication and authorization
- GPU instance provisioning (create, list, delete)
- Job submission and management
- Metrics collection and monitoring
- Error handling and edge cases

### UI Tests (Playwright)
- End-to-end user workflows
- Form validations and error states
- Dashboard interactions
- Responsive design testing
- Cross-browser compatibility

### Performance Tests (Locust)
- Load testing with concurrent users
- Stress testing API endpoints
- Performance benchmarking
- Scalability validation

## 📊 Reporting

The framework generates comprehensive reports:

1. **HTML Reports**: Pytest-html reports in `reports/` directory
2. **Allure Reports**: Rich interactive reports (enable with `--alluredir`)
3. **Video Recordings**: UI test recordings in `reports/videos/`
4. **Performance Metrics**: Locust CSV and HTML reports
5. **Coverage Reports**: Code coverage in HTML and XML formats

## 🔧 Configuration

Environment variables in `.env` file:

```bash
BASE_URL=http://localhost:8000
UI_URL=http://localhost:3000
TEST_USER=test_user
TEST_PASSWORD=test_pass
TEST_TIMEOUT=30
```

## 🐳 Docker Support

Run the entire stack with Docker:

```bash
# Build and run all services
docker-compose up --build

# Run only mock server
docker-compose up mock-server

# Run tests in container
docker-compose run tests
```

## 🤝 CI/CD Integration

The framework includes GitHub Actions workflow that:

1. Runs tests on multiple Python versions
2. Generates test reports and coverage
3. Uploads artifacts for review
4. Performs security scanning
5. Can deploy demo to cloud platforms

## 🎯 Demo Scenario

To see the framework in action:

```bash
# Terminal 1: Start mock server
python mock_gpuas_simulator.py

# Terminal 2: Run complete test suite
./run_all_tests.sh

# Terminal 3: View reports
open reports/pytest-report.html
```

## 📈 What This Demonstrates

This project showcases:

✅ **Test Architecture Design**: Scalable, maintainable framework  
✅ **Modern Tools**: Playwright, Pytest, Locust, Allure  
✅ **CI/CD Integration**: GitHub Actions with comprehensive reporting  
✅ **Domain Knowledge**: GPUaaS platform testing concepts  
✅ **Best Practices**: Page Object Model, custom assertions, test factories  
✅ **Professional Quality**: Documentation, error handling, logging  

## 🔮 Future Enhancements

1. **Real GPU Integration**: Test with actual NVIDIA GPUs
2. **Kubernetes Testing**: Test GPU orchestration in K8s
3. **Multi-cloud Testing**: Extend to AWS, Azure, GCP
4. **AI/ML Testing**: Specialized tests for training/inference workloads
5. **Security Testing**: OWASP ZAP integration

## 📝 License

MIT License

## 🤔 Need Help?

Create an issue in the GitHub repository or contact the maintainer.

---

**Built with ❤️ for modern QA engineering**
