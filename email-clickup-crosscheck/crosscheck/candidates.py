"""Picks the ClickUp tasks most likely to correspond to an email thread.

The Space can hold hundreds of tasks, so we do not send all of them to the
model for every thread. We shortlist by:
  1. word overlap between the thread and the task (weighted so that rare
     words such as client or project names count more than common ones), and
  2. recent tasks assigned to the team members in the thread, which catches
     tasks that were created with a different wording from the email.
"""

from __future__ import annotations

import math
import re
import unicodedata
from collections import Counter
from datetime import datetime, timedelta

from .config import Config
from .models import ClickUpTask, EmailThread

STOPWORDS = set(
    """
    the and for are with this that from you your our have has was were will would
    could should can please thanks thank regards dear hello best kind also just about
    into more than then them they their there here what when where which who why how
    all any some one two not but its it's let know need needs send sent see attached
    find below above today tomorrow week next new email mail message re fw fwd
    para com uma que por mais como dos das nos nas aos este esta isto esse essa
    isso pelo pela pelos pelas ser sao são foi tem temos ter vamos favor obrigado
    obrigada cumprimentos caro cara bom boa dia tarde noite enviar envio segue anexo
    anexos abaixo acima hoje amanha amanhã semana proxima próxima ainda sobre muito
    bem sim não nao ate até apos após entre sem sua seu suas seus nossa nosso
    """.split()
)


def normalise(text: str) -> str:
    text = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in text if not unicodedata.combining(c))


def tokens(text: str) -> list[str]:
    words = re.findall(r"[a-z0-9]{3,}", normalise(text))
    return [w for w in words if w not in STOPWORDS and not w.isdigit()]


def _task_text(task: ClickUpTask) -> tuple[list[str], list[str]]:
    strong = tokens(f"{task.name} {task.list_name} {task.folder_name} {' '.join(task.tags)}")
    weak = tokens(task.description[:1500])
    return strong, weak


def _thread_text(thread: EmailThread) -> tuple[list[str], list[str]]:
    external_domains = []
    for addr in thread.participants(window_only=False):
        domain = addr.rsplit("@", 1)[-1]
        external_domains.append(domain.split(".")[0])
    strong = tokens(f"{thread.subject} {' '.join(external_domains)}")
    weak = tokens(" ".join(m.body[:3000] for m in thread.window_messages))
    return strong, weak


class CandidateFinder:
    def __init__(self, tasks: list[ClickUpTask], config: Config):
        self.tasks = tasks
        self.config = config
        self._task_tokens = [_task_text(t) for t in tasks]
        df = Counter()
        for strong, weak in self._task_tokens:
            df.update(set(strong) | set(weak))
        n = max(1, len(tasks))
        self._idf = {w: math.log(1 + n / c) for w, c in df.items()}

    def _score(self, thread_strong: set[str], thread_weak: set[str], idx: int) -> float:
        strong, weak = self._task_tokens[idx]
        s_strong, s_weak = set(strong), set(weak)
        score = 0.0
        for w in s_strong:
            idf = self._idf.get(w, 0.0)
            if w in thread_strong:
                score += 3.0 * idf
            elif w in thread_weak:
                score += 1.5 * idf
        for w in s_weak - s_strong:
            idf = self._idf.get(w, 0.0)
            if w in thread_strong:
                score += 1.0 * idf
            elif w in thread_weak:
                score += 0.3 * idf
        return score

    def find(self, thread: EmailThread, now: datetime) -> list[ClickUpTask]:
        limit = self.config.max_candidates
        strong, weak = _thread_text(thread)
        thread_strong, thread_weak = set(strong), set(weak)
        scored = [
            (self._score(thread_strong, thread_weak, i), i) for i in range(len(self.tasks))
        ]
        scored = [(s, i) for s, i in scored if s > 0]
        scored.sort(reverse=True)

        picked: list[int] = [i for _, i in scored[: max(1, limit * 2 // 3)]]

        # Recent tasks owned by the team members on the thread.
        people = {
            a for a in thread.participants(window_only=True) if self.config.is_team_address(a)
        }
        recent_cut = now - timedelta(days=14)
        def last_activity(t: ClickUpTask) -> datetime:
            return t.updated_at or t.created_at or datetime.min.replace(tzinfo=now.tzinfo)

        recent = [
            i
            for i, t in enumerate(self.tasks)
            if people.intersection(t.assignees) and last_activity(t) >= recent_cut
        ]
        recent.sort(key=lambda i: last_activity(self.tasks[i]), reverse=True)
        for i in recent:
            if len(picked) >= limit:
                break
            if i not in picked:
                picked.append(i)

        # Fill the remaining places with the next best word matches.
        for _, i in scored:
            if len(picked) >= limit:
                break
            if i not in picked:
                picked.append(i)
        return [self.tasks[i] for i in picked[:limit]]
