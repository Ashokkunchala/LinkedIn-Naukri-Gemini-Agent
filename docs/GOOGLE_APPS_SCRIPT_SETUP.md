# Free-first hosted deployment: Google Apps Script

Recommended for a personal no-local-setup workflow. The code runs on Google's infrastructure, checks a Gmail label every five minutes, calls Gemini, deduplicates qualifying jobs, and sends alerts to Telegram and email. It does not scrape LinkedIn/Naukri, apply for jobs, message recruiters, or change account settings.

## Setup
1. Create LinkedIn Job Alerts and Naukri job alerts. Make sure they arrive in Gmail. Platform email frequency is controlled by the platform, so five-minute inbox polling does not guarantee five-minute job discovery.
2. Create a Gmail label `job-alerts` and filters using the real sender addresses from your own inbox.
3. Open https://script.google.com/ and create a new Apps Script project.
4. Copy `apps-script/Code.gs` from this repository into the editor.
5. In Project Settings, enable the `appsscript.json` manifest editor if you want to use the included manifest.
6. Add these Script Properties separately (never commit secrets): `GEMINI_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `ALERT_EMAIL`, `CANDIDATE_PROFILE`.
7. Run `testConnections`, authorize the requested scopes, and confirm test messages arrive in Telegram and email.
8. Run `setupCareerAgent` to create the five-minute trigger. Check the Apps Script Executions page and test a real labelled job-alert email before relying on it.

## Cost and limits
Apps Script avoids a separate hosting subscription for ordinary personal use, but Google quotas apply and can change: https://developers.google.com/apps-script/guides/services/quotas. Five-minute triggers are supported: https://developers.google.com/apps-script/reference/script/clock-trigger-builder. Gemini free-tier availability and limits vary by model and account: https://ai.google.dev/gemini-api/docs/pricing. Telegram bot messaging is normally free.

The workflow only scores and notifies; applications, recruiter messages, and account changes remain manual and approval-gated. Do not scrape pages, reuse browser cookies, or call undocumented endpoints. Monitoring is not active until the script is deployed, authorized, and verified in execution history.