# Acceptance Criteria Validation — Comprehensive Reference

This document describes how to systematically validate acceptance criteria (ACs) from a requirements document, map them to test cases, run tests, and produce a structured QA report with a traceability matrix.

---

## 1. Parsing Acceptance Criteria

### Where to Find ACs

ACs are located in `pipeline_output/requirements.md`. They may appear in several formats:

#### Format 1: Numbered AC list
```markdown
## Acceptance Criteria
- AC-1: User can view a list of all active tasks
- AC-2: User can create a new task with title and description
- AC-3: User sees a loading indicator while tasks are being fetched
```

#### Format 2: Given/When/Then (Gherkin-style)
```markdown
## Acceptance Criteria
- **AC-1**: Given I am on the tasks screen, When the screen loads, Then I see a list of all active tasks
- **AC-2**: Given I am on the tasks screen, When I tap the add button, Then I see a form to create a new task
- **AC-3**: Given I submit the new task form with valid data, When the API responds successfully, Then the new task appears in the list
```

#### Format 3: Inline in user story
```markdown
As a user, I want to manage my tasks so that I can track my work.

The user should be able to:
1. View all active tasks in a scrollable list
2. Create a new task with title (required) and description (optional)
3. Delete a task by swiping left
4. See a loading spinner while data is fetching
5. See an error message if the network call fails
```

#### Format 4: Mixed/Informal
```markdown
Requirements:
- Task list screen showing all tasks
- Add task functionality
- Delete task (swipe to delete)
- Loading states
- Error handling for network failures
- Empty state when no tasks exist
```

### Extraction Rules

1. **Assign IDs**: If ACs don't have IDs, assign them sequentially: `AC-1`, `AC-2`, etc.
2. **Normalize format**: Convert all ACs to a consistent format:
   ```
   AC-{N}: {Concise description of the expected behavior}
   ```
3. **Split compound ACs**: If one AC contains multiple behaviors, split it:
   ```
   ❌ "User can create, edit, and delete tasks"
   ✅ AC-1: "User can create a task"
       AC-2: "User can edit a task"
       AC-3: "User can delete a task"
   ```
4. **Clarify implicit ACs**: Some behaviors are implied but not stated. Add them with an `[IMPLICIT]` tag:
   ```
   AC-7 [IMPLICIT]: Loading indicator is shown while tasks are being fetched
   AC-8 [IMPLICIT]: Error message is shown if API call fails
   ```

---

## 2. Classifying Acceptance Criteria

Each AC should be classified by **type** to determine the appropriate test level:

| AC Type | Description | Primary Test Level | Secondary Test Level |
|---------|-------------|-------------------|---------------------|
| **Functional** | Core feature logic works as described | Unit Test (ViewModel) | Widget Test |
| **UI/Visual** | Screen renders correctly, layout is correct | Widget Test | Golden Test |
| **Navigation** | User flow / routing between screens works | Integration Test | Widget Test |
| **Error Handling** | Errors are caught and displayed gracefully | Unit Test (error mocks) | Widget Test (error state) |
| **Edge Case** | Boundary conditions are handled correctly | Unit Test | — |
| **Data** | Data serialization, persistence, or transformation | Unit Test (Model/Repo) | — |
| **Performance** | Timing or resource constraints are met | Integration Test | — |
| **Accessibility** | Semantic labels, contrast, screen reader support | Widget Test | — |

### Classification Examples

| AC | Type | Rationale |
|----|------|-----------|
| "User can view a list of tasks" | Functional | Core feature — data fetching and display |
| "Tasks are shown in a scrollable list" | UI/Visual | Specific UI behavior |
| "Tapping a task navigates to detail screen" | Navigation | Screen-to-screen flow |
| "Error message shown on network failure" | Error Handling | Graceful degradation |
| "Empty state shown when no tasks exist" | Edge Case | Boundary condition (empty data) |
| "Task title is required, description is optional" | Data | Input validation rules |
| "List loads within 2 seconds" | Performance | Timing constraint |

---

## 3. Mapping ACs to Test Cases

### Mapping Rules

1. **Every AC must have at least one test.** No exceptions.
2. **Functional ACs need at least 2 tests**: happy path + error path.
3. **One AC may map to many tests** (different inputs, states, edge cases).
4. **One test should not try to validate multiple ACs.** Keep tests focused.

### Mapping Template

For each AC, create a mapping entry:

```markdown
### AC-1: User can view a list of all active tasks

**Type**: Functional
**Test Level**: Unit + Widget

**Test Cases:**
| TC ID | Test Name | Level | File |
|-------|-----------|-------|------|
| TC-1.1 | should fetch tasks from repository on init | Unit | `task_viewmodel_test.dart` |
| TC-1.2 | should populate tasks list on successful fetch | Unit | `task_viewmodel_test.dart` |
| TC-1.3 | should set loading state during fetch | Unit | `task_viewmodel_test.dart` |
| TC-1.4 | should display task items in ListView | Widget | `task_list_screen_test.dart` |
| TC-1.5 | should show loading indicator while fetching | Widget | `task_list_screen_test.dart` |
| TC-1.6 | should handle fetch failure with error state | Unit | `task_viewmodel_test.dart` |
| TC-1.7 | should display error message on fetch failure | Widget | `task_list_screen_test.dart` |
```

### Coverage Matrix Visualization

Use this matrix to ensure complete coverage:

```
                    Unit   Widget   Integration
AC-1 (view list)    ✅      ✅        —
AC-2 (create)       ✅      ✅        ✅
AC-3 (delete)       ✅      ✅        —
AC-4 (loading)      ✅      ✅        —
AC-5 (error)        ✅      ✅        —
AC-6 (empty state)  ✅      ✅        —
AC-7 (navigation)   —       —         ✅
```

---

## 4. Writing Tests for Each AC Type

### 4.1 Functional AC → Unit + Widget Tests

**AC: "User can create a new task with title and description"**

```dart
// Unit test — ViewModel
group('createTask', () {
  test('should call repository.createTask with correct parameters', () async {
    // Arrange
    when(mockRepo.createTask(any))
        .thenAnswer((_) async => Task(id: '1', title: 'New', description: 'Desc'));

    // Act
    await viewModel.createTask(title: 'New', description: 'Desc');

    // Assert
    verify(mockRepo.createTask(argThat(
      predicate<CreateTaskRequest>((req) =>
          req.title == 'New' && req.description == 'Desc'),
    ))).called(1);
  });

  test('should add new task to tasks list on success', () async {
    // Arrange
    final newTask = Task(id: '1', title: 'New', description: 'Desc');
    when(mockRepo.createTask(any)).thenAnswer((_) async => newTask);

    // Act
    await viewModel.createTask(title: 'New', description: 'Desc');

    // Assert
    expect(viewModel.tasks, contains(newTask));
  });

  test('should set error when title is empty', () async {
    // Act
    await viewModel.createTask(title: '', description: 'Desc');

    // Assert
    expect(viewModel.error, isNotNull);
    expect(viewModel.error, contains('Title is required'));
    verifyNever(mockRepo.createTask(any)); // Should not call API
  });

  test('should handle API failure gracefully', () async {
    // Arrange
    when(mockRepo.createTask(any)).thenThrow(Exception('Server error'));

    // Act
    await viewModel.createTask(title: 'New', description: 'Desc');

    // Assert
    expect(viewModel.error, isNotNull);
    expect(viewModel.error, contains('Server error'));
  });
});

// Widget test — Form interaction
testWidgets('should submit form with valid data', (tester) async {
  // Arrange
  when(mockViewModel.createTask(
    title: anyNamed('title'),
    description: anyNamed('description'),
  )).thenAnswer((_) async {});

  await tester.pumpWidget(createTestWidget());
  await tester.pumpAndSettle();

  // Act
  await tester.enterText(find.byKey(const Key('title_field')), 'My Task');
  await tester.enterText(find.byKey(const Key('description_field')), 'Details');
  await tester.tap(find.byKey(const Key('submit_button')));
  await tester.pumpAndSettle();

  // Assert
  verify(mockViewModel.createTask(
    title: 'My Task',
    description: 'Details',
  )).called(1);
});

testWidgets('should show validation error when title is empty', (tester) async {
  await tester.pumpWidget(createTestWidget());
  await tester.pumpAndSettle();

  // Act — submit without entering title
  await tester.tap(find.byKey(const Key('submit_button')));
  await tester.pumpAndSettle();

  // Assert
  expect(find.text('Title is required'), findsOneWidget);
});
```

### 4.2 Error Handling AC → Unit + Widget Tests

**AC: "User sees an error message when network call fails"**

```dart
// Unit test — error state
test('should set error message when network fails', () async {
  when(mockRepo.getTasks()).thenThrow(
    const SocketException('No internet connection'),
  );

  await viewModel.fetchTasks();

  expect(viewModel.error, isNotNull);
  expect(viewModel.isLoading, isFalse);
  expect(viewModel.tasks, isEmpty);
});

test('should set error message when server returns 500', () async {
  when(mockRepo.getTasks()).thenThrow(
    ApiException(statusCode: 500, message: 'Internal Server Error'),
  );

  await viewModel.fetchTasks();

  expect(viewModel.error, contains('Server Error'));
});

test('should set error message when request times out', () async {
  when(mockRepo.getTasks()).thenThrow(
    TimeoutException('Request timed out'),
  );

  await viewModel.fetchTasks();

  expect(viewModel.error, isNotNull);
});

// Widget test — error UI
testWidgets('should display error message and retry button', (tester) async {
  when(mockViewModel.isLoading).thenReturn(false);
  when(mockViewModel.tasks).thenReturn([]);
  when(mockViewModel.error).thenReturn('Network error. Please try again.');

  await tester.pumpWidget(createTestWidget(viewModel: mockViewModel));
  await tester.pumpAndSettle();

  expect(find.text('Network error. Please try again.'), findsOneWidget);
  expect(find.byKey(const Key('retry_button')), findsOneWidget);
});

testWidgets('should call fetchTasks when retry is tapped', (tester) async {
  when(mockViewModel.isLoading).thenReturn(false);
  when(mockViewModel.tasks).thenReturn([]);
  when(mockViewModel.error).thenReturn('Network error');
  when(mockViewModel.fetchTasks()).thenAnswer((_) async {});

  await tester.pumpWidget(createTestWidget(viewModel: mockViewModel));
  await tester.pumpAndSettle();

  await tester.tap(find.byKey(const Key('retry_button')));
  await tester.pumpAndSettle();

  verify(mockViewModel.fetchTasks()).called(1);
});
```

### 4.3 Edge Case AC → Unit Tests

**AC: "Empty state shown when no tasks exist"**

```dart
// Unit test — empty data
test('should have empty tasks list when API returns empty array', () async {
  when(mockRepo.getTasks()).thenAnswer((_) async => []);

  await viewModel.fetchTasks();

  expect(viewModel.tasks, isEmpty);
  expect(viewModel.isLoading, isFalse);
  expect(viewModel.error, isNull); // empty is not an error
});

// Widget test — empty state UI
testWidgets('should show empty state illustration when no tasks', (tester) async {
  when(mockViewModel.isLoading).thenReturn(false);
  when(mockViewModel.tasks).thenReturn([]);
  when(mockViewModel.error).thenReturn(null);

  await tester.pumpWidget(createTestWidget(viewModel: mockViewModel));
  await tester.pumpAndSettle();

  expect(find.text('No tasks yet'), findsOneWidget);
  expect(find.byKey(const Key('empty_state_image')), findsOneWidget);
  expect(find.byType(ListView), findsNothing); // No list when empty
});
```

### 4.4 Navigation AC → Integration Test

**AC: "Tapping a task navigates to the task detail screen"**

```dart
// Integration test
testWidgets('should navigate from task list to task detail', (tester) async {
  app.main();
  await tester.pumpAndSettle(const Duration(seconds: 5));

  // Verify we're on the list screen
  expect(find.text('My Tasks'), findsOneWidget);

  // Tap first task
  await tester.tap(find.byType(ListTile).first);
  await tester.pumpAndSettle();

  // Verify we navigated to detail screen
  expect(find.text('Task Details'), findsOneWidget);

  // Verify back button works
  await tester.tap(find.byIcon(Icons.arrow_back));
  await tester.pumpAndSettle();
  expect(find.text('My Tasks'), findsOneWidget);
});
```

---

## 5. Traceability Matrix

The traceability matrix is the **core deliverable** linking every AC to its tests and results.

### Full Traceability Matrix Template

```markdown
## Acceptance Criteria Traceability Matrix

| AC ID | Acceptance Criterion | Type | Test File(s) | Test Name(s) | Level | Result | Notes |
|-------|---------------------|------|-------------|-------------|-------|--------|-------|
| AC-1 | User can view list of tasks | Functional | `task_vm_test.dart`, `task_list_screen_test.dart` | `should populate tasks on success`, `should display task items` | Unit, Widget | ✅ PASS | |
| AC-2 | User can create a new task | Functional | `task_vm_test.dart`, `create_task_screen_test.dart` | `should call createTask`, `should submit form` | Unit, Widget | ✅ PASS | |
| AC-3 | User can delete a task | Functional | `task_vm_test.dart`, `task_list_screen_test.dart` | `should remove task on delete`, `should call delete on swipe` | Unit, Widget | ❌ FAIL | Swipe gesture not implemented |
| AC-4 | Loading indicator during fetch | UI | `task_vm_test.dart`, `task_list_screen_test.dart` | `should set loading true`, `should show CircularProgressIndicator` | Unit, Widget | ✅ PASS | |
| AC-5 | Error message on network failure | Error | `task_vm_test.dart`, `task_list_screen_test.dart` | `should set error on failure`, `should show error text` | Unit, Widget | ✅ PASS | |
| AC-6 | Empty state when no tasks | Edge Case | `task_vm_test.dart`, `task_list_screen_test.dart` | `should have empty list`, `should show empty state` | Unit, Widget | ✅ PASS | |
| AC-7 | Navigate to task detail | Navigation | `task_flow_test.dart` | `should navigate from list to detail` | Integration | ⏭️ SKIP | No device available |
```

### Summary Calculations

From the traceability matrix, derive:

```
Total ACs: 7
- Passing: 5 (AC-1, AC-2, AC-4, AC-5, AC-6)
- Failing: 1 (AC-3 — delete not implemented)
- Skipped: 1 (AC-7 — no device for integration test)

Coverage: 6/7 ACs tested (85.7%)
Pass Rate: 5/6 tested ACs passing (83.3%)
```

---

## 6. QA Report Template

Use this exact template for the final QA report at `pipeline_output/qa/qa_report.md`:

```markdown
# QA Report — {Story/Feature Title}

## Metadata
| Field | Value |
|-------|-------|
| **Date** | {YYYY-MM-DD} |
| **Feature** | {feature name} |
| **Requirements Doc** | `pipeline_output/requirements.md` |
| **Test Plan** | `pipeline_output/qa/test_plan.md` |
| **QA Engineer** | AI Agent |

---

## Executive Summary

| Metric | Value |
|--------|-------|
| **Verdict** | ✅ PASS / ❌ FAIL / ⚠️ CONDITIONAL PASS |
| **Total Acceptance Criteria** | {X} |
| **ACs Fully Validated** | {Y} |
| **ACs Failing** | {Z} |
| **ACs Blocked/Skipped** | {W} |
| **Total Tests Written** | {N} |
| **Tests Passing** | {P} |
| **Tests Failing** | {F} |
| **Regression Issues** | {R} |

---

## Test Results by Level

### Unit Tests
| Metric | Value |
|--------|-------|
| Total | {X} |
| Passed | {Y} |
| Failed | {Z} |
| Skipped | {W} |

**Coverage Breakdown:**
| Component Type | Total in Feature | Tested | Coverage |
|---------------|-----------------|--------|----------|
| ViewModels | {X} | {Y} | {%} |
| Repositories | {X} | {Y} | {%} |
| Models | {X} | {Y} | {%} |
| Utils | {X} | {Y} | {%} |

### Widget Tests
| Metric | Value |
|--------|-------|
| Total | {X} |
| Passed | {Y} |
| Failed | {Z} |
| Skipped | {W} |

**States Tested:**
- [ ] Loading state
- [ ] Success state (with data)
- [ ] Error state
- [ ] Empty state
- [ ] Disabled state (if applicable)

### Integration Tests
| Metric | Value |
|--------|-------|
| Total | {X} |
| Passed | {Y} |
| Failed | {Z} |
| Skipped | {W} |
| Reason for skip (if any) | {reason} |

---

## Acceptance Criteria Traceability Matrix

{Insert full traceability matrix from Section 5}

---

## Issues Found

### 🔴 Blockers
> Issues that prevent the feature from shipping. These MUST be fixed.

#### BLOCKER-1: {Title}
- **AC**: AC-{N}
- **Description**: {Detailed description of the issue}
- **Test**: `{test_file.dart}` → `{test name}`
- **Expected Behavior**: {What should happen}
- **Actual Behavior**: {What actually happens}
- **Error Output**:
  ```
  {paste the test failure output}
  ```
- **Suggested Fix**: {Your recommendation}
- **Severity Justification**: {Why this is a blocker}

---

### 🟠 Major Issues
> Issues that significantly degrade functionality but have potential workarounds.

#### MAJOR-1: {Title}
- **AC**: AC-{N}
- **Description**: {description}
- **Impact**: {how this affects the user}
- **Workaround**: {if any}
- **Suggested Fix**: {recommendation}

---

### 🟡 Minor Issues
> Cosmetic issues, minor UX problems, or edge cases with low probability.

#### MINOR-1: {Title}
- **AC**: AC-{N} (or N/A)
- **Description**: {description}
- **Impact**: Low
- **Suggested Fix**: {recommendation}

---

### ⚪ Observations
> Not bugs, but worth noting — code quality, potential improvements, technical debt.

1. {observation}
2. {observation}

---

## Regression Check

| Existing Test File | Tests | Status | Notes |
|-------------------|-------|--------|-------|
| `test/existing/foo_test.dart` | {N} | ✅ All Pass | |
| `test/existing/bar_test.dart` | {N} | ✅ All Pass | |

**Regression Verdict**: ✅ No regressions detected / ❌ Regressions found (see issues)

---

## Ambiguous or Untestable Acceptance Criteria

| AC ID | Criterion | Issue | Question for PM |
|-------|-----------|-------|-----------------|
| AC-{X} | {text} | Ambiguous: {explain} | {specific question} |
| AC-{Y} | {text} | Untestable: {explain} | {what information is needed} |

---

## Test Files Created

| File Path | # Tests | Test Level | Description |
|-----------|---------|------------|-------------|
| `test/features/.../xxx_test.dart` | {N} | Unit | {what it tests} |
| `test/features/.../yyy_test.dart` | {N} | Widget | {what it tests} |
| `integration_test/zzz_test.dart` | {N} | Integration | {what it tests} |
| `test/helpers/mock_data.dart` | — | Helper | Shared mock data |

---

## Test Execution Log

### Command
```bash
flutter test --reporter expanded
```

### Output Summary
```
{Paste relevant sections of flutter test output}
```

### Timing
| Phase | Duration |
|-------|----------|
| Test setup | {X}s |
| Unit tests | {X}s |
| Widget tests | {X}s |
| Integration tests | {X}s |
| Total | {X}s |

---

## Recommendations

1. **{Category}**: {specific recommendation}
2. **{Category}**: {specific recommendation}
3. **{Category}**: {specific recommendation}

---

## Verdict Rationale

{2-3 paragraphs explaining the verdict. Reference specific ACs, test results, and issues.
Explain what is working well, what is broken, and what needs attention before shipping.}

### Conditions for Passing (if CONDITIONAL PASS)
{List specific conditions that must be met}

### Next Steps
1. {action item}
2. {action item}
```

---

## 7. Common Flutter Testing Pitfalls

### Pitfall 1: Not awaiting `tester.pumpAndSettle()`

```dart
// ❌ WRONG — widget hasn't finished building/animating
await tester.pumpWidget(createTestWidget());
expect(find.text('Hello'), findsOneWidget); // May fail intermittently

// ✅ CORRECT — wait for all frames and animations
await tester.pumpWidget(createTestWidget());
await tester.pumpAndSettle();
expect(find.text('Hello'), findsOneWidget);
```

**When `pumpAndSettle` hangs**: If there are infinite animations (e.g., `CircularProgressIndicator`), use `pump()` with a specific duration instead:
```dart
await tester.pump(const Duration(milliseconds: 100));
```

### Pitfall 2: Testing Implementation Instead of Behavior

```dart
// ❌ WRONG — testing internal state variable name
expect(viewModel._internalState, equals(State.loaded)); // Private!

// ✅ CORRECT — testing through public API
expect(viewModel.isLoading, isFalse);
expect(viewModel.items, isNotEmpty);
```

### Pitfall 3: Not Cleaning Up Resources

```dart
// ❌ WRONG — leaks stream controller
test('should emit events', () {
  final controller = StreamController<int>();
  // ... test ...
  // controller never closed!
});

// ✅ CORRECT — clean up in tearDown or addTearDown
test('should emit events', () {
  final controller = StreamController<int>();
  addTearDown(controller.close);
  // ... test ...
});
```

### Pitfall 4: Not Testing Error Paths

```dart
// ❌ INCOMPLETE — only happy path
test('should fetch users', () async {
  when(mockRepo.getUsers()).thenAnswer((_) async => users);
  await viewModel.fetchUsers();
  expect(viewModel.users, isNotEmpty);
});

// ✅ COMPLETE — happy path + error paths
test('should fetch users on success', () async { /* ... */ });
test('should set error on network failure', () async { /* ... */ });
test('should set error on timeout', () async { /* ... */ });
test('should set error on server error', () async { /* ... */ });
test('should handle empty response', () async { /* ... */ });
```

### Pitfall 5: Brittle Widget Tree Assertions

```dart
// ❌ BRITTLE — depends on exact widget tree structure
expect(find.byType(Padding).at(2), findsOneWidget);

// ✅ ROBUST — uses keys or semantic finders
expect(find.byKey(const Key('user_name')), findsOneWidget);
expect(find.text('Alice'), findsOneWidget);
```

### Pitfall 6: Missing `tearDown` for ChangeNotifier

```dart
// ❌ WRONG — ViewModel may leak listeners
setUp(() {
  viewModel = MyViewModel(repository: mockRepo);
});

// ✅ CORRECT — dispose in tearDown
setUp(() {
  viewModel = MyViewModel(repository: mockRepo);
});
tearDown(() {
  viewModel.dispose();
});
```

### Pitfall 7: Forgetting `registerFallbackValue` with Mocktail

```dart
// ❌ WRONG — crashes with "No matching calls" for custom types
when(() => mockRepo.createUser(any())).thenAnswer((_) async => user);

// ✅ CORRECT — register fallback first
setUpAll(() {
  registerFallbackValue(User(id: '', name: '', email: ''));
});

when(() => mockRepo.createUser(any())).thenAnswer((_) async => user);
```

### Pitfall 8: Tests That Depend on Execution Order

```dart
// ❌ WRONG — test 2 depends on state from test 1
test('should add user', () {
  viewModel.addUser(user);
  expect(viewModel.users.length, equals(1));
});
test('should have one user', () {
  // Assumes previous test ran! Will fail if run independently.
  expect(viewModel.users.length, equals(1));
});

// ✅ CORRECT — each test sets up its own state
test('should add user', () {
  viewModel.addUser(user);
  expect(viewModel.users.length, equals(1));
});
test('should start with empty users', () {
  // setUp creates a fresh viewModel for each test
  expect(viewModel.users, isEmpty);
});
```

### Pitfall 9: Using `tester.binding.addPostFrameCallback` Incorrectly

```dart
// ❌ WRONG — callback may not fire in test
tester.binding.addPostFrameCallback((_) {
  expect(find.text('Done'), findsOneWidget);
});

// ✅ CORRECT — use pump to advance frames
await tester.pump();
expect(find.text('Done'), findsOneWidget);
```

### Pitfall 10: Not Handling Async Gaps

```dart
// ❌ WRONG — assertion runs before async operation completes
viewModel.fetchData(); // async but not awaited
expect(viewModel.items, isNotEmpty); // items still empty!

// ✅ CORRECT — await the async operation
await viewModel.fetchData();
expect(viewModel.items, isNotEmpty);
```

---

## 8. Severity Classification Guide

Use this guide to consistently classify issues:

| Severity | Criteria | Examples | Action |
|----------|----------|----------|--------|
| **🔴 Blocker** | Core functionality broken, app crashes, data loss | App crashes on launch, data not saved, security vulnerability | Must fix before shipping |
| **🟠 Major** | Feature works partially, significant UX degradation | Delete works but no confirmation dialog, list doesn't refresh after add | Should fix before shipping |
| **🟡 Minor** | Cosmetic issues, rare edge cases, minor UX issues | Wrong font size, missing empty state illustration, no loading animation | Can ship, fix in next release |
| **⚪ Info** | Not a bug, but worth noting | Code quality concern, missing documentation, potential improvement | Optional, note for future |

### Decision Matrix

```
Is it a crash or data loss? → BLOCKER
Does core functionality fail? → BLOCKER
Is the feature unusable? → BLOCKER
Is the feature degraded? → MAJOR
Is it a visual/cosmetic issue? → MINOR
Is it a rare edge case? → MINOR (unless data loss, then BLOCKER)
Is it an improvement idea? → INFO
```
