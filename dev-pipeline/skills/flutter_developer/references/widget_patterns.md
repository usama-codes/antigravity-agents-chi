# Widget Patterns Reference

Flutter widget best practices and reusable patterns for the development team.

---

## Widget Decomposition Rules

### Rule 1 — 60-Line Limit on `build()`

If a `build()` method exceeds ~60 lines, split it into named private widgets.

```dart
// ❌ Bad: One giant build method
class ProductScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Products'),
        actions: [
          IconButton(icon: Icon(Icons.search), onPressed: () {}),
          IconButton(icon: Icon(Icons.filter_list), onPressed: () {}),
        ],
      ),
      body: Column(
        children: [
          // ... 80 more lines of nested widgets
        ],
      ),
    );
  }
}

// ✅ Good: Decomposed into named widgets
class ProductScreen extends StatelessWidget {
  const ProductScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: const _ProductAppBar(),
      body: const _ProductBody(),
    );
  }
}

class _ProductAppBar extends StatelessWidget implements PreferredSizeWidget {
  const _ProductAppBar();

  @override
  Widget build(BuildContext context) { ... }

  @override
  Size get preferredSize => const Size.fromHeight(kToolbarHeight);
}

class _ProductBody extends StatelessWidget {
  const _ProductBody();

  @override
  Widget build(BuildContext context) { ... }
}
```

### Rule 2 — StatelessWidget by Default

Use `StatelessWidget` unless the widget needs local state that:
- Is purely UI-related (animation controller, scroll position, focus node)
- Does not represent business data

```dart
// ✅ StatelessWidget — reads data from ViewModel
class ProductCard extends StatelessWidget {
  final Product product;
  const ProductCard({super.key, required this.product});
  // ...
}

// ✅ StatefulWidget — local animation state only
class AnimatedProductCard extends StatefulWidget {
  final Product product;
  const AnimatedProductCard({super.key, required this.product});

  @override
  State<AnimatedProductCard> createState() => _AnimatedProductCardState();
}

class _AnimatedProductCardState extends State<AnimatedProductCard>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  // Local animation state — not business data ✅
}
```

---

## Standard State Widget Patterns

Every list/data screen needs these three state widgets:

### Loading State — Skeleton UI

```dart
class _ProductListSkeleton extends StatelessWidget {
  const _ProductListSkeleton();

  @override
  Widget build(BuildContext context) {
    return ListView.separated(
      itemCount: 8,
      separatorBuilder: (_, __) => const SizedBox(height: 8),
      padding: const EdgeInsets.all(16),
      itemBuilder: (_, __) => const _ProductCardSkeleton(),
    );
  }
}

class _ProductCardSkeleton extends StatelessWidget {
  const _ProductCardSkeleton();

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Container(
      height: 80,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: theme.colorScheme.surfaceVariant,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          // Avatar placeholder
          Container(
            width: 48,
            height: 48,
            decoration: BoxDecoration(
              color: theme.colorScheme.outline.withOpacity(0.2),
              shape: BoxShape.circle,
            ),
          ),
          const SizedBox(width: 12),
          // Text placeholder
          Expanded(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  height: 14,
                  width: double.infinity,
                  color: theme.colorScheme.outline.withOpacity(0.2),
                ),
                const SizedBox(height: 8),
                Container(
                  height: 12,
                  width: 120,
                  color: theme.colorScheme.outline.withOpacity(0.2),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
```

### Error State

```dart
class ErrorStateWidget extends StatelessWidget {
  final String message;
  final String? actionLabel;
  final VoidCallback? onAction;

  const ErrorStateWidget({
    super.key,
    required this.message,
    this.actionLabel = 'Try Again',
    this.onAction,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Center(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              Icons.error_outline_rounded,
              size: 64,
              color: theme.colorScheme.error,
            ),
            const SizedBox(height: 16),
            Text(
              message,
              style: theme.textTheme.bodyLarge,
              textAlign: TextAlign.center,
            ),
            if (onAction != null) ...[
              const SizedBox(height: 24),
              FilledButton(
                onPressed: onAction,
                child: Text(actionLabel!),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
```

### Empty State

```dart
class EmptyStateWidget extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;
  final String? actionLabel;
  final VoidCallback? onAction;

  const EmptyStateWidget({
    super.key,
    required this.icon,
    required this.title,
    required this.subtitle,
    this.actionLabel,
    this.onAction,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Center(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 80, color: theme.colorScheme.outlineVariant),
            const SizedBox(height: 16),
            Text(
              title,
              style: theme.textTheme.titleMedium,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 8),
            Text(
              subtitle,
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
              textAlign: TextAlign.center,
            ),
            if (onAction != null && actionLabel != null) ...[
              const SizedBox(height: 24),
              FilledButton(
                onPressed: onAction,
                child: Text(actionLabel!),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
```

---

## List Patterns

### Basic ListView with States

```dart
class ProductListView extends StatelessWidget {
  const ProductListView({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer<ProductListViewModel>(
      builder: (context, vm, _) => switch (vm) {
        // Use pattern matching on ViewModel state
        _ when vm.isLoading && vm.products.isEmpty =>
          const _ProductListSkeleton(),
        _ when vm.hasError && vm.products.isEmpty =>
          ErrorStateWidget(
            message: vm.errorMessage!,
            onAction: () => vm.loadProducts(),
          ),
        _ when vm.isEmpty =>
          const EmptyStateWidget(
            icon: Icons.inventory_2_outlined,
            title: 'No products yet',
            subtitle: 'Products you create will appear here.',
          ),
        _ => _ProductListBody(viewModel: vm),
      },
    );
  }
}
```

### Infinite Scroll List

```dart
class _ProductListBody extends StatefulWidget {
  final ProductListViewModel viewModel;
  const _ProductListBody({required this.viewModel});

  @override
  State<_ProductListBody> createState() => _ProductListBodyState();
}

class _ProductListBodyState extends State<_ProductListBody> {
  final _scrollController = ScrollController();

  @override
  void initState() {
    super.initState();
    _scrollController.addListener(_onScroll);
  }

  void _onScroll() {
    if (_scrollController.position.pixels >=
        _scrollController.position.maxScrollExtent - 200) {
      widget.viewModel.loadProducts(); // Load next page
    }
  }

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final vm = widget.viewModel;
    return RefreshIndicator(
      onRefresh: () => vm.loadProducts(refresh: true),
      child: ListView.separated(
        controller: _scrollController,
        padding: const EdgeInsets.all(16),
        itemCount: vm.products.length + (vm.hasMorePages ? 1 : 0),
        separatorBuilder: (_, __) => const SizedBox(height: 8),
        itemBuilder: (context, index) {
          if (index == vm.products.length) {
            return const Padding(
              padding: EdgeInsets.all(16),
              child: Center(child: CircularProgressIndicator()),
            );
          }
          return ProductCard(product: vm.products[index]);
        },
      ),
    );
  }
}
```

---

## Form Patterns

### Standard Form with Validation

```dart
class CreateProductForm extends StatelessWidget {
  const CreateProductForm({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer<CreateProductViewModel>(
      builder: (context, vm, _) {
        return Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Name field
            TextField(
              onChanged: vm.onNameChanged,
              decoration: InputDecoration(
                labelText: 'Product Name',
                errorText: vm.nameError,
                filled: true,
              ),
              textInputAction: TextInputAction.next,
            ),
            const SizedBox(height: 16),

            // Price field
            TextField(
              onChanged: vm.onPriceChanged,
              decoration: InputDecoration(
                labelText: 'Price',
                prefixText: '\$',
                errorText: vm.priceError,
                filled: true,
              ),
              keyboardType: const TextInputType.numberWithOptions(decimal: true),
              textInputAction: TextInputAction.done,
              onSubmitted: (_) => vm.submit(),
            ),
            const SizedBox(height: 24),

            // Submit button
            FilledButton(
              onPressed: vm.isValid && !vm.isSubmitting ? vm.submit : null,
              child: vm.isSubmitting
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: Colors.white,
                      ),
                    )
                  : const Text('Create Product'),
            ),

            // Error message
            if (vm.hasError)
              Padding(
                padding: const EdgeInsets.only(top: 12),
                child: Text(
                  vm.errorMessage!,
                  style: TextStyle(color: Theme.of(context).colorScheme.error),
                  textAlign: TextAlign.center,
                ),
              ),
          ],
        );
      },
    );
  }
}
```

---

## Card Patterns

### Standard Card

```dart
class ProductCard extends StatelessWidget {
  final Product product;
  final VoidCallback? onTap;
  final VoidCallback? onDelete;

  const ProductCard({
    super.key,
    required this.product,
    this.onTap,
    this.onDelete,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Card(
      clipBehavior: Clip.antiAlias, // Required for InkWell splash on cards
      child: InkWell(
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              // Leading
              ClipRRect(
                borderRadius: BorderRadius.circular(8),
                child: product.imageUrl != null
                    ? Image.network(
                        product.imageUrl!,
                        width: 56,
                        height: 56,
                        fit: BoxFit.cover,
                        errorBuilder: (_, __, ___) => const _ProductPlaceholderImage(),
                      )
                    : const _ProductPlaceholderImage(),
              ),
              const SizedBox(width: 12),

              // Content
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      product.name,
                      style: theme.textTheme.titleMedium,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '\$${product.price.toStringAsFixed(2)}',
                      style: theme.textTheme.bodyMedium?.copyWith(
                        color: theme.colorScheme.primary,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
              ),

              // Actions
              if (onDelete != null)
                IconButton(
                  icon: const Icon(Icons.delete_outline),
                  onPressed: onDelete,
                  tooltip: 'Delete product',
                  style: IconButton.styleFrom(
                    foregroundColor: theme.colorScheme.error,
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
}

class _ProductPlaceholderImage extends StatelessWidget {
  const _ProductPlaceholderImage();

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 56,
      height: 56,
      color: Theme.of(context).colorScheme.surfaceVariant,
      child: Icon(
        Icons.inventory_2_outlined,
        color: Theme.of(context).colorScheme.outlineVariant,
      ),
    );
  }
}
```

---

## Dialog and Bottom Sheet Patterns

### Confirmation Dialog

```dart
Future<bool?> showDeleteConfirmationDialog(BuildContext context) {
  return showDialog<bool>(
    context: context,
    builder: (context) => AlertDialog(
      title: const Text('Delete Product?'),
      content: const Text(
        'This action cannot be undone. The product will be permanently deleted.',
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(false),
          child: const Text('Cancel'),
        ),
        FilledButton(
          style: FilledButton.styleFrom(
            backgroundColor: Theme.of(context).colorScheme.error,
          ),
          onPressed: () => Navigator.of(context).pop(true),
          child: const Text('Delete'),
        ),
      ],
    ),
  );
}
```

### Modal Bottom Sheet

```dart
Future<void> showProductFilterSheet(BuildContext context) {
  return showModalBottomSheet(
    context: context,
    isScrollControlled: true,
    useSafeArea: true,
    shape: const RoundedRectangleBorder(
      borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
    ),
    builder: (context) => DraggableScrollableSheet(
      expand: false,
      initialChildSize: 0.5,
      maxChildSize: 0.9,
      builder: (context, scrollController) => const ProductFilterSheet(),
    ),
  );
}
```

---

## Accessibility Standards

```dart
// ✅ Add Semantics to icons and images that convey meaning
IconButton(
  icon: const Icon(Icons.delete),
  tooltip: 'Delete product',        // ✅ Required for icon-only buttons
  onPressed: onDelete,
  // Tooltip provides semantic label automatically
),

// ✅ For decorative images, use excludeFromSemantics
Image.network(
  imageUrl,
  excludeFromSemantics: true,       // Decorative, not informative
),

// ✅ For informative images, provide a label
Semantics(
  label: 'Product thumbnail for ${product.name}',
  child: Image.network(imageUrl),
),

// ✅ Ensure minimum touch target size
SizedBox(
  width: 48,
  height: 48,
  child: IconButton(
    iconSize: 20,                   // Visual size can be smaller
    onPressed: onPressed,
    icon: const Icon(Icons.close),
  ),
),
```

---

## Performance Checklist

- [ ] `const` constructor on every `StatelessWidget` subclass
- [ ] `const` on every widget that doesn't use dynamic data
- [ ] `Key` provided on list items when list can reorder/add/remove
- [ ] `ListView.builder` used for lists (never `ListView` with `children`)
- [ ] Images use `cacheWidth`/`cacheHeight` to avoid memory issues
- [ ] `Consumer` scope is as narrow as possible (wrap only what needs to rebuild)
- [ ] `select()` used when only one field from ViewModel is needed
