# NexusAgile

> *"The human decides WHAT. The agents execute HOW."*

You describe a feature to Claude. It writes code confidently, imports a module that doesn't exist, follows patterns inconsistent with your project, and modifies files it wasn't supposed to touch. You spend 40 minutes fixing what should have taken 10.

That's not a Claude problem. That's a structure problem.

**NexusAgile is a software development methodology designed for AI agents.** It covers the full software development lifecycle: sprint planning, feature implementation, adversarial review, QA, retrospectives, and sprint closure. All with specialized agents, strict gates, and zero tolerance for hallucination.

Inspired by Scrum, NexusAgile organizes work in sprints with planning, status, and retrospective ceremonies. Each sprint contains one or more User Stories that move through a structured pipeline until they ship. The difference is that the agents execute the process, not the team.

Stack-agnostic. Installs in minutes as a Claude Code skill.


## The Problem It Solves

| Problem | NexusAgile Solution |
|---|---|
| AI invents imports/modules | **Codebase Grounding:** read real files before generating anything |
| AI creates inconsistent patterns | **Exemplar Pattern:** reference existing files in the codebase |
| AI ignores restrictions | **Constraint Directives:** explicit REQUIRED/FORBIDDEN per task |
| Implementation drifted from the plan | **Drift Detection:** plan vs implementation verified in QA |
| Errors repeat across sessions | **Auto-Blindaje:** document errors immediately when they occur |
| Unstructured implementation | **Waves:** W0 serial, W1+ parallel with re-mapping between waves |
| Components talking in incompatible formats | **Integration Contract:** exact request/response format between components, blocking |
| No visibility on sprint progress | **Sprint Cadence:** Planning, Status and Retrospective ceremonies built in |


## How a Sprint Works

NexusAgile manages the full sprint lifecycle. Every sprint starts with a planning ceremony and ends with a retrospective. Between those two points, features move through the implementation pipeline one by one.

```
⛔ SPRINT_APPROVED     ← Sprint Planning: HU list, estimates, order, branch strategy

  For each HU in the sprint:
  ┌─────────────────────────────────────────────────────┐
  │  F0: Bootstrap + Smart Sizing                       │
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

The human makes decisions at the gates. Everything else runs automatically.


## The Sprint Ceremonies

### Sprint Planning

**Activate:** `"NexusAgil, sprint planning"`

The SM agent runs the ceremony: reviews the backlog, proposes the HU list for the sprint, estimates effort, identifies dependencies between HUs, and proposes execution order (parallel where safe, sequential where needed). The Architect validates the technical feasibility.

Output: `sprint-status.yaml` with the HU list, order, and branch strategy.

Gate: `SPRINT_APPROVED`

### Status Meeting

**Activate:** `"NexusAgil, status"`

Mid-sprint check. The SM reviews what's done, what's in progress, and what's blocked. If a HU is behind, the SM proposes adjustments (reduce scope, carry over, or escalate).

Gate: `REVIEW_APPROVED`

### Retrospective

**Activate:** `"NexusAgil, retro"`

End of sprint. The SM runs the retrospective: what went well, what didn't, what to improve. Then executes the Sprint Closure Checklist: all HUs closed in the tracker, `_INDEX.md` updated, `sprint-status.yaml` marked CLOSED, lessons documented.

Gate: `RETRO_APPROVED`


## The Feature Pipeline (per HU)

Each HU goes through this pipeline inside the sprint. The two human gates are `HU_APPROVED` and `SPEC_APPROVED`. Everything else runs automatically.

### F0: Bootstrap + Smart Sizing

The Architect checks if `project-context.md` exists. If not, it reads the codebase from scratch (dependencies, folder structure, representative files, commands, DB, auth) and generates it. This file is created once and reused across every session.

Then it classifies the HU by SDD_MODE:

| Signal | SDD_MODE | What happens |
|--------|----------|--------------|
| Max 2 files, no DB, no new logic | patch | Redirects to FAST pipeline |
| Bug with reproduction steps | bugfix | Lightweight SDD |
| Refactor, tech task, no visible change | mini | Minimal SDD |
| Feature or improvement with logic | full | Full pipeline |

### F1: Discovery

The Analyst normalizes the HU into a Work Item: objective, EARS Acceptance Criteria, Scope IN/OUT, and missing inputs. The UX agent contributes microcopy and user flows when UI is involved.

The Architect analyzes dependencies with other HUs in the sprint and proposes execution order: parallel where there are no file conflicts, sequential where there are.

Output: `work-item.md` saved to `doc/sdd/NNN-title/`.

Gate: `HU_APPROVED` (approves the Work Item and the execution order)

### F2: SDD

The Architect does deep Codebase Grounding: reads at least 2-3 real files related to the HU, extracts patterns (imports, naming, structure), identifies an Exemplar for every file that will be created or modified, and documents everything in a Context Map.

Then writes the SDD using the template that matches the SDD_MODE (FULL / BUGFIX / MINI), including routes, schema, Constraint Directives (REQUIRED / FORBIDDEN), and a Readiness Check that verifies every AC has a file and every file has a valid Exemplar.

The Adversary reviews the SDD before it reaches the human. Any `[NEEDS CLARIFICATION]` must be resolved before the gate.

Output: `sdd.md` saved to `doc/sdd/NNN-title/`.

Gate: `SPEC_APPROVED`

### F2.5: Story File

The Architect generates the autocontained contract for Dev. Dev reads ONLY this document, nothing else — no SDD, no original HU. It contains: goal in 1-2 sentences, ACs copied from the SDD, a table of files to create/modify each with a real Exemplar, Integration Contract when components communicate (blocking: Dev cannot start without it), Constraint Directives, Waves, Out of Scope, and an Escalation Rule.

**No Story File = No coding. No exceptions.**

Output: `story-file.md` saved to `doc/sdd/NNN-title/`.

### F3: Implementation

Dev follows the Anti-Hallucination Protocol before each task: reads the assigned Exemplar, verifies that imports exist, follows the project's patterns. No adding dependencies not approved in the SDD. No touching files outside Scope IN.

Work is organized in Waves. W0 is always serial (the foundation). W1+ can run in parallel. Before each wave Dev re-maps: reads the files created or modified in the previous wave to verify that what the current wave needs actually exists. Every error found is documented immediately in Auto-Blindaje: what failed, how it was fixed, where else it applies.

Incremental verification: typecheck passes after every wave. If it fails, Dev fixes before continuing.

### Adversarial Review

A separate agent attacks the full implementation across 8 categories: authorization, input validation, injection, secret exposure, race conditions, data exposure, mock data in production, and DB security. BLOCKER findings must be fixed before the pipeline continues. The Adversary re-reviews after each fix. MINOR findings are documented and fixed if quick.

### Code Review

Pattern compliance vs Story File Exemplars: naming consistency, function complexity, duplication, approved imports, and scope boundaries.

### F4: QA

Drift Detection compares what was built against the plan: files created, files modified, new dependencies, files outside scope. Every AC is verified with `file:line` evidence. No evidence = not done. Quality gates: typecheck + lint + build clean.

Output: `validation.md` saved to `doc/sdd/NNN-title/`.

### DONE

The Docs agent writes `report.md` with the summary, AC status, AR/CR findings, and the Auto-Blindaje log. Updates `_INDEX.md` and closes the issue in the tracker.

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


## 3 Modes

| | FAST | LAUNCH | QUALITY |
|---|---|---|---|
| **Best for** | Fix a bug, update a text, tweak a style | Build an MVP or prototype from scratch | Ship a feature to real users |
| **You get** | Working code in minutes | A structured codebase with anti-hallucination from day one | Full audit trail: spec, adversarial review, QA evidence |
| **Human decisions** | None. Just describe the change. | One gate: approve the HU list before Dev starts | Two gates per HU + three sprint ceremony gates |
| **Sprint ceremonies** | No | No | Yes |
| **Speed** | ⚡⚡⚡ | ⚡⚡ | ⚡ |
| **When in doubt** | | | Use this one |


## The 9 Agents

Agents are roles Claude assumes depending on the phase. They are not separate people, it's Claude switching hats. Who specifies does not implement. Who implements does not validate.

| Agent | Role | Active in |
|---|---|---|
| **Triage** | Evaluates if a change qualifies as FAST or escalates to LAUNCH/QUALITY | Quick Flow |
| **Analyst** | Extracts requirements, normalizes User Stories, defines EARS Acceptance Criteria | F0, F1 |
| **Architect** | Codebase Grounding, SDD, Story File, Code Review, dependency analysis | F0, F1, F2, F2.5, CR |
| **UX** | Microcopy, user flows, accessibility | F1 (when UI is involved) |
| **Adversary** | Attacks the solution looking for security and logic flaws | AR, CR, F2 review |
| **Dev** | Implements ONLY from the Story File, waves, anti-hallucination | F3 |
| **SM** | Sprint Planning, Status Meeting, Retrospective, Sprint Closure Checklist | Sprint cadence |
| **QA** | Validates ACs with file:line evidence, Drift Detection | F4 |
| **Docs** | Documents artifacts, updates `_INDEX.md`, closes issues in tracker | DONE |

**Separation rules:**
- Architect specifies, Dev implements, QA validates. Never the same agent.
- Adversary reviews code it did NOT write.
- SM runs ceremonies. SM does not implement.


## The Artifacts

| Artifact | Author | Purpose |
|---|---|---|
| `project-context.md` | Architect (F0, once) | Real stack, patterns, absolute rules. Every agent reads this. |
| `sprint-status.yaml` | SM | Live sprint state, updated at every ceremony |
| Work Item | Analyst + Architect (F1) | Normalized HU with EARS ACs, Scope IN/OUT, dependencies |
| SDD | Architect + Adversary (F2) | Technical spec: routes, schema, UI, Constraint Directives |
| Story File | Architect (F2.5) | The only document Dev reads. Autocontained contract. |
| Adversarial Review | Adversary (AR) | Attack report: BLOCKER / MINOR / OK |
| Code Review | Adversary + QA (CR) | Pattern compliance vs Exemplars |
| Validation Report | QA (F4) | Drift Detection + AC evidence file:line |
| `report.md` | Docs (DONE) | Final summary + Auto-Blindaje log |
| `_INDEX.md` | Docs | Historical record of all closed HUs |


## Gates

| Gate | Exact text | When |
|---|---|---|
| `SPRINT_APPROVED` | `SPRINT_APPROVED` | After Sprint Planning |
| `HU_APPROVED` | `HU_APPROVED` | After F1 Work Item + execution order |
| `SPEC_APPROVED` | `SPEC_APPROVED` | After F2 SDD |
| `REVIEW_APPROVED` | `REVIEW_APPROVED` | After Status Meeting |
| `RETRO_APPROVED` | `RETRO_APPROVED` | After Retrospective |

Only the exact text activates the gate. "yes", "ok", "go", "sounds good" do NOT activate any gate.

Between gates, the pipeline runs automatically. The agent never asks "shall I continue?" between phases. That is a process error.


## Installation

```bash
git clone https://github.com/ferrosasfp/nexus-agile.git /tmp/nexus-agile
cp -r /tmp/nexus-agile/.claude/skills/nexus-agile/ your-project/.claude/skills/nexus-agile/
rm -rf /tmp/nexus-agile
```

Restart Claude Code. Skills load automatically at startup.

**First session, automatic bootstrap:**
```
NexusAgile, this is a new project. Read the codebase and generate project-context.md
```

Claude discovers on its own: language, framework, architecture, commands, patterns. No manual editing needed.


## Skill Structure

```
.claude/skills/nexus-agile/
├── SKILL.md                             # Full pipeline, 3 modes, global rules
└── references/
    ├── agents_roster.md                 # 9 agents with personality and responsibilities
    ├── sdd_template.md                  # SDD templates (FULL / BUGFIX / MINI)
    ├── story_file_template.md           # Architect-Dev contract (incl. Integration Contract)
    ├── adversarial_review_checklist.md  # 8 attack categories for the Adversary
    ├── validation_report_template.md    # QA: drift + ACs + quality gates
    ├── launch_flow.md                   # Detailed LAUNCH mode pipeline
    ├── quick_flow.md                    # Detailed FAST mode pipeline
    ├── sprint_cadence.md                # SM Planning / Status / Retro / Sprint Closure Checklist
    └── project_context_template.md      # Stack-agnostic project-context template
```


## Relationship with NexusFactory

```
NexusFactory  =  opinionated project template (stack + structure)
             +   NexusAgile preinstalled (stack-aware version)

NexusAgile    =  standalone methodology (any stack)
```

**Key difference:**
- **NexusAgile standalone** (this repo) is fully stack-agnostic. It discovers the project stack at the beginning of each session and generates `project-context.md`.
- **NexusAgile inside NexusFactory** comes pre-configured for the NexusFactory Golden Path (Next.js + Supabase + Viem + Foundry). The `project-context.md` is already provided, no bootstrap needed.

NexusAgile works without NexusFactory.
NexusFactory includes NexusAgile by default.

[NexusFactory repo](https://github.com/ferrosasfp/NexusFactory)


## Credits

Methodology created by [Fernando Rosas](https://github.com/ferrosasfp).
Merges Nexus SDD Workflow and agile practices with specialized AI roles.

MIT License
