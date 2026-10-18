"""Daily cross-check: team emails vs ClickUp tasks.

Usage:
  python -m crosscheck run [--config config.yaml] [--date YYYY-MM-DD] [--days N]
                           [--no-email] [--output report.html]
  python -m crosscheck spaces          # list ClickUp workspace and Space IDs

Logs never contain email subjects, bodies or names, so the tool can run on a
public CI without exposing content. The content only goes into the report.
"""

from __future__ import annotations

import argparse
import logging
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from .config import Config, load_config
from .models import MISSING
from .report import NO_OWNER, build_report, render_html, render_nudge, render_text, subject_line

log = logging.getLogger("crosscheck")


def review_window(today: date, tz: ZoneInfo, day: date | None = None, days: int | None = None):
    """Return (start, end) datetimes for the period to review.

    Default: the previous working day. On Monday that is Friday to Sunday, so
    weekend emails are not lost. --date picks a specific day, --days N reviews
    the N days ending on that day (or yesterday).
    """
    if day is None and days is None:
        if today.weekday() == 0:  # Monday
            first, last = today - timedelta(days=3), today - timedelta(days=1)
        elif today.weekday() == 6:  # Sunday run: review Friday and Saturday
            first, last = today - timedelta(days=2), today - timedelta(days=1)
        else:
            first = last = today - timedelta(days=1)
    else:
        last = day or (today - timedelta(days=1))
        first = last - timedelta(days=max(1, days or 1) - 1)
    start = datetime.combine(first, time.min, tzinfo=tz)
    end = datetime.combine(last + timedelta(days=1), time.min, tzinfo=tz)
    return start, end


def run(config: Config, args) -> int:
    from .analyzer import Analyzer
    from .candidates import CandidateFinder
    from .clickup_client import ClickUpClient
    from .gmail_client import GmailReader, build_service

    tz = ZoneInfo(config.timezone)
    now = datetime.now(tz)
    day = date.fromisoformat(args.date) if args.date else None
    start, end = review_window(now.date(), tz, day, args.days)
    log.info("Reviewing %s to %s (%s)", start.isoformat(), end.isoformat(), config.timezone)

    gmail = GmailReader(build_service(), config)
    threads, _ = gmail.fetch_threads(start, end)
    capped = len(threads) > config.max_threads
    if capped:
        log.warning("Thread limit reached: analysing %d of %d", config.max_threads, len(threads))
        threads = threads[: config.max_threads]

    tasks = ClickUpClient().fetch_tasks(config, now.astimezone(timezone.utc))
    finder = CandidateFinder(tasks, config)
    analyzer = Analyzer(config)

    def work(thread):
        return analyzer.analyse(thread, finder.find(thread, now.astimezone(timezone.utc)))

    with ThreadPoolExecutor(max_workers=config.parallel_requests) as pool:
        results = list(pool.map(work, threads))

    report = build_report(results, tasks, config, start, end, capped)
    totals = report.totals
    log.info(
        "Result: %d work items, %d covered, %d to confirm, %d missing, %d errors",
        totals.total, totals.covered, totals.uncertain, totals.missing, len(report.errors),
    )

    html = render_html(report, config)
    text = render_text(report, config)
    if args.output:
        Path(args.output).write_text(html, encoding="utf-8")
        log.info("Report written to %s", args.output)

    if args.no_email:
        return 0

    gmail.send(config.report_recipients, subject_line(report, config), html, text)
    log.info("Report emailed to %d recipient(s)", len(config.report_recipients))

    if config.send_individual_nudges:
        missing = report.by_status(MISSING)
        sent = 0
        for person in report.people:
            if person.key == NO_OWNER:
                continue
            mine = [i for i in missing if i.owner_email == person.key]
            if not mine:
                continue
            subject, nudge_html, nudge_text = render_nudge(person, mine, report, config)
            gmail.send([person.key], subject, nudge_html, nudge_text, cc=config.nudge_cc)
            sent += 1
        log.info("Individual reminders sent: %d", sent)
    return 0


def list_spaces() -> int:
    from .clickup_client import ClickUpClient

    client = ClickUpClient()
    for ws in client.workspaces():
        print(f"Workspace: {ws.get('name')}  id={ws.get('id')}")
        for space in client.spaces(ws["id"]):
            print(f"    Space: {space.get('name')}  id={space.get('id')}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="crosscheck", description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command")
    p_run = sub.add_parser("run", help="run the cross-check and send the report")
    p_run.add_argument("--config", help="path to config YAML (default: CROSSCHECK_CONFIG env)")
    p_run.add_argument("--date", help="last day to review, YYYY-MM-DD (default: previous working day)")
    p_run.add_argument("--days", type=int, help="number of days to review, ending on --date")
    p_run.add_argument("--no-email", action="store_true", help="do not send any email")
    p_run.add_argument("--output", help="also save the HTML report to this file")
    sub.add_parser("spaces", help="list ClickUp workspace and Space IDs")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    # Library loggers can print request details; keep them quiet.
    for noisy in ("googleapiclient", "urllib3", "httpx", "anthropic"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    if args.command == "spaces":
        return list_spaces()
    if args.command == "run":
        return run(load_config(args.config), args)
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
