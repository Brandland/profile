"""Reads team email threads from Gmail and sends the report.

Uses an OAuth refresh token for the mailbox owner (see scripts/get_gmail_token.py).
Scopes: gmail.readonly (to read) and gmail.send (to send the report).
"""

from __future__ import annotations

import base64
import html
import logging
import os
import re
from datetime import datetime, timezone
from email.message import EmailMessage as MimeMessage
from email.utils import getaddresses, parsedate_to_datetime

from .config import Config
from .models import EmailMessage, EmailThread

log = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
]

# Characters kept per message. Messages in the analysis window get more room
# than older messages, which are only there to give context.
WINDOW_BODY_CHARS = 6000
CONTEXT_BODY_CHARS = 800
MAX_CONTEXT_MESSAGES = 4


def build_service():
    """Gmail API service from environment variables."""
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    creds = Credentials(
        token=None,
        refresh_token=os.environ["GMAIL_REFRESH_TOKEN"],
        client_id=os.environ["GMAIL_CLIENT_ID"],
        client_secret=os.environ["GMAIL_CLIENT_SECRET"],
        token_uri="https://oauth2.googleapis.com/token",
        scopes=SCOPES,
    )
    return build("gmail", "v1", credentials=creds, cache_discovery=False)


# ---------------------------------------------------------------------------
# Query and parsing helpers (pure functions, unit tested)
# ---------------------------------------------------------------------------


def build_query(config: Config, start: datetime, end: datetime) -> str:
    """Gmail search query for threads with team traffic inside the window."""
    # Members on a team domain are already covered by the domain filter.
    targets = list(config.team_domains) + [
        m.email for m in config.team_members if m.email.rsplit("@", 1)[-1] not in config.team_domains
    ]
    who = " OR ".join(
        f"{field}:{t}" for t in targets for field in ("from", "to", "cc")
    )
    parts = [
        f"after:{int(start.timestamp())}",
        f"before:{int(end.timestamp())}",
        f"({who})",
        "-category:promotions",
        "-category:social",
        "-in:chats",
    ]
    if config.extra_gmail_query:
        parts.append(config.extra_gmail_query)
    return " ".join(parts)


def _addresses(value: str | None) -> list[str]:
    return [addr.lower() for _, addr in getaddresses([value or ""]) if addr]


def _decode(data: str | None) -> str:
    if not data:
        return ""
    raw = base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))
    return raw.decode("utf-8", errors="replace")


def html_to_text(value: str) -> str:
    value = re.sub(r"(?is)<(script|style|head).*?</\1>", " ", value)
    value = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</tr>|</li>", "\n", value)
    value = re.sub(r"<[^>]+>", " ", value)
    value = html.unescape(value)
    value = re.sub(r"[ \t\r\f\v]+", " ", value)
    return re.sub(r"\n\s*\n+", "\n\n", value).strip()


def _walk_parts(payload: dict):
    yield payload
    for part in payload.get("parts", []) or []:
        yield from _walk_parts(part)


def extract_body(payload: dict) -> tuple[str, list[str]]:
    """Return (plain text body, attachment file names)."""
    plain, rich, attachments = [], [], []
    for part in _walk_parts(payload):
        mime = part.get("mimeType", "")
        filename = part.get("filename") or ""
        body = part.get("body", {}) or {}
        if filename:
            attachments.append(filename)
            continue
        if mime == "text/plain" and body.get("data"):
            plain.append(_decode(body["data"]))
        elif mime == "text/html" and body.get("data"):
            rich.append(_decode(body["data"]))
    text = "\n".join(plain) if plain else html_to_text("\n".join(rich))
    return text, attachments


_REPLY_MARKERS = [
    re.compile(r"^\s*On .{5,200} wrote:\s*$", re.I),
    re.compile(r"^\s*Em .{5,200} escreveu:\s*$", re.I),
    re.compile(r"^\s*-{2,}\s*(Original Message|Mensagem original|Forwarded message|Mensagem encaminhada)\s*-{2,}", re.I),
    re.compile(r"^\s*(From|De):\s.+$", re.I),
    re.compile(r"^\s*_{10,}\s*$"),
]


def strip_quoted(text: str) -> str:
    """Drop quoted reply history so each message only carries new content."""
    lines = text.replace("\r\n", "\n").split("\n")
    kept = []
    for i, line in enumerate(lines):
        if any(p.match(line) for p in _REPLY_MARKERS):
            # A "From:" line only counts as a reply header when followed by
            # other header lines (Sent/Enviado/To/Para/Subject/Assunto).
            if re.match(r"^\s*(From|De):", line, re.I):
                nxt = " ".join(lines[i + 1 : i + 4])
                if not re.search(r"(Sent|Enviado|Date|Data|To|Para|Subject|Assunto):", nxt, re.I):
                    kept.append(line)
                    continue
            break
        if line.lstrip().startswith(">"):
            continue
        kept.append(line)
    return re.sub(r"\n{3,}", "\n\n", "\n".join(kept)).strip()


def _truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + f"\n[... {len(text) - limit} more characters not shown]"


def parse_thread(raw: dict, start: datetime, end: datetime, mailbox: str) -> EmailThread:
    messages = []
    for msg in raw.get("messages", []) or []:
        payload = msg.get("payload", {}) or {}
        headers = {h["name"].lower(): h["value"] for h in payload.get("headers", []) or []}
        if "DRAFT" in (msg.get("labelIds") or []):
            continue
        try:
            sent_at = parsedate_to_datetime(headers.get("date", ""))
            if sent_at.tzinfo is None:
                sent_at = sent_at.replace(tzinfo=timezone.utc)
        except (TypeError, ValueError):
            sent_at = datetime.fromtimestamp(int(msg.get("internalDate", "0")) / 1000, timezone.utc)
        body, attachments = extract_body(payload)
        sender = (_addresses(headers.get("from")) or [""])[0]
        messages.append(
            EmailMessage(
                message_id=msg.get("id", ""),
                sent_at=sent_at,
                sender=sender,
                to=_addresses(headers.get("to")),
                cc=_addresses(headers.get("cc")),
                subject=headers.get("subject", "").strip(),
                body=strip_quoted(body),
                attachments=attachments,
                in_window=start <= sent_at < end,
            )
        )
    messages.sort(key=lambda m: m.sent_at)
    subject = next((m.subject for m in messages if m.subject), "(no subject)")
    thread_id = raw.get("id", "")
    url = f"https://mail.google.com/mail/?authuser={mailbox}#all/{thread_id}"
    return EmailThread(thread_id=thread_id, subject=subject, messages=messages, url=url)


def is_relevant(thread: EmailThread, config: Config) -> bool:
    """Keep threads where a team member (other than management) took part
    in the window, and the window traffic is not only automated mail."""
    window = thread.window_messages
    if not window:
        return False
    if all(config.is_ignored(m.sender) for m in window):
        return False
    team = [
        a
        for a in thread.participants(window_only=True)
        if config.is_team_address(a) and not config.is_ignored(a) and not config.is_manager(a)
    ]
    return bool(team)


def thread_to_prompt_text(thread: EmailThread, config: Config) -> str:
    """Readable rendering of the thread for the model."""
    def who(addr: str) -> str:
        tag = " [TEAM]" if config.is_team_address(addr) and not config.is_manager(addr) else ""
        tag = " [MANAGEMENT]" if config.is_manager(addr) else tag
        return f"{addr}{tag}"

    context = [m for m in thread.messages if not m.in_window][-MAX_CONTEXT_MESSAGES:]
    omitted = len([m for m in thread.messages if not m.in_window]) - len(context)
    blocks = [f"Subject: {thread.subject}"]
    if omitted > 0:
        blocks.append(f"({omitted} older messages omitted)")
    for m in context + thread.window_messages:
        label = "NEW MESSAGE (in review window)" if m.in_window else "Earlier message (context only)"
        limit = WINDOW_BODY_CHARS if m.in_window else CONTEXT_BODY_CHARS
        lines = [
            f"--- {label} ---",
            f"Date: {m.sent_at.isoformat()}",
            f"From: {who(m.sender)}",
            f"To: {', '.join(who(a) for a in m.to) or '-'}",
        ]
        if m.cc:
            lines.append(f"Cc: {', '.join(who(a) for a in m.cc)}")
        if m.attachments:
            lines.append(f"Attachments: {', '.join(m.attachments)}")
        lines.append("")
        lines.append(_truncate(m.body, limit) or "(empty body)")
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)


# ---------------------------------------------------------------------------
# API calls
# ---------------------------------------------------------------------------


class GmailReader:
    def __init__(self, service, config: Config):
        self.service = service
        self.config = config

    def fetch_threads(self, start: datetime, end: datetime) -> tuple[list[EmailThread], int]:
        """Return (relevant threads, total threads matched by the search)."""
        query = build_query(self.config, start, end)
        ids, token = [], None
        while True:
            resp = (
                self.service.users()
                .threads()
                .list(userId="me", q=query, maxResults=100, pageToken=token)
                .execute()
            )
            ids.extend(t["id"] for t in resp.get("threads", []) or [])
            token = resp.get("nextPageToken")
            if not token:
                break
        threads = []
        for thread_id in ids:
            raw = self.service.users().threads().get(userId="me", id=thread_id, format="full").execute()
            thread = parse_thread(raw, start, end, self.config.mailbox_address)
            if is_relevant(thread, self.config):
                threads.append(thread)
        log.info("Gmail: %d threads matched, %d relevant", len(ids), len(threads))
        return threads, len(ids)

    def send(self, to: list[str], subject: str, html_body: str, text_body: str, cc: list[str] | None = None):
        msg = MimeMessage()
        msg["To"] = ", ".join(to)
        if cc:
            msg["Cc"] = ", ".join(cc)
        msg["Subject"] = subject
        msg.set_content(text_body)
        msg.add_alternative(html_body, subtype="html")
        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        self.service.users().messages().send(userId="me", body={"raw": raw}).execute()
