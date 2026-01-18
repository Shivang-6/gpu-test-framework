#!/usr/bin/env python
"""Verify that the test framework is properly set up"""
import sys
from pathlib import Path


def check_python():
    version = sys.version_info
    if version.major == 3 and version.minor >= 9:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} is supported")
        return True
    print(f"❌ Python 3.9+ required, found {version.major}.{version.minor}")
    return False


def check_dependencies():
    required = [
        "pytest",
        "playwright",
        "requests",
        "fastapi",
        "locust",
        "pydantic",
        "allure-pytest",
    ]

    all_installed = True
    for package in required:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is NOT installed")
            all_installed = False

    return all_installed


def check_directories():
    required_dirs = [
        "config",
        "core",
        "tests/api",
        "tests/ui/pages",
        "tests/performance",
        "utils",
        "reports",
    ]

    all_exist = True
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"✅ Directory {dir_path} exists")
        else:
            print(f"❌ Directory {dir_path} is missing")
            all_exist = False

    return all_exist


def check_files():
    required_files = [
        "requirements.txt",
        "pytest.ini",
        "mock_gpuas_simulator.py",
        "core/api_client.py",
        "tests/api/test_auth.py",
        "tests/ui/test_workflow.py",
        "README.md",
    ]

    all_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ File {file_path} exists")
        else:
            print(f"❌ File {file_path} is missing")
            all_exist = False

    return all_exist


def main():
    print("🔍 Verifying GPUaaS Test Framework Setup")
    print("=" * 50)

    checks = [
        ("Python Version", check_python),
        ("Dependencies", check_dependencies),
        ("Directory Structure", check_directories),
        ("Required Files", check_files),
    ]

    results = []
    for check_name, check_func in checks:
        print(f"\n📋 {check_name}:")
        results.append((check_name, check_func()))

    print("\n" + "=" * 50)
    print("📊 Verification Summary:")

    all_passed = True
    for check_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {check_name}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\n🎉 All checks passed! The framework is ready to use.")
        print("\nNext steps:")
        print("1. Install Playwright browsers: playwright install chromium")
        print("2. Start mock server: python mock_gpuas_simulator.py")
        print("3. Run tests: pytest tests/api/ -v")
    else:
        print("\n⚠️ Some checks failed. Please fix the issues above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
