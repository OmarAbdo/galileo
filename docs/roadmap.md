# Roadmap

Each line is one doctrine item: one purpose, within doctrine's limits (400 lines, 15 files), its
tests named before the code. Feature items record those tests red first. Cases A1 to A24 come
from [attacks.md](attacks.md).

Status: ⬜ open · 🟨 in progress · ✅ merged.

## Phase 0: ground (docs)

| # | Kind | Item | Status |
|---|---|---|---|
| 0.1 | chore | README, CLAUDE.md, STARTER_PROMPT.md, docs/decisions.md | ✅ |
| 0.2 | chore | docs/problem.md, docs/design.md | ✅ |
| 0.3 | chore | docs/roadmap.md, docs/attacks.md | ✅ |

## Phase 1: the meter

Measuring comes before changing anything: without a baseline week, nothing later can be shown to
help.

| # | Kind | Item | Tests first | Status |
|---|---|---|---|---|
| 1.1 | feature | Scores and the outcome, domain and application: the three kinds (hands is better when lower), the last 7 days, the share of baseline, and the lowest share, 0 while any kind has no data | unit: lowest of three; a missing kind or baseline gives 0; hands inverted; only the last 7 days count | ✅ |
| 1.2 | feature | The outcome command and the data folder: `python -m galileo.adapters.outcome` reads one JSON-lines file per kind from `%LOCALAPPDATA%\Galileo`, found through the account's profile on Windows, not through environment variables | integration: a temporary data folder; a corrupt line stops the command and names its file and line; environment variables don't move the folder (A21); the command prints one number | ✅ |
| 1.2b | chore | `[outcome]` in doctrine.toml: the metric's name and the first `doctrine metric record`. A goalpost, so it waits for Omar's approval | none | 🟨 |
| 1.3 | feature | Recording scores and freezing the baseline: an append-only writer for the kinds, and `galileo baseline` at the end of the first week | unit: the baseline from a week of records. integration: append and read back | ⬜ |
| 1.4 | feature | Hands, Python: `galileo kata` picks an exercise, opens it in the editor, runs its tests, records the time to pass | unit: selection spaces repeats. integration: a real pytest run passes and fails | ⬜ |
| 1.5 | feature | Hands: Go, Java and TypeScript katas | integration per language; a missing toolchain is skipped with its reason | ⬜ |
| 1.6 | feature | Focus: the active-window sampler, and blocks of 10+ minutes on apps Omar marks as work | unit: blocks from samples. integration: a fake window source | ⬜ |
| 1.7 | feature | Understanding: questions from a merged diff (changed functions, inputs from tests, answers by running) and `galileo quiz` | unit: selection. integration: a real diff in a temporary repo | ⬜ |
| 1.8 | feature | `galileo score`: the three scores and the lowest | acceptance: a seeded data folder | ⬜ |
| 1.9 | chore | Baseline week: Omar works as usual; Galileo only measures | none | ⬜ |

## Phase 2: the guard (rules 3 and 4, modes)

| # | Kind | Item | Tests first | Status |
|---|---|---|---|---|
| 2.1 | feature | `galileo upgrade`, and `galileo mode` with its reason log and the optional cooldown | unit: normal needs a reason; the cooldown refuses normal; extending works, shortening doesn't | ⬜ |
| 2.2 | feature | `galileo hook <event>` and the chat guard: no edits from a learn-mode chat, protected `.galileo/` and data folder, refused commands | unit per decision; A1–A5, A16–A20, A24 | ⬜ |
| 2.3 | feature | The ask budget | unit: timing; A6 | ⬜ |
| 2.4 | feature | Reserved paths | unit; A7 | ⬜ |
| 2.5 | feature | The MessageDisplay filter for long code blocks | unit: blocks across batches; A8 | ⬜ |
| 2.6 | feature | `galileo selftest`: runs `samples/attacks.toml`, fails below 1 | acceptance | ⬜ |
| 2.7 | feature | Galileo's admin installer: the release under `C:\Program Files\Galileo` and `managed-settings.d\50-galileo.json`. Doctrine stays untouched (G13) | integration: install into a temporary folder; the installer refuses to finish if a normal account could change what it installed; doctrine's settings file is byte-for-byte unchanged; A22, A23 | ⬜ |
| 2.8 | chore | The voice notification is off by default, and a thread turns it on for itself only. Done outside both repositories on 2026-10-25 (G15) | tested by hand: silent by default, `on` for one thread leaves the others silent, `off` | ✅ |

## Phase 3: jobs and review (rules 1, 2, 5)

| # | Kind | Item | Tests first | Status |
|---|---|---|---|---|
| 3.1 | feature | Jobs and the queue: `galileo job add` and `list`, reserved paths, the size cap | unit | ⬜ |
| 3.2 | feature | The job runner: worktree, a doctrine item per job, a registered session id, `claude -p`, the size check, the doctrine check result | integration with a fake `claude`; A14, A15 | ⬜ |
| 3.3 | feature | The report from facts | unit: no free text but the decision log; A12, A13 | ⬜ |
| 3.4 | feature | `galileo review`: prediction, report, diff, questions, review record | acceptance; A10 | ⬜ |
| 3.5 | feature | CI: no merge of a job's pull request without a review record (a `.github/` change, so Omar approves) | integration; A11 | ⬜ |
| 3.6 | feature | `galileo pair`: Omar's part first, the job after, hidden until he's done; an early finish gets the prediction and a kata | acceptance with a fake job | ⬜ |
| 3.7 | feature | `galileo batch start`: the queue runs silently while he's away | acceptance | ⬜ |

## Phase 4: adapt

| # | Kind | Item | Tests first | Status |
|---|---|---|---|---|
| 4.1 | feature | Tightening and loosening from the scores | unit | ⬜ |
| 4.2 | feature | The optional start ritual, measured | unit | ⬜ |

## Phase 5: the real test

| # | Kind | Item | Status |
|---|---|---|---|
| 5.1 | chore | Upgrade the first learning project (Omar picks it) | ⬜ |
| 5.2 | chore | Four weeks alternating learn and normal; compare the three scores | ⬜ |

## Phase 6: later

- Short explanations for wrong answers, judged with doctrine's eval kit against Omar's labels.
- A measure for critical thinking: Omar's predictions against what CI and review found.

## Open questions for Omar

1. Is the lowest of the three the outcome, and what is the stop value? (1.1)
2. May the daily outcome number be public in this repository? (G10)
3. In normal mode, keep the short, praise-free report and the silent notifications?
4. Is the proposed job cap right: 150 lines and 6 files?
5. Which project is the first learning project? (5.1)

## Risks

- Omar will want to bypass the rules: the designs that help most are the ones people like least
  (Buçinca et al. 2021). Gates take seconds, and the cooldown is his own tool.
- Galileo could become the next big build while Omar's number falls. Doctrine's line stop on
  Galileo's own outcome is the guard.
- Claude Code's hooks change between versions (MessageDisplay is recent). Integration tests run
  against the installed Claude Code.
- Batch runs count against Pro's usage limits (G14).
- An admin hook that runs a script a normal account can change is only as safe as that script.
  Galileo's hooks run only files under `C:\Program Files\Galileo`. Doctrine's settings run Omar's
  own voice script from his home folder; Omar sees it as his personal script, not a doctrine gap
  (2026-10-25), and it is silent by default now (G15).
