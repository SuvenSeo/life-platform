# Security Policy

## Supported project state

Ariva is currently an early public project. Security fixes should target the default branch unless an active release branch exists.

## Reporting a vulnerability

Do not open public issues for suspected vulnerabilities involving credentials, authentication bypass, stored data exposure, or abuse paths.

Report privately to the repository owner with:

- affected area: backend, frontend, CI/CD, deployment, or dependency
- reproduction steps
- expected vs actual behavior
- impact assessment
- relevant logs, request IDs, or screenshots with secrets removed

## Secret handling

Never commit:

- `.env` or `.env.*` files
- Firebase service-account JSON
- Fly, Vercel, GitHub, or database credentials
- local SQLite databases
- production logs containing bearer tokens or account identifiers

## Operational controls

The API includes request IDs, process-time headers, baseline security headers, and a lightweight in-process rate limiter. These controls reduce operational risk but do not replace production network controls, WAF/edge rules, or managed secret rotation.

## Dependency updates

Dependabot is configured for GitHub Actions, backend pip dependencies, and frontend npm dependencies. Security updates should be reviewed and merged ahead of routine maintenance updates.
