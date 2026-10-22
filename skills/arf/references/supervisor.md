# Supervisor protocol

The human is the supervisor. They do not need to write; they need to decide.

## Checkpoint report (every iteration)
```
Did: <one or two lines>
Files: <paths>
Decide:
  1. <question> (suggested: <option>)
  2. ...
Risks: <unsourced claims, thin evidence, scope creep, word budget>
```
Keep it short; put detail in the artifact.

## Supervisor commands (natural language is fine)
- `devam` / `continue` — approve the gate as presented.
- `revize: <note>` / `revise: <note>` — redo the current unit with this note.
- `geri: <phase>` / `reopen: <phase>` — reopen an earlier gate.
- `durum` / `status` — show phase, gates, word count, open risks.
- `kaynak ekle: <ref or file>` / `add source: …` — add to ledger and verify.
- `ses` / `voice` — show or edit the voice profile.
- `denetim` / `audit` — run the audit now.

## Logging
Every piece of supervisor feedback is appended verbatim to `revisions/log.md` with the date, the phase, and what the agent changed in response. This is the paper's editorial history and helps the author explain their process.

## Teaching mode
At undergraduate and master's levels, when the supervisor is also the student, briefly explain *why* a structural or argumentative choice was made at each gate (one or two sentences). The aim is that the author learns to make these decisions themselves.
