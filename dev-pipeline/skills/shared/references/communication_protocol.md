# Inter-Agent Communication Protocol

> All agents in the dev-pipeline MUST follow this protocol for status updates, artifact handoff, completion reporting, and failure escalation.

---

## 1. Message Format — Status Updates

Agents should send structured status updates to their parent (orchestrator or team lead) at key milestones. Use the `send_message` tool with the following format:

### Progress Update
```
[STATUS] <agent-role> — <phase>

Progress: <brief description of what was just completed>
Next: <what the agent will do next>
Artifacts: <list of files created/modified, if any>
```

**Example:**
```
[STATUS] Flutter Developer — Implementation

Progress: Created Order model with JSON serialization and OrderRepository interface.
Next: Implementing OrderHistoryViewModel with state management.
Artifacts:
  - lib/features/order_history/models/order.dart
  - lib/features/order_history/repositories/order_repository.dart
```

---

## 2. Completion Reporting

When an agent finishes its assigned work, it MUST send a completion message with the following structure:

### Completion Message
```
[COMPLETE] <agent-role>

Summary: <1-2 sentence summary of what was delivered>
Artifacts:
  - <absolute-path-to-artifact-1>
  - <absolute-path-to-artifact-2>
  - ...
Exit Criteria Met:
  - <criterion 1>: ✅
  - <criterion 2>: ✅
Branch: <branch-name, if applicable>
Notes: <any additional context, warnings, or decisions made>
```

**Example:**
```
[COMPLETE] Project Manager

Summary: Requirements document created with 3 user stories, acceptance criteria, edge cases, and technical constraints for the order history feature.
Artifacts:
  - C:\Users\usama\Desktop\project\pipeline_output\requirements.md
Exit Criteria Met:
  - Requirements document exists: ✅
  - Contains user stories: ✅
  - Contains acceptance criteria: ✅
Notes: Added edge case for offline mode since the app may be used in low-connectivity environments.
```

---

## 3. Failure Reporting

When an agent encounters an error it cannot resolve, it MUST report the failure:

### Failure Message
```
[FAILURE] <agent-role> — <phase>

Error: <concise description of what went wrong>
Attempted Fix: <what the agent tried to do to resolve it>
Impact: <what this blocks or affects>
Artifacts So Far:
  - <any partial artifacts created>
Needs: <what is needed to unblock — clarification, different input, manual intervention>
```

**Example:**
```
[FAILURE] Flutter Developer — Implementation

Error: flutter analyze reports 3 errors related to missing dependency 'provider' in pubspec.yaml.
Attempted Fix: Added provider ^6.1.0 to pubspec.yaml and ran flutter pub get, but the dependency resolution failed due to a version conflict with an existing dependency.
Impact: Cannot proceed with ViewModel implementation until dependency conflict is resolved.
Artifacts So Far:
  - lib/features/order_history/models/order.dart (complete)
  - lib/features/order_history/repositories/order_repository.dart (complete)
Needs: Manual resolution of the provider version conflict in pubspec.yaml, or approval to downgrade to provider ^6.0.0.
```

---

## 4. Blocker Reporting

For issues that don't constitute a complete failure but block progress:

### Blocker Message
```
[BLOCKED] <agent-role> — <phase>

Blocker: <description of what is blocking progress>
Waiting For: <what the agent needs to continue>
Can Continue With: <any parallel work the agent can do in the meantime, or "Nothing">
Timeout: <how long the agent will wait before escalating>
```

**Example:**
```
[BLOCKED] Designer — Mockup Generation

Blocker: Requirements document does not specify whether the order history should support dark mode.
Waiting For: Clarification from PM or orchestrator on dark mode requirement.
Can Continue With: Creating the light-mode mockups and component hierarchy.
Timeout: Will escalate to orchestrator if no response in 120 seconds.
```

---

## 5. Clarification Requests

When an agent needs additional information to proceed:

### To the Team Lead (from a developer)
```
[QUESTION] <agent-role> → <recipient-role>

Context: <what the agent is working on>
Question: <specific question>
Options: <proposed solutions, if any>
  A) <option A>
  B) <option B>
Default: <which option the agent will use if no response within timeout>
Timeout: 60 seconds
```

### To the Orchestrator (escalation)
```
[ESCALATE] <agent-role> → Orchestrator

Original Question: <the question that couldn't be resolved at the team level>
Asked: <who was originally asked>
Reason for Escalation: <why it couldn't be resolved at the team level>
Impact: <what is blocked>
```

---

## 6. Artifact Handoff Protocol

When passing artifacts between pipeline stages:

### Rules
1. **Always use absolute file paths** when referencing artifacts in messages.
2. **Verify artifacts exist** before referencing them — use `view_file` to confirm.
3. **All pipeline artifacts** go in the `pipeline_output/` directory at the workspace root.
4. **Name artifacts consistently:**

| Stage | Artifact | Path |
|---|---|---|
| Requirements | Requirements document | `pipeline_output/requirements.md` |
| Design | Design specification | `pipeline_output/design_spec.md` |
| Design | Mockup images | `pipeline_output/mockups/<screen_name>.png` |
| Development | Source code | `lib/features/<feature>/` |
| Development | Tests | `test/features/<feature>/` |
| QA | QA report | `pipeline_output/qa_report.md` |
| Completion | Final report | `pipeline_output/completion_report.md` |

5. **The orchestrator is responsible** for passing artifact paths between stages via the subagent's prompt.

### Handoff Message Format
```
[HANDOFF] <from-role> → <to-role>

Artifacts for your stage:
  - <artifact-1-path>: <brief description of contents>
  - <artifact-2-path>: <brief description of contents>

Key context: <anything the receiving agent should know>
```

---

## 7. Timing Expectations

| Communication Type | Expected Response Time |
|---|---|
| Status update | Sent at each significant milestone (every 30–60 seconds of work) |
| Completion report | Immediately upon finishing all work |
| Failure report | Immediately upon encountering an unrecoverable error |
| Clarification request | Within 60 seconds (default timeout) |
| Escalation | After clarification timeout expires |

---

## 8. Message Priority

| Priority | Prefix | When to Use |
|---|---|---|
| Critical | `[FAILURE]` | Unrecoverable errors that halt the pipeline |
| High | `[BLOCKED]`, `[ESCALATE]` | Issues that prevent progress |
| Normal | `[COMPLETE]`, `[HANDOFF]` | Stage completion and artifact transfer |
| Low | `[STATUS]`, `[QUESTION]` | Progress updates and clarifications |

---

## 9. Global Token Minimization Hook (Mandatory Protocol)

All agents MUST enforce the following context-saving rules when composing messages or status updates to minimize token usage:

### 9.1 Rule-Based Truncation (Logs & Dumps)
- **Do NOT paste raw logs or code dumps** (such as `flutter test` traces, terminal errors, or entire source files) directly in your chat messages if they exceed **15 lines** or **500 characters**.
- **Scratch Archiving**: Write the log or dump output to a scratch file under `pipeline_output/scratch/` (e.g., `pipeline_output/scratch/test_fail_log.txt`).
- **Markdown Referencing**: Insert a clean hyperlink in your message referencing the scratch file path:
  `[Test failure details logged here](file:///c:/path/to/pipeline_output/scratch/test_fail_log.txt)`

### 9.2 Dialogue Context Compression
- When summarizing previous discussion turns, do not restate prior messages verbatim. 
- Collapse historical threads into a single consolidated, high-level summary table or bullet list:
  | Past Event | Summary | Status |
  |---|---|---|
  | Requirements | Login & Auth Flow spec created | Approved |
  | UI Design | Login mockups & style spec completed | Passed QA Checkpoint |
- Use referenced file links for all deep contexts.

