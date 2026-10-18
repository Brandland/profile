import json
from datetime import date, datetime, timezone
from types import SimpleNamespace
from zoneinfo import ZoneInfo

import pytest

from crosscheck import analyzer as analyzer_mod
from crosscheck.analyzer import Analyzer, interpret
from crosscheck.candidates import CandidateFinder, tokens
from crosscheck.clickup_client import ClickUpClient, parse_task
from crosscheck.gmail_client import build_query, is_relevant, parse_thread, strip_quoted, thread_to_prompt_text
from crosscheck.main import review_window
from crosscheck.models import COVERED, MISSING, UNCERTAIN
from crosscheck.report import build_report, render_html, render_nudge, render_text, subject_line

from helpers import config, raw_message, raw_task

TZ = ZoneInfo("Africa/Maputo")
START = datetime(2026, 10, 16, tzinfo=TZ)
END = datetime(2026, 10, 17, tzinfo=TZ)
NOW = datetime(2026, 10, 17, 8, tzinfo=timezone.utc)


def vodacom_thread():
    raw = {
        "id": "t1",
        "messages": [
            raw_message("m0", "Mon, 12 Oct 2026 09:00:00 +0200", "Client <joao@vodacom.co.mz>",
                        "ana.silva@playground.co.mz", "Video institucional", "Old request, already handled."),
            raw_message("m1", "Fri, 16 Oct 2026 10:00:00 +0200", "Client <joao@vodacom.co.mz>",
                        "Ana Silva <ana.silva@playground.co.mz>", "RE: Video institucional",
                        "Please revise the institutional video with the new logo by Friday.\n\n"
                        "On Mon, 12 Oct 2026 Ana wrote:\n> old text",
                        cc="director@playground.co.mz", attachment="logo.pdf"),
        ],
    }
    return parse_thread(raw, START, END, "boss@gmail.com")


# ---------------------------------------------------------------- windows

@pytest.mark.parametrize(
    "today, first, last",
    [
        (date(2026, 10, 20), date(2026, 10, 19), date(2026, 10, 19)),  # Tuesday -> Monday
        (date(2026, 10, 19), date(2026, 10, 16), date(2026, 10, 18)),  # Monday -> Fri..Sun
    ],
)
def test_review_window_default(today, first, last):
    start, end = review_window(today, TZ)
    assert start.date() == first
    assert (end.date() - date.resolution) == last
    assert start.tzinfo == TZ


def test_review_window_explicit_days():
    start, end = review_window(date(2026, 10, 20), TZ, date(2026, 10, 16), 5)
    assert start.date() == date(2026, 10, 12)
    assert end.date() == date(2026, 10, 17)


# ---------------------------------------------------------------- gmail

def test_query_uses_domain_and_window():
    q = build_query(config(), START, END)
    assert f"after:{int(START.timestamp())}" in q
    assert "from:playground.co.mz" in q and "cc:playground.co.mz" in q
    # Ana is on the team domain, so she is not listed separately.
    assert "ana.silva" not in q


def test_parse_thread_marks_window_and_strips_quotes():
    thread = vodacom_thread()
    assert [m.in_window for m in thread.messages] == [False, True]
    new = thread.window_messages[0]
    assert "old text" not in new.body
    assert new.attachments == ["logo.pdf"]
    assert new.cc == ["director@playground.co.mz"]
    assert thread.url.endswith("#all/t1")


def test_strip_quoted_portuguese_outlook_header():
    text = "Segue a proposta.\n\nDe: Joao\nEnviado: segunda\nPara: Ana\nAssunto: X\n\nold"
    assert strip_quoted(text) == "Segue a proposta."


def test_strip_quoted_keeps_from_inside_text():
    text = "From: our side we agree.\nThanks"
    assert strip_quoted(text) == text


def test_relevance_rules():
    cfg = config()
    assert is_relevant(vodacom_thread(), cfg)
    only_manager = parse_thread(
        {"id": "t2", "messages": [raw_message("m", "Fri, 16 Oct 2026 10:00:00 +0200",
                                              "director@playground.co.mz", "x@client.com", "Hi", "Hello")]},
        START, END, "boss@gmail.com")
    assert not is_relevant(only_manager, cfg)
    automatic = parse_thread(
        {"id": "t3", "messages": [raw_message("m", "Fri, 16 Oct 2026 10:00:00 +0200",
                                              "noreply@system.com", "ana.silva@playground.co.mz", "Alert", "x")]},
        START, END, "boss@gmail.com")
    assert not is_relevant(automatic, cfg)


def test_prompt_text_labels_people_and_context():
    text = thread_to_prompt_text(vodacom_thread(), config())
    assert "ana.silva@playground.co.mz [TEAM]" in text
    assert "director@playground.co.mz [MANAGEMENT]" in text
    assert "Earlier message (context only)" in text
    assert "NEW MESSAGE (in review window)" in text


def test_html_body_fallback():
    raw = {"id": "t4", "messages": [raw_message("m", "Fri, 16 Oct 2026 10:00:00 +0200", "a@x.com",
                                                "ana.silva@playground.co.mz", "S",
                                                "<p>Hello&nbsp;<b>team</b></p><p>Line 2</p>", html=True)]}
    thread = parse_thread(raw, START, END, "boss@gmail.com")
    assert "Hello" in thread.messages[0].body and "<b>" not in thread.messages[0].body


# ---------------------------------------------------------------- clickup

class FakeResponse:
    def __init__(self, payload, status=200):
        self.payload, self.status_code, self.headers = payload, status, {}

    def json(self):
        return self.payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(self.status_code)


class FakeSession:
    def __init__(self):
        self.calls = []

    def get(self, url, headers, params, timeout):
        self.calls.append(dict(params))
        page = dict(params)["page"]
        closed = dict(params)["include_closed"] == "true"
        if closed:
            return FakeResponse({"tasks": [raw_task("c1", "Old closed", status="complete")], "last_page": True})
        if page == "0":
            return FakeResponse({"tasks": [raw_task("a1", "A")], "last_page": False})
        return FakeResponse({"tasks": [raw_task("a2", "B"), raw_task("c1", "Old closed")], "last_page": True})


def test_clickup_pagination_and_dedupe():
    session = FakeSession()
    tasks = ClickUpClient(token="pk_x", session=session).fetch_tasks(config(), NOW)
    assert sorted(t.task_id for t in tasks) == ["a1", "a2", "c1"]
    assert {"space_ids[]", "date_updated_gt"} <= {k for c in session.calls for k in c}


def test_parse_task_fields():
    task = parse_task(raw_task("x", "Vodacom - Video", status="complete"))
    assert task.closed and task.assignees == ["ana.silva@playground.co.mz"]
    assert task.updated_at.tzinfo is not None


# ---------------------------------------------------------------- candidates

def test_tokens_remove_accents_and_stopwords():
    assert tokens("Revisão do vídeo para a Vodacom") == ["revisao", "video", "vodacom"]


def test_candidate_finder_ranks_relevant_task_first():
    tasks = [parse_task(raw_task(str(i), f"Unrelated task {i}", assignee="other@playground.co.mz",
                                 list_name="Admin")) for i in range(40)]
    tasks.append(parse_task(raw_task("v", "Vodacom - Video institucional revisão", assignee="other@playground.co.mz")))
    found = CandidateFinder(tasks, config(analysis={"max_candidate_tasks": 5})).find(vodacom_thread(), NOW)
    assert found[0].task_id == "v"
    assert len(found) <= 5


def test_candidate_finder_includes_recent_tasks_of_people_in_thread():
    tasks = [parse_task(raw_task("r", "Something worded differently", list_name="Misc"))]
    tasks += [parse_task(raw_task(str(i), f"Vodacom item {i}", assignee="x@playground.co.mz")) for i in range(30)]
    found = CandidateFinder(tasks, config(analysis={"max_candidate_tasks": 10})).find(vodacom_thread(), NOW)
    assert "r" in [t.task_id for t in found]


# ---------------------------------------------------------------- analysis rules

def _model_output(**item):
    base = {
        "summary": "Revise institutional video", "owner_email": "ana.silva@playground.co.mz",
        "client": "Vodacom", "item_type": "revision", "status": COVERED, "matched_task_ids": ["v"],
        "reason": "Matches task", "suggested_task_name": None, "due_date": None,
    }
    base.update(item)
    return {"thread_is_work": True, "skip_reason": None, "work_items": [base]}


def test_interpret_downgrades_covered_without_valid_task():
    cfg = config()
    cands = [parse_task(raw_task("v", "Vodacom video"))]
    result = interpret(_model_output(matched_task_ids=["invented"]), vodacom_thread(), cands, cfg)
    assert result.items[0].status == UNCERTAIN and result.items[0].matched_task_ids == []


def test_interpret_rejects_owner_not_in_thread():
    result = interpret(_model_output(owner_email="someone@playground.co.mz"), vodacom_thread(), [], config())
    assert result.items[0].owner_email is None


def test_interpret_ignores_items_when_not_work():
    data = _model_output()
    data["thread_is_work"] = False
    assert interpret(data, vodacom_thread(), [], config()).items == []


class FakeMessages:
    def __init__(self, payload, stop="end_turn"):
        self.payload, self.stop, self.kwargs = payload, stop, None

    def create(self, **kwargs):
        self.kwargs = kwargs
        return SimpleNamespace(
            stop_reason=self.stop,
            content=[SimpleNamespace(type="text", text=json.dumps(self.payload))],
        )


def fake_client(payload, stop="end_turn"):
    messages = FakeMessages(payload, stop)
    return SimpleNamespace(beta=SimpleNamespace(messages=messages)), messages


def test_analyzer_request_shape():
    client, messages = fake_client(_model_output())
    cands = [parse_task(raw_task("v", "Vodacom video"))]
    result = Analyzer(config(), client=client).analyse(vodacom_thread(), cands)
    assert result.items[0].status == COVERED
    kw = messages.kwargs
    assert kw["model"] == "claude-opus-5-5"
    assert kw["output_config"]["format"]["type"] == "json_schema"
    assert kw["fallbacks"] == "default"
    assert "Vodacom video" in kw["messages"][0]["content"]
    assert "European Portuguese" not in kw["system"]  # test config is English


def test_analyzer_refusal_becomes_error():
    client, _ = fake_client({}, stop="refusal")
    result = Analyzer(config(), client=client).analyse(vodacom_thread(), [])
    assert result.error and not result.items


def test_policy_notes_reach_prompt():
    cfg = config(analysis={"policy_notes": "Invoices are out of scope."})
    assert "Invoices are out of scope." in analyzer_mod.build_system_prompt(cfg)


# ---------------------------------------------------------------- report

def _results():
    cfg = config()
    thread = vodacom_thread()
    tasks = [parse_task(raw_task("v", "Vodacom video"))]
    data = {"thread_is_work": True, "skip_reason": None, "work_items": [
        _model_output()["work_items"][0],
        _model_output(summary="Send quote <b>", status=MISSING, matched_task_ids=[],
                      suggested_task_name="Vodacom - Quote")["work_items"][0],
        _model_output(summary="Unclear", status=UNCERTAIN, owner_email=None)["work_items"][0],
    ]}
    return cfg, tasks, [interpret(data, thread, tasks, cfg)]


def test_report_stats_and_rendering():
    cfg, tasks, results = _results()
    report = build_report(results, tasks, cfg, START, END, capped=False)
    totals = report.totals
    assert (totals.total, totals.covered, totals.missing, totals.uncertain) == (3, 1, 1, 1)
    ana = report.people[0]
    assert ana.name == "Ana Silva" and ana.rate == 0.5
    assert report.period_label == "16/10/2026"
    html = render_html(report, cfg)
    assert "Send quote &lt;b&gt;" in html  # escaped
    assert "https://app.clickup.com/t/v" in html
    assert "Owner not identified" in html
    assert "1 missing" in subject_line(report, cfg)
    assert "Vodacom - Quote" in render_text(report, cfg)


def test_portuguese_report_and_nudge():
    cfg, tasks, results = _results()
    cfg.language = "pt"
    report = build_report(results, tasks, cfg, START, END, capped=True)
    html = render_html(report, cfg)
    assert "Em falta" in html and "limite de 150" in html
    subject, nudge_html, text = render_nudge(report.people[0], report.by_status(MISSING), report, cfg)
    assert subject.startswith("ClickUp: 1 pedido")
    assert "Olá Ana" in text and "Vodacom - Quote" in nudge_html


def test_empty_report():
    cfg = config()
    report = build_report([], [], cfg, START, END, capped=False)
    assert "No work requests" in render_html(report, cfg)
    assert report.totals.rate is None
