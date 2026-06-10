# MVVM Implementation Reference

Practical patterns for implementing MVVM in Flutter. Use this as a lookup guide when implementing features.

---

## Base ViewModel

Every ViewModel in the project extends this base class:

```dart
// lib/core/viewmodels/base_viewmodel.dart

import 'package:flutter/foundation.dart';

/// Base class for all ViewModels in the application.
/// Provides common state management patterns for loading and error handling.
abstract class BaseViewModel extends ChangeNotifier {
  bool _isLoading = false;
  String? _errorMessage;
  bool _isDisposed = false;

  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  bool get hasError => _errorMessage != null;

  /// Safely notifies listeners. No-ops if disposed.
  @override
  void notifyListeners() {
    if (!_isDisposed) {
      super.notifyListeners();
    }
  }

  /// Sets loading state and notifies listeners.
  @protected
  void setLoading(bool loading) {
    _isLoading = loading;
    notifyListeners();
  }

  /// Sets error state and notifies listeners.
  @protected
  void setError(String message) {
    _errorMessage = message;
    notifyListeners();
  }

  /// Clears error state.
  @protected
  void clearError() {
    _errorMessage = null;
  }

  /// Converts exceptions to user-friendly messages.
  @protected
  String friendlyError(Object error) {
    if (error is NetworkException) {
      return 'No internet connection. Please check your connection and try again.';
    }
    if (error is UnauthorisedException) {
      return 'Your session has expired. Please log in again.';
    }
    if (error is NotFoundException) {
      return 'The requested item was not found.';
    }
    if (error is ApiException) {
      return 'Something went wrong on our end. Please try again.';
    }
    debugPrint('Unexpected error: $error');
    return 'An unexpected error occurred. Please try again.';
  }

  @override
  void dispose() {
    _isDisposed = true;
    super.dispose();
  }
}
```

---

## Feature Module Structure

```
lib/features/product_list/
├── models/
│   ├── product.dart              # Data model
│   └── product_filter.dart       # Value objects
├── repositories/
│   ├── product_repository.dart   # Abstract interface
│   └── product_repository_impl.dart  # Concrete implementation
└── views/
    ├── product_list/             # Folder for the Product List screen
    │   ├── product_list_vu.dart  # screen_VU: View page
    │   └── product_list_vm.dart  # screen_VM: ViewModel page (ChangeNotifier)
    └── widgets/
        ├── product_card.dart
        ├── product_filter_bar.dart
        └── product_empty_state.dart
```

---

## Data Model Patterns

### Simple Model

```dart
class Product {
  final String id;
  final String name;
  final double price;
  final String? imageUrl;
  final bool isAvailable;

  const Product({
    required this.id,
    required this.name,
    required this.price,
    this.imageUrl,
    required this.isAvailable,
  });

  factory Product.fromJson(Map<String, dynamic> json) => Product(
    id: json['id'] as String,
    name: json['name'] as String,
    price: (json['price'] as num).toDouble(),
    imageUrl: json['image_url'] as String?,
    isAvailable: json['is_available'] as bool,
  );

  Map<String, dynamic> toJson() => {
    'id': id,
    'name': name,
    'price': price,
    'image_url': imageUrl,
    'is_available': isAvailable,
  };

  Product copyWith({
    String? id,
    String? name,
    double? price,
    String? imageUrl,
    bool? isAvailable,
  }) => Product(
    id: id ?? this.id,
    name: name ?? this.name,
    price: price ?? this.price,
    imageUrl: imageUrl ?? this.imageUrl,
    isAvailable: isAvailable ?? this.isAvailable,
  );

  @override
  bool operator ==(Object other) =>
      identical(this, other) || other is Product && id == other.id;

  @override
  int get hashCode => id.hashCode;

  @override
  String toString() => 'Product(id: $id, name: $name, price: $price)';
}
```

### Sealed State Class Pattern

Use sealed classes to represent UI state explicitly:

```dart
sealed class ProductListState {
  const ProductListState();
}

class ProductListInitial extends ProductListState {
  const ProductListInitial();
}

class ProductListLoading extends ProductListState {
  const ProductListLoading();
}

class ProductListLoaded extends ProductListState {
  final List<Product> products;
  final bool hasMorePages;

  const ProductListLoaded({
    required this.products,
    required this.hasMorePages,
  });
}

class ProductListError extends ProductListState {
  final String message;

  const ProductListError(this.message);
}

class ProductListEmpty extends ProductListState {
  const ProductListEmpty();
}
```

---

## Repository Pattern

### Interface

```dart
// lib/features/products/repositories/product_repository.dart

abstract class ProductRepository {
  /// Fetches a paginated list of products.
  /// 
  /// Throws [NetworkException] on connectivity issues.
  /// Throws [ApiException] on server errors.
  Future<List<Product>> fetchProducts({
    int page = 1,
    int limit = 20,
    String? searchQuery,
  });

  /// Fetches a single product by ID.
  ///
  /// Throws [NotFoundException] if product doesn't exist.
  Future<Product> fetchProduct(String id);

  /// Creates a new product.
  Future<Product> createProduct(Map<String, dynamic> data);

  /// Updates an existing product.
  Future<Product> updateProduct(String id, Map<String, dynamic> data);

  /// Deletes a product.
  Future<void> deleteProduct(String id);
}
```

### Implementation

```dart
// lib/features/products/repositories/product_repository_impl.dart

import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:io';

class ProductRepositoryImpl implements ProductRepository {
  final http.Client _client;
  final String _baseUrl;

  ProductRepositoryImpl({
    required http.Client client,
    required String baseUrl,
  })  : _client = client,
        _baseUrl = baseUrl;

  @override
  Future<List<Product>> fetchProducts({
    int page = 1,
    int limit = 20,
    String? searchQuery,
  }) async {
    try {
      final queryParams = {
        'page': '$page',
        'limit': '$limit',
        if (searchQuery != null && searchQuery.isNotEmpty)
          'search': searchQuery,
      };

      final uri = Uri.parse('$_baseUrl/products')
          .replace(queryParameters: queryParams);

      final response = await _client
          .get(uri, headers: _headers)
          .timeout(const Duration(seconds: 30));

      return _handleResponse(
        response,
        onSuccess: (data) => (data as List)
            .map((e) => Product.fromJson(e as Map<String, dynamic>))
            .toList(),
      );
    } on SocketException {
      throw const NetworkException('No internet connection');
    } on TimeoutException {
      throw const NetworkException('Request timed out. Please try again.');
    }
  }

  // Generic response handler to avoid repetition
  T _handleResponse<T>(
    http.Response response, {
    required T Function(dynamic data) onSuccess,
  }) {
    final body = jsonDecode(response.body);

    switch (response.statusCode) {
      case 200:
      case 201:
        return onSuccess(body);
      case 401:
        throw const UnauthorisedException('Authentication required');
      case 404:
        throw const NotFoundException('Resource not found');
      case >= 500:
        throw ApiException(
          'Server error: ${response.statusCode}',
          response.statusCode,
        );
      default:
        throw ApiException(
          'Unexpected status: ${response.statusCode}',
          response.statusCode,
        );
    }
  }

  Map<String, String> get _headers => {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  };
}
```

---

## ViewModel Patterns

### List with Pagination

```dart
class ProductListVM extends BaseViewModel {
  final ProductRepository _repository;

  List<Product> _products = [];
  int _currentPage = 1;
  bool _hasMorePages = true;
  String? _searchQuery;

  List<Product> get products => List.unmodifiable(_products);
  bool get hasMorePages => _hasMorePages;
  bool get isEmpty => !isLoading && !hasError && _products.isEmpty;

  ProductListVM({required ProductRepository repository})
      : _repository = repository;

  Future<void> loadProducts({bool refresh = false}) async {
    if (isLoading) return;

    if (refresh) {
      _currentPage = 1;
      _products = [];
      _hasMorePages = true;
    }

    setLoading(true);
    clearError();

    try {
      final results = await _repository.fetchProducts(
        page: _currentPage,
        limit: 20,
        searchQuery: _searchQuery,
      );

      _products = refresh ? results : [..._products, ...results];
      _hasMorePages = results.length == 20;
      if (_hasMorePages) _currentPage++;
      notifyListeners();
    } catch (e) {
      setError(friendlyError(e));
    } finally {
      setLoading(false);
    }
  }

  Future<void> search(String query) async {
    _searchQuery = query.isEmpty ? null : query;
    await loadProducts(refresh: true);
  }

  Future<void> deleteProduct(String id) async {
    setLoading(true);
    try {
      await _repository.deleteProduct(id);
      _products = _products.where((p) => p.id != id).toList();
      notifyListeners();
    } catch (e) {
      setError(friendlyError(e));
    } finally {
      setLoading(false);
    }
  }
}
```

### Form ViewModel

```dart
class CreateProductVM extends BaseViewModel {
  final ProductRepository _repository;

  // Form state
  String _name = '';
  String _price = '';
  bool _isSubmitting = false;
  bool _isSuccess = false;

  String get name => _name;
  String get price => _price;
  bool get isSubmitting => _isSubmitting;
  bool get isSuccess => _isSuccess;

  // Validation
  String? get nameError => _name.isEmpty ? 'Name is required' : null;
  String? get priceError {
    if (_price.isEmpty) return 'Price is required';
    if (double.tryParse(_price) == null) return 'Enter a valid price';
    if (double.parse(_price) <= 0) return 'Price must be greater than 0';
    return null;
  }
  bool get isValid => nameError == null && priceError == null;

  CreateProductVM({required ProductRepository repository})
      : _repository = repository;

  void onNameChanged(String value) {
    _name = value;
    notifyListeners();
  }

  void onPriceChanged(String value) {
    _price = value;
    notifyListeners();
  }

  Future<void> submit() async {
    if (!isValid || _isSubmitting) return;

    _isSubmitting = true;
    clearError();
    notifyListeners();

    try {
      await _repository.createProduct({
        'name': _name,
        'price': double.parse(_price),
      });
      _isSuccess = true;
      notifyListeners();
    } catch (e) {
      setError(friendlyError(e));
    } finally {
      _isSubmitting = false;
      notifyListeners();
    }
  }
}
```

---

## Navigation from ViewModel

Never use `BuildContext` in a ViewModel. Use one of these patterns:

### Callback Pattern (Simple)

```dart
// ViewModel exposes a callback slot
class LoginVM extends BaseViewModel {
  final VoidCallback? onLoginSuccess;

  LoginVM({this.onLoginSuccess});

  Future<void> login(String email, String password) async {
    setLoading(true);
    try {
      // ... login logic ...
      onLoginSuccess?.call(); // ✅ No BuildContext
    } catch (e) {
      setError(friendlyError(e));
    } finally {
      setLoading(false);
    }
  }
}

// In the View:
ChangeNotifierProvider(
  create: (_) => LoginVM(
    onLoginSuccess: () => context.go('/home'), // Navigation in View ✅
  ),
)
```

### NavigationService Pattern (Complex)

```dart
// lib/core/services/navigation_service.dart

abstract class NavigationService {
  void navigateTo(String route, {Object? arguments});
  void replace(String route, {Object? arguments});
  void pop([Object? result]);
  bool canPop();
}

class GoRouterNavigationService implements NavigationService {
  final GoRouter _router;
  GoRouterNavigationService(this._router);

  @override
  void navigateTo(String route, {Object? arguments}) => _router.go(route);

  @override
  void replace(String route, {Object? arguments}) => _router.replace(route);

  @override
  void pop([Object? result]) => _router.pop();

  @override
  bool canPop() => _router.canPop();
}

// In ViewModel:
class LoginVM extends BaseViewModel {
  final NavigationService _navigation;

  LoginVM({required NavigationService navigation})
      : _navigation = navigation;

  Future<void> login(String email, String password) async {
    // ... login ...
    _navigation.navigateTo('/home'); // ✅ No BuildContext
  }
}
```

---

## Provider Setup

```dart
// lib/main.dart or feature-level provider scope

MultiProvider(
  providers: [
    // Singletons — created once
    Provider<http.Client>(create: (_) => http.Client()),
    Provider<NavigationService>(
      create: (ctx) => GoRouterNavigationService(router),
    ),

    // Repositories
    ProxyProvider<http.Client, ProductRepository>(
      update: (_, client, __) => ProductRepositoryImpl(
        client: client,
        baseUrl: AppConstants.baseUrl,
      ),
    ),

    // ViewModels ─── created per scope (not singletons)
    ChangeNotifierProxyProvider<ProductRepository, ProductListVM>(
      create: (ctx) => ProductListVM(
        repository: ctx.read<ProductRepository>(),
      ),
      update: (ctx, repo, previous) =>
          previous ?? ProductListVM(repository: repo),
    ),
  ],
  child: MaterialApp.router(...),
)
```

---

## Exception Classes

```dart
// lib/core/errors/exceptions.dart

/// Base exception for all app-specific errors.
abstract class AppException implements Exception {
  final String message;
  const AppException(this.message);

  @override
  String toString() => '$runtimeType: $message';
}

/// Thrown when there is no internet connectivity or request times out.
class NetworkException extends AppException {
  const NetworkException(super.message);
}

/// Thrown when the server returns a 401 response.
class UnauthorisedException extends AppException {
  const UnauthorisedException(super.message);
}

/// Thrown when the server returns a 404 response.
class NotFoundException extends AppException {
  const NotFoundException(super.message);
}

/// Thrown for other API errors (4xx/5xx).
class ApiException extends AppException {
  final int statusCode;
  const ApiException(super.message, this.statusCode);
}

/// Thrown for local validation errors.
class ValidationException extends AppException {
  final Map<String, String> fieldErrors;
  const ValidationException(super.message, this.fieldErrors);
}
```
