import base64
from datetime import datetime, timezone

from crosscheck.config import parse_config

CONFIG = {
    "gmail": {"mailbox_address": "boss@gmail.com"},
    "team": {
        "domains": ["playground.co.mz"],
        "members": [{"email": "ana.silva@playground.co.mz", "name": "Ana Silva"}],
        "manager_addresses": ["director@playground.co.mz", "boss@gmail.com"],
        "ignored_addresses": ["contacto@playground.co.mz"],
    },
    "clickup": {"workspace_id": "1", "space_ids": ["10"]},
    "report": {"language": "en"},
}


def config(**overrides):
    data = {k: dict(v) for k, v in CONFIG.items()}
    for section, values in overrides.items():
        data.setdefault(section, {}).update(values)
    return parse_config(data)


def b64(text: str) -> str:
    return base64.urlsafe_b64encode(text.encode()).decode().rstrip("=")


def raw_message(mid, date, sender, to, subject, body, cc="", html=False, attachment=None):
    parts = [
        {
            "mimeType": "text/html" if html else "text/plain",
            "filename": "",
            "body": {"data": b64(body)},
        }
    ]
    if attachment:
        parts.append({"mimeType": "application/pdf", "filename": attachment, "body": {"attachmentId": "x"}})
    headers = [
        {"name": "From", "value": sender},
        {"name": "To", "value": to},
        {"name": "Subject", "value": subject},
        {"name": "Date", "value": date},
    ]
    if cc:
        headers.append({"name": "Cc", "value": cc})
    return {
        "id": mid,
        "labelIds": ["INBOX"],
        "payload": {"mimeType": "multipart/mixed", "headers": headers, "parts": parts},
    }


def raw_task(tid, name, assignee="ana.silva@playground.co.mz", list_name="Vodacom", status="in progress",
             updated=datetime(2026, 10, 15, tzinfo=timezone.utc), description=""):
    ms = str(int(updated.timestamp() * 1000))
    return {
        "id": tid,
        "name": name,
        "text_content": description,
        "status": {"status": status, "type": "closed" if status == "complete" else "custom"},
        "assignees": [{"email": assignee, "username": assignee.split("@")[0]}],
        "list": {"name": list_name},
        "folder": {"name": "Clients"},
        "url": f"https://app.clickup.com/t/{tid}",
        "date_created": ms,
        "date_updated": ms,
        "tags": [],
    }
