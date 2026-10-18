"""One-time helper: authorise the app to read the mailbox and send the report.

Run this on your own computer (not on the server):

    pip install google-auth-oauthlib
    python scripts/get_gmail_token.py path/to/client_secret.json

A browser window opens. Sign in with the mailbox that receives the team emails
and accept. The script prints the three values to store as GitHub secrets.
"""

import json
import sys

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
]


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("Usage: python scripts/get_gmail_token.py client_secret.json")
    flow = InstalledAppFlow.from_client_secrets_file(sys.argv[1], SCOPES)
    creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")
    with open(sys.argv[1], encoding="utf-8") as f:
        client = json.load(f)
    client = client.get("installed") or client.get("web") or {}
    print("\nStore these as GitHub repository secrets:\n")
    print(f"GMAIL_CLIENT_ID      = {client.get('client_id')}")
    print(f"GMAIL_CLIENT_SECRET  = {client.get('client_secret')}")
    print(f"GMAIL_REFRESH_TOKEN  = {creds.refresh_token}")
    print("\nDo not save these values in the repository.")


if __name__ == "__main__":
    main()
