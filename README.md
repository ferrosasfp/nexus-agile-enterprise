# NexusAgile Enterprise

> *"The human decides WHAT. The agents decide HOW."*

You describe a feature. Claude writes code confidently, imports a module that doesn't exist, follows patterns inconsistent with your codebase, and modifies files it wasn't supposed to touch. You spend 40 minutes fixing what should have taken 10.

That's not a Claude problem. That's a structure problem.

**NexusAgile is a software development methodology built for AI agents.** It covers the full lifecycle: sprint planning, feature implementation, adversarial review, QA, and retrospectives — with specialized agents, strict gates, and zero tolerance for hallucination.

Stack-agnostic. Installs in minutes as a Claude Code skill. Works with any framework.

```
npm i  →  No.  Just copy one folder into your project.  Done.
```


## The Problem It Solves

| Problem | NexusAgile Solution |
|---|---|
| AI invents imports and modules | **Codebase Grounding** — reads real files before generating anything |
| AI creates inconsistent patterns | **Exemplar Pattern** — references existing files in your codebase |
| AI ignores restrictions | **Constraint Directives** — explicit REQUIRED / FORBIDDEN per task |
| Implementation drifted from the plan | **Drift Detection** — plan vs implementation verified in QA |
| Errors repeat across sessions | **Auto-Blindaje** — documents errors immediately when they occur |
| Context overload → hallucinations | **Sub-Agent Protocol** — each phase starts with a clean context window |
| Wrong skills loaded for the task | **Skills Router** — loads only the 1-2 skills relevant to each HU |
| Components talking in incompatible formats | **Integration Contract** — exact request/response format between components |
| No sprint visibility | **Sprint Cadence** — Planning, Status, and Retrospective built in |


## How a Sprint Works

```
⛔ SPRINT_APPROVED     ← Sprint Planning: HU list, estimates, order, branch strategy

  For each HU in the sprint:
  ┌─────────────────────────────────────────────────────┐
  │  F0: Bootstrap + Smart Sizing + Skills Router       │
  │  F1: Work Item + EARS ACs + Scope + Dependencies    │
  │  ⛔ HU_APPROVED                                     │
  │  F2: Codebase Grounding + SDD + Adversary Review    │
  │  ⛔ SPEC_APPROVED                                   │
  │  F2.5: Story File (the only thing Dev reads)        │
  │  F3: Implementation — Waves + Anti-Hallucination    │
  │  AR: Adversarial Review — BLOCKER / MINOR / OK      │
  │  CR: Code Review — pattern compliance               │
  │  F4: QA — AC evidence file:line + quality gates     │
  │  DONE: report + _INDEX.md + issue closed            │
  └─────────────────────────────────────────────────────┘

⛔ REVIEW_APPROVED     ← Mid-sprint Status Meeting (optional)
⛔ RETRO_APPROVED      ← Sprint Retrospective + Closure Checklist
```

The human makes decisions at the gates. **Everything else runs automatically.**


## 3 Modes

| | FAST | LAUNCH | QUALITY |
|---|---|---|---|
| **Best for** | Fix a bug, update a text, tweak a style | Build an MVP or prototype from scratch | Ship a feature to real users |
| **You get** | Working code in minutes | A structured codebase with anti-hallucination from day one | Full audit trail: spec, adversarial review, QA evidence |
| **Human gates** | None | One: approve the HU list | Two per HU + three sprint ceremony gates |
| **Sprint ceremonies** | No | No | Yes |
| **When in doubt** | | | Use this one |


## What's New — Sub-Agent Protocol + Skills Router

Two additions that solve context overload in complex features:

### Sub-Agent Protocol

Without sub-agents, a full QUALITY pipeline accumulates context in a single session. By F4, the context window is saturated — and that's where hallucinations start.

With sub-agents, each phase starts fresh:

```
Orchestrator (minimal context — coordinates only)
     │
     ├─► [sub-agent F0]   → delivers: project-context.md + sizing
     ├─► [sub-agent F1]   → delivers: work-item.md
     │         ⛔ HU_APPROVED
     ├─► [sub-agent F2]   → delivers: sdd.md
     │         ⛔ SPEC_APPROVED
     ├─► [sub-agent F2.5] → delivers: story-file.md
     ├─► [sub-agent F3]   → delivers: code + auto-blindaje log
     ├─► [sub-agent AR]   → delivers: adversarial review report
     ├─► [sub-agent CR]   → delivers: code review report
     ├─► [sub-agent F4]   → delivers: validation.md
     └─► [sub-agent DONE] → delivers: report.md + _INDEX updated
```

The orchestrator never writes code, generates SDDs, or touches files. It coordinates, receives artifacts, and manages gates.

**Works with:** Claude Code (Task tool), OpenCode (spawned agents), or any IDE with sub-agent support. Falls back gracefully to single-session with Skills Router when sub-agents aren't available.

### Skills Router

Without a router: a monolithic `AGENTS.md` with 1000+ lines loaded on every turn — Angular patterns loaded for a Supabase migration, blockchain instructions loaded for a CSS fix.

With the Skills Router, the Architect runs a lightweight detection at F0 and loads only the 1-2 skills relevant to the current HU:

| Signal in the HU | Skill loaded |
|---|---|
| component, UI, React, layout | `skill-frontend` |
| table, migration, query, Supabase | `skill-database` |
| auth, JWT, session, permissions | `skill-auth` |
| contract, Solidity, Web3, wallet | `skill-web3` |
| endpoint, route, REST, middleware | `skill-backend` |

Max 2 domain skills per HU. More than 2 is a signal the HU is too large — split it.

Skills can come from your own project-specific skill files or from a shared `skills/` directory in your monorepo. The router is agnostic to the source.


## The Feature Pipeline (per HU)

### F0: Bootstrap + Smart Sizing + Skills Router

Checks for `project-context.md`. If not found, reads the codebase from scratch (dependencies, structure, patterns, commands, DB, auth) and generates it — once, reused across every session.

Classifies the HU by SDD_MODE:

| Signal | SDD_MODE |
|---|---|
| Max 2 files, no DB, no new logic | `patch` → FAST pipeline |
| Bug with reproduction steps | `bugfix` → lightweight SDD |
| Refactor or tech task | `mini` → minimal SDD |
| Feature with logic | `full` → full pipeline |

Then runs the Skills Router: detects the domain from the HU and loads only the relevant skills.

### F1: Discovery

Analyst normalizes the HU into a Work Item: objective, EARS Acceptance Criteria, Scope IN/OUT, and missing inputs. UX contributes microcopy and user flows when UI is involved. Architect analyzes dependencies and proposes execution order.

Output: `work-item.md`

Gate: `HU_APPROVED`

### F2: SDD

Deep Codebase Grounding: reads 2-3 real files related to the HU, extracts patterns (imports, naming, structure), identifies an Exemplar for every file that will be touched. Everything documented in a Context Map.

Then writes the SDD: routes, schema, UI spec, Constraint Directives (REQUIRED / FORBIDDEN), Integration Contract when components communicate, and a Readiness Check that verifies every AC has a file and every file has a valid Exemplar.

Adversary reviews the SDD before it reaches the human. No `[NEEDS CLARIFICATION]` items allowed at the gate.

Output: `sdd.md`

Gate: `SPEC_APPROVED`

### F2.5: Story File

The autocontained contract Dev reads — and **only** this document. Contains: goal in 1-2 sentences, ACs from the SDD, files to create/modify each with a real Exemplar, Integration Contract, Constraint Directives, Waves, and an Escalation Rule.

**No Story File = No coding. No exceptions.**

Output: `story-file.md`

### F3: Implementation

Dev follows the Anti-Hallucination Protocol before each task: reads the Exemplar, verifies imports exist, follows the project's patterns. No unapproved dependencies. No touching files outside Scope IN.

Work organized in Waves. W0 serial (the foundation). W1+ parallel. Before each wave, Dev re-maps: reads files created or modified in the previous wave to verify what the current wave needs actually exists. Every error documented immediately in Auto-Blindaje.

Incremental typecheck: passes after every wave. Fails → fix before continuing.

### Adversarial Review

A separate agent attacks the implementation across 8 categories: authorization, input validation, injection, secret exposure, race conditions, data exposure, mock data in production, and DB security.

BLOCKER findings must be fixed before continuing. Adversary re-reviews after each fix.

### F4: QA

Drift Detection: files created vs expected, files modified vs expected, new dependencies, files outside scope. Every AC verified with `file:line` evidence. No evidence = not done. Quality gates: typecheck + lint + build clean.

Output: `validation.md`

### DONE

```
doc/sdd/
└── NNN-title/
    ├── work-item.md      ← F1
    ├── sdd.md            ← F2
    ├── story-file.md     ← F2.5
    ├── validation.md     ← F4
    └── report.md         ← DONE
doc/sdd/_INDEX.md         ← history of every closed HU
```


## The 9 Agents

| Agent | Role | Active in |
|---|---|---|
| **Analyst** | Interprets input, normalizes into Work Item, writes EARS ACs, defines scope | F0, F1 |
| **Architect** | Codebase Grounding, Context Map, Exemplars, SDD, Story File, Code Review | F0, F1, F2, F2.5, CR |
| **UX** | Microcopy, user flows, accessibility — only when the HU has UI | F1 (UI only) |
| **Adversary** | Attacks SDD (F2) and implementation (AR) across 8 categories. Never implements. | F2, AR, CR |
| **Dev** | Reads ONLY the Story File. Implements in Waves. Anti-Hallucination Protocol always on. | F3, post-AR fixes |
| **SM** | Sprint Planning, Status Meeting, Retrospective, Sprint Closure Checklist | Sprint cadence |
| **QA** | Drift Detection, AC evidence file:line, quality gates, Validation Report | F4, CR |
| **Triage** | Evaluates if a change qualifies for FAST. Escalates if it grows beyond scope. | FAST flow |
| **Docs** | Compiles report, updates `_INDEX.md`, verifies all artifacts, closes issue | DONE |

**Separation rules:**
```
Analyst (defines)   ≠  Architect (specifies)  ≠  Dev (implements)  ≠  Adversary (attacks)  ≠  QA (validates)
```


## Gates

| Gate | Exact text | When |
|---|---|---|
| `SPRINT_APPROVED` | `SPRINT_APPROVED` | After Sprint Planning |
| `HU_APPROVED` | `HU_APPROVED` | After F1 Work Item |
| `SPEC_APPROVED` | `SPEC_APPROVED` | After F2 SDD |
| `REVIEW_APPROVED` | `REVIEW_APPROVED` | After Status Meeting |
| `RETRO_APPROVED` | `RETRO_APPROVED` | After Retrospective |

Only the exact text activates the gate. "yes", "ok", "go", "sure" do **not** activate any gate.

Between gates, the pipeline runs automatically. The agent never asks "shall I continue?" — that is a process error.


## Installation

```bash
git clone https://github.com/ferrosasfp/nexus-agile-enterprise /tmp/nexus-agile
cp -r /tmp/nexus-agile/.claude/skills/nexus-agile/ your-project/.claude/skills/nexus-agile/
rm -rf /tmp/nexus-agile
```

Restart Claude Code. Skills load automatically.

**First session:**
```
NexusAgile, this is a new project. Read the codebase and generate project-context.md
```

Claude discovers: language, framework, architecture, commands, patterns. No manual setup.

**Or use it immediately on an existing project:**
```
NexusAgile, sprint planning
```


## Skill Structure

```
.claude/skills/nexus-agile/
├── SKILL.md                             # Full pipeline, 3 modes, global rules
└── references/
    ├── agents_roster.md                 # 9 agents — personality + responsibilities
    ├── sdd_template.md                  # SDD templates: FULL / BUGFIX / MINI
    ├── story_file_template.md           # Architect-Dev contract + Integration Contract
    ├── adversarial_review_checklist.md  # 8 attack categories for the Adversary
    ├── validation_report_template.md    # QA: drift + ACs + quality gates
    ├── skills_router.md                 # Selective skill loading — clean context per HU
    ├── subagent_protocol.md             # Orchestration — each phase in a fresh context
    ├── launch_flow.md                   # Detailed LAUNCH mode pipeline
    ├── quick_flow.md                    # Detailed FAST mode pipeline
    ├── sprint_cadence.md                # SM Planning / Status / Retro / Closure Checklist
    ├── project_context_template.md      # Stack-agnostic project-context template
    ├── roles_matrix.md                  # 🆕 Enterprise: human roles + gate authority matrix
    ├── concurrent_work_protocol.md      # 🆕 Enterprise: multi-dev branches, PRs, conflicts
    ├── metrics.md                       # 🆕 Enterprise: KPIs, dashboard, sprint reports
    ├── onboarding.md                    # 🆕 Enterprise: quick start by role + cheat sheet
    ├── governance.md                    # 🆕 Enterprise: scope changes, disputes, incidents
    ├── greenfield_bootstrap.md          # 🆕 Enterprise: new project from scratch
    ├── cross_team_protocol.md           # 🆕 Enterprise: multi-team coordination
    └── integration_contract_template.md # 🆕 Enterprise: API/service contract template
```




## Enterprise — Teams & Organizations

NexusAgile Enterprise extends the core methodology for teams of 2+ developers working concurrently on the same codebase.

### What's New

| Capability | Solo | Enterprise |
|---|---|---|
| **Human roles** | One person does everything | PO, Tech Lead, Dev, QA Lead, SM — each with defined authority |
| **Gate approval** | Self-approved | Specific human approver per gate, with backup and audit trail |
| **Concurrent work** | Sequential HUs | Multiple devs in parallel with branch protection and PR workflow |
| **AI delegation** | Full autonomy | Autonomy matrix: what AI can do alone vs what needs human approval |
| **Metrics** | None | Lead time, BLOQUEANTE rate, drift rate, cost/HU, sprint dashboard |
| **Onboarding** | Read everything | Role-based reading paths, first HU in <1 hour |
| **Escalation** | N/A | Dev → TL (2h) → PO (4h) with defined timeouts |

### Enterprise References

| Document | What it covers |
|---|---|
| `references/roles_matrix.md` | 5 human roles, gate authority matrix, AI delegation levels, escalation paths, team size configs |
| `references/concurrent_work_protocol.md` | Branch strategy, PR workflow, HU ownership, conflict prevention, dependency coordination |
| `references/metrics.md` | 20+ KPIs across velocity/quality/anti-hallucination/AI efficiency, dashboard template, sprint report |
| `references/onboarding.md` | Role-based quick start, first HU walkthrough, cheat sheet, common mistakes, FAQ |

### Team Size Configurations

| Size | Setup |
|---|---|
| **Solo (1)** | Original NexusAgile. Self-approved gates. Max AI delegation. |
| **Small (2-4)** | PO part-time. TL doubles as QA. 1-2 devs. SM rotates. |
| **Medium (5-8)** | Dedicated PO, TL, QA. 3-5 devs. SM dedicated. |
| **Large (9+)** | Split into 2+ independent NexusAgile teams. Scrum of Scrums for coordination. |



### Governance & Exception Protocols

Real-world development is messy. NexusAgile Enterprise defines protocols for when things don't go as planned:

| Situation | Protocol | Reference |
|---|---|---|
| PO changes scope after approval gate | Scope Change Tiers (Trivial/Minor/Major) | `references/governance.md` |
| Dev disputes an AR BLOQUEANTE finding | Dispute Resolution (Confirm/Downgrade/Dismiss) | `references/governance.md` |
| Production incident mid-sprint | Incident Protocol (P0/P1/P2) with severity, SLA, and sprint adjustment | `references/governance.md` |
| FAST mode turns out to be complex | Clean escalation to QUALITY with artifact carry-over | `references/governance.md` |
| Building from scratch (no codebase) | Greenfield Bootstrap with stack capture + scaffold | `references/greenfield_bootstrap.md` |
| Cross-team dependencies | Scrum of Scrums, dependency board, escalation ladder | `references/cross_team_protocol.md` |
| Components/services communicate | Formal Integration Contract with schema + SLA | `references/integration_contract_template.md` |

### Use Cases — Real-World Simulations

12 simulated scenarios covering every team size and mode combination. Each case shows the complete flow: what the human does, what the AI does, and where the gates are.

> Full document: `use-cases.md` in the root of this repo.

| # | Scenario | Team | Mode | Status |
|---|----------|------|------|--------|
| 1 | Solo dev — Payment integration | 1 person | QUALITY | Documented |
| 2 | Solo dev — Typo fix | 1 person | FAST | Documented |
| 3 | 2-person team — Feature + Fix | 2 people | QUALITY + FAST | Documented |
| 4 | Medium team — 3 HUs in parallel | 5 people | QUALITY + FAST | Documented |
| 5-12 | Large teams + edge cases | 6-12 people | Mixed | Planned |


## Relationship with NexusFactory

```
NexusFactory  =  opinionated project template (Next.js + Supabase + Viem + Foundry)
             +   NexusAgile pre-configured (stack-aware, no bootstrap needed)

NexusAgile    =  standalone methodology (any stack, any framework)
```

NexusAgile works without NexusFactory.
NexusFactory includes NexusAgile by default.

→ [NexusFactory repo](https://github.com/ferrosasfp/NexusFactory)


## Credits

Methodology created by [Fernando Rosas](https://github.com/ferrosasfp).
Merges the Nexus SDD Workflow with agile sprint practices and specialized AI agent roles.

MIT License

