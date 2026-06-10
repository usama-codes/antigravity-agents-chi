---
name: shared-dev-standards
description: >-
  Shared coding standards, Git conventions, and communication protocols for all dev-pipeline agents. Not a standalone skill. Referenced by other skills in the dev-pipeline plugin.
---

# Shared Development Standards

> **⚠️ This is a shared library skill — it is NOT invoked directly.**

This skill provides shared reference documents used by all agents in the dev-pipeline plugin. Individual agent skills reference these documents to ensure consistency across the entire pipeline.

## Contents

The `references/` directory contains the following shared standards:

| Document | Purpose |
|---|---|
| `coding_standards.md` | Flutter/Dart MVVM architecture rules, file naming, directory structure, and code quality guidelines |
| `git_conventions.md` | Branch naming, conventional commit messages, PR templates, and review checklists |
| `communication_protocol.md` | Inter-agent message formats, status updates, completion reporting, failure escalation |

## How Other Skills Use This

Agent skills (e.g., `pipeline_orchestrator`, `mobile_team_lead`, `flutter_developer`) should instruct their agents to read relevant reference documents from this directory before beginning work. For example:

- The **Mobile Team Lead** reads `coding_standards.md` to enforce MVVM compliance during code review.
- The **Flutter Developer** reads `coding_standards.md` and `git_conventions.md` before writing any code.
- **All agents** follow `communication_protocol.md` for status updates and artifact handoff.

## Path Reference

From any skill in this plugin, the shared references are located at:

```
skills/shared/references/<document>.md
```

Resolve the absolute path relative to the plugin root directory.
