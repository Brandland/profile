"""Configuration loading.

The configuration holds team names and email addresses, so it is never
committed. It is read from (in order):
  1. the --config file path, or
  2. the CROSSCHECK_CONFIG environment variable (full YAML text, used by
     GitHub Actions where it is stored as a secret).
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml


DEFAULT_IGNORED_SENDER_PATTERNS = [
    "noreply",
    "no-reply",
    "donotreply",
    "do-not-reply",
    "mailer-daemon",
    "postmaster",
    "notification",
    "calendar-notification",
    "workspace-noreply",
]


@dataclass
class TeamMember:
    email: str
    name: str


@dataclass
class Config:
    # Mailbox
    mailbox_address: str
    team_domains: list[str]
    team_members: list[TeamMember]
    manager_addresses: list[str]
    ignored_sender_patterns: list[str]
    ignored_addresses: list[str]
    extra_gmail_query: str

    # ClickUp
    clickup_workspace_id: str
    clickup_space_ids: list[str]
    closed_task_lookback_days: int

    # Analysis
    model: str
    effort: str
    max_threads: int
    max_candidates: int
    parallel_requests: int
    policy_notes: str

    # Report
    timezone: str
    language: str
    report_recipients: list[str]
    send_individual_nudges: bool
    nudge_cc: list[str] = field(default_factory=list)

    # ---- helpers -------------------------------------------------------

    def is_team_address(self, address: str) -> bool:
        address = address.lower()
        if address in {m.email for m in self.team_members}:
            return True
        domain = address.rsplit("@", 1)[-1]
        return domain in self.team_domains

    def is_ignored(self, address: str) -> bool:
        address = address.lower()
        if address in self.ignored_addresses:
            return True
        local = address.split("@", 1)[0]
        return any(p in local for p in self.ignored_sender_patterns)

    def is_manager(self, address: str) -> bool:
        return address.lower() in self.manager_addresses

    def display_name(self, address: str) -> str:
        address = address.lower()
        for member in self.team_members:
            if member.email == address:
                return member.name
        local = address.split("@", 1)[0]
        parts = [p for p in local.replace("_", ".").replace("-", ".").split(".") if p]
        return " ".join(p.capitalize() for p in parts) or address


def _lower_list(values) -> list[str]:
    return [str(v).strip().lower() for v in (values or []) if str(v).strip()]


def parse_config(data: dict) -> Config:
    gmail = data.get("gmail", {}) or {}
    team = data.get("team", {}) or {}
    clickup = data.get("clickup", {}) or {}
    analysis = data.get("analysis", {}) or {}
    report = data.get("report", {}) or {}

    mailbox = str(gmail.get("mailbox_address", "")).strip().lower()
    if not mailbox:
        raise ValueError("gmail.mailbox_address is required")

    members = []
    for m in team.get("members", []) or []:
        email = str(m.get("email", "")).strip().lower()
        if email:
            members.append(TeamMember(email=email, name=str(m.get("name") or email)))

    domains = _lower_list(team.get("domains"))
    if not domains and not members:
        raise ValueError("team.domains or team.members must be set")

    workspace = str(clickup.get("workspace_id", "")).strip()
    spaces = [str(s).strip() for s in clickup.get("space_ids", []) or [] if str(s).strip()]
    if not workspace or not spaces:
        raise ValueError("clickup.workspace_id and clickup.space_ids are required")

    language = str(report.get("language", "pt")).lower()
    if language not in ("pt", "en"):
        raise ValueError("report.language must be 'pt' or 'en'")

    recipients = _lower_list(report.get("recipients")) or [mailbox]

    return Config(
        mailbox_address=mailbox,
        team_domains=domains,
        team_members=members,
        manager_addresses=_lower_list(team.get("manager_addresses")),
        ignored_sender_patterns=_lower_list(
            team.get("ignored_sender_patterns", DEFAULT_IGNORED_SENDER_PATTERNS)
        ),
        ignored_addresses=_lower_list(team.get("ignored_addresses")),
        extra_gmail_query=str(gmail.get("extra_query", "")).strip(),
        clickup_workspace_id=workspace,
        clickup_space_ids=spaces,
        closed_task_lookback_days=int(clickup.get("closed_task_lookback_days", 45)),
        model=str(analysis.get("model", "claude-opus-5-5")),
        effort=str(analysis.get("effort", "medium")),
        max_threads=int(analysis.get("max_threads", 150)),
        max_candidates=int(analysis.get("max_candidate_tasks", 30)),
        parallel_requests=max(1, int(analysis.get("parallel_requests", 4))),
        policy_notes=str(analysis.get("policy_notes", "")).strip(),
        timezone=str(report.get("timezone", "Africa/Maputo")),
        language=language,
        report_recipients=recipients,
        send_individual_nudges=bool(report.get("send_individual_nudges", False)),
        nudge_cc=_lower_list(report.get("nudge_cc")),
    )


def load_config(path: str | None) -> Config:
    if path:
        text = Path(path).read_text(encoding="utf-8")
    else:
        text = os.environ.get("CROSSCHECK_CONFIG", "")
        if not text.strip():
            raise SystemExit(
                "No configuration found. Pass --config config.yaml or set CROSSCHECK_CONFIG."
            )
    return parse_config(yaml.safe_load(text) or {})
