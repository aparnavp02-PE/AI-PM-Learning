import os
import threading
from flask import Flask, request, jsonify
from slack_sdk import WebClient
from slack_sdk.signature import SignatureVerifier
from dotenv import load_dotenv
from .auditor import audit_image
from .slack_handler import download_file, post_audit_report

load_dotenv()

app = Flask(__name__)
slack_client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
verifier = SignatureVerifier(os.environ["SLACK_SIGNING_SECRET"])

SUPPORTED_MIME_TYPES = {"image/png", "image/jpeg", "image/jpg", "image/webp"}


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/slack/events", methods=["POST"])
def slack_events():
    if not verifier.is_valid_request(request.get_data(), request.headers):
        return jsonify({"error": "Invalid signature"}), 403

    payload = request.json

    # Respond to Slack's URL verification handshake
    if payload.get("type") == "url_verification":
        return jsonify({"challenge": payload["challenge"]})

    event = payload.get("event", {})

    # Only process user messages that contain image attachments
    if event.get("type") == "message" and not event.get("bot_id") and event.get("files"):
        thread = threading.Thread(target=_process_event, args=(event,), daemon=True)
        thread.start()

    # Always return 200 immediately so Slack doesn't retry
    return jsonify({"ok": True})


def _process_event(event: dict) -> None:
    channel = event["channel"]
    thread_ts = event.get("thread_ts", event["ts"])
    context = event.get("text", "")

    for file_info in event.get("files", []):
        if file_info.get("mimetype") not in SUPPORTED_MIME_TYPES:
            continue

        image_data = download_file(slack_client, file_info["url_private"])
        if not image_data:
            continue

        report = audit_image(image_data, context)
        post_audit_report(slack_client, channel, thread_ts, report)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port, debug=False)
