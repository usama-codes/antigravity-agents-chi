# State Management Reference

State management using **Provider + ChangeNotifier** — the project's chosen pattern.

---

## Setup

### pubspec.yaml Dependencies

```yaml
dependencies:
  flutter:
    sdk: flutter
  provider: ^6.1.1
  http: ^1.2.0

dev_dependencies:
  flutter_test:
    sdk: flutter
  mockito: ^5.4.4
  build_runner: ^2.4.8
```

---

## Provider Registration

### App-Level Providers (Singletons)

Register long-lived singletons at the top of the widget tree:

```dart
// lib/main.dart

void main() {
  runApp(
    MultiProvider(
      providers: [
        // HTTP client — singleton
        Provider<http.Client>(
          create: (_) => http.Client(),
          dispose: (_, client) => client.close(),
        ),

        // Configuration
        Provider<AppConfig>(
          create: (_) => AppConfig.fromEnvironment(),
        ),

        // Repositories — created once, shared
        ProxyProvider2<http.Client, AppConfig, ProductRepository>(
          update: (_, client, config, __) => ProductRepositoryImpl(
            client: client,
            baseUrl: config.apiBaseUrl,
          ),
        ),

        ProxyProvider2<http.Client, AppConfig, UserRepository>(
          update: (_, client, config, __) => UserRepositoryImpl(
            client: client,
            baseUrl: config.apiBaseUrl,
          ),
        ),
      ],
      child: MyApp(),
    ),
  );
}
```

### Feature-Level Providers (Scoped)

For ViewModels that only exist while a specific screen is visible, scope them to the route:

```dart
// Using go_router with provider scoping
GoRoute(
  path: '/products',
  builder: (context, state) => ChangeNotifierProvider(
    create: (ctx) => ProductListViewModel(
      repository: ctx.read<ProductRepository>(),
    ),
    child: const ProductListScreen(),
  ),
),
```

Or with a `ChangeNotifierProvider` wrapping the screen directly:

```dart
class ProductListRoute extends StatelessWidget {
  const ProductListRoute({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (ctx) => ProductListViewModel(
        repository: ctx.read<ProductRepository>(),
      ),
      child: const ProductListScreen(),
    );
  }
}
```

---

## Consuming State in Views

### `Consumer<T>` — Rebuilds the Consumer's subtree

Best for rebuilding a large portion of the screen:

```dart
Consumer<ProductListViewModel>(
  builder: (context, viewModel, child) {
    // 'child' is the part that does NOT need to rebuild
    return Column(
      children: [
        // This rebuilds when viewModel changes
        if (viewModel.isLoading) const LinearProgressIndicator(),
        child!,   // This does NOT rebuild
      ],
    );
  },
  child: const _StaticHeader(), // Built once, passed through
),
```

### `context.watch<T>()` — Rebuilds the whole `build()` method

Use sparingly — only when the whole widget depends on the ViewModel:

```dart
@override
Widget build(BuildContext context) {
  final vm = context.watch<UserViewModel>();
  return Text(vm.user?.name ?? 'Guest');
}
```

### `context.read<T>()` — Reads without subscribing

Use inside event handlers where you need to call a ViewModel method but NOT rebuild:

```dart
ElevatedButton(
  onPressed: () {
    // ✅ read() in event handlers — no rebuild subscription
    context.read<ProductListViewModel>().loadProducts(refresh: true);
  },
  child: const Text('Refresh'),
),
```

### `context.select<T, R>()` — Rebuilds on specific field only

Optimise rebuilds by selecting only the property you need:

```dart
// Only rebuilds when isLoading changes — not when products list changes
final isLoading = context.select<ProductListViewModel, bool>(
  (vm) => vm.isLoading,
);
```

---

## State Class Pattern (Sealed Types)

For complex state machines, use sealed classes instead of multiple booleans:

```dart
// lib/features/checkout/viewmodels/checkout_state.dart

sealed class CheckoutState {
  const CheckoutState();
}

class CheckoutIdle extends CheckoutState {
  final CartModel cart;
  const CheckoutIdle(this.cart);
}

class CheckoutValidating extends CheckoutState {
  const CheckoutValidating();
}

class CheckoutProcessing extends CheckoutState {
  final PaymentMethod method;
  const CheckoutProcessing(this.method);
}

class CheckoutSuccess extends CheckoutState {
  final String orderId;
  const CheckoutSuccess(this.orderId);
}

class CheckoutFailure extends CheckoutState {
  final String message;
  final bool isRetryable;
  const CheckoutFailure({required this.message, required this.isRetryable});
}
```

```dart
// In ViewModel
class CheckoutViewModel extends BaseViewModel {
  CheckoutState _state = const CheckoutIdle(CartModel.empty());
  CheckoutState get state => _state;

  void _setState(CheckoutState s) {
    _state = s;
    notifyListeners();
  }

  Future<void> processPayment(PaymentMethod method) async {
    _setState(const CheckoutProcessing(method));
    try {
      final orderId = await _repository.processPayment(method);
      _setState(CheckoutSuccess(orderId));
    } catch (e) {
      _setState(CheckoutFailure(
        message: friendlyError(e),
        isRetryable: e is NetworkException,
      ));
    }
  }
}
```

```dart
// In View — use switch expression for exhaustive matching
Consumer<CheckoutViewModel>(
  builder: (context, vm, _) => switch (vm.state) {
    CheckoutIdle(cart: final cart) => CheckoutForm(cart: cart),
    CheckoutValidating() => const _ValidatingOverlay(),
    CheckoutProcessing(method: final m) => ProcessingView(method: m),
    CheckoutSuccess(orderId: final id) => SuccessView(orderId: id),
    CheckoutFailure(message: final msg, isRetryable: final retry) =>
      FailureView(message: msg, showRetry: retry),
  },
),
```

---

## Handling Async Operations

### Standard Pattern

```dart
Future<void> fetchData() async {
  if (isLoading) return;     // Prevent duplicate calls

  setLoading(true);
  clearError();

  try {
    final data = await _repository.getData();
    _data = data;
    notifyListeners();
  } catch (e) {
    setError(friendlyError(e));
  } finally {
    setLoading(false);       // Always called, even on error
  }
}
```

### Preventing Stale State (Cancellation Token Pattern)

For cases where the user might navigate away during a request:

```dart
class SearchViewModel extends BaseViewModel {
  int _requestId = 0;

  Future<void> search(String query) async {
    final requestId = ++_requestId; // Increment on each call

    setLoading(true);
    clearError();

    try {
      final results = await _repository.search(query);

      if (requestId != _requestId) return; // Stale — a newer request was made

      _results = results;
      notifyListeners();
    } catch (e) {
      if (requestId != _requestId) return;
      setError(friendlyError(e));
    } finally {
      if (requestId == _requestId) setLoading(false);
    }
  }
}
```

---

## ChangeNotifier Lifecycle

### Initialising Data on Creation

```dart
class ProductDetailViewModel extends BaseViewModel {
  final ProductRepository _repository;
  final String productId;

  ProductModel? _product;
  ProductModel? get product => _product;

  ProductDetailViewModel({
    required ProductRepository repository,
    required this.productId,
  }) : _repository = repository {
    // Start loading immediately on creation
    loadProduct();
  }

  Future<void> loadProduct() async { ... }
}

// In Provider:
ChangeNotifierProvider(
  create: (ctx) => ProductDetailViewModel(
    repository: ctx.read<ProductRepository>(),
    productId: productId,
  ),
  child: const ProductDetailScreen(),
)
```

### Cleaning Up

```dart
class StreamViewModel extends BaseViewModel {
  StreamSubscription? _subscription;

  void startListening() {
    _subscription = _repository.dataStream.listen((data) {
      _data = data;
      notifyListeners();
    });
  }

  @override
  void dispose() {
    _subscription?.cancel();  // ✅ Always cancel subscriptions
    super.dispose();
  }
}
```

---

## Testing ViewModels

```dart
// test/features/products/viewmodels/product_list_viewmodel_test.dart

import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/annotations.dart';
import 'package:mockito/mockito.dart';

@GenerateMocks([ProductRepository])
void main() {
  late MockProductRepository mockRepo;
  late ProductListViewModel viewModel;

  setUp(() {
    mockRepo = MockProductRepository();
    viewModel = ProductListViewModel(repository: mockRepo);
  });

  tearDown(() {
    viewModel.dispose();
  });

  group('loadProducts', () {
    test('sets isLoading true then false during fetch', () async {
      // Arrange
      when(mockRepo.fetchProducts()).thenAnswer((_) async => []);

      // Act & Assert (check intermediate states)
      final loadingStates = <bool>[];
      viewModel.addListener(() => loadingStates.add(viewModel.isLoading));

      await viewModel.loadProducts();

      expect(loadingStates, containsAllInOrder([true, false]));
    });

    test('populates products list on success', () async {
      // Arrange
      final products = [
        Product(id: '1', name: 'A', price: 10.0, isAvailable: true),
        Product(id: '2', name: 'B', price: 20.0, isAvailable: true),
      ];
      when(mockRepo.fetchProducts()).thenAnswer((_) async => products);

      // Act
      await viewModel.loadProducts();

      // Assert
      expect(viewModel.products, equals(products));
      expect(viewModel.isLoading, isFalse);
      expect(viewModel.errorMessage, isNull);
    });

    test('sets friendly error message on network failure', () async {
      // Arrange
      when(mockRepo.fetchProducts()).thenThrow(
        const NetworkException('Connection refused'),
      );

      // Act
      await viewModel.loadProducts();

      // Assert
      expect(viewModel.errorMessage, isNotNull);
      expect(
        viewModel.errorMessage!,
        contains('No internet connection'),
      );
      expect(viewModel.products, isEmpty);
    });
  });
}
```

---

## ProxyProvider for Dependent ViewModels

When a ViewModel depends on another ViewModel's state:

```dart
// AuthViewModel must be available before CartViewModel
MultiProvider(
  providers: [
    ChangeNotifierProvider<AuthViewModel>(
      create: (ctx) => AuthViewModel(repo: ctx.read()),
    ),
    ChangeNotifierProxyProvider<AuthViewModel, CartViewModel>(
      create: (ctx) => CartViewModel(
        repo: ctx.read(),
        userId: ctx.read<AuthViewModel>().userId,
      ),
      update: (ctx, auth, cart) {
        cart?.updateUser(auth.userId); // Update when auth changes
        return cart ?? CartViewModel(repo: ctx.read(), userId: auth.userId);
      },
    ),
  ],
  child: const MyApp(),
),
```
