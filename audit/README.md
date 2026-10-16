# Upgrade Audit (Verify Before Done module)

Part of the **Verify Before Done** pack by Martial Systems LLC. MIT licensed, same as the rest of the pack ([LICENSE](LICENSE)). Privacy: [docs/PRIVACY.md](docs/PRIVACY.md).

When a new model generation ships, Upgrade Audit re-reads the **shipped** logic of every repo in your catalog, has a second agent try to refute each finding, and writes a PDF of the confirmed ones. It is Verify Before Done applied to code you already shipped.

## Run it

```bash
cd audit
python3 -m pip install -r requirements.txt
export PATH="$PWD/bin:$PATH"
upgrade-audit configure --mode audit --kill stall
upgrade-audit doctor
upgrade-audit inventory --adopt      # writes ~/.config/upgrade-audit/repos.yaml
```

Needs Python 3.9+ and `git`. `gh` is optional for audit mode: public repos clone over `git` https when `gh` is missing or signed out (`doctor` warns). `inventory` and `pr` mode need `gh auth login`.

The shipped `catalog/repos.yaml` is empty. Your catalog lives per user at `~/.config/upgrade-audit/repos.yaml` (or `$UPGRADE_AUDIT_CATALOG`), never inside the pack checkout.

## Modes

| Action mode | After the PDF |
|-------------|---------------|
| `audit` (default) | Read-only. Findings and proposed fixes only. |
| `fix` | Apply confirmed findings on a new branch. No push, no PR, no merge. |
| `pr` | Same as fix, then open a PR only after you explicitly approve. Never merges. |

| Child kill | During the walk |
|------------|-----------------|
| `stall` (recommended) | Kill an agent whose snapshots show no progress for the stall window. |
| `none` | Never auto-kill. |

Slots that never launch, or agents that vanish from the snapshot, are released after 10 minutes whichever kill policy you pick, so a walk cannot hang.

## Where it runs

- **Grok terminal**: the `/verify-before-done` skill's upgrade audit mode, or `upgrade-audit send-grok` (macOS only; hidden elsewhere).
- **Grok Bot / Cursor**: see `editions/grok-bot/SKILL.md`, "Upgrade audit mode". The bot spawns auditor and verifier subagents and drives `upgrade-audit walk-step` through its shell.

Protocol for auditors and verifiers: [protocol/AUDIT.md](protocol/AUDIT.md).

## Tests

```bash
sh scripts/sanity.sh     # pytest + schemas + fixture PDF
```
