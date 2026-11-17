---
name: team-board
description: Refresh the Playground Team Board, the tap-through dashboard of who is doing what (open, overdue and completed tasks and logged hours per person and per client) from ClickUp, and republish it. Use when Miguel types /team-board or asks to refresh the team dashboard, the workload board, or "who is working on what".
---

# Team board refresh

The board lives at a fixed page: https://claude.ai/artifact/5SsVLSf99kLbep7gFbHCCg. The page itself (`brief/team-dashboard.html` in this repo) does not change on a refresh; only its data file `team-data.json` does. Read-only towards ClickUp: never create, update or delete anything there.

## What to produce

Regenerate `brief/team-data.json` with the schema below, then republish:

```
Artifact publish, file_path brief/team-dashboard.html, url https://claude.ai/artifact/5SsVLSf99kLbep7gFbHCCg,
files {"team-data.json": "brief/team-data.json"}, label "Snapshot <date>"
```

Then commit both files and reply with four lines at most: the totals line, who has the most open and overdue tasks, how many people logged hours, and the link.

## Where the data comes from

Workspace 1200450000017344, timezone Africa/Maputo. Call `clickup_get_user` first for today's date; the week runs Monday to Sunday.

Spaces: CLIENTES 1200450000071542 (one folder per client, sub-folders per project), GROWTH 1200450000076869 (new business, tenders), OPERATIONS 1200450000073476 (internal). Build a list_id -> client map with `clickup_get_workspace_hierarchy` max_depth "2": client = top-level folder under CLIENTES; folders PLAYGROUND, Playground(Interno), Profile and everything in OPERATIONS = "Internal"; GROWTH = "New business" with the folder name in `project`.

Statuses. Finished: complete, completed, closed, done, cancelled. Waiting (open, group "waiting"): sent to client, revert, on hold, int approval, int. approval, pending, in review, planning. Everything else open is "active".

Tasks: `clickup_filter_tasks` on the three spaces, subtasks false, fields status, assignees, due_date, date_updated, date_closed, list, priority. Run (a) due_date_to = end of next month, all pages; (b) order_by updated, first 3 pages, to catch open tasks with no due date; (c) date_closed_from = 14 days ago, include_closed true, all pages. Deduplicate by id. Epoch strings are milliseconds.

Time entries: `clickup_get_time_entries` with assignee ["any"]. Known problems: plain-date queries are date-shifted and only return entries fully inside the window, so query each day with explicit "YYYY-MM-DD 00:00" to "YYYY-MM-DD 23:59" plus a 20:00 to 04:00 night window; entries with no task make the tool fail with an outputSchema error, so when a window fails, split it, and if it still fails, record it in data_quality.notes and move on (or fetch per task for that person's tasks). Ignore entries under 5 minutes. Hours are decimal, 1 decimal place.

Names: "afonso.mulungo@..." -> Afonso Mulungo, "esmenia.macie@..." -> Esménia Macie, id 112610402 -> Lúria Mabui, "Elton Victor José Macuácua" -> Elton Macuácua, merge "MIGUEL ALMEIDA PROENCA" and "Miguel Playground" into Miguel Proença (id 246151538).

## Schema of team-data.json

```
{"generated_at": ISO+02:00, "week_start": "YYYY-MM-DD", "hours_window": {"from","to"},
 "totals": {"open","overdue","due_this_week","completed_14d","hours","people_with_hours","people_active"},
 "people": [{"id","name","first","initials","open","active","waiting","overdue","due_this_week","completed_14d","hours",
             "hours_by_day": {"YYYY-MM-DD": h}, "clients": [{"name","open","overdue","completed_14d","hours"}],
             "tasks": [{"id","name","client","status","group":"active|waiting|done","due","overdue","priority","updated","hours","url"}]}],
 "clients": [{"name","open","overdue","completed_14d","hours","people":[names]}],
 "unassigned": [{"id","name","client","status","due","overdue","priority","url"}],
 "data_quality": {"tasks_fetched","time_entries","notes":[...]}}
```

A task counts for every assignee. overdue = open and due before this Monday. due_this_week = open and due this Monday to Sunday. completed_14d = finished and date_closed (else date_updated) within 14 days. Per person, tasks = all open plus completed_14d, sorted overdue first (oldest due), then open by due (no date last), then done by updated desc, capped at 80. People sorted by open desc; include anyone with a task or an hour. Clients sorted by open desc.

A reusable generator from a previous run is in the repo at `brief/scripts/build.py` if present; prefer adapting it over rewriting.
