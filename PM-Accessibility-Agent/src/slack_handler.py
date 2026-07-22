import requests
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

REPORT_FOOTER = (
    "\n\n_Note: This is an AI-assisted check. "
    "Use the Stark plugin or Figma's built-in accessibility checker for pixel-perfect verification._"
)


def download_file(client: WebClient, url: str) -> bytes | None:
    response = requests.get(
        url,
        headers={"Authorization": f"Bearer {client.token}"},
        timeout=30,
    )
    if response.status_code == 200:
        return response.content
    return None


def post_audit_report(client: WebClient, channel: str, thread_ts: str, report: str) -> None:
    message = f"*Accessibility Audit Report*\n\n{report}{REPORT_FOOTER}"
    try:
        client.chat_postMessage(
            channel=channel,
            thread_ts=thread_ts,
            text=message,
            mrkdwn=True,
        )
    except SlackApiError as e:
        print(f"Slack post failed: {e.response['error']}")
