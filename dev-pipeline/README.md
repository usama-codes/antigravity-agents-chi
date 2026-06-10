# Dev Pipeline — Antigravity Plugin

> **Multi-agent feature development pipeline that automates the full story-to-ship workflow.**

## Overview

The **Dev Pipeline** plugin transforms a single Jira-style user story into a fully implemented, tested, and review-ready feature — orchestrated entirely by a coordinated team of AI agents. Each agent owns a discrete phase of the software delivery lifecycle, producing verified artifacts that feed into the next stage.

**Input:** A user story (plain text or structured Jira format)
**Output:** A feature branch with implemented code, design assets, test results, and a comprehensive completion report — ready for human PR review.

---

## How It Works

Give the orchestrator a story like:

```
As a user, I want to reset my password via email so that I can regain access to my account.

Acceptance Criteria:
- User can request a password reset from the login screen
- System sends a reset link to the registered email
- User can set a new password via the reset link
- Link expires after 24 hours
```

The pipeline takes it from there:

```
Story → Requirements → Design → Development → QA → Ship-Ready
```

---

## Agent Hierarchy

```
┌─────────────────────────────────────────────────┐
│              Pipeline Orchestrator               │
│    (Brain — coordinates all stages & agents)     │
└──────────┬──────────┬──────────┬────────────────┘
           │          │          │
     ┌─────▼──┐  ┌────▼───┐  ┌──▼──────────────┐
     │   PM   │  │Designer│  │ Mobile Team Lead │
     └────────┘  └────────┘  └──────┬───────────┘
                                    │
                              ┌─────▼──────┐
                              │ Flutter Dev│
                              └────────────┘
                                    │
                              ┌─────▼──────────┐
                              │  QA Engineer   │
                              └────────────────┘
```

| Agent | Responsibility | Workspace |
|---|---|---|
| **Orchestrator** | Parses story, spawns agents in sequence, validates stage exits, compiles final report | Inherited |
| **Project Manager (PM)** | Breaks story into detailed requirements, user stories, acceptance criteria, edge cases | Inherited |
| **Designer** | Creates UI mockups (via image generation), writes design spec with component hierarchy, spacing, colors | Inherited |
| **Mobile Team Lead** | Plans implementation, spawns Flutter Dev(s), reviews code, ensures MVVM compliance | Branched |
| **Flutter Dev** | Implements features in Dart/Flutter following MVVM architecture and coding standards | Inherited from TL branch |
| **QA Engineer** | Writes and runs `flutter test`, validates acceptance criteria, produces QA report | Shared with TL branch |

---

## Pipeline Stages

### Stage 1 — Requirements (PM Agent)
- **Input:** Raw user story
- **Output:** `pipeline_output/requirements.md` — structured requirements with user stories, acceptance criteria, edge cases, technical constraints
- **Exit Criteria:** Document exists with ≥1 user story and acceptance criteria section

### Stage 2 — Design (Designer Agent)
- **Input:** `requirements.md`
- **Output:** `pipeline_output/design_spec.md` + mockup images in `pipeline_output/mockups/`
- **Exit Criteria:** Design spec exists with component hierarchy; at least one mockup image generated

### Stage 3 — Development (Mobile Team Lead → Flutter Dev)
- **Input:** `requirements.md` + `design_spec.md`
- **Output:** Implemented Flutter code on a feature branch, following MVVM architecture
- **Exit Criteria:** TL reports branch name; code compiles (`flutter analyze` passes)

### Stage 4 — QA (QA Engineer Agent)
- **Input:** Acceptance criteria from `requirements.md`, feature branch code
- **Output:** `pipeline_output/qa_report.md` — test results, coverage notes, pass/fail status
- **Exit Criteria:** All acceptance-criteria tests pass; QA report is complete

### Stage 5 — Completion Report
- **Output:** Summary sent to the user with: what was built, design decisions, test results, branch name, and next steps for PR review

---

## Usage

1. **Trigger the pipeline** by providing a user story to the agent when the `pipeline-orchestrator` skill is active.
2. **Wait for completion** — the orchestrator manages all inter-agent coordination, artifact validation, and failure recovery.
3. **Review the output** — check `pipeline_output/` in your workspace for all artifacts, and the reported feature branch for the code.

### Example Prompt
```
Run the dev pipeline for this story:

As a customer, I want to view my order history so I can track past purchases.

Acceptance Criteria:
- Orders displayed in reverse chronological order
- Each order shows date, total, and status
- Tapping an order shows full details
- Empty state shown when no orders exist
```

---

## Phase 1 Scope (Current)

| Aspect | Detail |
|---|---|
| **Platform** | Flutter only (mobile) |
| **Architecture** | MVVM (Model-View-ViewModel) |
| **Testing** | `flutter test` (unit + widget tests) |
| **Review** | PR-based (agent creates feature branch, human reviews) |
| **Git Workflow** | Conventional commits, feature branches |

---

## Phase 2 Roadmap

- **Web Team**: Add web developer agents (React/Next.js)
- **Native Teams**: C++ / Java / Swift developer agents for platform-specific features
- **CI/CD Integration**: Automated pipeline triggers from Jira/Linear webhooks
- **Design System Sync**: Figma integration for design spec generation
- **Multi-platform Orchestration**: Coordinate across Flutter, web, and native teams simultaneously
- **Advanced QA**: Integration tests, performance benchmarks, accessibility audits

---

## Directory Structure

```
dev-pipeline/
├── plugin.json
├── README.md
└── skills/
    ├── pipeline_orchestrator/
    │   ├── SKILL.md              # The brain — orchestrator instructions
    │   └── references/
    │       ├── pipeline_stages.md # Detailed stage definitions
    │       └── agent_registry.md  # Agent role → config lookup table
    └── shared/
        ├── SKILL.md              # Shared standards (not standalone)
        └── references/
            ├── coding_standards.md      # Flutter/Dart MVVM standards
            ├── git_conventions.md       # Branch/commit/PR conventions
            └── communication_protocol.md # Inter-agent messaging protocol
```

---

## Architecture Decisions

1. **Stage-gated workflow**: Each stage must pass exit criteria before the next begins. No skipping.
2. **Artifact-based communication**: Agents communicate via files in `pipeline_output/`, not ephemeral messages. This ensures traceability.
3. **Branched workspaces for development**: The Mobile TL works in a branched workspace to isolate in-progress code from the main workspace.
4. **Shared workspaces for QA**: The QA agent shares the TL's branch so it can run tests against the actual implementation.
5. **Watchdog timers**: 300-second timeouts on every subagent invocation prevent hung pipelines.
6. **Retry-once policy**: If a stage fails, it retries once before escalating to the user.

---

## License

MIT
