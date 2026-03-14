# NexusAgile

> *"The human decides WHAT. The agents execute HOW."*

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Works with Claude Code](https://img.shields.io/badge/Claude%20Code-ready-blue)](https://claude.ai/code)
[![Stack agnostic](https://img.shields.io/badge/stack-agnostic-orange)](https://github.com/ferrosasfp/NexusAgile)

---

You describe a feature to Claude. It writes confident code that imports a module that doesn't exist, follows patterns inconsistent with your project, and touches files it wasn't supposed to. You spend 40 minutes fixing what should have taken 10.

That's not a Claude problem. That's a **structure problem**.

**NexusAgile is a software development methodology built for AI agents.** It covers the full lifecycle — sprint planning, feature implementation, adversarial review, QA, retrospectives — with specialized agents, strict human gates, and zero tolerance for hallucination.

No fluff. No long prompts that get ignored. Just a structured process that ships code you trust.

---

## Why NexusAgile

| Without it | With NexusAgile |
|---|---|
| AI invents imports that don't exist | **Codebase Grounding** — reads real files before generating anything |
| AI creates inconsistent patterns | **Exemplar Pattern** — references existing code in every task |
| AI ignores restrictions | **Constraint Directives** — explicit REQUIRED / FORBIDDEN per task |
| Implementation drifted from the spec | **Drift Detection** — QA verifies plan vs actual, file by file |
| Same errors appear every session | **Auto-Blindaje** — errors documented immediately when they occur |
| Context window saturates mid-sprint | **Sub-agent Protocol** — each phase starts fresh, no context overload |
| Loading irrelevant instructions | **Skills Router** — loads only the skills relevant to the current task |
| Components talk in incompatible formats | **Integration Contract** — exact request/response format, blocking |
| No visibility on sprint progress | **Sprint Cadence** — Planning, Status, Retrospective built in |

---

## Quick Start

```bash
# Clone into your project
git clone https://github.com/ferrosasfp/nexus-agile.git /tmp/nexus-agile
cp -r /tmp/nexus-agile/.claude/skills/nexus-agile/ your-project/.claude/skills/nexus-agile/
rm -rf /tmp/nexus-agile
```

Restart Claude Code. Then bootstrap:

```
NexusAgile, this is a new project. Read the codebase and generate project-context.md
```

Claude discovers your stack automatically: language, framework, folder structure, commands, DB, auth. No manual editing needed. From the next feature, just say:

```
NexusAgile, implement [your feature description]
```

---

## 3 Modes

Pick based on what you're building:

| | FAST | LAUNCH | QUALITY |
|---|---|---|---|
| **Use when** | Bug fix, text change, style tweak | MVP, prototype, new app | Feature for real users (DB, auth, payments) |
| **Pipeline** | Triage → Patch | Simplified story → Dev → Light QA | Full pipeline below |
| **Human gates** | None | One: approve HU list | Two per HU + sprint ceremonies |
| **Sprint ceremonies** | No | No | Yes |
| **Speed** | ⚡⚡⚡ | ⚡⚡ | ⚡ |

When in doubt: **QUALITY**.

---

## The Pipeline

Every feature in QUALITY mode moves through this pipeline. You only make decisions at the two gates — everything else runs automatically.

```
⛔ SPRINT_APPROVED     ← Sprint Planning: HU list, estimates, order

  For each HU in the sprint:
  ┌─────────────────────────────────────────────────────┐
  │  F0:   Bootstrap + Smart Sizing + Skills Router     │
  │  F1:   Work Item + EARS ACs + Scope + Dependencies  │
  │  ⛔   HU_APPROVED                                   │
  │  F2:   Codebase Grounding + SDD + Adversary Review  │
  │  ⛔   SPEC_APPROVED                                 │
  │  F2.5: Story File — the only document Dev reads     │
  │  F3:   Implementation — Waves + Anti-Hallucination  │
  │  AR:   Adversarial Review — BLOCKER / MINOR / OK    │
  │  CR:   Code Review — pattern compliance             │
  │  F4:   QA — AC evidence file:line + quality gates   │
  │  DONE: report + _INDEX.md updated                   │
  └─────────────────────────────────────────────────────┘

⛔ RETRO_APPROVED      ← Sprint Retrospective + Closure Checklist
```

The human makes decisions at the gates. Between gates, the pipeline runs automatically — Claude never asks "shall I continue?". That is a process error.

---

## What's New

### Skills Router *(added March 2026)*

Loads only the skills relevant to the current task. No more 1000-line AGENTS.md loaded on every turn.

```
HU about React component → loads skill-frontend only
HU about DB migration    → loads skill-database only
HU about a Solidity fix  → loads skill-web3 only
```

Maximum 2 domain skills per HU. More than 2 is a signal the HU is too large.

The Architect declares which skills it loaded in F0, before any code is written.

→ Full reference: [`references/skills_router.md`](.claude/skills/nexus-agile/references/skills_router.md)

---

### Sub-agent Protocol *(added March 2026)*

Each phase of the pipeline runs in a fresh sub-agent with clean context. The orchestrator only coordinates — it never reads files, writes code, or generates specs.

```
Without sub-agents:
F0 → F1 → F2 → ... → DONE   (one session, context saturates, hallucinations spike)

With sub-agents:
Orchestrator
  ├─► [sub-agent F0] → project-context.md
  ├─► [sub-agent F1] → work-item.md
  ├─► [sub-agent F2] → sdd.md
  ├─► [sub-agent F2.5] → story-file.md
  ├─► [sub-agent F3]   → code
  ├─► [sub-agent AR]   → adversarial report
  ├─► [sub-agent F4]   → validation.md
  └─► [sub-agent DONE] → report.md + _INDEX.md
```

Works with Claude Code (Task tool), OpenCode, or any agent with sub-agent support. Falls back gracefully to single-session with Skills Router when sub-agents aren't available.

→ Full reference: [`references/subagent_protocol.md`](.claude/skills/nexus-agile/references/subagent_protocol.md)

---

## The Story File

The single most important concept in NexusAgile.

After the SDD is approved, the Architect generates a **Story File** — a self-contained contract that Dev reads and executes. It contains:

- Goal in 1-2 sentences
- Acceptance Criteria copied from the SDD
- Every file to create/modify, each with a real Exemplar from the codebase
- Integration Contract: exact input/output format between components (blocking)
- Constraint Directives: REQUIRED / FORBIDDEN per task
- Waves: W0 serial (foundation), W1+ parallel
- Out of Scope: explicit list of what Dev cannot touch

**No Story File = No coding. No exceptions.**

Dev reads only the Story File. Not the SDD, not the original HU, not the conversation history. This is what eliminates hallucination at the implementation phase.

---

## The 9 Agents

Roles Claude assumes depending on the phase. Not separate people — Claude switching hats.

| Agent | Active in | Does |
|---|---|---|
| **Analyst** | F0, F1 | Normalizes HU into Work Item, writes EARS ACs, defines Scope IN/OUT |
| **Architect** | F0, F1, F2, F2.5, CR | Codebase Grounding, SDD, Exemplars, Story File, Code Review |
| **UX** | F1 (UI only) | Microcopy, user flows, accessibility |
| **Adversary** | F2, AR, CR | Attacks SDD and implementation across 8 security categories |
| **Dev** | F3 | Reads only the Story File. Implements in Waves. Never improvises. |
| **SM** | Sprint cadence | Planning, Status, Retrospective, Closure Checklist |
| **QA** | F4, CR | Drift Detection + AC evidence file:line + quality gates |
| **Triage** | FAST flow | Evaluates if FAST applies. Escalates when it doesn't. |
| **Docs** | DONE | Final report + `_INDEX.md` + issue closed |

**Separation rules (non-negotiable):**
```
Analyst (defines)     ≠  Architect (specifies)
Architect (specifies) ≠  Dev (implements)
Dev (implements)      ≠  Adversary (attacks)
Adversary (attacks)   ≠  QA (validates)
```

---

## The Artifacts

```
doc/sdd/
└── NNN-feature-title/
    ├── work-item.md       ← F1: normalized HU + EARS ACs
    ├── sdd.md             ← F2: routes, schema, Constraint Directives
    ├── story-file.md      ← F2.5: the only document Dev reads
    ├── validation.md      ← F4: Drift Detection + AC evidence
    └── report.md          ← DONE: summary + Auto-Blindaje log
doc/sdd/_INDEX.md          ← history of every closed HU
sprint-status.yaml         ← live sprint state
project-context.md         ← real stack + patterns (generated once, reused forever)
```

---

## The Gates

| Gate | Exact text | Activates |
|---|---|---|
| `SPRINT_APPROVED` | `SPRINT_APPROVED` | Dev starts the sprint |
| `HU_APPROVED` | `HU_APPROVED` | Architect starts the SDD |
| `SPEC_APPROVED` | `SPEC_APPROVED` | Architect generates Story File, Dev starts |
| `REVIEW_APPROVED` | `REVIEW_APPROVED` | Pipeline continues after Status Meeting |
| `RETRO_APPROVED` | `RETRO_APPROVED` | Sprint closed |

"yes", "ok", "go", "sounds good", "dale" do **NOT** activate any gate. Only the exact text.

---

## Skill Structure

```
.claude/skills/nexus-agile/
├── SKILL.md                             # Full pipeline — all phases, all rules
└── references/
    ├── agents_roster.md                 # 9 agents with personalities and responsibilities
    ├── sdd_template.md                  # SDD templates (FULL / BUGFIX / MINI)
    ├── story_file_template.md           # Architect-Dev contract template
    ├── adversarial_review_checklist.md  # 8 attack categories for the Adversary
    ├── validation_report_template.md    # QA: Drift Detection + ACs + quality gates
    ├── skills_router.md                 # ✨ Selective context loading per task
    ├── subagent_protocol.md             # ✨ Per-phase sub-agent orchestration
    ├── launch_flow.md                   # LAUNCH mode detailed pipeline
    ├── quick_flow.md                    # FAST mode detailed pipeline
    ├── sprint_cadence.md                # SM Planning / Status / Retro / Closure Checklist
    └── project_context_template.md      # Stack-agnostic project-context template
```

---

## Relationship with NexusFactory

```
NexusFactory  =  opinionated project template (Next.js + Supabase + Viem + Foundry)
             +   NexusAgile preinstalled (stack-aware, project-context.md preconfigured)

NexusAgile    =  standalone methodology (any stack, any framework)
```

NexusAgile works without NexusFactory. NexusFactory includes NexusAgile by default.

→ [NexusFactory repo](https://github.com/ferrosasfp/NexusFactory)

---

## What Teams Are Shipping With It

NexusAgile is actively used in production across:

- **[WasiAI](https://app.wasiai.io)** — AI agent marketplace on Avalanche mainnet. Full sprint cadence with 6+ sprints closed, 180+ tests passing.
- **[Troker](https://troker-ap.vercel.app)** — barter platform. Complex features (dashboard, proposals, real-time chat) shipped in QUALITY mode.

Both projects use the full QUALITY pipeline with NexusFactory as the base stack.

---

## FAQ

**Does it work with stacks other than Next.js?**
Yes. NexusAgile is fully stack-agnostic. F0 discovers your stack and generates `project-context.md` from scratch. It has been used with Next.js, Vite, plain Node.js, and Foundry (Solidity).

**What if I'm mid-project and don't have project-context.md?**
Run: `NexusAgile, read the codebase and generate project-context.md`. Done in one session.

**Can I use it without sub-agent support?**
Yes. Falls back to single-session with Skills Router. Context stays manageable. Sub-agents are an optimization, not a requirement.

**How is this different from just prompting Claude well?**
Good prompts get you one good response. NexusAgile gets you a whole sprint's worth of consistent, auditable, reviewable work — with human control at the two moments that matter.

**What if Claude doesn't follow the process?**
That's a training signal. Document it in Auto-Blindaje, adjust the SKILL.md, and the process improves over time.

---

## Credits

Methodology created by [Fernando Rosas](https://github.com/ferrosasfp).
Combines Nexus SDD Workflow, Scrum ceremonies, and specialized AI agent roles.

MIT License
