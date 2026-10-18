"""Builds the daily report (HTML for email, plain text as fallback)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from html import escape

from .config import Config
from .models import COVERED, MISSING, UNCERTAIN, ClickUpTask, ThreadResult, WorkItem

STRINGS = {
    "pt": {
        "title": "Controlo diário Email vs ClickUp",
        "period": "Período analisado",
        "summary": "Resumo",
        "threads": "conversas de email da equipa analisadas",
        "items": "pedidos ou compromissos de trabalho identificados",
        "covered": "Registado",
        "uncertain": "A confirmar",
        "missing": "Em falta",
        "rate": "Taxa de registo",
        "by_person": "Por pessoa",
        "person": "Pessoa",
        "no_owner": "Responsável não identificado",
        "missing_title": "Trabalho sem tarefa no ClickUp",
        "uncertain_title": "A confirmar (possível tarefa encontrada)",
        "covered_title": "Registado no ClickUp",
        "client": "Cliente",
        "email": "Email",
        "suggested": "Tarefa sugerida",
        "due": "Prazo",
        "why": "Observação",
        "possible": "Possível tarefa",
        "task": "Tarefa",
        "errors": "Conversas que não foi possível analisar",
        "none_missing": "Nenhum trabalho em falta. Bom trabalho.",
        "no_items": "Não foram identificados pedidos de trabalho neste período.",
        "capped": "Atenção: o limite de {n} conversas foi atingido. Algumas conversas não foram analisadas.",
        "note": (
            "Este relatório só vê os emails que chegam a esta caixa de correio. "
            "A selecção de tarefas é automática, por isso confirme os itens 'Em falta' antes de agir. "
            "A taxa de registo considera 'A confirmar' como não registado."
        ),
        "nudge_subject": "ClickUp: {n} pedido(s) de email sem tarefa ({date})",
        "nudge_intro": (
            "Olá {name},\n\nO controlo diário encontrou os seguintes pedidos de trabalho nos emails "
            "de {date} que ainda não têm tarefa no ClickUp. Por favor crie as tarefas ou, se já "
            "existem, verifique se o nome permite identificá-las."
        ),
        "nudge_outro": "Obrigado.",
        "subject": "Controlo Email vs ClickUp {date}: {rate} registado, {missing} em falta",
    },
    "en": {
        "title": "Daily Email vs ClickUp check",
        "period": "Period reviewed",
        "summary": "Summary",
        "threads": "team email threads reviewed",
        "items": "work requests or commitments found",
        "covered": "In ClickUp",
        "uncertain": "To confirm",
        "missing": "Missing",
        "rate": "Registration rate",
        "by_person": "By person",
        "person": "Person",
        "no_owner": "Owner not identified",
        "missing_title": "Work without a ClickUp task",
        "uncertain_title": "To confirm (possible task found)",
        "covered_title": "Registered in ClickUp",
        "client": "Client",
        "email": "Email",
        "suggested": "Suggested task",
        "due": "Due",
        "why": "Note",
        "possible": "Possible task",
        "task": "Task",
        "errors": "Threads that could not be analysed",
        "none_missing": "No missing work. Well done.",
        "no_items": "No work requests were found in this period.",
        "capped": "Warning: the limit of {n} threads was reached. Some threads were not analysed.",
        "note": (
            "This report only sees emails that reach this mailbox. Task shortlisting is automatic, "
            "so please confirm 'Missing' items before acting. The registration rate counts "
            "'To confirm' as not registered."
        ),
        "nudge_subject": "ClickUp: {n} email request(s) without a task ({date})",
        "nudge_intro": (
            "Hi {name},\n\nThe daily check found the following work requests in the emails of "
            "{date} that do not have a ClickUp task yet. Please create the tasks or, if they "
            "already exist, check that the name makes them easy to identify."
        ),
        "nudge_outro": "Thank you.",
        "subject": "Email vs ClickUp check {date}: {rate} registered, {missing} missing",
    },
}

NO_OWNER = "__none__"


@dataclass
class PersonStats:
    key: str
    name: str
    covered: int = 0
    uncertain: int = 0
    missing: int = 0

    @property
    def total(self) -> int:
        return self.covered + self.uncertain + self.missing

    @property
    def rate(self) -> float | None:
        return self.covered / self.total if self.total else None


@dataclass
class Report:
    period_label: str
    date_label: str
    threads_reviewed: int
    capped: bool
    items: list[WorkItem]
    errors: list[ThreadResult]
    tasks_by_id: dict[str, ClickUpTask]
    people: list[PersonStats] = field(default_factory=list)

    def by_status(self, status: str) -> list[WorkItem]:
        return [i for i in self.items if i.status == status]

    @property
    def totals(self) -> PersonStats:
        total = PersonStats(key="all", name="all")
        for p in self.people:
            total.covered += p.covered
            total.uncertain += p.uncertain
            total.missing += p.missing
        return total


def build_report(
    results: list[ThreadResult],
    tasks: list[ClickUpTask],
    config: Config,
    start: datetime,
    end: datetime,
    capped: bool,
) -> Report:
    items = [i for r in results for i in r.items]
    people: dict[str, PersonStats] = {}
    for item in items:
        key = item.owner_email or NO_OWNER
        if key not in people:
            name = config.display_name(key) if key != NO_OWNER else STRINGS[config.language]["no_owner"]
            people[key] = PersonStats(key=key, name=name)
        stats = people[key]
        setattr(stats, item.status, getattr(stats, item.status) + 1)

    ordered = sorted(
        people.values(),
        key=lambda p: (p.key == NO_OWNER, -(p.missing + p.uncertain), p.name),
    )
    last_day = (end.astimezone(start.tzinfo) - timedelta(seconds=1)).date()
    first_day = start.date()
    if first_day == last_day:
        period = first_day.strftime("%d/%m/%Y")
    else:
        period = f"{first_day.strftime('%d/%m/%Y')} – {last_day.strftime('%d/%m/%Y')}"
    return Report(
        period_label=period,
        date_label=last_day.strftime("%d/%m/%Y"),
        threads_reviewed=len(results),
        capped=capped,
        items=items,
        errors=[r for r in results if r.error],
        tasks_by_id={t.task_id: t for t in tasks},
        people=ordered,
    )


def _pct(value: float | None) -> str:
    return "–" if value is None else f"{round(value * 100)}%"


def subject_line(report: Report, config: Config) -> str:
    s = STRINGS[config.language]
    t = report.totals
    return s["subject"].format(date=report.date_label, rate=_pct(t.rate), missing=t.missing)


# ---------------------------------------------------------------------------
# HTML
# ---------------------------------------------------------------------------

CSS = """
body{font-family:Arial,Helvetica,sans-serif;color:#1f2328;font-size:14px;line-height:1.45;margin:0;padding:16px;background:#ffffff}
h1{font-size:20px;margin:0 0 4px}
h2{font-size:16px;margin:28px 0 8px;border-bottom:1px solid #d0d7de;padding-bottom:4px}
h3{font-size:14px;margin:18px 0 6px}
.muted{color:#59636e;font-size:12px}
table{border-collapse:collapse;width:100%;max-width:900px}
th,td{text-align:left;padding:6px 8px;border-bottom:1px solid #e6e9ed;vertical-align:top}
th{background:#f6f8fa;font-size:12px;text-transform:uppercase;letter-spacing:.02em;color:#59636e}
td.num{text-align:right;white-space:nowrap}
.kpis td{border:none;padding:4px 16px 4px 0}
.kpi{font-size:24px;font-weight:bold}
.missing{color:#b42318}.uncertain{color:#9a6700}.covered{color:#1a7f37}
.item{border-left:3px solid #d0d7de;padding:4px 10px;margin:8px 0;max-width:900px}
.item.missing{border-color:#b42318;color:inherit}.item.uncertain{border-color:#bf8700;color:inherit}
.item .s{font-weight:bold}
.item div{margin:2px 0}
a{color:#0969da}
"""


def _task_links(item: WorkItem, report: Report) -> str:
    links = []
    for tid in item.matched_task_ids:
        task = report.tasks_by_id.get(tid)
        if task:
            links.append(f'<a href="{escape(task.url)}">{escape(task.name)}</a> ({escape(task.status)})')
    return ", ".join(links)


def _item_html(item: WorkItem, report: Report, s: dict, show_task_label: str | None) -> str:
    parts = [f'<div class="s">{escape(item.summary)}</div>']
    meta = []
    if item.client:
        meta.append(f"{s['client']}: {escape(item.client)}")
    meta.append(f'{s["email"]}: <a href="{escape(item.thread.url)}">{escape(item.thread.subject)}</a>')
    if item.due_date:
        meta.append(f"{s['due']}: {escape(item.due_date)}")
    parts.append(f"<div>{' · '.join(meta)}</div>")
    if show_task_label and item.matched_task_ids:
        parts.append(f"<div>{show_task_label}: {_task_links(item, report)}</div>")
    if item.suggested_task_name and item.status != COVERED:
        parts.append(f"<div>{s['suggested']}: <i>{escape(item.suggested_task_name)}</i></div>")
    if item.reason:
        parts.append(f'<div class="muted">{s["why"]}: {escape(item.reason)}</div>')
    return f'<div class="item {item.status}">{"".join(parts)}</div>'


def _grouped(items: list[WorkItem], report: Report, s: dict, task_label: str | None) -> str:
    out = []
    for person in report.people:
        mine = [i for i in items if (i.owner_email or NO_OWNER) == person.key]
        if not mine:
            continue
        out.append(f"<h3>{escape(person.name)} ({len(mine)})</h3>")
        out.extend(_item_html(i, report, s, task_label) for i in mine)
    return "\n".join(out)


def render_html(report: Report, config: Config) -> str:
    s = STRINGS[config.language]
    t = report.totals
    rows = "\n".join(
        f"<tr><td>{escape(p.name)}</td><td class='num'>{p.total}</td>"
        f"<td class='num covered'>{p.covered}</td><td class='num uncertain'>{p.uncertain}</td>"
        f"<td class='num missing'>{p.missing}</td><td class='num'><b>{_pct(p.rate)}</b></td></tr>"
        for p in report.people
    )
    html = [
        f"<!doctype html><html lang='{config.language}'><head><meta charset='utf-8'>"
        f"<meta name='viewport' content='width=device-width,initial-scale=1'>"
        f"<title>{escape(s['title'])}</title><style>{CSS}</style></head><body>",
        f"<h1>{escape(s['title'])}</h1>",
        f"<div class='muted'>{s['period']}: {escape(report.period_label)} · "
        f"{report.threads_reviewed} {s['threads']} · {t.total} {s['items']}</div>",
    ]
    if report.capped:
        html.append(f"<p class='missing'>{escape(s['capped'].format(n=config.max_threads))}</p>")

    if not t.total:
        html.append(f"<p>{escape(s['no_items'])}</p>")
    else:
        html.append(
            "<table class='kpis'><tr>"
            f"<td><div class='kpi'>{_pct(t.rate)}</div><div class='muted'>{s['rate']}</div></td>"
            f"<td><div class='kpi covered'>{t.covered}</div><div class='muted'>{s['covered']}</div></td>"
            f"<td><div class='kpi uncertain'>{t.uncertain}</div><div class='muted'>{s['uncertain']}</div></td>"
            f"<td><div class='kpi missing'>{t.missing}</div><div class='muted'>{s['missing']}</div></td>"
            "</tr></table>"
        )
        html.append(f"<h2>{s['by_person']}</h2>")
        html.append(
            f"<table><tr><th>{s['person']}</th><th>Total</th><th>{s['covered']}</th>"
            f"<th>{s['uncertain']}</th><th>{s['missing']}</th><th>{s['rate']}</th></tr>{rows}</table>"
        )
        missing = report.by_status(MISSING)
        html.append(f"<h2 class='missing'>{s['missing_title']} ({len(missing)})</h2>")
        html.append(_grouped(missing, report, s, None) if missing else f"<p>{escape(s['none_missing'])}</p>")
        uncertain = report.by_status(UNCERTAIN)
        if uncertain:
            html.append(f"<h2 class='uncertain'>{s['uncertain_title']} ({len(uncertain)})</h2>")
            html.append(_grouped(uncertain, report, s, s["possible"]))
        covered = report.by_status(COVERED)
        if covered:
            html.append(f"<h2 class='covered'>{s['covered_title']} ({len(covered)})</h2>")
            html.append("<table>")
            for i in covered:
                html.append(
                    f"<tr><td>{escape(config.display_name(i.owner_email) if i.owner_email else s['no_owner'])}</td>"
                    f"<td>{escape(i.summary)}</td><td>{_task_links(i, report)}</td></tr>"
                )
            html.append("</table>")

    if report.errors:
        html.append(f"<h2>{s['errors']} ({len(report.errors)})</h2><ul>")
        for r in report.errors:
            html.append(
                f"<li><a href='{escape(r.thread.url)}'>{escape(r.thread.subject)}</a> "
                f"<span class='muted'>({escape(r.error or '')})</span></li>"
            )
        html.append("</ul>")
    html.append(f"<p class='muted' style='margin-top:28px'>{escape(s['note'])}</p></body></html>")
    return "\n".join(html)


def render_text(report: Report, config: Config) -> str:
    s = STRINGS[config.language]
    t = report.totals
    lines = [
        s["title"],
        f"{s['period']}: {report.period_label}",
        f"{report.threads_reviewed} {s['threads']}, {t.total} {s['items']}",
        f"{s['rate']}: {_pct(t.rate)} | {s['covered']}: {t.covered} | "
        f"{s['uncertain']}: {t.uncertain} | {s['missing']}: {t.missing}",
        "",
        s["by_person"].upper(),
    ]
    for p in report.people:
        lines.append(
            f"- {p.name}: {_pct(p.rate)} ({p.covered}/{p.total}), "
            f"{s['missing'].lower()} {p.missing}, {s['uncertain'].lower()} {p.uncertain}"
        )
    for status, title in ((MISSING, s["missing_title"]), (UNCERTAIN, s["uncertain_title"])):
        items = report.by_status(status)
        if not items:
            continue
        lines += ["", title.upper()]
        for i in items:
            owner = config.display_name(i.owner_email) if i.owner_email else s["no_owner"]
            lines.append(f"- [{owner}] {i.summary}")
            lines.append(f"  {s['email']}: {i.thread.subject} {i.thread.url}")
            if i.suggested_task_name:
                lines.append(f"  {s['suggested']}: {i.suggested_task_name}")
    lines += ["", s["note"]]
    return "\n".join(lines)


def render_nudge(person: PersonStats, items: list[WorkItem], report: Report, config: Config) -> tuple[str, str, str]:
    """(subject, html, text) for an individual reminder to one team member."""
    s = STRINGS[config.language]
    first_name = person.name.split(" ")[0]
    intro = s["nudge_intro"].format(name=first_name, date=report.period_label)
    subject = s["nudge_subject"].format(n=len(items), date=report.date_label)
    text_lines = [intro, ""]
    for i in items:
        text_lines.append(f"- {i.summary}")
        text_lines.append(f"  {s['email']}: {i.thread.subject}")
        if i.suggested_task_name:
            text_lines.append(f"  {s['suggested']}: {i.suggested_task_name}")
    text_lines += ["", s["nudge_outro"]]
    body = "".join(_item_html(i, report, s, None) for i in items)
    intro_html = "".join(f"<p>{escape(p)}</p>" for p in intro.split("\n\n"))
    html = (
        f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>"
        f"{intro_html}{body}<p>{escape(s['nudge_outro'])}</p></body></html>"
    )
    return subject, html, "\n".join(text_lines)
