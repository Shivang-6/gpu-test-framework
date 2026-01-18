import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

import allure
from config.settings import settings
from utils.logger import logger


class TestReporter:
    """Test reporting utilities with Allure integration"""

    @staticmethod
    def attach_screenshot(page, name: str = "screenshot"):
        """Attach screenshot to Allure report."""
        try:
            screenshot = page.screenshot()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{name}_{timestamp}.png"

            allure.attach(
                screenshot,
                name=filename,
                attachment_type=allure.attachment_type.PNG
            )

            screenshot_path = settings.SCREENSHOT_DIR / filename
            screenshot_path.write_bytes(screenshot)

            logger.debug(f"Screenshot saved: {screenshot_path}")

        except Exception as exc:
            logger.error(f"Failed to capture screenshot: {exc}")

    @staticmethod
    def attach_api_trace(request: Dict, response: Dict, name: str = "api_trace"):
        """Attach API request/response trace to Allure report."""
        try:
            trace_data = {
                "timestamp": datetime.now().isoformat(),
                "request": request,
                "response": response
            }

            allure.attach(
                json.dumps(trace_data, indent=2),
                name=name,
                attachment_type=allure.attachment_type.JSON
            )

        except Exception as exc:
            logger.error(f"Failed to attach API trace: {exc}")

    @staticmethod
    def attach_text(content: str, name: str = "text_attachment"):
        """Attach plain text to Allure report."""
        try:
            allure.attach(
                content,
                name=name,
                attachment_type=allure.attachment_type.TEXT
            )
        except Exception as exc:
            logger.error(f"Failed to attach text: {exc}")

    @staticmethod
    def attach_html(content: str, name: str = "html_attachment"):
        """Attach HTML content to Allure report."""
        try:
            allure.attach(
                content,
                name=name,
                attachment_type=allure.attachment_type.HTML
            )
        except Exception as exc:
            logger.error(f"Failed to attach HTML: {exc}")

    @staticmethod
    def attach_json(data: Dict, name: str = "json_data"):
        """Attach JSON data to Allure report."""
        try:
            allure.attach(
                json.dumps(data, indent=2),
                name=name,
                attachment_type=allure.attachment_type.JSON
            )
        except Exception as exc:
            logger.error(f"Failed to attach JSON: {exc}")

    @staticmethod
    def log_test_step(step: str, details: Optional[Dict] = None):
        """Log a test step to Allure report."""
        with allure.step(step):
            logger.info(f"Test Step: {step}")
            if details:
                logger.debug(f"Step Details: {details}")
                TestReporter.attach_json(details, f"step_{step.lower().replace(' ', '_')}")

    @staticmethod
    def generate_html_report(test_results: Dict):
        """Generate a simple HTML test report."""
        try:
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>GPUaaS Test Report</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .summary {{ background: #f5f5f5; padding: 20px; border-radius: 5px; }}
                    .test {{ border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }}
                    .passed {{ background: #d4edda; }}
                    .failed {{ background: #f8d7da; }}
                    .skipped {{ background: #fff3cd; }}
                    .timestamp {{ color: #666; font-size: 0.9em; }}
                </style>
            </head>
            <body>
                <h1>GPUaaS Platform Test Report</h1>
                <div class="summary">
                    <h2>Summary</h2>
                    <p>Total Tests: {test_results.get('total', 0)}</p>
                    <p>Passed: {test_results.get('passed', 0)}</p>
                    <p>Failed: {test_results.get('failed', 0)}</p>
                    <p>Skipped: {test_results.get('skipped', 0)}</p>
                    <p>Success Rate: {test_results.get('success_rate', 0)}%</p>
                    <p class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                <h2>Test Details</h2>
            """

            for test in test_results.get('tests', []):
                status_class = test.get('status', '').lower()
                html_content += f"""
                <div class="test {status_class}">
                    <h3>{test.get('name', 'Unknown Test')}</h3>
                    <p>Status: <strong>{test.get('status', 'UNKNOWN')}</strong></p>
                    <p>Duration: {test.get('duration', 0):.2f} seconds</p>
                    <p>Message: {test.get('message', '')}</p>
                </div>
                """

            html_content += """
            </body>
            </html>
            """

            report_file = settings.REPORT_DIR / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            report_file.write_text(html_content)

            logger.info(f"HTML report generated: {report_file}")

            return html_content

        except Exception as exc:
            logger.error(f"Failed to generate HTML report: {exc}")
            return None
