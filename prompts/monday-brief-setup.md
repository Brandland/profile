# Prompt: build and schedule my Monday management brief

Paste everything below this line into a new Claude Code session. Where you see [square brackets], fill in your own details first, or leave them and Claude will ask you.

---

I want you to build a Monday management brief for me and put it on a weekly schedule. Read the whole request before you start, then confirm your understanding with me in a few sentences before building anything.

## Who I am and why I want this

I am Miguel Proença, CEO of Playground, a communication, marketing and strategic advisory company in Maputo, Mozambique, with a team of around 30 to 35 people and more than 100 projects per year. I am trying to move from being involved in every operational issue towards stronger strategic leadership. The problem this brief solves is visibility. I want to know, every Monday morning, what needs my attention this week without asking my team for updates. My team keeps working in their normal tools. I read one page.

My timezone is CAT (UTC+2). I want the brief ready by 07:00 on Monday.

## Where the information lives

You have access to three connected tools. Use only these three. Do not try to connect anything else.

ClickUp is where our projects and tasks live. [My workspace is called X. Client projects are organised as: one Space per client / one Folder per client / one List per project. Tell Claude which it is, or let it look at the hierarchy and ask you.] The things I care about from ClickUp are: tasks overdue by more than two days, tasks due this week that are still unassigned or have no progress, projects that have had no activity in the last 10 days, and any task that has been in the same status for more than 14 days.

Gmail is where client communication happens. The thing I care about is: threads where a client or partner sent the last message, more than two working days ago, and nobody from Playground has replied. Our domain is [playground.co.mz or whatever yours is]. Treat any thread where the last sender is outside our domain and the thread is unanswered as "waiting on Playground". Ignore newsletters, notifications, automatic emails and anything that is clearly not a person writing to us. If a thread is marked with the label [Clients, if you use one], prioritise it.

Google Calendar is where my commitments are. I care about: every meeting this week with external participants, any day with more than four hours of meetings, meetings with no agenda or description, and anything in the next two weeks that looks like a deadline, a pitch, a presentation or a board or client meeting I should prepare for.

## What the brief should look like

One page. If it does not fit on one page, you are including too much. Plain language, normal paragraphs where paragraphs make sense, short lists only where a list is clearer. No decorative icons, no bold on every line, no separators, no corporate language.

The structure is:

1. Three things that need my attention this week. Pick the three most important issues across all three sources and say in one or two sentences each what the issue is and why it matters. If there is a client waiting on us for a week, that goes here. If a large project has stalled, that goes here. Use judgement, not just counts.

2. Clients waiting on Playground. A short list: client name, subject of the thread, who at Playground was last involved, and how many days it has been waiting. Longest wait first. If there are more than eight, show the eight oldest and say how many more there are.

3. Projects and tasks. Overdue items grouped by project, with the assignee. Stalled projects with the last activity date. Keep this section tight. I do not need every task, I need the ones that are at risk.

4. My week. The external meetings and the preparation they need, the heavy days, and anything coming in the next two weeks I should start preparing for now.

5. One question for me. End with one specific question you think I should answer or one decision I should make this week, based on what you found. Not a generic question. Something like "The [client] proposal has been waiting 9 days for a reply from [person]. Do you want to follow up yourself or ask [person] to?"

Write it as if a sharp chief of staff wrote it for me. Direct, warm, no padding. Do not start with a summary of what you did. Start with the content.

## Rules

Read-only. You never send emails, never reply to anyone, never change a task in ClickUp, never move a calendar event. You read and you report. If you think something should be done, say so in the brief and let me decide.

Do not invent information. If a source is unavailable or a connector fails, say so at the top of the brief in one line and produce the brief with what you have.

Do not include anything from my personal email that is not related to Playground, Southwise or my EMBA. If you are unsure whether an email is personal, leave it out.

Keep the brief in English unless the source material is in Portuguese, in which case keep names, subjects and quotes as they are.

## Where to put the brief

Save each brief as a Claude Doc titled "Monday Brief, [date]". [Alternative: save it as a page in Notion under X, or as a Google Doc in the Drive folder Y. Choose one and delete the others.] Then send me a short message with the three attention items and the link.

## How to build it

Step 1. Before building anything, look at my ClickUp workspace hierarchy, a sample of recent Gmail threads and my calendar for this week, and come back to me with any questions about how our data is actually organised. Do not assume. For example, you need to confirm how to tell a client project from an internal one, and how to recognise a Playground email address.

Step 2. Create a skill called `monday-brief` in this repository under `.claude/skills/monday-brief/SKILL.md` that contains the full instructions above, so I can also run it on demand by typing `/monday-brief` on any day.

Step 3. Run the brief once now, for the current week, and show it to me. I will give you feedback on what is useful and what is noise. Adjust the skill based on my feedback.

Step 4. Only after I approve the test run, schedule it as a weekly task that runs every Monday at 06:30 CAT, in a fresh session, with access to ClickUp, Gmail and Google Calendar only. Tell me exactly what you scheduled and how I can pause or change it.

Step 5. Commit the skill and this prompt to the repository with a clear commit message.

## What good looks like

In three months, I should open the brief on Monday, read it in five minutes, and know which clients are waiting, which projects are at risk, and what my week looks like, without having asked anyone. If the brief regularly tells me things I already knew or does not tell me things I later discover were important, it is not working and we adjust it.
