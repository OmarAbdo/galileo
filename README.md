# Galileo

A learning mode for Claude Code, built on top of doctrine. A doctrine project meant for learning
is upgraded to a Galileo project, and its sessions then run under rules that keep Omar's
attention, understanding and coding skill in use instead of handing them to the agent.

**What:** admin-owned hooks that plug in next to doctrine's without changing it, a `galileo`
command, and a meter that measures Omar: focus, understanding and coding from memory.
**Why:** an agent that turns one line of effort into minutes of visible work trains the loop of a
slot machine: a cheap pull, a restless wait, a payout that looks big, reading that gets skimmed,
the next pull. Over weeks, real work feels unbearable next to it. Quitting LLMs isn't realistic,
so Galileo tames the harness around Claude ([docs/problem.md](docs/problem.md)).
**Who:** Omar owns it and approves every change. Claude builds it under doctrine.
**Where:** this repository, from doctrine's `python-hexagonal` template (doctrine 0.3.2).
**When:** planned on 2026-10-24 and 2026-10-25. Nothing is built yet.

## Read this first

| You want to | Read |
|---|---|
| Continue the work in a new thread | [STARTER_PROMPT.md](STARTER_PROMPT.md) |
| Know the problem and the evidence | [docs/problem.md](docs/problem.md) |
| Know how Galileo works | [docs/design.md](docs/design.md) |
| Know what was decided, by whom, and what was rejected | [docs/decisions.md](docs/decisions.md) |
| See what gets built, in which order, with which tests | [docs/roadmap.md](docs/roadmap.md) |
| See every bypass the self-test must catch | [docs/attacks.md](docs/attacks.md) |

## A learn session in one screen (planned)

```text
galileo upgrade                      # once: this doctrine project becomes a Galileo project
galileo mode learn                   # galileo mode normal --reason "..." switches back at once
galileo pair "Search by city"        # you start your part; Claude's job starts after you
                                     # ... its result stays hidden until you're done ...
galileo review                       # predict, read the machine's report, answer two questions
galileo job add "Cover the importer" # needs nothing from you: it goes to the batch
galileo batch start                  # before you leave; nothing pings you
galileo kata                         # a coding exercise from memory, timed, no AI
galileo score                        # focus, understanding, hands, and the lowest of the three
```

## Status

| Part | Status (2026-10-25) |
|---|---|
| Problem, design, decisions, roadmap, attacks | Written, in review |
| Everything else | Not built ([docs/roadmap.md](docs/roadmap.md)) |
