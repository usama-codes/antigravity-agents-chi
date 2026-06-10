# Delegation Strategy — Mobile Team Lead

This document guides the Mobile Team Lead on how to break down development work, assign it to Flutter developer agents, track progress, and handle escalations.

---

## Core Principle

The Team Lead's job is **not** to write code — it is to plan, supervise, review, and unblock. Delegate implementation to Flutter developer agents. Only write code yourself when demonstrating a pattern to a developer or resolving a critical blocker that requires immediate action.

---

## Task Chunking Strategy

Work must be broken into sequential chunks that respect the MVVM dependency order. Each chunk should be deliverable in one developer session and independently reviewable.

### Chunk Order (Always Bottom-Up)

```
Chunk 1: Data Layer (Models + Repository Interface)
  └─ Models: data classes, DTOs, enums
  └─ Repository interface: abstract class defining the contract

Chunk 2: Repository Implementation
  └─ Concrete repository class implementing the interface
  └─ API calls, local storage, error handling, data mapping

Chunk 3: ViewModel Layer
  └─ ViewModel class extending ChangeNotifier
  └─ State management (loading/error/success)
  └─ Business logic and data transformations
  └─ Calls repository interface (not implementation — inject the interface)

Chunk 4: View Layer — Base Structure
  └─ Screen scaffold (AppBar, body structure, navigation)
  └─ Provider setup (MultiProvider or ChangeNotifierProvider)
  └─ Connects to ViewModel but shows placeholder content

Chunk 5: View Layer — UI Components
  └─ List widgets, cards, forms, dialogs
  └─ All states wired up (loading spinner, error widget, empty state)
  └─ User interactions delegated to ViewModel

Chunk 6: Navigation & Integration
  └─ Named routes or GoRouter configuration
  └─ Deep link handling (if applicable)
  └─ Cross-feature integration (shared state, shared services)

Chunk 7: Polish & Edge Cases
  └─ Accessibility labels
  └─ Keyboard handling
  └─ Performance optimisations (const constructors, keys)
  └─ Remaining edge cases from requirements
```

> **Rule**: Never assign Chunk N+1 until Chunk N has been reviewed and approved.

---

## Writing Clear Task Descriptions

Each task message to the developer agent must contain:

### Task Description Template
```
## Task: {Chunk Name} — {Feature Name}

### Context
{Brief description of the overall feature and how this chunk fits in}

### Architecture Reference
- Read: skills/flutter_developer/references/mvvm_implementation.md
- Read: pipeline_output/architecture.md (section: {relevant section})

### Design Reference  
- Read: pipeline_output/design/specs/{screen_name}_spec.md (if UI task)

### Files to Create
| File Path | Description |
|-----------|-------------|
| lib/features/{feature}/models/{model_name}.dart | {purpose} |
| lib/features/{feature}/repositories/{repo}_interface.dart | {purpose} |
| ... | ... |

### Files to Modify
| File Path | What to Change |
|-----------|----------------|
| lib/main.dart | Register providers |
| ... | ... |

### Requirements
- {Specific requirement 1}
- {Specific requirement 2}
- {Error cases to handle: ...}
- {Acceptance criteria this chunk fulfils: AC-1, AC-2}

### Expected Output
Confirm via send_message when done. Include:
- List of all files created/modified
- Any assumptions made
- Any blockers or questions

### Do NOT
- {Specific thing to avoid for this chunk}
- Skip error handling on API calls
- Import Flutter UI packages in models or viewmodels
```

---

## Developer Spawning Pattern

### Spawning One Developer Agent

For Phase 1, spawn a single Flutter developer who works through the chunks sequentially:

```
1. Read skills/flutter_developer/SKILL.md
2. define_subagent with:
   - name: "flutter_developer"
   - description: "Flutter developer implementing {feature} for {story}"
   - system_prompt: [full content of flutter_developer/SKILL.md]
   - enable_write_tools: true
   - enable_mcp_tools: true  (for dart analysis)
   - enable_subagent_tools: false
3. invoke_subagent with:
   - Workspace: inherit  (shares the TL's branched workspace)
   - Prompt: [Chunk 1 task description from template above]
```

### Sequential Task Assignment

After each chunk completes:
1. Review the code (see code_review_checklist.md)
2. If approved → send Chunk N+1 task via send_message to the developer's conversation ID
3. If rejected → send specific correction instructions via send_message, wait for fix, re-review
4. Repeat until all chunks are done

**Pattern:**
```
invoke_subagent (Chunk 1)
  → developer completes and sends message back
  → TL reviews code
  → TL approved: send_message(developer_id, "Chunk 1 approved. Now do Chunk 2: [task description]")
  → developer completes Chunk 2 and sends message back
  → TL reviews code
  → ... continue ...
  → All chunks done → TL sends completion to orchestrator
```

---

## Code Review Process

After each chunk, review before assigning the next one. See `code_review_checklist.md` for the full checklist. Minimum review requirements per chunk:

| Chunk | Key Review Focus |
|-------|-----------------|
| 1 (Models) | No Flutter imports, proper null safety, json serialisation correct, equatable/freezed if needed |
| 2 (Repository) | Interface correctly implemented, all error paths handled, no direct ViewModel imports |
| 3 (ViewModel) | No BuildContext, no import of Flutter widgets, proper state notifications, injected repository is the interface |
| 4–5 (Views) | No business logic, properly consumes ViewModel via Consumer/watch, correct widget decomposition |
| 6 (Navigation) | Clean route definitions, no navigation logic in Widgets (use NavigationService) |
| 7 (Polish) | Const constructors present, accessibility labels on icons/images |

---

## Handling Developer Questions and Blockers

### When the developer asks a question
Always answer specifically. Never say "figure it out" or "use your best judgement" on architectural matters.

**Response format:**
```
Clear answer to the question.

Example implementation:
[concrete code snippet]

Why: [brief reasoning]

Continue with the task. Let me know if you need further clarification.
```

### When the developer reports a blocker

**Classify the blocker:**

| Type | Example | Resolution |
|------|---------|-----------|
| **Ambiguous requirement** | "It's unclear whether the list should paginate" | Re-read requirements.md; if still unclear, send message to orchestrator asking for PM clarification |
| **Missing design spec** | "No spec for the error state of this screen" | Define a sensible default based on design system; document your decision in architecture.md |
| **Technical uncertainty** | "Not sure how to implement offline caching" | Provide the answer yourself (you're the lead) or write the pattern code |
| **Missing dependency** | "Need package X not in pubspec.yaml" | Instruct the developer to add it to pubspec.yaml with the correct version |
| **Build error in existing code** | "Chunk 1 code breaks the build" | Provide the exact fix; if systemic, fix it yourself then re-delegate |

### Escalation to Orchestrator

Escalate (via send_message to orchestrator) only when:
- A requirement is fundamentally unclear and blocking progress
- The feature requires a significant architectural change to the base app that goes beyond the story scope
- You've tried to resolve a blocker twice and failed

When escalating, include:
1. What is blocked and why
2. What you've already tried
3. Specific question or decision needed
4. Estimated impact on timeline

---

## Architecture Planning

Before delegating any code, create `pipeline_output/architecture.md` with:

### Architecture Document Template
```markdown
# Architecture Plan — {Feature Name}

## Overview
{One paragraph describing the approach}

## Directory Structure
lib/features/{feature_name}/
├── models/
│   └── {model_name}.dart
├── repositories/
│   ├── {repo}_interface.dart
│   └── {repo}_impl.dart
├── viewmodels/
│   └── {vm_name}_viewmodel.dart
└── views/
    ├── screens/
    │   └── {screen_name}_screen.dart
    └── widgets/
        └── {widget_name}.dart

## Class Diagram
{mermaid classDiagram}

## Data Flow
{mermaid sequenceDiagram showing user action → view → viewmodel → repository → API → back}

## Key Decisions
- {Decision 1 and rationale}
- {Decision 2 and rationale}

## Chunk Breakdown
| Chunk | Files | Dependencies |
|-------|-------|-------------|
| 1 | models/, repository interface | None |
| 2 | repository implementation | Chunk 1 |
| ... | ... | ... |
```

---

## Progress Tracking

Keep a mental model of what's done. After each chunk completion, update your internal state:

```
✅ Chunk 1: Models + Repository Interface — reviewed and approved
✅ Chunk 2: Repository Implementation — reviewed and approved  
🔄 Chunk 3: ViewModel — developer working on it
⏳ Chunk 4: View Base — not started
⏳ Chunk 5: View Components — not started
⏳ Chunk 6: Navigation — not started
⏳ Chunk 7: Polish — not started
```

When all chunks are ✅, compile the completion report for the orchestrator:

```
✅ Development complete for {feature name}.

Branch: feature/{story-id}-{short-description}

Files created:
- lib/features/{feature}/models/{model}.dart
- lib/features/{feature}/repositories/...
- lib/features/{feature}/viewmodels/...
- lib/features/{feature}/views/...

Chunks completed: 7/7
Code reviewed: ✅ All chunks approved
Known issues: {none / list any minor items}

Ready for Stage 4 (QA).
```

---

## When to Do Work Yourself vs Delegate

| Task | Do Yourself | Delegate |
|------|-------------|---------|
| Architecture planning | ✅ | |
| Class diagram | ✅ | |
| Writing task descriptions | ✅ | |
| Reviewing code | ✅ | |
| Answering architectural questions | ✅ | |
| Implementing a pattern example (3–5 lines) | ✅ | |
| Writing boilerplate models | | ✅ |
| Writing repository implementation | | ✅ |
| Writing ViewModel logic | | ✅ |
| Writing View widgets | | ✅ |
| Writing all tests | | Delegate to QA |
