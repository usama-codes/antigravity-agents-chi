# Git Conventions — PR-Based Workflow

> All dev-pipeline agents MUST follow these conventions when creating branches, commits, and preparing code for review.

---

## 1. Branch Naming

### Format
```
feature/<story-id>-<short-description>
```

### Rules
- `<story-id>`: The Jira/Linear ticket ID or a sanitized slug derived from the story title. If no ID is provided, generate one from the first few words of the story (e.g., `password-reset`, `order-history`).
- `<short-description>`: 2–4 words, lowercase, hyphen-separated. Describes the feature being built.
- Branch names are **all lowercase** with **hyphens** as separators.
- Maximum length: **50 characters**.

### Examples
```
feature/PROJ-123-password-reset
feature/PROJ-456-order-history-screen
feature/password-reset-flow
feature/order-history-view
```

### Branch Lifecycle
1. Create the branch from the current `main` or `develop` branch.
2. All implementation work happens on the feature branch.
3. The branch is reported to the orchestrator upon completion.
4. A human reviewer merges via PR.

---

## 2. Commit Message Format

### Convention: [Conventional Commits](https://www.conventionalcommits.org/)

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types

| Type | When to Use |
|---|---|
| `feat` | A new feature or user-facing functionality |
| `fix` | A bug fix |
| `refactor` | Code restructuring with no behavior change |
| `test` | Adding or updating tests |
| `docs` | Documentation changes |
| `style` | Formatting, whitespace, linting (no logic change) |
| `chore` | Build config, dependency updates, tooling |

### Scope
- Use the **feature name** or **module name** as scope.
- Examples: `order-history`, `auth`, `password-reset`, `core`.

### Description
- **Imperative mood**: "add", "fix", "update" — not "added", "fixes", "updated".
- **Lowercase** first letter.
- **No period** at the end.
- Maximum **72 characters** for the first line.

### Examples
```
feat(order-history): add order list screen with empty state
feat(order-history): implement order detail view
feat(password-reset): add email validation logic
test(order-history): add ViewModel unit tests for load and error states
refactor(core): extract API client to shared module
fix(auth): handle expired token refresh race condition
chore(deps): update provider to v6.1.0
docs(readme): add setup instructions for development
```

### Commit Body (Optional)
Use the body for:
- Explaining **why** a change was made (not what — the diff shows that).
- Listing **breaking changes**.
- Referencing **story IDs**.

```
feat(order-history): add order list screen with empty state

Implements the main order history screen with three states:
loading, empty, and populated. Uses ChangeNotifier pattern
for state management.

Refs: PROJ-456
```

### Commit Frequency
- **Commit after each logical unit of work** — not after every file save.
- Typical commits per feature: 3–8.
- Good granularity: one commit per MVVM layer or component.

Recommended commit sequence for a typical feature:
```
1. feat(feature): add data models and serialization
2. feat(feature): implement repository layer
3. feat(feature): add ViewModel with state management
4. feat(feature): create UI screens and widgets
5. test(feature): add ViewModel and model unit tests
6. style(feature): run flutter format and fix analyzer warnings
```

---

## 3. PR Description Template

When the pipeline completes, the orchestrator should prepare a PR description following this template:

```markdown
## Summary
<!-- One-paragraph description of the feature -->

## Story
<!-- Original user story or link to ticket -->

## Changes
<!-- List of key changes made -->
- Added `OrderHistoryScreen` with loading, empty, and populated states
- Implemented `OrderHistoryViewModel` with `loadOrders()` method
- Created `Order` model with JSON serialization
- Added `OrderRepository` interface and implementation

## Architecture
<!-- MVVM layer breakdown -->
- **Model:** `Order`, `OrderStatus`
- **ViewModel:** `OrderHistoryViewModel`
- **View:** `OrderHistoryScreen`, `OrderListTile`
- **Repository:** `OrderRepository` → `OrderRepositoryImpl`

## Testing
<!-- Test summary -->
- [ ] ViewModel unit tests (X tests, all passing)
- [ ] Model serialization tests
- [ ] Widget tests for key screens

## Screenshots / Mockups
<!-- Design mockups or screenshots if available -->

## Checklist
- [ ] `flutter analyze` passes with zero issues
- [ ] `flutter test` passes with zero failures
- [ ] Code follows MVVM architecture standards
- [ ] All files use snake_case naming
- [ ] No hard-coded strings in views
- [ ] Dependencies injected via constructors
```

---

## 4. Review Checklist

Before a feature branch is considered complete, verify:

### Code Quality
- [ ] `flutter analyze` reports **zero issues**
- [ ] `flutter test` — **all tests pass**
- [ ] No `print()` or `debugPrint()` statements in production code
- [ ] No commented-out code
- [ ] No `// TODO` without a story/issue reference

### Architecture Compliance
- [ ] Models contain no Flutter imports
- [ ] ViewModels contain no widget/UI imports
- [ ] Views delegate all logic to ViewModels
- [ ] Dependencies injected via constructors
- [ ] Repository interfaces defined as abstract classes

### Git Hygiene
- [ ] Branch name follows `feature/<id>-<description>` format
- [ ] All commits follow conventional commit format
- [ ] No merge commits (rebase preferred)
- [ ] No large binary files committed
- [ ] `.gitignore` is up to date

---

## 5. How Agents Should Create Branches and Commit

### Creating a Branch
```bash
# From the workspace root
git checkout -b feature/<story-id>-<short-description>
```

### Staging and Committing
```bash
# Stage specific files (preferred over git add .)
git add lib/features/order_history/
git commit -m "feat(order-history): add data models and repository"

# Stage tests
git add test/features/order_history/
git commit -m "test(order-history): add ViewModel unit tests"
```

### Final Validation Before Reporting
```bash
# Run analysis
flutter analyze

# Run tests
flutter test

# Verify branch name
git branch --show-current
```

### Reporting to Orchestrator
After all commits are made and validated, the agent reports to the orchestrator:
- Branch name
- Number of commits
- Summary of changes
- Test results (`flutter test` output)
- `flutter analyze` output
