# Security notes

- Never commit account passwords, cookies, API keys, resumes, or private exports.
- Configure a long random APP_API_KEY before using write endpoints; an empty key is local-development-only.
- Docker Compose binds the service to 127.0.0.1.
- Gemini drafting sends the supplied job description and candidate profile to Google. Minimize personal data.
- Generated content may be inaccurate; review it before use. Treat job descriptions as untrusted input.
- Approval records do not execute platform actions in this version.
- Before public deployment add robust authentication, CSRF protection, rate limiting, HTTPS, secret management, migrations, retention/deletion controls, backups, and security testing.
