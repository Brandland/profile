# Email vs ClickUp daily check

Every working morning this tool reviews the previous day's team emails, finds the work that was
requested or promised, and checks whether each piece of work has a task in the ClickUp Space.
It then emails a short report: registration rate per person, the work with no task, and the
cases to confirm.

On Monday it reviews Friday, Saturday and Sunday.

## How it decides

1. **Gmail.** It searches the mailbox for threads with a `@playground.co.mz` address (from, to or
   cc) in the review period. Automatic mail (no-reply, notifications), promotions and threads where
   only management took part are dropped. Quoted reply history is removed so each message only
   carries what is new.
2. **ClickUp.** It loads all open tasks in the Space, plus tasks closed in the last 45 days.
3. **Shortlist.** For each thread it picks the 30 most likely tasks: tasks sharing client,
   project or subject words with the email, and recent tasks assigned to the team members in the
   thread.
4. **Claude.** Claude reads the thread and the shortlist and returns, for each work item:
   a one-line summary, the owner, and one of three results:
   - **Registado / In ClickUp**: a task clearly covers it (a broader task such as a monthly
     retainer task counts).
   - **A confirmar / To confirm**: a task may cover it, but it is not clear.
   - **Em falta / Missing**: no task corresponds. A task name is suggested.

   Only work from the new messages is judged. Requests from earlier days are context, so the same
   request is not reported every day.
5. **Checks in code.** "Covered" without a real task link becomes "to confirm". An owner must be a
   team member who is on the thread, otherwise the item goes to "owner not identified".
6. **Report.** Sent by email from the same Gmail account. Optionally each person also receives
   their own list of missing items (`send_individual_nudges`).

The registration rate is `covered / all work items`. "To confirm" counts as not registered, which
pushes people to name tasks clearly.

## What it cannot see

- Emails that never reach this mailbox. If you are not in copy, the tool does not see the thread.
  The coverage is as wide as your mailbox.
- Work agreed by phone, WhatsApp or in meetings.
- The shortlist is automatic. If a task has a name that shares nothing with the email and is not
  assigned to someone on the thread, the tool may report it as missing. Check "Missing" items
  before acting on them, especially in the first weeks.

## Setup (about 30 minutes, once)

You need four things: a ClickUp token, a Claude API key, Gmail access, and the configuration.

### 1. ClickUp

1. In ClickUp: avatar > **Settings** > **Apps** > **API Token** > Generate. It starts with `pk_`.
   Use the account of someone who can see the whole Space.
2. Find the workspace and Space IDs (on any computer with Python):
   ```bash
   cd email-clickup-crosscheck
   pip install -r requirements.txt
   CLICKUP_API_TOKEN=pk_... python -m crosscheck spaces
   ```

### 2. Claude API key

Create a key at <https://platform.claude.com> (Settings > API keys). Set a monthly spend limit
there as a safety net.

### 3. Gmail access (Google Cloud, free)

1. Go to <https://console.cloud.google.com>, create a project (e.g. "Playground ClickUp check").
2. **APIs & Services > Library**: enable **Gmail API**.
3. **APIs & Services > OAuth consent screen**: user type **External**, fill in the app name and
   your email. Add the scopes `gmail.readonly` and `gmail.send`. Add your Gmail address as a
   test user.
4. Then click **Publish app** (status "In production"). This matters: while the app is in
   "Testing", Google expires the access every 7 days and the daily run stops. You do not need
   Google verification for your own use; you will see an "unverified app" warning once, click
   *Advanced > Continue*.
5. **APIs & Services > Credentials > Create credentials > OAuth client ID**, type
   **Desktop app**. Download the JSON file.
6. On your computer:
   ```bash
   pip install google-auth-oauthlib
   python scripts/get_gmail_token.py ~/Downloads/client_secret_XXXX.json
   ```
   Sign in with the Gmail account that receives the team emails. The script prints
   `GMAIL_CLIENT_ID`, `GMAIL_CLIENT_SECRET` and `GMAIL_REFRESH_TOKEN`.

### 4. Configuration

Copy `config.example.yaml`, fill in the mailbox, ClickUp IDs, management addresses and the
`policy_notes` (your own rules in plain language, e.g. what finance handles outside ClickUp).

### 5. GitHub secrets

In GitHub: repository **Settings > Secrets and variables > Actions > New repository secret**.
Create:

| Secret | Value |
|---|---|
| `CROSSCHECK_CONFIG` | the full text of your config file |
| `ANTHROPIC_API_KEY` | Claude API key |
| `CLICKUP_API_TOKEN` | ClickUp token |
| `GMAIL_CLIENT_ID` | from step 3 |
| `GMAIL_CLIENT_SECRET` | from step 3 |
| `GMAIL_REFRESH_TOKEN` | from step 3 |

### 6. First run

The schedule only runs from the default branch, so this folder and
`.github/workflows/email-clickup-crosscheck.yml` must be merged into `master` first.

Then: **Actions > Email vs ClickUp daily check > Run workflow**. Leave the fields empty to review
the previous working day, or pick a date. The report arrives by email in a few minutes.

To run on your own computer instead (the report is saved as a file, nothing is sent):
```bash
export ANTHROPIC_API_KEY=... CLICKUP_API_TOKEN=... GMAIL_CLIENT_ID=... \
       GMAIL_CLIENT_SECRET=... GMAIL_REFRESH_TOKEN=...
python -m crosscheck run --config config.yaml --no-email --output report.html
```

## Privacy

This repository is **public**. The tool is built so that nothing confidential lands in it:
configuration and credentials are GitHub secrets, logs only contain counts, and the report is only
sent by email (never uploaded as a file to GitHub). Even so, moving this folder to a private
repository is the better long-term home for internal tools.

Email content is sent to the Claude API for analysis. Under Anthropic's commercial terms, API
data is not used to train models.

## Cost (estimate)

Each thread costs roughly USD 0.04 to 0.08 with Claude Opus 5.5 at medium effort. At 50 to 80
relevant threads per day that is about USD 2 to 6 per day, or USD 50 to 120 per month. The
`max_threads` setting caps each run. Once the pilot shows the quality is right, a cheaper model
(`claude-sonnet-5-5`) can be tested by changing `analysis.model`; compare a week of reports
before switching.

## Development

```bash
pip install -r requirements.txt pytest
python -m pytest -q
```

Code map: `gmail_client.py` (search, parsing, sending), `clickup_client.py` (tasks),
`candidates.py` (shortlist), `analyzer.py` (Claude prompt and rules), `report.py` (report and
reminders), `main.py` (review period and orchestration).
