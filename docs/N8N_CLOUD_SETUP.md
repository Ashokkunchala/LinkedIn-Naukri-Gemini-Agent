# n8n Cloud setup — LinkedIn-Naukri-Gemini-Agent

This workflow is an **importable starter**, not an active service. It has no embedded credentials and is exported inactive by design. It processes job-alert emails rather than scraping LinkedIn or Naukri.

## What it does

1. Polls a Gmail label named `job-alerts` every 5 minutes.
2. Fetches the alert email body.
3. Sends the alert text and your candidate profile to Gemini for structured job extraction and fit scoring.
4. Filters jobs at a default fit score of 70/100.
5. Sends each qualifying match to both Telegram and email.
6. Does not apply for jobs, message recruiters, or modify either platform account.

The Schedule/Gmail trigger cadence controls email intake, **not when LinkedIn/Naukri generate their alerts**. LinkedIn supports daily or weekly job-alert emails, and Naukri job alerts are sent to email; therefore an end-to-end alert can arrive later than five minutes.

## Prerequisites

- An n8n Cloud account with permission to create/import workflows.
- Gmail or Google Workspace mailbox receiving both platforms' job-alert emails.
- Gemini API key from Google AI Studio.
- Telegram account and a bot created through Telegram's official BotFather.
- An alert email address (can be the connected Gmail account).

## 1. Enable native job-alert emails

**LinkedIn**
1. Open LinkedIn and search for a role/location you want.
2. Turn on **Job alert** for that search.
3. Open **Manage alerts** and enable email notifications. LinkedIn's documented alert cadence is daily or weekly, not every five minutes.
4. Use relevant searches for role, location, and seniority rather than scraping pages.

Official help: https://www.linkedin.com/help/linkedin/answer/a511279/job-alerts-on-linkedin

**Naukri**
1. Sign in to Naukri and create job alerts using role, experience, location, and salary preferences.
2. Ensure alerts are delivered to the mailbox connected to n8n.

Official help: https://resume.naukri.com/frequently-asked-questions-faq/how-to-create-free-job-alerts/

## 2. Label the source emails in Gmail

Create a Gmail label named `job-alerts`. Create Gmail filters for LinkedIn and Naukri alert emails that apply this label. Use the sender addresses shown in your own received alerts; sender addresses can vary. Test each filter by applying it to one existing alert email. The workflow's Gmail trigger listens for `label:job-alerts`.

## 3. Import into n8n Cloud

1. Download `n8n/workflows/linkedin-naukri-gemini-alerts.json` from this repository.
2. In n8n, create a workflow and choose **Import from File** (menu wording may vary).
3. Keep it inactive while configuring credentials and testing.

## 4. Connect credentials

- **New Job Alert Email** and **Fetch Email Body**: select the same Gmail OAuth2 credential. Grant only the Gmail permissions requested by n8n.
- **Gemini Job Matching**: create an HTTP Header Auth credential with header name `x-goog-api-key` and value your Gemini API key. Select that credential on the HTTP Request node. Do not put the key in the URL, workflow JSON, or repository.
- **Send Telegram Alert**: create a Telegram bot via https://t.me/BotFather, store its token in an n8n Telegram credential, and select it on this node. Start a chat with the bot (or add it to your intended group) and obtain the correct chat ID.
- **Send Email Alert**: select your Gmail OAuth2 credential. Replace `REPLACE_WITH_YOUR_ALERT_EMAIL` with the destination address.
- Replace `REPLACE_WITH_TELEGRAM_CHAT_ID` with your Telegram chat ID.

## 5. Personalize the match

Open **Prepare Alert + Candidate Profile** and replace the `candidateProfile` placeholder with a concise, factual profile: target roles, skills, years of experience, location, salary range, notice period, and work preferences. Avoid account passwords, government IDs, or unnecessary personal information. Set `scoreThreshold = 70` to your preferred value.

The workflow sends job alert email content and the profile to Gemini. Review Google's current API terms and data handling before sharing personal data.

## 6. Test safely before activation

1. Keep the workflow inactive and run a manual test using a real alert email already in the labelled mailbox.
2. Verify the Gmail nodes can read the message body.
3. Verify the HTTP Request node returns Gemini JSON and the **Join Email + Gemini Result** merge contains both email metadata and Gemini response. n8n node versions can differ; adjust node parameters if your workspace shows validation warnings.
4. Test Telegram and email nodes with a low-risk test message.
5. Confirm low-scoring jobs do not alert and matching jobs reach both channels.
6. Verify no application or profile-edit nodes are present.
7. Review execution logs for exposed personal data; limit execution-data retention if available.
8. Publish/activate only after all tests pass.

## Rate limits and timing

- n8n's Schedule Trigger supports a five-minute interval; Gmail Trigger polling is separately configured. Cloud plan execution and concurrency limits still apply.
- LinkedIn documents job alerts as daily or weekly. Five-minute polling cannot force LinkedIn to send jobs more often.
- Naukri's native email alert frequency is controlled by Naukri; this workflow does not query its internal website/API.
- Gemini API quotas depend on model, project, and billing tier. Handle quota/rate-limit errors with retries/backoff; do not repeatedly hammer the endpoint.
- No direct LinkedIn/Naukri API connector is included. Add one only with documented authorization and permitted scopes.

## Approval gate

This workflow only scores and notifies. It has no nodes that submit applications, send recruiter messages, or edit account settings. If application automation is added later, it must stop at a human approval step and require a fresh review of the exact application payload before any external action.

## Activation status

**Not active.** This file is not deployed to an n8n account, and credentials have not been connected or tested. Successful deployment must be verified in n8n execution history before describing monitoring as active.
