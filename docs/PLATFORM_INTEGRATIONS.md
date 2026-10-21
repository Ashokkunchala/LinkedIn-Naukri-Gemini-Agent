# Platform integration policy and limits

## Configured target

- Cadence: 300 seconds (5 minutes), with a hard minimum of 300 seconds in configuration.
- Alerts: immediate after a supported connector discovers and deduplicates a new matching job.
- Application submissions, profile changes, and recruiter messages must remain approval-gated.
- Current runtime state: inactive. No authorized LinkedIn or Naukri job-search connector is implemented. Setting MONITOR_ENABLED=true does not create access or start polling. Check GET /api/monitor/status.

## LinkedIn

LinkedIn API access requires OAuth and appropriate product permissions; many permissions require explicit approval. Do not assume this project has access to a general candidate job-search API. Limits vary by endpoint and application. LinkedIn's documentation notes that authorized limits can be inspected in the Developer Portal and that limits are not universally published. On HTTP 429, honor Retry-After/provider guidance and back off; never intensify requests.

Official references:
- API access and permissions: https://learn.microsoft.com/linkedin/shared/authentication/getting-access
- Rate limits: https://learn.microsoft.com/linkedin/shared/api-guide/concepts/rate-limits
- User Agreement: https://www.linkedin.com/legal/user-agreement

## Naukri

This project has not verified a public, general-purpose candidate job-search API or a universal polling quota. Do not infer candidate-side search access from partner/company job-posting APIs. Obtain written permission or documented authorized API access before building a connector. Until then, use Naukri's built-in job alerts or user-driven manual import. Do not scrape pages, call undocumented internal endpoints, reuse session cookies, or bypass CAPTCHA/Akamai/access controls.

Naukri job-alert guidance: https://www.naukri.com/blog/how-to-get-maximum-value-out-of-naukri-job-alerts/

## Requirements before activation

1. Add a separate connector only for an explicitly authorized API, feed, or integration.
2. Respect provider-documented quotas, OAuth scopes, Retry-After, backoff, and retention terms. Keep this project's cadence at or above 300 seconds.
3. Deduplicate using provider job IDs when available; otherwise normalize URL/title/company.
4. Score newly discovered permitted job data with Gemini and alert after persistence/deduplication.
5. Store tokens in a secret manager/environment. Never ask for platform passwords or session cookies.
6. Never auto-submit applications, edit profiles, or send messages. Require a recorded approval and a final human action on the platform.
7. Test connector contracts, retries, rate limiting, alert delivery, and audit logs before enabling monitoring.

## Current fallback

Use platform-native alerts and paste/import job details into this app. The cadence and alert policy are configured, but no background monitor is claimed to be running until authorized connectors are implemented and verified.
