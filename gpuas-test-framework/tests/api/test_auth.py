import concurrent.futures
import pytest
from core.api_client import GPUaaSClient, APIError
from core.assertions import CustomAssertions
from core.reporting import TestReporter
from utils.logger import logger


class TestAuthentication:
    """Test authentication endpoints"""

    @pytest.fixture
    def client(self):
        return GPUaaSClient()

    @pytest.mark.smoke
    @pytest.mark.auth
    def test_successful_login(self, client):
        TestReporter.log_test_step("Test successful login")

        response = client.login()

        TestReporter.attach_json(response, "login_response")

        assert "access_token" in response
        assert response["access_token"] is not None
        assert response["token_type"] == "bearer"
        assert "user_id" in response

        logger.info(f"Login successful for user: {response.get('user_id')}")

    @pytest.mark.auth
    @pytest.mark.negative
    def test_invalid_credentials(self, client):
        TestReporter.log_test_step("Test invalid credentials")

        with pytest.raises(APIError) as exc_info:
            client.login(username="invalid_user", password="wrong_pass")

        error_message = str(exc_info.value)
        assert "Authentication failed" in error_message or "401" in error_message

        logger.info("Invalid credentials test passed - authentication correctly rejected")

    @pytest.mark.auth
    def test_token_verification(self, client):
        TestReporter.log_test_step("Test token verification")

        login_response = client.login()
        _ = login_response["access_token"]

        is_valid = client.verify_token()

        assert is_valid is True

        logger.info("Token verification successful")

    @pytest.mark.auth
    def test_concurrent_logins(self, client):
        TestReporter.log_test_step("Test concurrent logins")

        def single_login():
            temp_client = GPUaaSClient()
            return temp_client.login()

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(single_login) for _ in range(5)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]

        assert len(results) == 5
        for result in results:
            assert "access_token" in result

        logger.info(f"Concurrent logins successful: {len(results)} requests")
