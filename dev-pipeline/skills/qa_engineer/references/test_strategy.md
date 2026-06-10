# Flutter Testing Strategy — Comprehensive Reference

This document provides detailed testing patterns, strategies, and best practices for Flutter applications following the MVVM architecture. Use this as a reference when writing and organizing tests.

---

## 1. The Testing Pyramid

The testing pyramid is a strategy that balances speed, coverage, and confidence:

```
        ╱╲
       ╱  ╲         Integration Tests (10%)
      ╱    ╲        → Full user flows, real navigation
     ╱──────╲       → Slowest, most brittle, highest confidence
    ╱        ╲
   ╱          ╲     Widget Tests (20%)
  ╱            ╲    → UI rendering, user interactions
 ╱──────────────╲   → Medium speed, medium confidence
╱                ╲
╱                  ╲ Unit Tests (70%)
╱                    ╲→ Pure logic, isolated, fast
╱════════════════════╲→ Fastest, most numerous, foundation
```

| Level | Proportion | What to Test | Speed | Dependencies |
|-------|-----------|--------------|-------|-------------|
| **Unit** | ~70% | ViewModels, Models, Repositories, Utils | ⚡ Fast (ms) | All mocked |
| **Widget** | ~20% | UI widgets, state rendering, interactions | 🔄 Medium (s) | ViewModel mocked |
| **Integration** | ~10% | Full user flows, navigation, end-to-end | 🐌 Slow (min) | Real or mocked backend |

---

## 2. Unit Test Patterns

### 2.1 Testing ViewModels

ViewModels are the **most critical** layer to test. They contain business logic and manage state.

#### Pattern: ViewModel with ChangeNotifier

```dart
// lib/features/users/viewmodels/user_list_viewmodel.dart
class UserListViewModel extends ChangeNotifier {
  final UserRepository _repository;
  
  UserListViewModel({required UserRepository repository})
      : _repository = repository;

  List<User> _users = [];
  List<User> get users => _users;
  
  bool _isLoading = false;
  bool get isLoading => _isLoading;
  
  String? _error;
  String? get error => _error;

  Future<void> fetchUsers() async {
    _isLoading = true;
    _error = null;
    notifyListeners();
    
    try {
      _users = await _repository.getUsers();
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> deleteUser(String id) async {
    try {
      await _repository.deleteUser(id);
      _users.removeWhere((u) => u.id == id);
      notifyListeners();
    } catch (e) {
      _error = 'Failed to delete user: ${e.toString()}';
      notifyListeners();
    }
  }
}
```

#### Test File: ViewModel Tests

```dart
// test/features/users/viewmodels/user_list_viewmodel_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/annotations.dart';
import 'package:mockito/mockito.dart';

import 'package:app/features/users/viewmodels/user_list_viewmodel.dart';
import 'package:app/features/users/repositories/user_repository.dart';
import 'package:app/features/users/models/user.dart';

@GenerateMocks([UserRepository])
import 'user_list_viewmodel_test.mocks.dart';

void main() {
  group('UserListViewModel', () {
    late MockUserRepository mockRepository;
    late UserListViewModel viewModel;

    setUp(() {
      mockRepository = MockUserRepository();
      viewModel = UserListViewModel(repository: mockRepository);
    });

    tearDown(() {
      viewModel.dispose();
    });

    group('initial state', () {
      test('should have empty users list', () {
        expect(viewModel.users, isEmpty);
      });

      test('should not be loading', () {
        expect(viewModel.isLoading, isFalse);
      });

      test('should have no error', () {
        expect(viewModel.error, isNull);
      });
    });

    group('fetchUsers', () {
      final testUsers = [
        User(id: '1', name: 'Alice', email: 'alice@example.com'),
        User(id: '2', name: 'Bob', email: 'bob@example.com'),
      ];

      test('should set isLoading to true when fetch starts', () {
        // Arrange
        when(mockRepository.getUsers())
            .thenAnswer((_) => Future.delayed(
                  const Duration(seconds: 1),
                  () => testUsers,
                ));

        // Act
        viewModel.fetchUsers(); // Don't await — check intermediate state

        // Assert
        expect(viewModel.isLoading, isTrue);
        expect(viewModel.error, isNull);
      });

      test('should populate users and set isLoading to false on success', () async {
        // Arrange
        when(mockRepository.getUsers())
            .thenAnswer((_) async => testUsers);

        // Act
        await viewModel.fetchUsers();

        // Assert
        expect(viewModel.users, equals(testUsers));
        expect(viewModel.users.length, equals(2));
        expect(viewModel.isLoading, isFalse);
        expect(viewModel.error, isNull);
      });

      test('should set error and clear users on failure', () async {
        // Arrange
        when(mockRepository.getUsers())
            .thenThrow(Exception('Network timeout'));

        // Act
        await viewModel.fetchUsers();

        // Assert
        expect(viewModel.error, isNotNull);
        expect(viewModel.error, contains('Network timeout'));
        expect(viewModel.isLoading, isFalse);
      });

      test('should handle empty response', () async {
        // Arrange
        when(mockRepository.getUsers())
            .thenAnswer((_) async => []);

        // Act
        await viewModel.fetchUsers();

        // Assert
        expect(viewModel.users, isEmpty);
        expect(viewModel.isLoading, isFalse);
        expect(viewModel.error, isNull);
      });

      test('should notify listeners on state changes', () async {
        // Arrange
        when(mockRepository.getUsers())
            .thenAnswer((_) async => testUsers);
        int notifyCount = 0;
        viewModel.addListener(() => notifyCount++);

        // Act
        await viewModel.fetchUsers();

        // Assert — should notify at least twice (loading start + complete)
        expect(notifyCount, greaterThanOrEqualTo(2));
      });

      test('should clear previous error on new fetch', () async {
        // Arrange — first call fails
        when(mockRepository.getUsers())
            .thenThrow(Exception('Error'));
        await viewModel.fetchUsers();
        expect(viewModel.error, isNotNull);

        // Arrange — second call succeeds
        when(mockRepository.getUsers())
            .thenAnswer((_) async => testUsers);

        // Act
        await viewModel.fetchUsers();

        // Assert
        expect(viewModel.error, isNull);
        expect(viewModel.users, equals(testUsers));
      });

      test('should call repository.getUsers exactly once', () async {
        // Arrange
        when(mockRepository.getUsers())
            .thenAnswer((_) async => testUsers);

        // Act
        await viewModel.fetchUsers();

        // Assert
        verify(mockRepository.getUsers()).called(1);
      });
    });

    group('deleteUser', () {
      test('should remove user from list on success', () async {
        // Arrange — populate users first
        final testUsers = [
          User(id: '1', name: 'Alice', email: 'alice@test.com'),
          User(id: '2', name: 'Bob', email: 'bob@test.com'),
        ];
        when(mockRepository.getUsers())
            .thenAnswer((_) async => testUsers);
        await viewModel.fetchUsers();

        when(mockRepository.deleteUser('1'))
            .thenAnswer((_) async => {});

        // Act
        await viewModel.deleteUser('1');

        // Assert
        expect(viewModel.users.length, equals(1));
        expect(viewModel.users.first.name, equals('Bob'));
        expect(viewModel.error, isNull);
      });

      test('should set error when delete fails', () async {
        // Arrange
        when(mockRepository.deleteUser(any))
            .thenThrow(Exception('Server error'));

        // Act
        await viewModel.deleteUser('1');

        // Assert
        expect(viewModel.error, isNotNull);
        expect(viewModel.error, contains('Failed to delete'));
      });

      test('should not remove user from list when delete fails', () async {
        // Arrange
        final testUsers = [
          User(id: '1', name: 'Alice', email: 'alice@test.com'),
        ];
        when(mockRepository.getUsers())
            .thenAnswer((_) async => testUsers);
        await viewModel.fetchUsers();

        when(mockRepository.deleteUser('1'))
            .thenThrow(Exception('Server error'));

        // Act
        await viewModel.deleteUser('1');

        // Assert
        expect(viewModel.users.length, equals(1)); // User still present
      });
    });
  });
}
```

#### Testing ViewModels with Riverpod

```dart
// Using Riverpod StateNotifier pattern
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('UserNotifier', () {
    late ProviderContainer container;
    late MockUserRepository mockRepo;

    setUp(() {
      mockRepo = MockUserRepository();
      container = ProviderContainer(
        overrides: [
          userRepositoryProvider.overrideWithValue(mockRepo),
        ],
      );
    });

    tearDown(() {
      container.dispose();
    });

    test('should start in initial state', () {
      final state = container.read(userNotifierProvider);
      expect(state, isA<UserInitial>());
    });

    test('should emit loaded state with users on success', () async {
      when(mockRepo.getUsers())
          .thenAnswer((_) async => [User(id: '1', name: 'Test')]);

      await container.read(userNotifierProvider.notifier).fetchUsers();

      final state = container.read(userNotifierProvider);
      expect(state, isA<UserLoaded>());
      expect((state as UserLoaded).users.length, equals(1));
    });
  });
}
```

#### Testing ViewModels with Bloc

```dart
// Using bloc_test package
import 'package:bloc_test/bloc_test.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('UserBloc', () {
    late MockUserRepository mockRepo;

    setUp(() {
      mockRepo = MockUserRepository();
    });

    blocTest<UserBloc, UserState>(
      'emits [loading, loaded] when FetchUsers is successful',
      build: () {
        when(mockRepo.getUsers())
            .thenAnswer((_) async => [User(id: '1', name: 'Test')]);
        return UserBloc(repository: mockRepo);
      },
      act: (bloc) => bloc.add(FetchUsersEvent()),
      expect: () => [
        UserLoadingState(),
        UserLoadedState(users: [User(id: '1', name: 'Test')]),
      ],
    );

    blocTest<UserBloc, UserState>(
      'emits [loading, error] when FetchUsers fails',
      build: () {
        when(mockRepo.getUsers()).thenThrow(Exception('Error'));
        return UserBloc(repository: mockRepo);
      },
      act: (bloc) => bloc.add(FetchUsersEvent()),
      expect: () => [
        UserLoadingState(),
        isA<UserErrorState>(),
      ],
    );
  });
}
```

---

### 2.2 Testing Models

Models are data classes. Test their serialization, equality, and copy behavior.

```dart
// test/features/users/models/user_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:app/features/users/models/user.dart';

void main() {
  group('User model', () {
    group('fromJson', () {
      test('should create User from valid JSON', () {
        // Arrange
        final json = {
          'id': '1',
          'name': 'Alice',
          'email': 'alice@example.com',
          'avatarUrl': 'https://example.com/avatar.jpg',
        };

        // Act
        final user = User.fromJson(json);

        // Assert
        expect(user.id, equals('1'));
        expect(user.name, equals('Alice'));
        expect(user.email, equals('alice@example.com'));
        expect(user.avatarUrl, equals('https://example.com/avatar.jpg'));
      });

      test('should handle null optional fields', () {
        final json = {
          'id': '1',
          'name': 'Alice',
          'email': 'alice@example.com',
          // avatarUrl is missing
        };

        final user = User.fromJson(json);

        expect(user.avatarUrl, isNull);
      });

      test('should throw when required fields are missing', () {
        final json = {'id': '1'}; // missing name and email

        expect(
          () => User.fromJson(json),
          throwsA(isA<TypeError>()),
        );
      });

      test('should handle numeric id by converting to string', () {
        final json = {
          'id': 1, // numeric instead of string
          'name': 'Alice',
          'email': 'alice@example.com',
        };

        // Behavior depends on implementation — test what your model does
        final user = User.fromJson(json);
        expect(user.id, equals('1'));
      });
    });

    group('toJson', () {
      test('should serialize all fields to JSON', () {
        final user = User(
          id: '1',
          name: 'Alice',
          email: 'alice@example.com',
          avatarUrl: 'https://example.com/avatar.jpg',
        );

        final json = user.toJson();

        expect(json['id'], equals('1'));
        expect(json['name'], equals('Alice'));
        expect(json['email'], equals('alice@example.com'));
        expect(json['avatarUrl'], equals('https://example.com/avatar.jpg'));
      });

      test('should produce JSON that roundtrips through fromJson', () {
        final original = User(
          id: '1',
          name: 'Alice',
          email: 'alice@example.com',
        );

        final json = original.toJson();
        final restored = User.fromJson(json);

        expect(restored, equals(original));
      });
    });

    group('equality', () {
      test('should be equal when all fields match', () {
        final user1 = User(id: '1', name: 'Alice', email: 'alice@test.com');
        final user2 = User(id: '1', name: 'Alice', email: 'alice@test.com');

        expect(user1, equals(user2));
        expect(user1.hashCode, equals(user2.hashCode));
      });

      test('should not be equal when id differs', () {
        final user1 = User(id: '1', name: 'Alice', email: 'alice@test.com');
        final user2 = User(id: '2', name: 'Alice', email: 'alice@test.com');

        expect(user1, isNot(equals(user2)));
      });
    });

    group('copyWith', () {
      test('should copy with updated name', () {
        final original = User(id: '1', name: 'Alice', email: 'alice@test.com');

        final copy = original.copyWith(name: 'Bob');

        expect(copy.name, equals('Bob'));
        expect(copy.id, equals('1')); // unchanged
        expect(copy.email, equals('alice@test.com')); // unchanged
      });

      test('should return identical copy when no params given', () {
        final original = User(id: '1', name: 'Alice', email: 'alice@test.com');

        final copy = original.copyWith();

        expect(copy, equals(original));
      });
    });

    group('toString', () {
      test('should return readable string representation', () {
        final user = User(id: '1', name: 'Alice', email: 'alice@test.com');

        final str = user.toString();

        expect(str, contains('Alice'));
        expect(str, contains('1'));
      });
    });
  });
}
```

---

### 2.3 Testing Repositories

Repositories wrap API/database calls. Mock the HTTP client and verify correct calls.

```dart
// test/features/users/repositories/user_repository_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:mockito/annotations.dart';
import 'package:mockito/mockito.dart';
import 'dart:convert';

import 'package:app/features/users/repositories/user_repository.dart';
import 'package:app/features/users/models/user.dart';

@GenerateMocks([http.Client])
import 'user_repository_test.mocks.dart';

void main() {
  group('UserRepository', () {
    late MockClient mockHttpClient;
    late UserRepository repository;

    setUp(() {
      mockHttpClient = MockClient();
      repository = UserRepository(client: mockHttpClient);
    });

    group('getUsers', () {
      test('should make GET request to correct endpoint', () async {
        // Arrange
        when(mockHttpClient.get(any, headers: anyNamed('headers')))
            .thenAnswer((_) async => http.Response(
                  jsonEncode([
                    {'id': '1', 'name': 'Alice', 'email': 'alice@test.com'}
                  ]),
                  200,
                ));

        // Act
        await repository.getUsers();

        // Assert
        final captured = verify(mockHttpClient.get(
          captureAny,
          headers: anyNamed('headers'),
        )).captured;
        expect(captured.first.toString(), contains('/api/users'));
      });

      test('should return list of users on 200 response', () async {
        // Arrange
        final responseBody = jsonEncode([
          {'id': '1', 'name': 'Alice', 'email': 'alice@test.com'},
          {'id': '2', 'name': 'Bob', 'email': 'bob@test.com'},
        ]);
        when(mockHttpClient.get(any, headers: anyNamed('headers')))
            .thenAnswer((_) async => http.Response(responseBody, 200));

        // Act
        final users = await repository.getUsers();

        // Assert
        expect(users.length, equals(2));
        expect(users[0].name, equals('Alice'));
        expect(users[1].name, equals('Bob'));
      });

      test('should throw exception on 404 response', () async {
        // Arrange
        when(mockHttpClient.get(any, headers: anyNamed('headers')))
            .thenAnswer((_) async => http.Response('Not found', 404));

        // Act & Assert
        expect(
          () => repository.getUsers(),
          throwsA(isA<ApiException>()),
        );
      });

      test('should throw exception on 500 response', () async {
        // Arrange
        when(mockHttpClient.get(any, headers: anyNamed('headers')))
            .thenAnswer((_) async => http.Response('Server error', 500));

        // Act & Assert
        expect(
          () => repository.getUsers(),
          throwsA(isA<ApiException>()),
        );
      });

      test('should throw exception on network error', () async {
        // Arrange
        when(mockHttpClient.get(any, headers: anyNamed('headers')))
            .thenThrow(const SocketException('No internet'));

        // Act & Assert
        expect(
          () => repository.getUsers(),
          throwsA(isA<NetworkException>()),
        );
      });

      test('should throw exception on timeout', () async {
        // Arrange
        when(mockHttpClient.get(any, headers: anyNamed('headers')))
            .thenThrow(TimeoutException('Timeout'));

        // Act & Assert
        expect(
          () => repository.getUsers(),
          throwsA(isA<NetworkException>()),
        );
      });

      test('should handle malformed JSON response', () async {
        // Arrange
        when(mockHttpClient.get(any, headers: anyNamed('headers')))
            .thenAnswer((_) async => http.Response('not json', 200));

        // Act & Assert
        expect(
          () => repository.getUsers(),
          throwsA(isA<FormatException>()),
        );
      });

      test('should handle empty array response', () async {
        // Arrange
        when(mockHttpClient.get(any, headers: anyNamed('headers')))
            .thenAnswer((_) async => http.Response('[]', 200));

        // Act
        final users = await repository.getUsers();

        // Assert
        expect(users, isEmpty);
      });
    });

    group('deleteUser', () {
      test('should make DELETE request with correct user ID', () async {
        // Arrange
        when(mockHttpClient.delete(any, headers: anyNamed('headers')))
            .thenAnswer((_) async => http.Response('', 204));

        // Act
        await repository.deleteUser('42');

        // Assert
        final captured = verify(mockHttpClient.delete(
          captureAny,
          headers: anyNamed('headers'),
        )).captured;
        expect(captured.first.toString(), contains('/api/users/42'));
      });

      test('should not throw on 204 response', () async {
        // Arrange
        when(mockHttpClient.delete(any, headers: anyNamed('headers')))
            .thenAnswer((_) async => http.Response('', 204));

        // Act & Assert — no exception thrown
        await expectLater(
          repository.deleteUser('1'),
          completes,
        );
      });
    });
  });
}
```

---

### 2.4 Testing Utility Functions

```dart
// test/core/utils/validators_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:app/core/utils/validators.dart';

void main() {
  group('EmailValidator', () {
    test('should return true for valid email', () {
      expect(Validators.isValidEmail('user@example.com'), isTrue);
    });

    test('should return true for email with subdomain', () {
      expect(Validators.isValidEmail('user@mail.example.com'), isTrue);
    });

    test('should return false for empty string', () {
      expect(Validators.isValidEmail(''), isFalse);
    });

    test('should return false for email without @', () {
      expect(Validators.isValidEmail('userexample.com'), isFalse);
    });

    test('should return false for email without domain', () {
      expect(Validators.isValidEmail('user@'), isFalse);
    });

    test('should return false for email with spaces', () {
      expect(Validators.isValidEmail('user @example.com'), isFalse);
    });
  });

  group('CurrencyFormatter', () {
    test('should format integer to currency', () {
      expect(Formatters.toCurrency(1000), equals('\$1,000.00'));
    });

    test('should format zero', () {
      expect(Formatters.toCurrency(0), equals('\$0.00'));
    });

    test('should format negative values', () {
      expect(Formatters.toCurrency(-500), equals('-\$500.00'));
    });

    test('should handle decimal values', () {
      expect(Formatters.toCurrency(19.99), equals('\$19.99'));
    });
  });
}
```

---

## 3. Widget Test Patterns

### 3.1 Basic Widget Test Structure

```dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('MyWidget', () {
    Widget createTestWidget({Widget? child}) {
      return MaterialApp(
        home: Scaffold(
          body: child ?? const MyWidget(),
        ),
      );
    }

    testWidgets('should render title text', (WidgetTester tester) async {
      await tester.pumpWidget(createTestWidget());
      expect(find.text('My Title'), findsOneWidget);
    });
  });
}
```

### 3.2 Testing with Dependency Injection (Provider)

```dart
Widget createTestWidget({
  required UserViewModel viewModel,
}) {
  return MaterialApp(
    home: ChangeNotifierProvider<UserViewModel>.value(
      value: viewModel,
      child: const UserListScreen(),
    ),
  );
}
```

### 3.3 Testing Different Widget States

```dart
testWidgets('should show loading spinner when isLoading is true',
    (tester) async {
  when(mockViewModel.isLoading).thenReturn(true);
  when(mockViewModel.users).thenReturn([]);
  when(mockViewModel.error).thenReturn(null);

  await tester.pumpWidget(createTestWidget(viewModel: mockViewModel));

  expect(find.byType(CircularProgressIndicator), findsOneWidget);
  expect(find.byType(ListView), findsNothing);
});

testWidgets('should show error message with retry button when error exists',
    (tester) async {
  when(mockViewModel.isLoading).thenReturn(false);
  when(mockViewModel.users).thenReturn([]);
  when(mockViewModel.error).thenReturn('Failed to load');

  await tester.pumpWidget(createTestWidget(viewModel: mockViewModel));
  await tester.pumpAndSettle();

  expect(find.text('Failed to load'), findsOneWidget);
  expect(find.byType(ElevatedButton), findsOneWidget); // Retry button
});

testWidgets('should show empty state when no users and no error',
    (tester) async {
  when(mockViewModel.isLoading).thenReturn(false);
  when(mockViewModel.users).thenReturn([]);
  when(mockViewModel.error).thenReturn(null);

  await tester.pumpWidget(createTestWidget(viewModel: mockViewModel));
  await tester.pumpAndSettle();

  expect(find.text('No users found'), findsOneWidget);
});

testWidgets('should show user list when users are loaded',
    (tester) async {
  when(mockViewModel.isLoading).thenReturn(false);
  when(mockViewModel.users).thenReturn([
    User(id: '1', name: 'Alice', email: 'alice@test.com'),
    User(id: '2', name: 'Bob', email: 'bob@test.com'),
  ]);
  when(mockViewModel.error).thenReturn(null);

  await tester.pumpWidget(createTestWidget(viewModel: mockViewModel));
  await tester.pumpAndSettle();

  expect(find.text('Alice'), findsOneWidget);
  expect(find.text('Bob'), findsOneWidget);
  expect(find.byType(ListTile), findsNWidgets(2));
});
```

### 3.4 Testing User Interactions

```dart
testWidgets('should call deleteUser when delete icon is tapped',
    (tester) async {
  // Arrange
  when(mockViewModel.isLoading).thenReturn(false);
  when(mockViewModel.users).thenReturn([
    User(id: '1', name: 'Alice', email: 'alice@test.com'),
  ]);
  when(mockViewModel.error).thenReturn(null);
  when(mockViewModel.deleteUser(any)).thenAnswer((_) async {});

  await tester.pumpWidget(createTestWidget(viewModel: mockViewModel));
  await tester.pumpAndSettle();

  // Act
  await tester.tap(find.byIcon(Icons.delete));
  await tester.pumpAndSettle();

  // Assert
  verify(mockViewModel.deleteUser('1')).called(1);
});

testWidgets('should submit form with entered text', (tester) async {
  // Arrange
  await tester.pumpWidget(createTestWidget());
  await tester.pumpAndSettle();

  // Act
  await tester.enterText(find.byType(TextField).first, 'Alice');
  await tester.enterText(find.byType(TextField).last, 'alice@test.com');
  await tester.tap(find.byType(ElevatedButton));
  await tester.pumpAndSettle();

  // Assert
  verify(mockViewModel.createUser(
    name: 'Alice',
    email: 'alice@test.com',
  )).called(1);
});

testWidgets('should scroll to load more items', (tester) async {
  // Arrange — set up a long list
  final manyUsers = List.generate(
    50,
    (i) => User(id: '$i', name: 'User $i', email: 'user$i@test.com'),
  );
  when(mockViewModel.users).thenReturn(manyUsers);
  // ...

  await tester.pumpWidget(createTestWidget(viewModel: mockViewModel));
  await tester.pumpAndSettle();

  // Act — scroll down
  await tester.drag(find.byType(ListView), const Offset(0, -500));
  await tester.pumpAndSettle();

  // Assert — later items now visible
  expect(find.text('User 10'), findsOneWidget);
});
```

### 3.5 Finding Widgets

```dart
// By type
find.byType(CircularProgressIndicator)
find.byType(ListTile)

// By text
find.text('Hello World')
find.textContaining('Hello') // partial match

// By key
find.byKey(const Key('user_list'))
find.byKey(const ValueKey('user_1'))

// By icon
find.byIcon(Icons.delete)
find.byIcon(Icons.refresh)

// By widget predicate
find.byWidgetPredicate(
  (widget) => widget is Text && widget.data?.startsWith('User') == true,
)

// By ancestor/descendant
find.descendant(
  of: find.byType(ListTile),
  matching: find.byType(Text),
)
find.ancestor(
  of: find.text('Alice'),
  matching: find.byType(ListTile),
)
```

### 3.6 Golden Tests (Visual Regression)

```dart
testWidgets('should match golden file for user card', (tester) async {
  await tester.pumpWidget(createTestWidget(
    child: UserCard(
      user: User(id: '1', name: 'Alice', email: 'alice@test.com'),
    ),
  ));
  await tester.pumpAndSettle();

  await expectLater(
    find.byType(UserCard),
    matchesGoldenFile('goldens/user_card.png'),
  );
});
```

To update golden files:
```bash
flutter test --update-goldens
```

---

## 4. Integration Test Patterns

### 4.1 Basic Integration Test

```dart
// integration_test/app_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:app/main.dart' as app;

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('end-to-end test', () {
    testWidgets('full user management flow', (tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Step 1: Verify home screen loads
      expect(find.text('Users'), findsOneWidget);

      // Step 2: Wait for data to load
      await tester.pumpAndSettle(const Duration(seconds: 5));

      // Step 3: Tap on add button
      await tester.tap(find.byIcon(Icons.add));
      await tester.pumpAndSettle();

      // Step 4: Fill form
      await tester.enterText(
        find.byKey(const Key('name_field')),
        'Test User',
      );
      await tester.enterText(
        find.byKey(const Key('email_field')),
        'test@example.com',
      );

      // Step 5: Submit
      await tester.tap(find.byKey(const Key('submit_button')));
      await tester.pumpAndSettle(const Duration(seconds: 3));

      // Step 6: Verify user appears in list
      expect(find.text('Test User'), findsOneWidget);
    });
  });
}
```

### 4.2 Integration Test with Mocked Backend

```dart
// integration_test/helpers/test_app.dart
Future<void> startTestApp({
  required MockApiClient mockApi,
}) async {
  // Override the service locator with mocked dependencies
  getIt.registerSingleton<ApiClient>(mockApi);
  
  runApp(const MyApp());
}
```

### 4.3 Navigation Flow Testing

```dart
testWidgets('should navigate from list to detail to edit', (tester) async {
  app.main();
  await tester.pumpAndSettle();

  // List screen
  expect(find.text('Users'), findsOneWidget);

  // Navigate to detail
  await tester.tap(find.text('Alice'));
  await tester.pumpAndSettle();
  expect(find.text('User Details'), findsOneWidget);
  expect(find.text('Alice'), findsOneWidget);

  // Navigate to edit
  await tester.tap(find.byIcon(Icons.edit));
  await tester.pumpAndSettle();
  expect(find.text('Edit User'), findsOneWidget);

  // Go back
  await tester.tap(find.byIcon(Icons.arrow_back));
  await tester.pumpAndSettle();
  expect(find.text('User Details'), findsOneWidget);
});
```

---

## 5. Mocking Strategy

### 5.1 Mockito vs Mocktail

| Feature | Mockito | Mocktail |
|---------|---------|----------|
| Code generation | Required (`build_runner`) | Not required |
| Null safety | Full support | Full support |
| Syntax | `when(mock.method()).thenReturn(value)` | Same |
| Setup complexity | Higher (annotations + build) | Lower (extend `Mock`) |
| Matchers | `any`, `argThat`, `captureAny` | Same, plus `any()` function |
| Recommendation | Large projects with many mocks | Smaller projects, faster iteration |

### 5.2 Mockito Setup

```dart
// In test file
@GenerateMocks([UserRepository, AuthService])
import 'my_test.mocks.dart';

// Generate mocks:
// flutter pub run build_runner build --delete-conflicting-outputs
```

### 5.3 Mocktail Setup

```dart
// No code generation needed
class MockUserRepository extends Mock implements UserRepository {}
class MockAuthService extends Mock implements AuthService {}

// Register fallback values for custom types
setUpAll(() {
  registerFallbackValue(User(id: '', name: '', email: ''));
});
```

### 5.4 Common Mock Patterns

#### Mocking HTTP Client

```dart
@GenerateMocks([http.Client])
import 'test.mocks.dart';

final mockClient = MockClient();
when(mockClient.get(any, headers: anyNamed('headers')))
    .thenAnswer((_) async => http.Response('{"data": []}', 200));
```

#### Mocking SharedPreferences

```dart
// Use the SharedPreferences test helper
SharedPreferences.setMockInitialValues({
  'auth_token': 'test_token_123',
  'user_id': '42',
  'onboarding_complete': true,
});
```

#### Mocking Platform Channels

```dart
const channel = MethodChannel('com.example/platform');
TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
    .setMockMethodCallHandler(channel, (MethodCall methodCall) async {
  if (methodCall.method == 'getBatteryLevel') {
    return 42;
  }
  return null;
});
```

#### Mocking Navigation

```dart
final mockNavigator = MockNavigatorObserver();

await tester.pumpWidget(MaterialApp(
  home: const MyScreen(),
  navigatorObservers: [mockNavigator],
));

// After navigation action
verify(mockNavigator.didPush(any, any)).called(1);
```

#### Mocking Streams

```dart
when(mockRepo.userStream())
    .thenAnswer((_) => Stream.fromIterable([
          User(id: '1', name: 'Alice'),
          User(id: '2', name: 'Bob'),
        ]));

// For StreamControllers in tests
final controller = StreamController<User>.broadcast();
when(mockRepo.userStream()).thenAnswer((_) => controller.stream);

// Emit values during test
controller.add(User(id: '1', name: 'Alice'));
await tester.pumpAndSettle();

// Clean up
controller.close();
```

---

## 6. Test File Organization

### 6.1 Standard Directory Structure

```
test/
├── features/                       # Feature-specific tests
│   ├── authentication/
│   │   ├── models/
│   │   │   └── auth_token_test.dart
│   │   ├── repositories/
│   │   │   └── auth_repository_test.dart
│   │   ├── viewmodels/
│   │   │   └── login_viewmodel_test.dart
│   │   └── views/
│   │       ├── login_screen_test.dart
│   │       └── register_screen_test.dart
│   └── users/
│       ├── models/
│       │   └── user_model_test.dart
│       ├── repositories/
│       │   └── user_repository_test.dart
│       ├── viewmodels/
│       │   └── user_list_viewmodel_test.dart
│       └── views/
│           ├── user_list_screen_test.dart
│           └── user_detail_screen_test.dart
├── core/                           # Shared/core module tests
│   ├── services/
│   │   ├── api_client_test.dart
│   │   └── storage_service_test.dart
│   └── utils/
│       ├── validators_test.dart
│       └── formatters_test.dart
├── helpers/                        # Test utilities
│   ├── test_helpers.dart           # Common test setup functions
│   ├── mock_data.dart              # Shared mock/fake data
│   ├── pump_app.dart               # Helper to pump app with providers
│   └── fakes.dart                  # Manual fake implementations
└── goldens/                        # Golden test images
    ├── user_card.png
    └── login_screen.png

integration_test/
├── helpers/
│   ├── test_app.dart               # Test app launcher
│   └── test_fixtures.dart          # Test data for integration tests
├── user_management_test.dart
└── authentication_flow_test.dart
```

### 6.2 Test Helpers File

```dart
// test/helpers/test_helpers.dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';

/// Wraps a widget in MaterialApp with all required providers.
Widget createTestableWidget({
  required Widget child,
  UserViewModel? userViewModel,
  AuthViewModel? authViewModel,
}) {
  return MaterialApp(
    home: MultiProvider(
      providers: [
        if (userViewModel != null)
          ChangeNotifierProvider<UserViewModel>.value(value: userViewModel),
        if (authViewModel != null)
          ChangeNotifierProvider<AuthViewModel>.value(value: authViewModel),
      ],
      child: Scaffold(body: child),
    ),
  );
}

/// Pumps a widget and settles animations with a timeout.
Future<void> pumpAndSettleWithTimeout(
  WidgetTester tester,
  Widget widget, {
  Duration timeout = const Duration(seconds: 10),
}) async {
  await tester.pumpWidget(widget);
  await tester.pumpAndSettle(timeout);
}
```

### 6.3 Mock Data File

```dart
// test/helpers/mock_data.dart
import 'package:app/features/users/models/user.dart';

class MockData {
  static final users = [
    User(id: '1', name: 'Alice Johnson', email: 'alice@example.com'),
    User(id: '2', name: 'Bob Smith', email: 'bob@example.com'),
    User(id: '3', name: 'Charlie Brown', email: 'charlie@example.com'),
  ];

  static final singleUser = users.first;

  static final emptyUserList = <User>[];

  static final userJson = {
    'id': '1',
    'name': 'Alice Johnson',
    'email': 'alice@example.com',
  };

  static final usersJsonList = users.map((u) => u.toJson()).toList();

  static const validEmail = 'test@example.com';
  static const invalidEmail = 'not-an-email';
  static const emptyString = '';
}
```

---

## 7. Test Execution Commands

### Running Tests

```bash
# Run all tests
flutter test

# Run all tests with verbose output
flutter test --reporter expanded

# Run tests in a specific file
flutter test test/features/users/viewmodels/user_list_viewmodel_test.dart

# Run tests in a specific directory
flutter test test/features/users/

# Run tests matching a name pattern
flutter test --name "should load users"

# Run tests with coverage
flutter test --coverage

# View coverage report (requires lcov)
genhtml coverage/lcov.info -o coverage/html
open coverage/html/index.html

# Run integration tests
flutter test integration_test/

# Run integration tests on a specific device
flutter test integration_test/ -d <device_id>

# Update golden files
flutter test --update-goldens
```

### CI/CD Test Commands

```bash
# Run with machine-readable output
flutter test --reporter json > test_results.json

# Run with fail-fast
flutter test --reporter expanded --fail-fast

# Run with concurrency control
flutter test --concurrency=4
```

---

## 8. Common Testing Patterns and Anti-Patterns

### ✅ DO

- Test behavior, not implementation
- Use descriptive test names that read as specifications
- Keep tests focused — one logical assertion per test
- Test edge cases and error paths
- Use `setUp`/`tearDown` for shared setup/cleanup
- Dispose of controllers, streams, and notifiers in `tearDown`
- Group related tests with `group()`

### ❌ DON'T

- Don't test Flutter framework internals
- Don't make assertions on private state — test through public API
- Don't write tests that depend on test execution order
- Don't test multiple unrelated behaviors in one test
- Don't use `sleep()` or hardcoded delays in tests — use `pumpAndSettle()`
- Don't skip failing tests without a tracking issue
- Don't test generated code (e.g., `.g.dart`, `.freezed.dart` files)
- Don't mock the class under test — only mock its dependencies
