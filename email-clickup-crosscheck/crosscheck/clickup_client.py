"""Reads tasks from the ClickUp Space(s) using the ClickUp API v2.

Authentication uses a personal API token (ClickUp > Settings > Apps > API Token),
passed in the CLICKUP_API_TOKEN environment variable.
"""

from __future__ import annotations

import logging
import os
import time
from datetime import datetime, timedelta, timezone

import requests

from .config import Config
from .models import ClickUpTask

log = logging.getLogger(__name__)

API = "https://api.clickup.com/api/v2"


def _ms_to_dt(value) -> datetime | None:
    if value in (None, "", 0, "0"):
        return None
    try:
        return datetime.fromtimestamp(int(value) / 1000, timezone.utc)
    except (TypeError, ValueError):
        return None


def parse_task(raw: dict) -> ClickUpTask:
    status = raw.get("status") or {}
    assignees = raw.get("assignees") or []
    return ClickUpTask(
        task_id=str(raw.get("id", "")),
        name=(raw.get("name") or "").strip(),
        description=(raw.get("text_content") or raw.get("description") or "").strip(),
        status=str(status.get("status", "")),
        closed=status.get("type") in ("closed", "done") or bool(raw.get("date_closed")),
        assignees=[str(a.get("email", "")).lower() for a in assignees if a.get("email")],
        assignee_names=[str(a.get("username") or a.get("email") or "") for a in assignees],
        list_name=((raw.get("list") or {}).get("name") or ""),
        folder_name=((raw.get("folder") or {}).get("name") or ""),
        url=raw.get("url") or f"https://app.clickup.com/t/{raw.get('id', '')}",
        created_at=_ms_to_dt(raw.get("date_created")),
        updated_at=_ms_to_dt(raw.get("date_updated")),
        due_at=_ms_to_dt(raw.get("due_date")),
        tags=[t.get("name", "") for t in raw.get("tags") or []],
    )


class ClickUpClient:
    def __init__(self, token: str | None = None, session: requests.Session | None = None):
        self.token = token or os.environ["CLICKUP_API_TOKEN"]
        self.session = session or requests.Session()

    def _get(self, path: str, params=None) -> dict:
        for attempt in range(5):
            resp = self.session.get(
                f"{API}{path}",
                headers={"Authorization": self.token},
                params=params,
                timeout=60,
            )
            if resp.status_code == 429 or resp.status_code >= 500:
                wait = int(resp.headers.get("Retry-After", 0) or 0) or 2 ** (attempt + 1)
                log.warning("ClickUp %s returned %s, retrying in %ss", path, resp.status_code, wait)
                time.sleep(wait)
                continue
            resp.raise_for_status()
            return resp.json()
        resp.raise_for_status()
        return {}

    # Discovery helpers, used by `python -m crosscheck spaces`
    def workspaces(self) -> list[dict]:
        return self._get("/team").get("teams", [])

    def spaces(self, workspace_id: str) -> list[dict]:
        return self._get(f"/team/{workspace_id}/space", {"archived": "false"}).get("spaces", [])

    def _task_pages(self, workspace_id: str, params: list[tuple[str, str]]):
        page = 0
        while True:
            data = self._get(f"/team/{workspace_id}/task", params + [("page", str(page))])
            tasks = data.get("tasks", []) or []
            yield from tasks
            if data.get("last_page", True) or not tasks:
                break
            page += 1

    def fetch_tasks(self, config: Config, now: datetime | None = None) -> list[ClickUpTask]:
        """All open tasks in the Space(s), plus tasks closed recently.

        Open tasks may relate to work requested long ago, so they are always
        included. Closed tasks are limited to the lookback period.
        """
        now = now or datetime.now(timezone.utc)
        base = [("space_ids[]", s) for s in config.clickup_space_ids] + [
            ("subtasks", "true"),
            ("order_by", "updated"),
        ]
        since = now - timedelta(days=config.closed_task_lookback_days)
        open_params = base + [("include_closed", "false")]
        recent_params = base + [
            ("include_closed", "true"),
            ("date_updated_gt", str(int(since.timestamp() * 1000))),
        ]
        tasks: dict[str, ClickUpTask] = {}
        for params in (open_params, recent_params):
            for raw in self._task_pages(config.clickup_workspace_id, params):
                task = parse_task(raw)
                tasks[task.task_id] = task
        log.info("ClickUp: %d tasks loaded", len(tasks))
        return list(tasks.values())
