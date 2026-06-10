# Flutter/Dart MVVM Coding Standards

> These standards are mandatory for all Flutter code produced by dev-pipeline agents.

---

## 1. MVVM Architecture — Layer Separation

The codebase follows strict **Model-View-ViewModel** separation. Every feature is organized into three layers with clear boundaries.

### Model Layer
- **Purpose:** Pure data structures and business logic entities.
- **Contains:** Data classes, enums, entity definitions, serialization logic.
- **Rules:**
  - Models are **pure Dart** — no Flutter imports (`package:flutter/...`).
  - Models are **immutable** — use `final` fields and `const` constructors.
  - Models contain **no business logic** beyond serialization (`fromJson`, `toJson`).
  - Models have **no dependencies** on ViewModels or Views.
  - Use `copyWith()` for creating modified copies.
  - Implement `==` and `hashCode` (or use `equatable` / `freezed`).

```dart
// ✅ CORRECT — Pure immutable data class
class User {
  const User({
    required this.id,
    required this.name,
    required this.email,
  });

  final String id;
  final String name;
  final String email;

  factory User.fromJson(Map<String, dynamic> json) => User(
        id: json['id'] as String,
        name: json['name'] as String,
        email: json['email'] as String,
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'name': name,
        'email': email,
      };

  User copyWith({String? id, String? name, String? email}) => User(
        id: id ?? this.id,
        name: name ?? this.name,
        email: email ?? this.email,
      );
}
```

### ViewModel Layer (screen_VM)
- **Purpose:** State management, business logic, and data transformation for the View.
- **File Name:** `<screen_name>_vm.dart`
- **Contains:** State holders, business logic methods, input validation, data fetching orchestration.
- **Rules:**
  - ViewModels extend `ChangeNotifier` (or use `StateNotifier` / `Riverpod` equivalents).
  - Class name MUST end with `VM` (e.g. `OrderHistoryVM`).
  - ViewModels have **no Flutter widget imports** — no `BuildContext`, no `Widget`, no `Navigator`.
  - ViewModels **expose state** via getters and **mutate state** via methods.
  - ViewModels **call repositories/services** for data access — never make HTTP calls directly.
  - ViewModels are **fully unit-testable** without a Flutter test environment.
  - One ViewModel per feature screen (avoid god-ViewModels).

```dart
// ✅ CORRECT — OrderHistoryVM in order_history_vm.dart (ViewModel with no UI dependencies)
class OrderHistoryVM extends ChangeNotifier {
  OrderHistoryVM({required OrderRepository orderRepository})
      : _orderRepository = orderRepository;

  final OrderRepository _orderRepository;

  List<Order> _orders = [];
  List<Order> get orders => List.unmodifiable(_orders);

  bool _isLoading = false;
  bool get isLoading => _isLoading;

  String? _errorMessage;
  String? get errorMessage => _errorMessage;

  bool get isEmpty => _orders.isEmpty && !_isLoading;

  Future<void> loadOrders() async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      _orders = await _orderRepository.fetchOrders();
    } catch (e) {
      _errorMessage = 'Failed to load orders. Please try again.';
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
}
```

### View Layer (screen_VU)
- **Purpose:** UI rendering and user interaction handling.
- **File Name:** `<screen_name>_vu.dart`
- **Contains:** Widgets, screens, UI components, navigation.
- **Rules:**
  - Views are **stateless when possible** — derive all state from the ViewModel.
  - Class name MUST end with `VU` (e.g. `OrderHistoryVU`).
  - Views contain **no business logic** — only UI logic (e.g., conditional rendering).
  - Views **never call repositories or services directly**.
  - Views **bind to ViewModel (screen_VM)** via `Consumer`, `Selector`, `Provider.of`, or equivalent.
  - Navigation is triggered by the View but may be informed by ViewModel state.
  - Views **never manipulate data** — they only display it and forward user actions to the ViewModel.

```dart
// ✅ CORRECT — OrderHistoryVU in order_history_vu.dart (View that delegates all logic to OrderHistoryVM)
class OrderHistoryVU extends StatelessWidget {
  const OrderHistoryVU({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Order History')),
      body: Consumer<OrderHistoryVM>(
        builder: (context, viewModel, child) {
          if (viewModel.isLoading) {
            return const Center(child: CircularProgressIndicator());
          }
          if (viewModel.errorMessage != null) {
            return Center(child: Text(viewModel.errorMessage!));
          }
          if (viewModel.isEmpty) {
            return const Center(child: Text('No orders yet.'));
          }
          return ListView.builder(
            itemCount: viewModel.orders.length,
            itemBuilder: (context, index) {
              final order = viewModel.orders[index];
              return OrderListTile(order: order);
            },
          );
        },
      ),
    );
  }
}
```

---

## 2. File Naming Conventions

| Element | Convention | Example |
|---|---|---|
| Dart files | `snake_case.dart` | `order_history_view_model.dart` |
| Classes | `PascalCase` | `OrderHistoryViewModel` |
| Variables & functions | `camelCase` | `loadOrders()`, `orderList` |
| Constants | `camelCase` (Dart convention) | `defaultTimeout`, `maxRetries` |
| Enums | `PascalCase` name, `camelCase` values | `enum OrderStatus { pending, shipped, delivered }` |
| Private members | Prefix with `_` | `_orders`, `_isLoading` |
| Test files | `<file_name>_test.dart` | `order_history_view_model_test.dart` |

---

## 3. Directory Structure

```
lib/
├── main.dart                          # App entry point
├── app.dart                           # MaterialApp / root widget
├── core/                              # App-wide utilities and base classes
│   ├── constants/                     # App constants (colors, strings, dimensions)
│   │   ├── app_colors.dart
│   │   ├── app_strings.dart
│   │   └── app_dimensions.dart
│   ├── errors/                        # Custom exceptions and failure classes
│   │   ├── app_exception.dart
│   │   └── failure.dart
│   ├── network/                       # HTTP client, interceptors, API config
│   │   ├── api_client.dart
│   │   └── api_endpoints.dart
│   ├── utils/                         # Helper functions, extensions
│   │   ├── date_utils.dart
│   │   └── string_extensions.dart
│   └── di/                            # Dependency injection setup
│       └── service_locator.dart
├── features/                          # Feature modules (one per feature)
│   └── order_history/                 # Example feature
│       ├── models/                    # Data classes for this feature
│       │   └── order.dart
│       ├── repositories/             # Data access layer
│       │   ├── order_repository.dart
│       │   └── order_repository_impl.dart
│       └── views/                     # UI screens and components
│           ├── order_history/         # Folder for the Order History screen
│           │   ├── order_history_vu.dart  # screen_VU: View page
│           │   └── order_history_vm.dart  # screen_VM: ViewModel page (ChangeNotifier)
│           └── widgets/
│               └── order_list_tile.dart
└── shared/                           # Shared widgets, themes, reusable components
    ├── widgets/                       # Reusable widget components
    │   ├── app_button.dart
    │   └── loading_indicator.dart
    └── theme/                         # App theming
        └── app_theme.dart

test/
├── features/
│   └── order_history/
│       ├── models/
│       │   └── order_test.dart
│       ├── repositories/
│       │   └── order_repository_test.dart
│       └── view_models/
│           └── order_history_view_model_test.dart
└── shared/
    └── widgets/
        └── app_button_test.dart
```

### Directory Rules
- **One feature = one directory** under `features/`.
- **Never cross-import between features** — shared code goes in `shared/` or `core/`.
- **Repositories** define an abstract interface and a concrete implementation.
- **Test directory** mirrors the `lib/` directory structure exactly.

---

## 4. Dart-Specific Rules

### Immutability & Safety
- **Prefer `final`** for all local variables and fields that don't need reassignment.
- **Use `const` constructors** wherever possible — especially for widgets and data classes.
- **Embrace null safety** — avoid `!` (bang operator) unless you can provably guarantee non-null.
- **Use `required` named parameters** for constructor arguments that must always be provided.
- **Never use `dynamic`** unless interfacing with JSON deserialization (and even then, cast immediately).

```dart
// ✅ CORRECT
final List<Order> orders = await repository.fetchOrders();
const EdgeInsets padding = EdgeInsets.all(16.0);

// ❌ WRONG
var orders = await repository.fetchOrders();  // Use final
List<Order>? orders;  // Don't use nullable if always initialized
```

### Null Safety Patterns
```dart
// ✅ CORRECT — Use null-aware operators
final userName = user?.name ?? 'Unknown';

// ✅ CORRECT — Early return pattern
Future<void> handleTap(Order? order) async {
  if (order == null) return;
  await viewModel.selectOrder(order);
}

// ❌ WRONG — Unsafe bang operator
final userName = user!.name;  // May crash at runtime
```

### Collections
- Use **`List.unmodifiable()`** when exposing lists from ViewModels.
- Prefer **collection literals** (`[]`, `{}`) over constructors (`List()`, `Map()`).
- Use **spread operators** and **collection if/for** for building collections.

```dart
// ✅ CORRECT
final items = [
  ...existingItems,
  if (showExtra) extraItem,
  for (final id in ids) Item(id: id),
];
```

---

## 5. Dependency Injection

- **Abstract all external dependencies** behind interfaces (abstract classes).
- **Inject dependencies via constructors** — never instantiate services inside ViewModels.
- **Use a service locator** (`get_it`) or provider-based DI for wiring.

```dart
// ✅ CORRECT — Constructor injection
class OrderHistoryViewModel extends ChangeNotifier {
  OrderHistoryViewModel({required OrderRepository orderRepository})
      : _orderRepository = orderRepository;

  final OrderRepository _orderRepository;
}

// ❌ WRONG — Hard-coded dependency
class OrderHistoryViewModel extends ChangeNotifier {
  final _orderRepository = OrderRepositoryImpl();  // Untestable!
}
```

---

## 6. Error Handling

### Repository Layer
- Repositories **catch platform exceptions** and convert them to domain-specific failures.
- Use a `Result` type or return nullable values with error state.

```dart
abstract class OrderRepository {
  Future<List<Order>> fetchOrders();
}

class OrderRepositoryImpl implements OrderRepository {
  OrderRepositoryImpl({required ApiClient apiClient}) : _apiClient = apiClient;

  final ApiClient _apiClient;

  @override
  Future<List<Order>> fetchOrders() async {
    try {
      final response = await _apiClient.get('/orders');
      return (response.data as List)
          .map((json) => Order.fromJson(json as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      throw AppException.fromDioError(e);
    }
  }
}
```

### ViewModel Layer
- ViewModels **catch domain exceptions** and translate them to user-friendly error messages.
- ViewModels expose error state (never throw unhandled exceptions).

### View Layer
- Views **display errors** from ViewModel state — they never catch exceptions themselves.

---

## 7. Testing Standards

- **Every ViewModel** must have corresponding unit tests.
- **Every Model** with serialization must have `fromJson`/`toJson` tests.
- **Mock dependencies** using `mockito` or `mocktail`.
- **Test file location** mirrors source location: `lib/features/x/` → `test/features/x/`.
- **Test naming:** `'should <expected behavior> when <condition>'`.

```dart
void main() {
  group('OrderHistoryViewModel', () {
    late MockOrderRepository mockRepository;
    late OrderHistoryViewModel viewModel;

    setUp(() {
      mockRepository = MockOrderRepository();
      viewModel = OrderHistoryViewModel(orderRepository: mockRepository);
    });

    test('should set isLoading to true when loading orders', () async {
      when(() => mockRepository.fetchOrders())
          .thenAnswer((_) async => []);

      final future = viewModel.loadOrders();
      expect(viewModel.isLoading, isTrue);
      await future;
    });

    test('should populate orders when fetch succeeds', () async {
      final testOrders = [Order(id: '1', total: 29.99, status: OrderStatus.delivered)];
      when(() => mockRepository.fetchOrders())
          .thenAnswer((_) async => testOrders);

      await viewModel.loadOrders();

      expect(viewModel.orders, equals(testOrders));
      expect(viewModel.isLoading, isFalse);
      expect(viewModel.errorMessage, isNull);
    });

    test('should set errorMessage when fetch fails', () async {
      when(() => mockRepository.fetchOrders())
          .thenThrow(AppException('Network error'));

      await viewModel.loadOrders();

      expect(viewModel.errorMessage, isNotNull);
      expect(viewModel.isLoading, isFalse);
    });
  });
}
```

---

## 8. Code Quality Checklist

Before any code is committed, verify:

- [ ] `flutter analyze` produces **zero issues**
- [ ] All classes follow MVVM layer rules (no cross-layer violations)
- [ ] All files use `snake_case` naming
- [ ] All public APIs have dartdoc comments
- [ ] No `print()` statements (use `logger` or `debugPrint`)
- [ ] No hard-coded strings in Views (use constants or localization)
- [ ] All dependencies injected via constructors
- [ ] All ViewModel state exposed via getters (not public fields)
- [ ] All tests pass (`flutter test`)
- [ ] No `// TODO` comments without a linked issue/story ID
