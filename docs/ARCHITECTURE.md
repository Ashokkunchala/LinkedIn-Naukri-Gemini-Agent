# Architecture

Browser UI -> FastAPI -> SQLite (jobs, approvals, applications, audit log)
                         -> Gemini API (draft generation)

The five-minute monitoring interval is configuration only. There are no active platform connectors or background polling in this version. Gemini has no tools to access user accounts. External actions are disabled.

For future authorized connectors, bind approvals to immutable payload hashes and expiry, invalidate approvals after edits, add concurrency-safe authorization checks, and test provider retries and alert delivery.
