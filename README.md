# LinkedIn-Naukri-Gemini-Agent

A Gemini-powered personal career copilot for LinkedIn and Naukri. It scores manually collected job descriptions, drafts truthful application materials, tracks applications, and records approvals before sensitive actions.

**Safety boundary:** this starter does not log into LinkedIn/Naukri, store passwords or cookies, scrape pages, bypass anti-bot controls, change profiles, or submit applications. Approval records are not platform actions. Use official/authorized interfaces only and review generated content.

## Status

- **Configured cadence:** 300 seconds (5 minutes).
- **Alert policy:** immediate after a supported connector detects a new matching job.
- **Monitoring state:** inactive until authorized connectors are implemented and verified.
- **LinkedIn and Naukri connectors:** not implemented in this version.
- **Applications/profile edits/messages:** approval records only; no external action is executed.

The status endpoint reports these limitations honestly: `GET /api/monitor/status`.

## Run locally (Python 3.11+)

```bash
python -m venv .venv
# Windows: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
# Add GEMINI_API_KEY and a long random APP_API_KEY to .env
uvicorn career_agent.main:app --reload
```

Open http://127.0.0.1:8000. Write requests use the `X-API-Key` header. If `APP_API_KEY` is blank, write endpoints warn and are suitable only for local development.

## Configure monitoring policy

Set these values in `.env`:

```dotenv
MONITOR_INTERVAL_SECONDS=300
ALERT_MODE=immediate
MONITOR_ENABLED=false
```

The interval has a 300-second minimum. **Do not set `MONITOR_ENABLED=true` expecting monitoring to start:** no authorized provider connector or background scheduler is implemented yet. Use LinkedIn/Naukri native alerts or manually import job descriptions until approved integrations are available.

## API

- `GET /api/health`
- `GET /api/monitor/status`
- `GET /api/jobs`
- `POST /api/jobs`
- `POST /api/jobs/{id}/match` — Gemini fit score, strengths, gaps, and rationale
- `POST /api/jobs/{id}/draft`
- `GET /api/approvals`
- `POST /api/approvals`
- `POST /api/approvals/{id}/decision`
- `GET /api/applications`
- `POST /api/applications`

Example job intake:

```bash
curl -X POST http://127.0.0.1:8000/api/jobs \
  -H "Content-Type: application/json" \
  -H "X-API-Key: change-me" \
  -d '{"platform":"manual","title":"Platform Engineer","company":"Example","description":"Kubernetes, AWS, Terraform, Python","skills":["Kubernetes","AWS","Terraform"]}'
```

## Platform access, rate limits, and fallback

See [Platform Integration Policy](docs/PLATFORM_INTEGRATIONS.md) for documented access constraints, rate-limit behavior, and authorized integration requirements. LinkedIn API limits depend on the application and endpoint; do not assume candidate job-search access. This project has not verified a public general-purpose Naukri candidate-search API or universal quota. Never scrape pages, use undocumented endpoints, reuse session cookies, or bypass platform controls.

## Security

Never commit `.env`, API keys, resumes, cookies, or account exports. Bind only to localhost until authentication, CSRF protections, rate limiting, TLS, secret management, audit retention, and a production database are configured. Gemini receives the job description and candidate profile submitted for drafting, so minimize personal data. See [Security](docs/SECURITY.md).

## Development

```bash
pip install -e ".[dev]"
pytest
ruff check .
```

MIT License. Not affiliated with LinkedIn, Naukri, or Google.
