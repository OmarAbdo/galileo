# Decisions

Each record says what was decided, when and by whom, why, and what was rejected. To change one,
agree it with Omar, change the code through an item, record the new decision here and keep the
old one struck through below it.

## G1. Tame the harness instead of quitting LLMs

- **When, who:** 2026-10-25, Omar.
- **What:** Galileo changes everything around Claude so the loop in [problem.md](problem.md) can't
  form. Claude itself can't be changed.
- **Why:** quitting isn't realistic while everyone works with LLMs, and taming may be the better
  answer if done right.
- **Rejected:** quitting; better prompts on their own.

## G2. Enforced by machinery, like doctrine

- **When, who:** 2026-10-25, Omar: "can we make sure that such rules won't be broken under stress
  by claude... a similar idea to doctrine".
- **What:** every rule runs as code in the admin-owned hook layer, and `galileo selftest` must
  catch every attempt in [attacks.md](attacks.md).
- **Why:** doctrine D1. Advice loses under pressure; a refusal doesn't.
- **Rejected:** output styles, CLAUDE.md instructions, a "learning" prompt.

## G3. Galileo builds on doctrine; learning projects are upgraded

- **When, who:** 2026-10-25, Omar: "if it's a learning project then we upgrade it from a doctrine
  project to a galileo project. so galileo builds on top of doctrine".
- **What:** every project starts as a doctrine project, in normal mode. `galileo upgrade` makes a
  learning project a Galileo project. Galileo itself is built under doctrine.

## G4. Mode switches are immediate and need a reason; a cooldown only when Omar sets one

- **When, who:** 2026-10-25, Omar: "i don't want to have to wait a whole day of cooling down if a
  learning project for some reason becomes needed commercially ... i would keep the reason though
  ... an optional flag called forced cooldown or something".
- **What:** `galileo mode normal --reason "..."` takes effect at once and is logged.
  `galileo mode learn --cooldown <duration>` locks learn mode until it expires; it can be
  extended, never shortened.
- **Rejected:** a mandatory cooldown of an hour or a day (Claude's proposal).
- **Confirmed:** 2026-10-25, Omar: the cooldown locks learn mode, nothing stronger ("you read
  disconnect correctly").

## G5. Three lanes: ask, paired, batch

- **When, who:** 2026-10-25, Claude, accepted by Omar.
- **What:** jobs keep taking minutes, and Omar never waits on them. An ask takes seconds and
  can't edit. A paired job starts after Omar starts his part and stays hidden until he's done. A
  batch runs while he's away, silently.
- **Rejected:** watching an agent work in a learn-mode chat.

## G6. Six rules

- **When, who:** 2026-10-24, Claude from the research; Omar: "Good job".
- **What:** Omar earns every result; results arrive without fanfare; no dead waiting; his part
  stays his; Claude talks less; it measures Omar ([design.md](design.md)).

## G7. The outcome: the lowest of focus, understanding and hands

- **When, who:** 2026-10-25, proposed by Claude. Omar: "we have many factors we care about here
  focus, understanding, ability to code". Asked again with the stop value (below 0.8 of the
  baseline), Omar answered "Perfect. I reviewed and everything seems alright"; defined in
  doctrine.toml in roadmap item 1.2b.
- **What:** each score as a share of the baseline week; the outcome is the lowest.
- **Why:** no score can be bought with another. Doctrine scores its judges by the lower of two
  rates for the same reason (doctrine D16).
- **Rejected:** a weighted average, which hides the weak score; a single score.

## G8. No GUI for now

- **When, who:** 2026-10-25, Omar: "I'm open to the idea if we won't have a gui".
- **What:** the terminal, the editor and the hooks. MessageDisplay covers what the chat shows.
- **Rejected for now:** a desktop app; a VS Code fork, which would be a permanent maintenance cost.

## G9. Documentation and tests first, ready for handover

- **When, who:** 2026-10-25, Omar: "plan everything and be testing and documentation first as
  this thread will probably not live long enough to finish the project".
- **What:** docs before code. Each feature item starts from its named tests and its attack cases,
  recorded red. Every thread leaves the roadmap and STARTER_PROMPT.md current.

## G10. Learner data stays off the repository

- **When, who:** 2026-10-25, Claude, following doctrine D5 (the repository is public).
- **What:** data lives in `%LOCALAPPDATA%\Galileo\`, found through the known-folder API. Only the
  outcome number goes into `metrics/`.
- **Open:** Omar to confirm that the daily outcome number may be public.

## G11. Understanding is graded by running code

- **When, who:** 2026-10-25, Claude.
- **What:** questions are "what does this return for this input", and the answer comes from
  running it.
- **Why:** a model grading its own teaching would be generous. A tutor plugin's quiz was passed by
  pressing enter, because the right answer always came first.

## G12. A start ritual only if it moves Omar's numbers (proposed)

- **When, who:** 2026-10-24, Claude, after Omar asked for cognitive exercises against the effects
  of screen time.
- **What:** an optional 2-minute start ritual, kept only if the focus score improves with it. No
  general brain-training games.
- **Why:** brain-training gains stay on the trained task (Simons et al. 2016).

## G13. Galileo extends doctrine without changing it

- **When, who:** 2026-10-25, Omar: "I'm thinking of doctrine as the vanilla solution and then of
  tools like galileo as extending plug-ins based on each case."
- **What:** a Galileo project is a doctrine project; doctrine knows nothing about Galileo.
  Galileo's admin installer adds its own file to Claude Code's drop-in folder,
  `C:\Program Files\ClaudeCode\managed-settings.d\50-galileo.json`, which Claude Code merges with
  doctrine's `managed-settings.json` (hook lists combine). Galileo's release lives under
  `C:\Program Files\Galileo`. Doctrine's repository and files are never changed for Galileo.
- **Why:** doctrine stays the vanilla base, and every later extension can plug in the same way
  with its own file. Doctrine's updater rewrites only its own settings file.
- **Rejected:** Galileo's hooks in doctrine's template (Claude's proposal of the same day);
  editing doctrine's `managed-settings.json`, which its updater rewrites.

## G14. Claude runs on Omar's Pro subscription; no API key

- **When, who:** 2026-10-25, Omar: "we also don't have a claude api key we only have the pro
  subscription"; earlier, paid tools are fine "except claude code because i already pay for that
  anyway".
- **What:** jobs run through `claude -p` on Omar's Pro login. Nothing in Galileo needs an API key
  or a paid service (doctrine D18).
- **Consequences:** `claude --bare`, which skips the hooks in settings, only logs in with an API
  key, so it can't start on this PC (attack A4 keeps a test for it). Batch runs count against
  Pro's usage limits.

## G15. The voice notification is off by default; a thread turns it on for itself only

- **When, who:** 2026-10-25, Omar: "now i really think it's problamtic to the attention part of
  the issue we're trying to solve here ... i want to be able to explicilty ask a claude code
  thread to enable it only on its own scope".
- **What:** Omar's own script, `C:\Users\Omar\.claude\hooks\voice-notify.mjs`, which doctrine's
  settings run at the end of every turn, now stays silent unless the thread turned it on:
  `node C:/Users/Omar/.claude/hooks/voice-notify.mjs on` (also `off`, `status`). The thread is
  found by `CLAUDE_CODE_SESSION_ID`, which equals the hook's `session_id`. Omar's global
  CLAUDE.md tells every thread how. Changed outside both repositories; the old version is kept
  next to it as `voice-notify.mjs.before-2026-10-25`.
- **In learn mode:** turning it on is refused (attack A24). Learn mode never pings.
- **Rejected:** keeping it on everywhere; removing it from doctrine's settings, which would change
  doctrine.
