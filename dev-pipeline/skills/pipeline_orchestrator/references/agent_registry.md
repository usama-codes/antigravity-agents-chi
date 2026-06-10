# Agent Registry — Role Configuration Lookup

> This document is the authoritative lookup table for the Pipeline Orchestrator. Use it to determine the correct tool grants, workspace mode, skill path, and artifact expectations for each agent role.

---

## Registry Table

| Role | Skill Path (relative to plugin) | `enable_write_tools` | `enable_mcp_tools` | `enable_subagent_tools` | Workspace Mode | Input Artifacts | Output Artifacts |
|---|---|---|---|---|---|---|---|
| **Project Manager** | `skills/project_manager/SKILL.md` | ✅ true | ❌ false | ❌ false | `inherit` | Raw user story (in prompt) | `pipeline_output/requirements.md` |
| **Designer** | `skills/designer/SKILL.md` | ✅ true | ❌ false | ❌ false | `inherit` | `pipeline_output/requirements.md` | `pipeline_output/design_spec.md`, `pipeline_output/mockups/*.png` |
| **Mobile Team Lead** | `skills/mobile_team_lead/SKILL.md` | ✅ true | ✅ true | ✅ true | `branch` | `pipeline_output/requirements.md`, `pipeline_output/design_spec.md` | Feature branch with code in `lib/features/`, tests in `test/features/` |
| **Flutter Developer** | `skills/flutter_developer/SKILL.md` | ✅ true | ✅ true | ❌ false | `inherit` (from TL's branch) | Implementation plan from TL | Feature code, unit tests |
| **QA Engineer** | `skills/qa_engineer/SKILL.md` | ✅ true | ❌ false | ❌ false | `share` (TL's branch) | `pipeline_output/requirements.md` (acceptance criteria), feature branch code | `pipeline_output/qa_report.md` |

---

## Detailed Role Configurations

### Project Manager (PM)

```yaml
role: Project Manager
skill_path: skills/project_manager/SKILL.md
define_subagent:
  enable_write_tools: true
  enable_mcp_tools: false
  enable_subagent_tools: false
invoke_subagent:
  workspace: inherit
input:
  - source: user prompt
    content: raw user story text
output:
  - path: pipeline_output/requirements.md
    description: Structured requirements with user stories, acceptance criteria, edge cases
validation:
  - file_exists: pipeline_output/requirements.md
  - contains: "## User Stories" or equivalent heading
  - contains: "## Acceptance Criteria" or equivalent heading
  - contains: "## Edge Cases" or equivalent heading
timeout_seconds: 300
max_retries: 1
```

### Designer

```yaml
role: Designer
skill_path: skills/designer/SKILL.md
define_subagent:
  enable_write_tools: true
  enable_mcp_tools: false
  enable_subagent_tools: false
invoke_subagent:
  workspace: inherit
input:
  - path: pipeline_output/requirements.md
    description: Requirements document from PM stage
output:
  - path: pipeline_output/design_spec.md
    description: Design specification with component hierarchy, colors, typography
  - path: pipeline_output/mockups/
    description: Directory containing UI mockup images (.png)
validation:
  - file_exists: pipeline_output/design_spec.md
  - contains: component hierarchy or widget tree section
  - directory_not_empty: pipeline_output/mockups/ (soft requirement)
timeout_seconds: 300
max_retries: 1
```

### Mobile Team Lead

```yaml
role: Mobile Team Lead
skill_path: skills/mobile_team_lead/SKILL.md
define_subagent:
  enable_write_tools: true
  enable_mcp_tools: true
  enable_subagent_tools: true
invoke_subagent:
  workspace: branch
input:
  - path: pipeline_output/requirements.md
    description: Requirements document
  - path: pipeline_output/design_spec.md
    description: Design specification and mockups
output:
  - type: message
    content: "[COMPLETE] with branch name, analyze results, architecture summary"
  - path: lib/features/<feature>/
    description: Implemented Flutter code following MVVM
  - path: test/features/<feature>/
    description: Unit and widget tests
validation:
  - completion_message: contains branch name
  - completion_message: reports flutter analyze passes
  - completion_message: confirms MVVM architecture
timeout_seconds: 600
max_retries: 1
notes: |
  The TL has subagent capabilities and will internally spawn Flutter Developer
  agents. The orchestrator does NOT spawn Flutter Developers directly.
  The TL's branched workspace is used by QA in the next stage via 'share' mode.
```

### Flutter Developer

```yaml
role: Flutter Developer
skill_path: skills/flutter_developer/SKILL.md
define_subagent:
  enable_write_tools: true
  enable_mcp_tools: true
  enable_subagent_tools: false
invoke_subagent:
  workspace: inherit  # Inherits the TL's branched workspace
input:
  - source: TL message
    content: Implementation plan with specific files to create, architecture guidance
output:
  - type: code files
    path: lib/features/<feature>/
  - type: test files
    path: test/features/<feature>/
  - type: message
    content: "[COMPLETE] with list of files created and any issues"
validation:
  - performed by TL, not orchestrator
timeout_seconds: 300
max_retries: 1
notes: |
  Flutter Developer is spawned by the Mobile Team Lead, NOT by the orchestrator.
  The orchestrator should never directly interact with Flutter Developer agents.
```

### QA Engineer

```yaml
role: QA Engineer
skill_path: skills/qa_engineer/SKILL.md
define_subagent:
  enable_write_tools: true
  enable_mcp_tools: false
  enable_subagent_tools: false
activities:
  - name: Design-Exit QA Checkpoint
    invoke_subagent:
      workspace: inherit
    input:
      - path: pipeline_output/requirements.md
      - path: pipeline_output/design_spec.md
    output:
      - path: pipeline_output/design_review_report.md
        description: Review checklist evaluating requirements compliance, spec completeness, and feasibility
    validation:
      - file_exists: pipeline_output/design_review_report.md
      - contains: "APPROVE" or "REJECT"
  - name: Build QA Verification
    invoke_subagent:
      workspace: share  # Shares the TL's branched workspace
    input:
      - path: pipeline_output/requirements.md (acceptance criteria)
      - context: Feature branch code (available in shared workspace)
    output:
      - path: pipeline_output/qa_report.md
        description: Test results, coverage notes, pass/fail per acceptance criterion
    validation:
      - file_exists: pipeline_output/qa_report.md
      - contains: acceptance criteria pass/fail status
      - contains: flutter test output
      - all_tests_pass: true
timeout_seconds: 300
max_retries: 1
notes: |
  QA plays a dual role: first executing a lightweight Design-Exit Checkpoint (using inherit mode to review specifications before development), and later performing Build QA Verification (using share mode to test the implementation on the TL's branch).
  For Build QA, use the conversation ID of the TL's subagent to set up the shared workspace.
```

---

## How the Orchestrator Uses This Registry

1. **Before spawning a stage**, look up the role in this table.
2. **Read the skill SKILL.md** at the specified `skill_path` to get the agent's system prompt.
3. **Call `define_subagent`** with:
   - `name`: a descriptive name (e.g., `"pipeline-pm"`, `"pipeline-designer"`)
   - `system_prompt`: contents of the role's SKILL.md
   - `enable_write_tools`: from the registry
   - `enable_mcp_tools`: from the registry
   - `enable_subagent_tools`: from the registry
4. **Call `invoke_subagent`** with:
   - `Workspace`: from the registry (inherit / branch / share)
   - `Prompt`: include the input artifacts and any context
5. **Set a watchdog timer** using the `schedule` tool with `DurationSeconds` from the registry's `timeout_seconds`.
6. **Validate outputs** using the registry's `validation` criteria after the agent completes.

---

## Important Notes

- **Skill paths are relative to the plugin root** (`dev-pipeline/`). Resolve them to absolute paths using the plugin directory location.
- **The Flutter Developer role** is included for documentation completeness but is **never spawned by the orchestrator** — only by the Mobile Team Lead.
- **Workspace modes matter critically:**
  - `inherit` = agent works in the same workspace as its parent
  - `branch` = agent gets an isolated copy (for safe development)
  - `share` = agent shares the parent's workspace (for QA to access dev code)
