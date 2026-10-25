# Design

Status: planned on 2026-10-24 and 2026-10-25. Nothing is built; "does" below means "will do".

## The idea

Every reward the harness gives depends on something Omar did with his head or hands, and the
harness never leaves him in an empty or painful gap. Six rules carry that out. Each is enforced
by code Claude can't change, in the same admin-owned hook layer as doctrine, and each has bypass
attempts that `galileo selftest` must catch ([attacks.md](attacks.md)).

## Projects and modes

- **Every project is a doctrine project first.** Normal mode is plain doctrine, as today.
- **A learning project is upgraded.** `galileo upgrade` adds `galileo.toml` through an item. From
  then on the project has a mode, and learn mode is where the six rules apply.
- **Switching is immediate and needs a reason.** `galileo mode learn` and
  `galileo mode normal --reason "..."`. Every switch is logged with its reason, and
  `galileo score` shows them. A learning project can suddenly be needed for paid work, so nothing
  waits (decision G4).
- **Forced cooldown is optional and Omar's own.** `galileo mode learn --cooldown 24h` (any
  duration) locks learn mode until it expires: `galileo mode normal` is refused, to Omar too. It
  can be extended, never shortened. It is for the moments he feels out of control, the way
  self-exclusion works in gambling.
- **Only Omar switches.** `galileo mode` is refused in Claude's sessions; Omar runs it in his own
  terminal. The state lives in `.galileo/state.json` (gitignored), which Claude's tools and shell
  can't write.
- **The status line shows the mode** in every session of a Galileo project.

## The six rules (learn mode)

### 1. Omar earns every result

- **What:** before a job's result is shown, Omar writes a prediction: what it changed and where
  it could break. In a paired job he also finishes his own part first.
- **Enforced:** a job's work stays on its own branch and worktree. Only `galileo review` shows
  it, after the prediction is saved. CI refuses to merge a job's pull request without a review
  record for that commit.
- **Why:** people who decide before they see the AI's answer rely on it less (Buçinca et al.
  2021, N=199), though they like it least. Rewarded effort becomes less aversive (Eisenberger
  1992). Tying a reward to the wanted behaviour is how contingency management works, one of the
  better-supported addiction treatments (Prendergast et al. 2006, d = 0.42).

### 2. Results arrive without fanfare

- **What:** no streaming text to watch. A job's report is assembled from facts: whether
  `doctrine check` passed, which files changed and by how much, what Claude decided, what isn't
  verified. It has no field for "All done ✅" or praise.
- **Enforced:** Galileo builds the report from doctrine's evidence and git. Claude's own words
  appear only in the job's decision log: one line per decision, length-capped, screened for
  celebration phrases. Doctrine's Stop hook already sends back unproven claims (doctrine D15).
- **Why:** a big result that hides problems still feels like a win. The UK Gambling Commission's
  2021 rules for online slots ban celebrating a "win" that returns no more than the stake, ban
  autoplay and turbo spins, and require showing the net position and time played. The report is
  that balance sheet. In METR's 2025 trial, developers felt 20% faster while being 19% slower.

### 3. No dead waiting

Claude's jobs still take minutes. What changes is what Omar does during them. Every job goes
into one of three lanes:

- **Ask (seconds).** The learn-mode chat answers questions and reads code, and can't edit. An ask
  gets about 30 seconds of tool time. Past that, Claude is stopped and offers `galileo job add`.
- **Paired (minutes).** Claude's job starts only after Omar has started his own part, which is
  sized to take longer. The job's result stays hidden until he's done. If he finishes first, he
  writes the prediction and does a kata while it finishes. Claude waits for Omar, never the other
  way round.
- **Batch (hours).** Jobs that need nothing from Omar go into a queue. He starts it when he
  leaves for a block. It runs the jobs one after another, each as a doctrine item, and nothing
  notifies him. `galileo review` takes him through the results when he's back. A task that can't
  be split into parts goes here.

**Enforced:** in a learn-mode chat, PreToolUse refuses Edit, Write, MultiEdit, NotebookEdit and
shell writes. Only job sessions may edit, and a session is a job session only if the runner
registered its id (`claude -p --session-id`) in a protected file before starting it. Running
`claude` from inside a session is refused, so Claude can't start a job of its own. The ask budget
is timed from UserPromptSubmit. Notifications are silent in learn mode, the voice notification
included.

**Why:** past about 10 seconds, attention leaves the dialogue (Nielsen's response-time limits).
METR saw developers drift to unrelated work while agents ran (2026). Switching tasks leaves
attention residue on the old one (Leroy 2009).

### 4. Omar's part stays his

- **What:** each paired job reserves the piece that carries the idea and sits at the edge of
  Omar's skill, in its own file. Claude can't write it or dictate it in chat.
- **Enforced:** a job's reserved paths are refused to Claude in every session and job. In a
  learn-mode chat, the MessageDisplay hook hides code blocks longer than a few lines (the limit is
  in `galileo.toml`; tightening it is free). Doctrine's item scope still includes the reserved
  files, because Omar's own edits must pass doctrine's scope gate.
- **Why:** felt effort tracks the best alternative in reach (Kurzban et al. 2013), so the
  alternative is removed for that piece. After automation wore down manual flying, the FAA asked
  airlines in 2013 to have pilots fly by hand regularly (SAFO 13002). A tutor plugin that only
  guarded files had Claude read the solution out in chat, so the display has to be covered too.

### 5. Claude talks less

- **What:** jobs run headless and silent, with one report each (rule 2). A job can't ask Omar
  anything: questions go to the job's question file and come up in review. Claude makes small
  decisions itself and logs them; a choice that can't be undone parks the job. Jobs are capped
  below doctrine's 400 lines and 15 files (proposed: 150 lines, 6 files; tightening is free).
  Bigger work is split.
- **Enforced:** a headless run has no way to prompt. AskUserQuestion is refused in jobs. The size
  cap is checked when the job ends, and a job over it fails.
- **Why:** people seldom check each AI recommendation and instead form rules of thumb about when
  to follow it (Buçinca et al. 2021). Fewer, smaller results get real attention.

### 6. It measures Omar

- **What:** three scores, each as a share of Omar's baseline week.
  - **Focus:** minutes per day in unbroken blocks of 10 minutes or more on his own work, from the
    active window. App names only, never titles or content.
  - **Understanding:** the share of questions about his own merged code he answers right,
    repeats a week later included. A question is an `assert <expression> == <expected>` from a
    test merged in the last 30 days: Omar says what the expression gives, and the expected value,
    which CI already ran, is the answer. Answers are compared by value. No model grades him.
  - **Hands:** his time to pass coding exercises (katas) from memory, without AI, in Python, Go,
    Java and TypeScript.
- **The number:** the lowest of the three, so no score can be bought with another. Doctrine
  scores its judges the same way (doctrine D16). It is Galileo's doctrine outcome (proposed;
  confirmed in roadmap item 1.1). Galileo's line stops when Omar's number falls: only restore
  items may change Galileo while he gets worse.
- **Adapts:** a falling score tightens its rule: focus gets shorter paired jobs and more batch,
  understanding gets smaller jobs and more questions, hands gets more katas. A rising score raises
  the bar: longer focus blocks, bigger parts for Omar.
- **Enforced:** only `galileo` commands write scores, into the data folder (below), which
  Claude's tools and shell can't write. Commands that record anything (katas, answers, reviews)
  are refused in Claude's sessions.

## Start ritual (optional)

Two minutes before a learn session: cyclic sighing, or nothing. In a one-month remote trial it
improved mood more than mindfulness did (Balban et al. 2023). It stays only if Omar's focus score
says it helps. General brain-training games aren't planned: gains stay on the trained task
(Simons et al. 2016).

## Where each rule is enforced

| Rule | Enforced by | It decides |
|---|---|---|
| 1 | `galileo review`; the CI gate `galileo ci review` | No result before the prediction; no merge without a review record |
| 2 | Galileo's report builder; doctrine's Stop hook | The report comes from facts; unproven claims are sent back |
| 3 | PreToolUse, UserPromptSubmit, the job registry, the notification hooks | Chat can't edit; the ask budget; only registered jobs edit; no nested `claude`; silence |
| 4 | PreToolUse; MessageDisplay | Reserved paths refused; long code hidden in chat |
| 5 | The job runner; PreToolUse | No questions from jobs; the size cap |
| 6 | The protected data folder; the outcome command | Scores by command only; the lowest of three |
| Mode | PreToolUse; `.galileo/` protected | `galileo mode` refused to Claude; the cooldown holds |

Doctrine's known weak spot applies: a command assembled from pieces inside a script can slip
past command patterns. Every one found goes into [attacks.md](attacks.md) and the self-test.

## Architecture

One service, `src/galileo`, hexagonal like every doctrine project.

| Layer | Holds |
|---|---|
| `domain/` | Mode and cooldown rules, lanes and the ask budget, reserved-path matching, the size cap, the report from facts, display filtering, question selection, scoring |
| `application/` | Use cases: switch mode, judge a hook event, filter a message, add and run jobs, review a job, run a kata, record a score, compute the outcome |
| `adapters/` | The `galileo` CLI; `galileo hook <event>`; files (state, data folder); git (worktrees, diffs); the `claude -p` runner; doctrine (`doctrine item`, `doctrine check`); the active-window reader (Windows); code runners for questions and katas |

## Claude Code features it relies on

Checked against the docs and Claude Code 2.1.301 on 2026-10-25.

| Feature | Used for |
|---|---|
| PreToolUse (deny with a reason) | Chat can't edit; reserved paths; protected files; refused commands |
| UserPromptSubmit | Starts the ask budget's clock |
| MessageDisplay (`displayContent`, display only) | Hiding long code blocks in a learn-mode chat. Verbose mode still shows the original, which is Omar's choice |
| Stop | Doctrine's honest-claims check; no voice notification in learn mode |
| SessionStart (`additionalContext`) | Tells Claude the mode and the lane |
| `claude -p --session-id <uuid> --output-format stream-json` | Running and registering job sessions |
| The drop-in folder `managed-settings.d\` | Installing Galileo's hooks next to doctrine's without changing doctrine's file |
| `claude --bare` | Skips the hooks in settings, and only logs in with an API key. Omar has only the Pro subscription, so it can't start on this PC. Attack A4 keeps a test for it |

## Installation

A Galileo project is a doctrine project, and doctrine knows nothing about Galileo (decision G13).
Galileo plugs in beside it:

- Doctrine sets `allowManagedHooksOnly`, so only admin hooks run. Claude Code reads them from
  `C:\Program Files\ClaudeCode\managed-settings.json` and from every `.json` file in the drop-in
  folder next to it, `managed-settings.d\`, merged in alphabetical order. Hook lists from all the
  files combine.
- Galileo's admin installer writes `managed-settings.d\50-galileo.json` with Galileo's hooks, and
  installs its release under `C:\Program Files\Galileo`, like doctrine. Both need administrator
  rights to change, and doctrine already refuses Claude's writes under
  `C:\Program Files\ClaudeCode`.
- Doctrine's updater rewrites only its own `managed-settings.json` (checked in its
  `policy/doctrine-release.psm1`), so it leaves Galileo's file alone.
- Galileo's hooks run only files under `C:\Program Files\Galileo`, never a script a normal account
  can change.
- Outside a Galileo project in learn mode, every Galileo hook allows everything.
- Any later extension can plug in the same way, with its own file in the drop-in folder.

Until the installer exists (roadmap 2.7), Galileo's commands work (scores, katas, reviews), and
nothing is enforced.

**The voice notification.** Doctrine's settings run Omar's own voice script,
`C:\Users\Omar\.claude\hooks\voice-notify.mjs`, at the end of every turn. Since 2026-10-25 it is
silent unless a thread turned it on for itself (decision G15). In learn mode, Galileo refuses
turning it on (attack A24).

## Data

- The repository is public (doctrine D5). Learner data never goes in it.
- Learner data lives in `%LOCALAPPDATA%\Galileo\`: scores, answers, focus blocks, job logs and
  job worktrees. Claude's tools and shell can't write it, and chat sessions can't read job
  worktrees.
- The folder is found through Windows' known-folder API, not environment variables, so a session
  can't point Galileo at a fake folder (attack A21).
- Only the daily outcome number goes into the repository (`metrics/outcome.jsonl`), because
  doctrine records it there (open question in the roadmap).
- Nothing leaves the PC.

## Cost

Jobs run through `claude -p` on Omar's Pro login (decision G14). Nothing needs an API key or a
paid service (doctrine D18). Batch runs count against Pro's usage limits, so a batch has a
maximum number of jobs.

## Out of scope for now

- A GUI (decision G8).
- Explanations for wrong answers: later (roadmap phase 6), measured with doctrine's eval kit
  against Omar's "clicked" or "lost me" labels.
- Cloud sessions: managed settings files don't reach them.

## Sources

- [Buçinca, Malaya & Gajos 2021, cognitive forcing functions](https://arxiv.org/abs/2102.09692)
- [Eisenberger 1992, learned industriousness](https://pubmed.ncbi.nlm.nih.gov/1594725/)
- [Prendergast et al. 2006, contingency management](https://pubmed.ncbi.nlm.nih.gov/17034434/)
- [UK Gambling Commission, online slot rules (2021)](https://sbcnews.co.uk/europe/uk/2021/02/02/ukgc-bans-online-slots-autoplay-and-quickspin-features/)
- [Nielsen, response-time limits](https://www.nngroup.com/videos/3-response-time-limits-interaction-design/)
- [METR, 2026](https://metr.org/blog/2026-02-24-uplift-update/)
- [FAA SAFO 13002 (2013), a summary](https://www.roughtype.com/?p=4007)
- [Kurzban et al. 2013, the opportunity cost of effort](https://pmc.ncbi.nlm.nih.gov/articles/PMC3856320)
- [Balban et al. 2023, breathwork and mood](https://pmc.ncbi.nlm.nih.gov/articles/9873947/)
- [Simons et al. 2016, brain training, via APS](https://www.psychologicalscience.org/news/releases/brain-training-claims-not-backed-by-science-report-shows.html)
- [Claude Code hooks](https://code.claude.com/docs/en/hooks)
- [Claude Code managed settings and the drop-in folder](https://code.claude.com/docs/en/managed-settings)
- [Doctrine](https://github.com/OmarAbdo/doctrine)
