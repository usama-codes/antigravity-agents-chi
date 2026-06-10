# Task Breakdown Template

Use this template to decompose user stories into concrete development tasks organized by the MVVM architectural layers used in Flutter. Every task must be traceable to a user story and have clear dependencies.

---

## Task Breakdown: {Feature Title}

### Legend
- **Story Ref**: The user story ID this task fulfills (e.g., `US-PROF-001`)
- **Depends On**: Task IDs that must be completed before this task can start
- **Estimated Hours**: Rough estimate for planning purposes

---

## Layer 1: Data Models (Model)

> Define all data classes, entities, enums, and serialization logic.

| Task ID | Title | Story Ref | Depends On | Est. Hours | Details |
|---|---|---|---|---|---|
| `T-MOD-001` | {Create `{ModelName}` data model with JSON serialization} | US-XXX-001 | — | {hours} | {Fields: id (String), name (String, required), email (String, nullable), createdAt (DateTime). Include `fromJson`, `toJson`, `copyWith`, and `==`/`hashCode` overrides.} |
| `T-MOD-002` | {Create `{EnumName}` enum for {purpose}} | US-XXX-001 | — | {hours} | {Values: value1, value2, value3. Include serialization helpers.} |
| ... | ... | ... | ... | ... | ... |

### Model Layer Checklist
- [ ] All models have `fromJson` / `toJson` factory methods
- [ ] All models implement `Equatable` or override `==` and `hashCode`
- [ ] All models have `copyWith` methods for immutable updates
- [ ] All nullable fields are explicitly typed with `?`
- [ ] All enums have serialization/deserialization helpers
- [ ] All models have `toString()` overrides for debugging

---

## Layer 2: Data Sources & Repositories (Model)

> Define API clients, local data sources, and repository abstractions.

| Task ID | Title | Story Ref | Depends On | Est. Hours | Details |
|---|---|---|---|---|---|
| `T-API-001` | {Create `{RepositoryName}` abstract repository interface} | US-XXX-001 | T-MOD-001 | {hours} | {Methods: `Future<UserProfile> getProfile(String userId)`, `Future<void> updateProfile(UserProfile profile)`. Define custom exceptions: `ProfileNotFoundException`, `ProfileUpdateFailedException`.} |
| `T-API-002` | {Implement `{RemoteDataSourceName}` with HTTP client} | US-XXX-001 | T-API-001 | {hours} | {Endpoints: `GET /api/v1/users/{id}` → `UserProfile`, `PUT /api/v1/users/{id}` → `void`. Include request/response interceptors, error mapping, timeout of 15 seconds.} |
| `T-API-003` | {Implement `{LocalDataSourceName}` with local storage} | US-XXX-002 | T-API-001 | {hours} | {Cache strategy: write-through. Storage: SharedPreferences for simple values, Hive/SQLite for complex objects. TTL: 5 minutes.} |
| `T-API-004` | {Implement `{RepositoryName}Impl` combining remote and local sources} | US-XXX-001, US-XXX-002 | T-API-002, T-API-003 | {hours} | {Strategy: fetch from remote, cache locally, return cached on network failure. Include retry logic with exponential backoff (max 3 retries).} |
| ... | ... | ... | ... | ... | ... |

### Repository Layer Checklist
- [ ] Repository interfaces are abstract (depend on abstractions, not implementations)
- [ ] Custom exception types defined for all failure modes
- [ ] HTTP client has timeout, retry, and error-mapping configuration
- [ ] Caching strategy is defined (TTL, invalidation triggers)
- [ ] All async methods return proper `Future` types with error handling

---

## Layer 3: ViewModels / State Management (ViewModel)

> Define state classes, state notifiers/cubits/blocs, and business logic.

| Task ID | Title | Story Ref | Depends On | Est. Hours | Details |
|---|---|---|---|---|---|
| `T-VM-001` | {Create `{ScreenName}State` sealed class hierarchy} | US-XXX-001 | T-MOD-001 | {hours} | {States: `Initial`, `Loading`, `Loaded(data: UserProfile)`, `Error(message: String, canRetry: bool)`, `Saving`, `SaveSuccess`, `SaveError(message: String)`. Use Dart 3 sealed classes.} |
| `T-VM-002` | {Create `{ScreenName}ViewModel` / Cubit / Notifier} | US-XXX-001 | T-VM-001, T-API-004 | {hours} | {Methods: `loadProfile()`, `updateField(String field, dynamic value)`, `saveProfile()`, `retry()`. Business rules: validate all fields before save, debounce auto-save by 500ms, prevent duplicate submissions.} |
| `T-VM-003` | {Create `{FormName}ValidationLogic`} | US-XXX-001 | T-MOD-001 | {hours} | {Rules: displayName (2-50 chars, alphanumeric + spaces), email (valid format, optional), bio (max 500 chars). Return field-specific error messages.} |
| ... | ... | ... | ... | ... | ... |

### ViewModel Layer Checklist
- [ ] All possible UI states are modeled (initial, loading, loaded, error, empty + feature-specific)
- [ ] State classes are immutable (sealed classes or freezed)
- [ ] All validation rules match acceptance criteria exactly
- [ ] Debounce/throttle applied where needed (form inputs, button taps)
- [ ] Duplicate submission prevention implemented
- [ ] Error states include actionable information (message, retry capability)
- [ ] Dispose/cleanup logic handles stream subscriptions and timers

---

## Layer 4: UI / Widgets (View)

> Define screens, reusable widgets, and visual components.

| Task ID | Title | Story Ref | Depends On | Est. Hours | Details |
|---|---|---|---|---|---|
| `T-UI-001` | {Create `{ScreenName}` screen widget} | US-XXX-001 | T-VM-002 | {hours} | {Layout: Scaffold → AppBar (title, back button) → SingleChildScrollView → Column. States: show shimmer loading placeholder during `Loading`, form during `Loaded`, error card with retry button during `Error`. Connect to ViewModel via Provider/Riverpod/Bloc.} |
| `T-UI-002` | {Create `{WidgetName}` reusable widget} | US-XXX-001 | — | {hours} | {Props: `String label`, `String? value`, `String? errorText`, `bool enabled`, `ValueChanged<String> onChanged`. States: default, focused, error, disabled. Follow design spec for colors, spacing, typography.} |
| `T-UI-003` | {Create `{DialogName}` confirmation dialog} | US-XXX-001 | — | {hours} | {Trigger: user taps back with unsaved changes. Content: "Discard changes?" with "Cancel" and "Discard" buttons. Discard = pop without saving, Cancel = dismiss dialog.} |
| ... | ... | ... | ... | ... | ... |

### View Layer Checklist
- [ ] Every screen handles all states defined in the ViewModel (loading, loaded, error, empty)
- [ ] Loading states use shimmer placeholders or progress indicators (not blank screens)
- [ ] Error states show user-friendly messages with retry actions
- [ ] Empty states show helpful content with calls to action
- [ ] All interactive elements meet 48x48dp minimum touch target
- [ ] SafeArea is applied to prevent notch/system bar overlap
- [ ] Keyboard handling: scroll to focused field, dismiss on tap outside
- [ ] All strings are extracted for future localization
- [ ] Theme-aware colors used (no hardcoded color values in widgets)

---

## Layer 5: Navigation

> Define route configuration, transitions, and deep link support.

| Task ID | Title | Story Ref | Depends On | Est. Hours | Details |
|---|---|---|---|---|---|
| `T-NAV-001` | {Register `{routeName}` route in router configuration} | US-XXX-001 | T-UI-001 | {hours} | {Path: `/profile/edit`, Parameters: `userId` (required). Transition: slide from right. Guard: must be authenticated.} |
| `T-NAV-002` | {Add navigation trigger from {SourceScreen} to {TargetScreen}} | US-XXX-001 | T-NAV-001 | {hours} | {Trigger: tap "Edit Profile" button on ProfileScreen. Pass `userId` as parameter. Handle result: refresh profile on pop with `true` result.} |
| ... | ... | ... | ... | ... | ... |

### Navigation Checklist
- [ ] All routes are registered in the central router
- [ ] Route guards enforce authentication/authorization where needed
- [ ] Back button behavior is correct on all screens
- [ ] Deep links resolve to the correct screen with correct parameters
- [ ] Navigation results are handled (e.g., refresh on return)
- [ ] No orphan routes (every route is reachable from the app)

---

## Layer 6: Testing

> Define unit tests, widget tests, and integration tests for all layers.

| Task ID | Title | Story Ref | Depends On | Est. Hours | Details |
|---|---|---|---|---|---|
| `T-TEST-001` | {Unit tests for `{ModelName}` serialization} | US-XXX-001 | T-MOD-001 | {hours} | {Test: fromJson with valid data, fromJson with missing optional fields, fromJson with null values, toJson roundtrip, copyWith creates independent copy, equality comparison.} |
| `T-TEST-002` | {Unit tests for `{RepositoryName}Impl`} | US-XXX-001 | T-API-004 | {hours} | {Test: successful fetch, network error returns cached data, cache miss + network error throws, timeout handling, retry logic. Mock: HTTP client and local data source.} |
| `T-TEST-003` | {Unit tests for `{ViewModel}` state transitions} | US-XXX-001 | T-VM-002 | {hours} | {Test: initial → loading → loaded on success, initial → loading → error on failure, loaded → saving → saveSuccess on save, validation rejects invalid input, debounce prevents rapid saves.} |
| `T-TEST-004` | {Widget tests for `{ScreenName}`} | US-XXX-001 | T-UI-001 | {hours} | {Test: renders loading state with shimmer, renders loaded state with data, renders error state with retry button, tap retry triggers reload, form validation shows inline errors, save button disabled during save.} |
| `T-TEST-005` | {Integration test for {end-to-end flow}} | US-XXX-001 | T-NAV-002 | {hours} | {Test: navigate to screen → load data → edit field → save → verify success → navigate back → verify updated data shown. Use mock server.} |
| ... | ... | ... | ... | ... | ... |

### Testing Checklist
- [ ] Every model has serialization roundtrip tests
- [ ] Every repository has success, failure, and edge case tests
- [ ] Every ViewModel has state transition tests for all states
- [ ] Every screen has widget tests for all visual states
- [ ] At least one integration test covers the primary happy path
- [ ] All mocks/fakes are properly configured and realistic
- [ ] Test coverage target: ≥80% for business logic, ≥60% for UI

---

## Build Order (Dependency Sequence)

> Tasks should be built in this order to minimize blocking:

```
Phase 1 (Parallelizable):
  T-MOD-001, T-MOD-002, ...          ← Data Models (no dependencies)

Phase 2 (Depends on Phase 1):
  T-API-001, T-VM-001, T-UI-002      ← Interfaces, States, Standalone Widgets

Phase 3 (Depends on Phase 2):
  T-API-002, T-API-003, T-VM-003     ← Implementations, Validation

Phase 4 (Depends on Phase 3):
  T-API-004, T-VM-002                ← Repository Impl, ViewModel

Phase 5 (Depends on Phase 4):
  T-UI-001, T-UI-003                 ← Screens, Dialogs

Phase 6 (Depends on Phase 5):
  T-NAV-001, T-NAV-002               ← Navigation

Phase 7 (Can run incrementally):
  T-TEST-001 through T-TEST-005      ← Tests (write as each layer completes)
```

---

## Summary

| Layer | Task Count | Total Est. Hours |
|---|---|---|
| Data Models | {count} | {hours} |
| Repositories / API | {count} | {hours} |
| ViewModels | {count} | {hours} |
| UI / Widgets | {count} | {hours} |
| Navigation | {count} | {hours} |
| Testing | {count} | {hours} |
| **Total** | **{count}** | **{hours}** |
