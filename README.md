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

## Use it now

Once, from this repository (any Python 3.12 or newer):

```text
python -m galileo.adapters.install   # run with PYTHONPATH=src; puts `galileo` in ~/.local/bin
```

Then, in a new terminal:

| Command | What it does |
|---|---|
| `galileo kata` | Starts the next Python kata, or shows the open one: prompt, file to write, time |
| `galileo kata check` | Runs the kata's tests; a pass records hands |
| `galileo kata stop` | Closes the kata without a record |
| `galileo quiz` | Up to three questions about code merged in your repositories (listed in `understanding.toml`); each answer records understanding |
| `galileo score` | This week's scores against the baseline, and the outcome |
| `galileo baseline` | At the end of the first week: freezes each baseline, once |
| `galileo update` | Installs the newest main |

The install also starts the focus sampler and adds `galileo-focus.vbs` to your Startup folder, so
it runs hidden at every logon. It records only the file name of the app in front and your idle
time; edit `focus.toml` in the data folder to choose which apps count as work. To stop it, delete
that Startup file and end `pythonw.exe` in Task Manager.

Scores live in `C:\Users\Omar\AppData\Local\Galileo`, never in this repository.

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
| Problem, design, decisions, roadmap, attacks | Written |
| Scores, the outcome, the baseline, Python katas, the install | Built ([docs/roadmap.md](docs/roadmap.md), phase 1) |
| Focus and understanding scores, the guard, jobs | Not built yet |
