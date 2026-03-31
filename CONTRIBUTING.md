
# Contributing

## How to Contribute

1. **Fork** the repository and create your feature branch from `main`.
2. **Make your changes** locally, following the project’s style and guidelines.
3. **Commit** using the provided commit message template.
4. **Open a Pull Request (PR)** to `main` using the PR template.
5. **Wait for review** — at least one team member must approve your PR.
6. **No direct pushes to `main`** — all changes must go through PRs and review.

See below for more details on guidelines, templates, and branch protection.

TAP is open-source software licensed under the GNU General Public License v3.0. Contributions are welcome.

By submitting a contribution you agree that your changes will be distributed under the same GPL v3 license.

## Getting started

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in your keys
```

## Project layout

| File | Purpose |
|---|---|
| `run.py` | Single entry point — starts poller thread + web server |
| `main.py` | Polling loop and event processing orchestration |
| `client_511ny.py` | 511NY REST API wrapper |
| `geo.py` | Haversine distance / proximity filtering |
| `capture.py` | Live camera snapshot (MJPEG, HLS/ffmpeg, still fallback) |
| `analyzer.py` | OpenAI vision analysis with structured output |
| `store.py` | SQLite persistence and incident file layout |
| `web_server.py` | Flask + waitress web UI backend |
| `web/index.html` | Single-page frontend |
| `config.py` | Centralised config loader (env vars / .env) |

## Data source compliance

This software consumes the 511NY data feed under the [511NY Developer's Access Agreement](https://511ny.org/developers/help). Contributors must be aware of the following obligations:

- **Data integrity:** Source data from 511NY must not be altered in any way. Display and store it as received.
- **Branding:** Do not use "511NY" in the product name or marketing materials. Attribution must use the approved form: *"powered by 511NY"* with a link to https://www.511NY.org.
- **Disclaimer:** Any feature that exposes 511NY data to end users must include the NYSDOT data disclaimer (see [LICENSE](LICENSE)).
- **No misrepresentation:** Nothing in the product may imply sponsorship, endorsement, or licensing by 511NY or NYSDOT.

## Guidelines

### Branch Protection & Review Process

All changes to the `main` branch must be made via pull requests (PRs). Direct commits to `main` are not allowed. Every PR must be reviewed and approved by at least one team member before merging.

#### How to contribute:
- Fork the repository and create your feature branch from `main`.
- Submit a pull request (PR) describing your changes.
- Ensure your PR passes all required checks and receives at least one approval.
- Only approved PRs will be merged into `main`.

### Issue, PR, and Commit Templates

Please use the provided templates for issues, feature requests, pull requests, and commit messages. These help maintain consistency and quality across the project.

- Bug reports: `.github/ISSUE_TEMPLATE/bug_report.md`
- Feature requests: `.github/ISSUE_TEMPLATE/feature_request.md`
- Pull requests: `.github/pull_request_template.md`
- Commit messages: `.github/commit_template.txt`

### Code Owners

Certain files or the entire repository may have designated code owners. At least one code owner must review and approve changes before merging.

---

- Keep the codebase lightweight — no frameworks or abstractions beyond what a feature actually needs.
- All secrets go in `.env`, never in source files.
- Test against the live 511NY API before submitting changes to the polling or capture logic — mocks will not catch real-world edge cases.
- The web UI is intentionally vanilla JS. Do not introduce a build step.
- `ffmpeg` is a system dependency; document any new system-level requirements clearly.

## Submitting changes

Open an issue before starting any non-trivial work so the approach can be agreed on first. Pull requests without prior discussion may be declined.
