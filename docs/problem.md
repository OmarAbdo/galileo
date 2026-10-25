# The problem

## The loop

Omar's description (2026-10-24 and 2026-10-25), restated as a loop that he confirmed:

1. One line of effort gets a big result.
2. Claude works for minutes. The wait is idle and restless, and the phone is one reach away.
3. The result arrives and feels like a big achievement.
4. Reading it hurts: long, unclear, full of small decisions. So it gets skimmed and approved.
5. The next prompt goes out.

Over weeks, effortful work starts to feel unbearable next to this. Attention gets shorter,
understanding thinner, and impatience and anger at the agent grow. Omar compared it to
pornography's effect on the reward system: an effortless, highly attractive reward that wears
down the drive to pursue the real thing.

Quitting LLMs isn't realistic. The second-best answer, and maybe the better one if done right, is
to tame the harness so the loop can't form. Claude itself can't be changed; everything around it
can.

## What the research says about each step

| Step | Mechanism | Evidence |
|---|---|---|
| The restless wait | Uncertain rewards pull hardest | In monkeys, dopamine activity while waiting for a reward peaks when the reward is 50/50 (Fiorillo, Tobler & Schultz 2003) |
| The result that looks big | A loss disguised as a win: it feels like a win and hides a net loss | Named in slot-machine research (Dixon et al.) and applied to vibe coding by fast.ai (2026). In METR's 2025 trial, developers felt 20% faster and were 19% slower |
| Real work feels unbearable | Felt effort tracks the value of the best alternative in reach | The opportunity cost model of effort (Kurzban et al. 2013). With an agent and a feed one click away, every effort feels expensive |
| Skills fade | Disuse | Endoscopists' detection rate without AI fell from 28.4% to 22.4% after AI came in (Budzyń et al. 2025, observational). Students who practised with plain GPT-4 scored 17% lower on the exam, and a tutor version with guardrails removed most of the harm (Bastani et al. 2025, field experiment) |
| Absorbed, and worse off | Dark flow: absorption without a skill that matches the challenge | Dixon et al. 2018 and 2019, on slot players, correlational. Csikszentmihalyi called it junk flow |

The slot machine is the closest studied match, and that is useful: regulators have already
written rules to tame one ([design.md](design.md), rule 2).

## Who else sees it

Developers describe the same loop: Steve Yegge ("The AI Vampire", 2026), Armin Ronacher ("agent
psychosis"), fast.ai ("dark flow"), Axios ("They operate like slot machines", 2026-04-04) and
LeadDev. Their remedies are personal advice. The search on 2026-10-25 found no harness that
enforces counter-rules. The closest is a tutor plugin whose guard hook stopped Claude writing the
learner's file; the tutor then read the solution out in chat, line by line. Its author's lesson:
"A PreToolUse hook bounds tool calls. It cannot bound prose." Anthropic's own engineers reported
worrying about losing hands-on skill (Anthropic, December 2025).

## What the evidence doesn't say

- No study tests this combination of rules. Each one is borrowed from a nearby field: gambling
  regulation, aviation, classroom trials, human-computer interaction.
- The neuroscience of pornography addiction is disputed. The comparison holds for the shape of
  the loop, and the slot machine is the better-studied match.
- Some sources are essays, trade press or vendor surveys. The table uses studies where they exist.
- Galileo's own weeks on and off are the real test ([roadmap.md](roadmap.md), phase 5).

## Sources

- [Fiorillo, Tobler & Schultz 2003, Science 299](https://doi.org/10.1126/science.1077349)
- [fast.ai, "Breaking the spell of vibe coding", also for METR's 2025 numbers](https://www.fast.ai/posts/2026-01-28-dark-flow/)
- [Dixon et al. 2018, dark flow](https://link.springer.com/10.1007/s10899-017-9695-1)
- [Kurzban et al. 2013, the opportunity cost of effort](https://pmc.ncbi.nlm.nih.gov/articles/PMC3856320)
- [Budzyń et al. 2025, endoscopist deskilling](https://wrap.warwick.ac.uk/id/eprint/191005)
- [Bastani et al. 2025, PNAS, via Wharton](https://knowledge.wharton.upenn.edu/article/without-guardrails-generative-ai-can-harm-education)
- [Axios, 2026-04-04](https://www.axios.com/2026/04/04/ai-agents-burnout-addiction-claude-code-openclaw)
- [LeadDev](https://leaddev.com/ai/addictive-agentic-coding-has-developers-losing-sleep)
- [The tutor plugin](https://blog.codeminer42.com/plugins-are-how-you-ship-a-claude-code-harness/)
- [Anthropic, "How AI is transforming work at Anthropic"](https://www.anthropic.com/research/how-ai-is-transforming-work-at-anthropic)
