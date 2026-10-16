# Privacy Policy

**Upgrade Audit (Verify Before Done audit module, MIT)**

**Effective date:** August 17, 2026
**Last updated:** October 16, 2026
**Developer:** Martial Systems LLC
**Contact:** martialsys@gmail.com

## What the Product does with data

The Product runs on your machine. It uses your installed `git` (and `gh` when signed in) to list and clone repositories you already have access to. Public repositories clone over plain `git` https when `gh` is missing or signed out.

Martial Systems LLC does **not** receive your repository contents, tokens, or audit PDFs. There is no Martial Systems upload, account, or analytics in this Product.

## What stays local

- Your catalog under `~/.config/upgrade-audit/repos.yaml` (or `$UPGRADE_AUDIT_CATALOG`); run JSON under the pack checkout
- Device policy (`audit` / `fix` / `pr` and `none` / `stall`) under your Grok home directory
- Detached git worktrees under your temp directory

## What goes to third parties

- GitHub, as the logged-in `gh` user or anonymously over https (repo list, clone; pull requests only in `pr` mode and only after you approve)
- No other network calls are required for an `audit` run

## Contact

martialsys@gmail.com
