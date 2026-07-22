import pytest
from unittest.mock import MagicMock, patch


MOCK_PASS_RESPONSE = "✅ Passed WCAG AA Check — no violations detected."

MOCK_FAIL_RESPONSE = """**Color Contrast Issues:**
- Body text appears light gray on white background. Estimated ratio is below 4.5:1.
  - **WCAG 1.4.3 Contrast Minimum** — Change text color from #CCCCCC to #767676 to achieve 4.5:1 ratio.

**Touch Target Issues:**
- The search icon button appears to be smaller than 44×44px.
  - **WCAG 2.5.5 Target Size** — Expand the tap area to at least 44×44px."""


@pytest.fixture
def mock_openai_pass():
    with patch("src.auditor.client") as mock_client:
        mock_response = MagicMock()
        mock_response.choices[0].message.content = MOCK_PASS_RESPONSE
        mock_client.chat.completions.create.return_value = mock_response
        yield mock_client


@pytest.fixture
def mock_openai_fail():
    with patch("src.auditor.client") as mock_client:
        mock_response = MagicMock()
        mock_response.choices[0].message.content = MOCK_FAIL_RESPONSE
        mock_client.chat.completions.create.return_value = mock_response
        yield mock_client


class TestAuditImage:
    def test_returns_pass_when_no_violations(self, mock_openai_pass):
        from src.auditor import audit_image
        result = audit_image(b"fake_image_bytes")
        assert "Passed WCAG AA Check" in result

    def test_returns_violations_when_issues_found(self, mock_openai_fail):
        from src.auditor import audit_image
        result = audit_image(b"fake_image_bytes")
        assert "WCAG 1.4.3" in result
        assert "WCAG 2.5.5" in result

    def test_includes_context_when_provided(self, mock_openai_fail):
        from src.auditor import audit_image
        audit_image(b"fake_image_bytes", context="This is a mobile login screen")
        call_args = mock_openai_fail.chat.completions.create.call_args
        user_content = call_args.kwargs["messages"][1]["content"]
        text_block = next(c for c in user_content if c["type"] == "text")
        assert "mobile login screen" in text_block["text"]

    def test_uses_gpt4o_model(self, mock_openai_pass):
        from src.auditor import audit_image
        audit_image(b"fake_image_bytes")
        call_args = mock_openai_pass.chat.completions.create.call_args
        assert call_args.kwargs["model"] == "gpt-4o"

    def test_uses_high_detail_vision(self, mock_openai_pass):
        from src.auditor import audit_image
        audit_image(b"fake_image_bytes")
        call_args = mock_openai_pass.chat.completions.create.call_args
        user_content = call_args.kwargs["messages"][1]["content"]
        image_block = next(c for c in user_content if c["type"] == "image_url")
        assert image_block["image_url"]["detail"] == "high"

    def test_uses_low_temperature(self, mock_openai_pass):
        from src.auditor import audit_image
        audit_image(b"fake_image_bytes")
        call_args = mock_openai_pass.chat.completions.create.call_args
        assert call_args.kwargs["temperature"] <= 0.2

    def test_context_is_optional(self, mock_openai_pass):
        from src.auditor import audit_image
        result = audit_image(b"fake_image_bytes")
        assert result is not None


class TestSlackHandler:
    def test_download_file_success(self):
        from src.slack_handler import download_file
        mock_client = MagicMock()
        mock_client.token = "xoxb-test-token"

        with patch("src.slack_handler.requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.content = b"image_bytes"
            result = download_file(mock_client, "https://example.com/file.png")

        assert result == b"image_bytes"
        mock_get.assert_called_once()
        headers = mock_get.call_args.kwargs["headers"]
        assert "Bearer xoxb-test-token" in headers["Authorization"]

    def test_download_file_returns_none_on_failure(self):
        from src.slack_handler import download_file
        mock_client = MagicMock()
        mock_client.token = "xoxb-test-token"

        with patch("src.slack_handler.requests.get") as mock_get:
            mock_get.return_value.status_code = 403
            result = download_file(mock_client, "https://example.com/file.png")

        assert result is None

    def test_post_audit_report_sends_to_thread(self):
        from src.slack_handler import post_audit_report
        mock_client = MagicMock()
        post_audit_report(mock_client, "C0123456", "1234567890.123456", "Test report")

        mock_client.chat_postMessage.assert_called_once()
        call_kwargs = mock_client.chat_postMessage.call_args.kwargs
        assert call_kwargs["channel"] == "C0123456"
        assert call_kwargs["thread_ts"] == "1234567890.123456"
        assert "Test report" in call_kwargs["text"]

    def test_post_audit_report_includes_footer(self):
        from src.slack_handler import post_audit_report
        mock_client = MagicMock()
        post_audit_report(mock_client, "C0123456", "1234567890.123456", "Test report")

        call_kwargs = mock_client.chat_postMessage.call_args.kwargs
        assert "AI-assisted check" in call_kwargs["text"]
