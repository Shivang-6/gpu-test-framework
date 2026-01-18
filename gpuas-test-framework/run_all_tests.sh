#!/bin/bash

echo "🚀 GPUaaS Test Automation Framework - Complete Test Suite"
echo "======================================================"
echo ""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${2}${1}${NC}"
}

check_success() {
    if [ $? -eq 0 ]; then
        print_status "✓ $1" "$GREEN"
    else
        print_status "✗ $1" "$RED"
        FAILED=true
    fi
}

FAILED=false

print_status "Step 1: Checking prerequisites..." "$YELLOW"
python --version
pip --version
playwright --version
echo ""

print_status "Step 2: Installing dependencies..." "$YELLOW"
pip install -r requirements.txt
check_success "Dependencies installed"
echo ""

print_status "Step 3: Starting mock GPUaaS server..." "$YELLOW"
python mock_gpuas_simulator.py &
SERVER_PID=$!
sleep 10

curl -s http://localhost:8000/health > /dev/null
if [ $? -eq 0 ]; then
    print_status "Mock server is running at http://localhost:8000" "$GREEN"
else
    print_status "Failed to start mock server" "$RED"
    kill $SERVER_PID 2>/dev/null
    exit 1
fi
echo ""

print_status "Step 4: Running API tests..." "$YELLOW"
pytest tests/api/ -v \
    --html=reports/api-report.html \
    --junitxml=reports/api-results.xml \
    --cov=core \
    --cov-report=html:reports/coverage-api
check_success "API tests completed"
echo ""

print_status "Step 5: Running UI tests..." "$YELLOW"
pytest tests/ui/ -v \
    --html=reports/ui-report.html \
    --junitxml=reports/ui-results.xml
check_success "UI tests completed"
echo ""

print_status "Step 6: Running performance tests..." "$YELLOW"
locust -f tests/performance/test_load.py \
    --host=http://localhost:8000 \
    --users=5 \
    --spawn-rate=1 \
    --run-time=30s \
    --headless \
    --csv=reports/performance \
    --html=reports/performance-report.html
check_success "Performance tests completed"
echo ""

print_status "Step 7: Stopping mock server..." "$YELLOW"
kill $SERVER_PID 2>/dev/null
print_status "Mock server stopped" "$GREEN"
echo ""

print_status "Step 8: Generating test summary..." "$YELLOW"
echo "📊 Test Results Summary" > reports/summary.txt
echo "======================" >> reports/summary.txt
echo "" >> reports/summary.txt

if [ -f reports/api-results.xml ]; then
    API_TESTS=$(grep -o 'tests="[0-9]*"' reports/api-results.xml | head -1 | grep -o '[0-9]*' || echo "0")
    API_FAILURES=$(grep -o 'failures="[0-9]*"' reports/api-results.xml | head -1 | grep -o '[0-9]*' || echo "0")
    echo "API Tests: $API_TESTS total, $API_FAILURES failures" >> reports/summary.txt
fi

if [ -f reports/ui-results.xml ]; then
    UI_TESTS=$(grep -o 'tests="[0-9]*"' reports/ui-results.xml | head -1 | grep -o '[0-9]*' || echo "0")
    UI_FAILURES=$(grep -o 'failures="[0-9]*"' reports/ui-results.xml | head -1 | grep -o '[0-9]*' || echo "0")
    echo "UI Tests: $UI_TESTS total, $UI_FAILURES failures" >> reports/summary.txt
fi

echo "" >> reports/summary.txt
echo "📁 Reports generated in 'reports/' directory:" >> reports/summary.txt
echo "- API Report: reports/api-report.html" >> reports/summary.txt
echo "- UI Report: reports/ui-report.html" >> reports/summary.txt
echo "- Performance Report: reports/performance-report.html" >> reports/summary.txt
echo "- Coverage Report: reports/coverage-api/index.html" >> reports/summary.txt

cat reports/summary.txt
echo ""

print_status "Step 9: Final status..." "$YELLOW"
if [ "$FAILED" = true ]; then
    print_status "❌ Some tests failed. Check the reports for details." "$RED"
    exit 1
else
    print_status "✅ All tests completed successfully!" "$GREEN"
    echo ""
    print_status "📁 View reports:" "$GREEN"
    echo "  - Open reports/api-report.html for API test results"
    echo "  - Open reports/ui-report.html for UI test results"
    echo "  - Open reports/performance-report.html for performance results"
    echo "  - Open reports/coverage-api/index.html for code coverage"
fi
