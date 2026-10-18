from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class EmailMessage:
    message_id: str
    sent_at: datetime
    sender: str
    to: list[str]
    cc: list[str]
    subject: str
    body: str
    attachments: list[str] = field(default_factory=list)
    in_window: bool = True

    @property
    def participants(self) -> list[str]:
        return [self.sender, *self.to, *self.cc]


@dataclass
class EmailThread:
    thread_id: str
    subject: str
    messages: list[EmailMessage]
    url: str

    @property
    def window_messages(self) -> list[EmailMessage]:
        return [m for m in self.messages if m.in_window]

    def participants(self, window_only: bool = True) -> set[str]:
        msgs = self.window_messages if window_only else self.messages
        return {a for m in msgs for a in m.participants if a}


@dataclass
class ClickUpTask:
    task_id: str
    name: str
    description: str
    status: str
    closed: bool
    assignees: list[str]  # emails, lower case
    assignee_names: list[str]
    list_name: str
    folder_name: str
    url: str
    created_at: datetime | None
    updated_at: datetime | None
    due_at: datetime | None
    tags: list[str] = field(default_factory=list)


# Coverage status for one work item found in an email thread.
COVERED = "covered"
UNCERTAIN = "uncertain"
MISSING = "missing"


@dataclass
class WorkItem:
    thread: EmailThread
    summary: str
    owner_email: str | None
    client: str | None
    item_type: str
    status: str
    matched_task_ids: list[str]
    reason: str
    suggested_task_name: str | None
    due_date: str | None


@dataclass
class ThreadResult:
    thread: EmailThread
    is_work: bool
    skip_reason: str | None
    items: list[WorkItem]
    error: str | None = None
