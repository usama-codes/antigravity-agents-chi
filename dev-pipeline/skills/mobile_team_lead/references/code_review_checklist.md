# Code Review Checklist — Mobile Team Lead

Use this checklist when reviewing every chunk of code produced by Flutter Developer agents. **Every item must pass before approving a chunk.** If any item fails, send specific correction instructions to the developer.

---

## How to Use This Checklist

1. For each file the developer created, read it completely using `view_file`
2. Check each applicable category below
3. Mark items as ✅ (pass) or ❌ (fail)
4. For failures, note the exact file, line, and issue
5. Send all failures to the developer in a single correction message
6. Re-review after corrections until all items pass

---

## 1. Architecture Compliance (MVVM Boundaries)

These are the most critical checks. MVVM violations compromise the entire architecture.

### Model Files (`lib/**/models/*.dart`)

| # | Check | How to Verify |
|---|-------|--------------|
| 1.1 | No Flutter imports | Search for `import 'package:flutter` — must not exist |
| 1.2 | No UI package imports | Search for `import 'package:provider`, `import 'package:go_router`, etc. |
| 1.3 | No business logic methods | Models should only have data fields, constructors, fromJson, toJson, copyWith, equality |
| 1.4 | Immutable fields | All fields must be `final` |
| 1.5 | Proper serialization | `fromJson` factory and `toJson` method present |
| 1.6 | Value equality | Uses `Equatable` or manual `==` / `hashCode` override |

### ViewModel Files (`lib/**/viewmodels/*.dart`)

| # | Check | How to Verify |
|---|-------|--------------|
| 1.7 | No `material.dart` import | Only `foundation.dart` is allowed from Flutter |
| 1.8 | No `BuildContext` usage | Search for `BuildContext` — must not appear as parameter, field, or local variable |
| 1.9 | No widget imports | Search for imports from `views/` or `widgets/` directories |
| 1.10 | No direct navigation | Should not use `Navigator.of()` — must use NavigationService |
| 1.11 | No `showDialog` / `showSnackBar` | UI popups must be triggered from Views, not ViewModels |
| 1.12 | Extends ChangeNotifier | Class declaration must include `extends ChangeNotifier` |
| 1.13 | Private state with public getters | State fields should be `_private` with public `get` accessors |
| 1.14 | Calls `notifyListeners()` | After every state change, `notifyListeners()` must be called |

### View Files (`lib/**/views/*.dart`)

| # | Check | How to Verify |
|---|-------|--------------|
| 1.15 | No direct repository usage | Views should never import or call repository classes |
| 1.16 | No business logic in build() | Build methods should only contain UI construction, not data processing |
| 1.17 | Uses Consumer/watch for state | ViewModel state must be consumed via Provider (Consumer, context.watch, Selector) |
| 1.18 | Delegates actions to ViewModel | Button presses, form submissions, etc. should call ViewModel methods |

### Repository Files (`lib/**/repositories/*.dart`)

| # | Check | How to Verify |
|---|-------|--------------|
| 1.19 | Interface exists | An abstract class defining the contract must exist |
| 1.20 | Implementation is separate | Concrete class in a separate file or clearly marked |
| 1.21 | No Flutter/UI imports | Repositories must not import Flutter or UI packages |
| 1.22 | Returns domain models | Methods return typed models, not raw JSON or HTTP responses |

---

## 2. Naming Conventions

| # | Check | Convention | Example |
|---|-------|-----------|---------|
| 2.1 | Class names | PascalCase | `UserListViewModel`, `ProductModel` |
| 2.2 | File names | snake_case, matches class | `user_list_viewmodel.dart` |
| 2.3 | Variable names | camelCase | `userName`, `isLoading` |
| 2.4 | Private members | _camelCase | `_isLoading`, `_users` |
| 2.5 | Constants | camelCase or SCREAMING_SNAKE | `defaultPageSize`, `API_KEY` |
| 2.6 | Enum values | camelCase | `UserRole.admin`, `OrderStatus.pending` |
| 2.7 | Boolean getters | isX, hasX, canX, shouldX | `isLoading`, `hasError`, `canSubmit` |
| 2.8 | Future methods | verbNoun pattern | `loadUsers()`, `deleteProduct()`, `submitForm()` |
| 2.9 | Callback parameters | onX naming | `onTap`, `onSubmit`, `onChanged` |
| 2.10 | Model class suffix | Model | `UserModel`, `ProductModel` (not `User`, `Product`) |
| 2.11 | ViewModel class suffix | ViewModel | `UserListViewModel` (not `UserListVM`, `UserListController`) |
| 2.12 | Repository class suffix | Repository / RepositoryImpl | `UserRepository`, `UserRepositoryImpl` |
| 2.13 | Screen class suffix | Screen | `LoginScreen`, `HomeScreen` |
| 2.14 | Widget subclass prefix | _ for private | `_UserListItem`, `_ErrorView` |

### Common Naming Mistakes to Catch:

```dart
// ❌ WRONG naming
class userModel { ... }           // Not PascalCase
class UserVM { ... }              // Abbreviation
File: UserModel.dart              // Not snake_case
var IsLoading = false;            // Not camelCase
class UserRepo { ... }            // Abbreviation

// ✅ CORRECT naming
class UserModel { ... }
class UserViewModel { ... }
File: user_model.dart
var isLoading = false;
class UserRepository { ... }
```

---

## 3. Null Safety

| # | Check | Details |
|---|-------|---------|
| 3.1 | No unnecessary `!` operators | The `!` null assertion should only be used when you've verified the value is non-null. Prefer `?` with null checks or `??` with defaults. |
| 3.2 | Nullable types are explicit | Fields that can be null use `?` type annotation |
| 3.3 | `required` keyword used | Constructor parameters that must be provided use `required` |
| 3.4 | No `late` without justification | `late` should only be used when initialization is guaranteed before access (e.g., in `initState`) |
| 3.5 | Null-aware operators used | Prefer `?.`, `??`, `??=` over explicit null checks where appropriate |
| 3.6 | fromJson handles nulls | `fromJson` must handle potentially null JSON values for optional fields |

### Examples to look for:

```dart
// ❌ DANGEROUS: Unnecessary null assertion
final name = json['name']!; // Crashes if null

// ✅ SAFE: Proper null handling
final name = json['name'] as String? ?? 'Unknown';

// ❌ DANGEROUS: Late without guarantee
late final UserModel user; // Might be accessed before set

// ✅ SAFE: Nullable with proper checks
UserModel? _user;
UserModel get user {
  if (_user == null) throw StateError('User not loaded');
  return _user!;
}
```

---

## 4. Error Handling

| # | Check | Details |
|---|-------|---------|
| 4.1 | Repository methods have try-catch | Every method that calls an API or database must catch exceptions |
| 4.2 | Typed exceptions used | Catch specific exception types (ApiException, NotFoundException), not just `catch (e)` |
| 4.3 | Generic catch as last resort | A generic `catch (e)` should follow specific catches as a fallback |
| 4.4 | ViewModel exposes error state | ViewModels must have `errorMessage` or `hasError` getter |
| 4.5 | Views display errors | Views must show error state to the user (error widget, snackbar, etc.) |
| 4.6 | Retry mechanism exists | Error states should include a retry button/action |
| 4.7 | User-friendly messages | Error messages shown to users must be human-readable, not stack traces |
| 4.8 | Loading state during operations | `isLoading` must be set to true before async ops and false after (including error paths) |
| 4.9 | Finally block for cleanup | Use `finally` to ensure loading state is reset even on error |

### Error Handling Anti-Patterns to Catch:

```dart
// ❌ WRONG: Empty catch
try {
  await _repo.getUsers();
} catch (e) {
  // Swallowed error — user has no idea what happened
}

// ❌ WRONG: No loading state reset on error
Future<void> load() async {
  _isLoading = true;
  notifyListeners();
  try {
    _data = await _repo.getData();
    _isLoading = false;      // Never reached if error!
    notifyListeners();
  } catch (e) {
    _error = e.toString();
    notifyListeners();
    // _isLoading is stuck at true!
  }
}

// ❌ WRONG: Stack trace shown to user
_errorMessage = e.toString();  // Shows "ApiException: ..."

// ✅ CORRECT: Proper pattern
Future<void> load() async {
  _isLoading = true;
  _errorMessage = null;
  notifyListeners();

  try {
    _data = await _repo.getData();
  } on ApiException catch (e) {
    _errorMessage = e.userFriendlyMessage;
  } catch (e) {
    _errorMessage = 'Something went wrong. Please try again.';
  } finally {
    _isLoading = false;
    notifyListeners();
  }
}
```

---

## 5. Widget Composition and Structure

| # | Check | Details |
|---|-------|---------|
| 5.1 | Build method ≤ ~50 lines | If longer, extract sub-widgets |
| 5.2 | Sub-widgets are separate classes | NOT helper methods returning widgets — separate classes for proper rebuilds |
| 5.3 | StatelessWidget preferred | Use StatefulWidget only when local state (animation controller, text editing controller, etc.) is needed |
| 5.4 | Data passed via constructor | Don't reach up the tree to get data — pass it down |
| 5.5 | Callbacks for events | Use `VoidCallback`, `ValueChanged<T>` for parent communication |
| 5.6 | Private sub-widgets prefixed with _ | `_UserCard`, `_ErrorView` — not exported |
| 5.7 | No deeply nested widget trees | If nesting exceeds 5-6 levels in build(), extract widgets |

### Widget Composition Anti-Patterns:

```dart
// ❌ WRONG: Helper method instead of widget class
Widget _buildUserCard(UserModel user) {
  return Card(child: Text(user.name));
}

// ✅ CORRECT: Separate widget class
class _UserCard extends StatelessWidget {
  final UserModel user;
  const _UserCard({required this.user});

  @override
  Widget build(BuildContext context) {
    return Card(child: Text(user.name));
  }
}
```

---

## 6. Performance

| # | Check | Details |
|---|-------|---------|
| 6.1 | `const` constructors used | Widgets that don't change should use `const` |
| 6.2 | `const` keyword on widget instances | `const Text('Hello')`, `const SizedBox(height: 16)` |
| 6.3 | `ListView.builder` for long lists | Never use `ListView(children: [...])` for dynamic/long lists |
| 6.4 | Keys used in lists | Items in `ListView.builder` should have keys for proper diffing |
| 6.5 | Consumer scope is narrow | Don't wrap entire screens in Consumer — wrap only the parts that need rebuilding |
| 6.6 | Selector for expensive rebuilds | Use `Selector` when only a specific property change should trigger rebuild |
| 6.7 | No unnecessary computations in build | Move complex computations to ViewModel, not computed in `build()` |
| 6.8 | Avoid `MediaQuery.of()` in build | Cache media query values or use LayoutBuilder for responsive layouts |
| 6.9 | Image caching | Network images should use `CachedNetworkImage` or similar |
| 6.10 | Dispose controllers | TextEditingController, AnimationController, ScrollController must be disposed |

### Performance Anti-Patterns:

```dart
// ❌ WRONG: Computing in build
Widget build(BuildContext context) {
  final sortedUsers = List.of(users)
    ..sort((a, b) => a.name.compareTo(b.name)); // Runs on every rebuild!
  return ListView(...);
}

// ✅ CORRECT: Computed in ViewModel
// In ViewModel:
List<UserModel> get sortedUsers => List.of(_users)
  ..sort((a, b) => a.name.compareTo(b.name));

// ❌ WRONG: Full screen Consumer
Consumer<UserViewModel>(
  builder: (context, vm, child) {
    return Scaffold(
      appBar: AppBar(...),  // Rebuilds even if only list changes
      body: ListView(...),
    );
  },
)

// ✅ CORRECT: Scoped Consumer
Scaffold(
  appBar: AppBar(...),  // Doesn't rebuild
  body: Consumer<UserViewModel>(
    builder: (context, vm, child) {
      return ListView(...);  // Only this rebuilds
    },
  ),
)
```

---

## 7. Accessibility

| # | Check | Details |
|---|-------|---------|
| 7.1 | Semantic labels on icons | `Icon(Icons.delete, semanticLabel: 'Delete item')` |
| 7.2 | Semantic labels on images | `Image.network(url, semanticLabel: 'Product photo')` |
| 7.3 | Sufficient touch targets | Interactive elements should be at least 48x48 logical pixels |
| 7.4 | Color contrast | Text must be readable against its background |
| 7.5 | Meaningful button labels | Not just icons — include text or tooltip |
| 7.6 | Semantics for custom widgets | Use `Semantics` widget for custom interactive elements |
| 7.7 | ExcludeSemantics for decorative elements | Decorative images/icons should be excluded from semantics tree |
| 7.8 | Focus order | Tab/focus order should be logical |

---

## 8. Code Documentation

| # | Check | Details |
|---|-------|---------|
| 8.1 | All public classes have dartdoc | `/// Description of what this class does.` |
| 8.2 | All public methods have dartdoc | Including parameter descriptions and return value |
| 8.3 | All public properties have dartdoc | Even simple getters deserve a one-liner |
| 8.4 | Complex logic has inline comments | Non-obvious algorithms or business rules |
| 8.5 | No commented-out code | Dead code should be deleted, not commented |
| 8.6 | No TODO without ticket | TODOs must reference a task or be approved by TL |
| 8.7 | File header for complex files | Optional but recommended for files with complex logic |

### Documentation Examples:

```dart
// ❌ WRONG: No documentation
class UserRepo {
  Future<List<User>> get() async { ... }
}

// ❌ WRONG: Useless documentation
/// User repository.
class UserRepository {
  /// Gets users.
  Future<List<UserModel>> getUsers() async { ... }
}

// ✅ CORRECT: Meaningful documentation
/// Repository interface for user data operations.
///
/// Provides methods to fetch, create, update, and delete users.
/// Implementations may use REST APIs, GraphQL, or local storage.
abstract class UserRepository {
  /// Fetches all users matching the optional [filter].
  ///
  /// Returns an empty list if no users match.
  /// Results are sorted by [name] in ascending order.
  ///
  /// Throws [ApiException] if the network request fails.
  /// Throws [AuthException] if the user's session has expired.
  Future<List<UserModel>> getUsers({UserFilter? filter});
}
```

---

## 9. Import Organization

| # | Check | Details |
|---|-------|---------|
| 9.1 | Imports are grouped | dart: → package: → relative, separated by blank lines |
| 9.2 | No unused imports | Every import must be referenced in the file |
| 9.3 | No wildcard imports | Never use `import '...' show *` |
| 9.4 | Relative imports for same package | Use relative paths within the same package |
| 9.5 | Alphabetical within groups | Imports within each group should be alphabetical |

---

## 10. Test Coverage Expectations

| # | Check | Minimum Expectation |
|---|-------|-------------------|
| 10.1 | Model serialization tests | Every `fromJson`/`toJson` must be tested |
| 10.2 | ViewModel state transitions | Test loading → success, loading → error, actions |
| 10.3 | Repository error handling | Test that exceptions are properly thrown/caught |
| 10.4 | Edge cases tested | Empty lists, null values, invalid data |

> **Note**: In Phase 1, tests may be deferred based on Team Lead decision. But if tests are part of the task, they must meet these expectations.

---

## Review Summary Template

After reviewing a chunk, use this template to record your findings:

```
REVIEW RESULTS: [Chunk Name]

STATUS: ✅ APPROVED / ❌ NEEDS CORRECTIONS

Files Reviewed:
- [file path]: ✅ / ❌
- [file path]: ✅ / ❌

Issues Found:
1. [file:line] [Category] [Description]
   Fix: [Specific instruction]

2. [file:line] [Category] [Description]
   Fix: [Specific instruction]

Commendations:
- [Any particularly good patterns or practices noticed]
```
