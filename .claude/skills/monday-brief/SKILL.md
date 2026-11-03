---
name: monday-brief
description: Produce Miguel's one-page Monday management brief for Playground from ClickUp, Gmail and Google Calendar, and republish it to the standing brief page. Use when Miguel types /monday-brief or asks for the Monday brief, the weekly brief, or "what needs my attention this week".
---

# Monday management brief

You are producing a one-page management brief for Miguel Proença, CEO of Playground (Maputo, Mozambique, around 30 to 35 people, 100+ projects a year). The purpose is visibility without asking the team for updates. Timezone is CAT (Africa/Maputo).

The brief lives at a fixed page: https://claude.ai/artifact/T4hAfmaeF51hw6iqHC1Asf. You update that page in place so Miguel always opens the same link. Read it first with the Artifact tool (`action: "read"`), keep its design and structure, and replace the content.

## Rules

Read-only. Never send or reply to email, never change a ClickUp task, never move a calendar event. Report; Miguel decides.

Do not invent. If a source fails, say so in one line at the top of the brief and continue with what you have.

Leave personal email out unless it concerns Playground, Southwise, Profile, BBrands or the EMBA. School, family, condominium and bank items are out.

Keep names, task titles and quotes in the language they appear in. Write the rest in English.

One page. Plain paragraphs where they read better, short lists where a list is clearer. No icons, no bold on every line, no corporate language. Sound like a sharp chief of staff, direct and warm.

## Sources and how to read them

### ClickUp
Workspace 1200450000017344. Client work is in space CLIENTES (1200450000071542), one folder per client, sub-folders or lists per project (codes like SAS.26.001, COR.26.003, PCD-26-001). New business and tenders are in GROWTH (1200450000076869). Internal work is under the folders PLAYGROUND, Playground(Interno) and the OPERATIONS space; include internal items only when they block clients or are high priority.

Call `clickup_get_user` first for the current date. Then `clickup_filter_tasks` on the two spaces with `subtasks: false`, fields status, assignees, due_date, date_updated, list, priority:
- overdue: `due_date_to` = yesterday, ordered by due_date ascending, all pages;
- this week: `due_date_from` = Monday, `due_date_to` = Sunday.
Treat statuses complete, completed, closed, done and cancelled as finished and leave them out. Statuses "sent to client" and "revert" mean waiting on someone. Flag tasks that are unassigned, priority urgent or high, or untouched (date_updated) for more than 14 days. Group by client folder; when the list name does not identify the client, use the task's project code or title.

### Gmail
The connector reads Miguel's personal Gmail. His Playground mailbox (miguel.proenca@playground.co.mz) already sends two automated notes to it: a daily "Inbox digest" and a Sunday "Weekly agenda". These cover both mailboxes and are the best email source. Search `subject:"Inbox digest" newer_than:4d` and `subject:"Weekly agenda" newer_than:8d`, read the most recent of each with `get_thread` (PLAIN_TEXT), and take the "Waiting on you", "Waiting on others", "Needs your reply" and "Money and contracts" items from them. Then search the inbox for the last 7 days (`in:inbox newer_than:7d -category:promotions -category:updates`) for any client or partner thread where the last sender is outside playground.co.mz and nobody from Playground replied. Ignore newsletters, bank notices, school and automatic mail.

### Google Calendar
Use the primary calendar (miguelalmeidaproenca@gmail.com) for Monday to Sunday of this week, plus the following week. Skip personal routines (Daily Shutdown, FlowState, Get Home, Casa, PT training, Learning Hour, Wins Journal, Weekly Review). Report external meetings (attendees outside playground.co.mz and gmail.com), days with more than four hours of meetings, duplicate or overlapping events, all-day travel markers, and anything in the next two weeks that needs preparation (pitches, client presentations, events, speeches). The list_events result is large; write it to a file and summarise with jq.

## Structure of the page

1. Header: "Week of [Monday date]", prepared date and time, sources, and one note line if a source failed or if the edition is a mid-week test.
2. Three things that need your attention this week. Three items, each with a short bold headline and one paragraph saying what the issue is and why it matters. Choose by judgement across all sources, not by counts. Cash already earned but not invoiced or collected, clients waiting more than a week, stalled large projects and security or operational risks rank highest.
3. Clients waiting on Playground. A table: client, what they are waiting for, who on our side, days waiting. Longest first. Eight rows at most, then "and N more".
4. Projects and tasks at risk. Grouped by client, with assignee. Only items that are overdue, unassigned, urgent or stalled. Keep it tight.
5. Your week. Day by day for the working days left, then a paragraph on next week and anything that needs preparation now. Mention duplicates, clashes and travel.
6. One question for you. One specific decision Miguel should make this week, based on what you found, with the one-line action that follows from each answer.
7. Footer: read-only statement, refresh schedule, how to run on demand.

## Publishing

Edit the HTML file you read from the artifact and republish to the same URL with the Artifact tool. Keep the `<title>` "Playground Monday Brief". Use a `label` like "Week of 9 Nov 2026". When done, reply with the three attention items in three short sentences and the link. Do not pin, share or create a new artifact.
