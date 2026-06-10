# Material Design 3 & Flutter Platform Guidelines

This reference documents key UI patterns, component behaviors, and platform conventions the Designer agent must follow when creating designs for Flutter apps. All designs must comply with these guidelines.

---

## 1. App Bar Patterns

### 1.1 Top App Bar Types

| Type | Height | When to Use | Behavior on Scroll |
|---|---|---|---|
| **Center-aligned** | 64dp | Simple screens with short titles | Stays fixed or scrolls away |
| **Small** | 64dp | Most screens, left-aligned title | Stays fixed or scrolls away |
| **Medium** | 112dp (expanded) → 64dp (collapsed) | Screens where context/title emphasis is important | Collapses on scroll, title moves from large to small |
| **Large** | 152dp (expanded) → 64dp (collapsed) | Hero screens, top-level destinations | Collapses on scroll, title moves from large to small |

### 1.2 App Bar Content Rules

| Element | Position | Requirements |
|---|---|---|
| Navigation icon (back/menu) | Leading | 48dp touch target, 24dp icon, 4dp from left edge |
| Title | Center or left-aligned | Title Large typography, single line, truncate with ellipsis |
| Action icons | Trailing | Max 3 icons, 48dp touch target each, 4dp spacing |
| Overflow menu | Trailing (last) | Use when > 3 actions, 48dp touch target |

### 1.3 App Bar Behavior Rules
- **Top-level destinations** (bottom nav screens): No back button, show app name or screen title
- **Detail/child screens**: Show back arrow (← on both platforms in Flutter)
- **Scrollable content**: Use `SliverAppBar` with `floating: true` for quick return, or `pinned: true` for persistent
- **Search**: Use `SearchBar` widget (M3 pattern) — full-width in app bar area, rounded rectangle, elevation 1
- **Color**: Surface color by default. Gets `surfaceTint` overlay on scroll (elevation change)

---

## 2. Navigation Patterns

### 2.1 Bottom Navigation Bar

| Property | Value |
|---|---|
| Use when | 3-5 top-level destinations |
| Height | 80dp |
| Icon | 24dp, centered above label |
| Label | Label Medium, always visible |
| Active indicator | Pill shape behind icon (64×32dp), `secondaryContainer` color |
| Active icon | Filled variant, `onSecondaryContainer` |
| Inactive icon | Outlined variant, `onSurfaceVariant` |
| Active label | `onSurface` |
| Inactive label | `onSurfaceVariant` |
| Max items | 5 |
| Min items | 3 |
| Badge | Small dot or number badge, `error` color |

**Rules**:
- Each destination should have its own navigation stack (preserve scroll position)
- Tapping the already-active destination scrolls its content to top
- Navigation bar must be visible on all top-level screens
- Hide on scroll only if explicitly designed (generally keep visible)

### 2.2 Navigation Rail (Tablet/Desktop)

| Property | Value |
|---|---|
| Use when | Screen width ≥ 600dp AND ≤ 1240dp |
| Width | 80dp (icons only) or 360dp (extended with labels) |
| Position | Left side of screen |
| Alignment | Top-aligned (with optional FAB above destinations) |

### 2.3 Navigation Drawer

| Property | Value |
|---|---|
| Use when | > 5 destinations, or complex hierarchy |
| Width | 360dp (standard), edge-to-edge on phones |
| Header | Optional, 64dp+ height for branding/user info |
| Items | 56dp height each, 12dp corner radius on active indicator |
| Sections | Separated by 1dp divider with 16dp vertical padding |
| Scrim | 32% opacity black behind modal drawer |

**Types**:
- **Modal Drawer**: Overlays content, has scrim, dismiss on outside tap. Use on phones.
- **Standard Drawer**: Side-by-side with content, persistent. Use on tablets/desktop.

### 2.4 Tabs

| Property | Value |
|---|---|
| Use when | 2-5 categories within a single screen |
| Height | 48dp |
| Indicator | 3dp bottom bar, `primary` color, animated slide between tabs |
| Label | Title Small, `primary` when active, `onSurfaceVariant` when inactive |
| Icon (optional) | 24dp, above label |
| Scrollable | Use when labels are long or > 4 tabs |
| Fixed | Use when ≤ 4 tabs with short labels |

**Rules**:
- Swiping between tab content is expected on mobile
- Tab content should lazy-load if expensive
- Preserve tab content state when switching (don't reload)

---

## 3. Card Patterns

### 3.1 Card Types

| Type | Elevation | Border | Background | Use Case |
|---|---|---|---|---|
| **Elevated** | Level 1 | None | `surface` + tint | Default card, emphasize content |
| **Filled** | Level 0 | None | `surfaceVariant` | Groups of related content, less emphasis |
| **Outlined** | Level 0 | 1dp `outline` | `surface` | Distinct boundaries, forms, settings |

### 3.2 Card Content Layout

```
Card (12dp radius, 16dp padding)
├── Header Row (optional)
│   ├── Leading: Avatar (40dp) or Icon (24dp)
│   ├── Column
│   │   ├── Title: Title Medium
│   │   └── Subtitle: Body Medium, onSurfaceVariant
│   └── Trailing: IconButton (more/overflow)
├── Media (optional) — full width, no padding
├── Body — Body Medium, 16dp top padding if after media
├── Actions Row — 8dp top padding
│   ├── TextButton (start-aligned)
│   └── TextButton / IconButton (end-aligned)
```

### 3.3 Card Interaction Rules
- Cards can be tappable (entire card is a touch target) — show ripple effect
- Cards can contain interactive elements (buttons, icons) — these get their own touch targets
- Don't combine both: either the whole card is tappable OR individual elements are, not both
- On long press: show context menu if applicable
- Card height: Use intrinsic height — no fixed heights unless in a grid layout

---

## 4. Form Input Patterns

### 4.1 Text Field Types

| Type | Visual | Use Case |
|---|---|---|
| **Filled** | Filled background (`surfaceVariant`), bottom border | Default — use in most forms |
| **Outlined** | Transparent background, full border | High emphasis forms, settings screens |

### 4.2 Text Field Anatomy

```
[Leading Icon (optional)] [Label / Value] [Trailing Icon (optional)]
[Supporting Text / Error Text]
```

| Element | Position | Typography | Color |
|---|---|---|---|
| Label (resting) | Inside field, vertically centered | Body Large | `onSurfaceVariant` |
| Label (floating) | Above field content | Body Small | `primary` (focused) / `onSurfaceVariant` (unfocused) |
| Input text | Inside field | Body Large | `onSurface` |
| Supporting text | Below field | Body Small | `onSurfaceVariant` |
| Error text | Below field | Body Small | `error` |
| Character counter | Below field, end-aligned | Body Small | `onSurfaceVariant` |

### 4.3 Text Field States

| State | Bottom Border / Outline | Label Color | Fill Color (filled variant) |
|---|---|---|---|
| Enabled (unfocused) | 1dp `onSurface` | `onSurfaceVariant` | `surfaceVariant` |
| Focused | 2dp `primary` | `primary` | `surfaceVariant` |
| Error | 2dp `error` | `error` | `surfaceVariant` |
| Error + Focused | 2dp `error` | `error` | `surfaceVariant` |
| Disabled | 1dp `onSurface` at 12% | `onSurface` at 38% | `onSurface` at 4% |
| Hovered | 1dp `onSurface` | `onSurfaceVariant` | `surfaceVariant` (hover overlay 8%) |

### 4.4 Form Layout Rules
- **Vertical spacing between fields**: 16dp
- **Label alignment**: Left-aligned (LTR locales)
- **Error text**: Appears instantly on blur/submit, disappears on valid input
- **Required indicator**: Red asterisk (*) after label text
- **Form sections**: Separate with 24dp spacing and optional section headers
- **Submit button**: Full-width at bottom or in app bar action slot
- **Keyboard**: Show appropriate keyboard type (`TextInputType`) for each field
- **Auto-fill**: Support platform auto-fill where applicable
- **Focus order**: Top-to-bottom, left-to-right, matching visual order

---

## 5. Dialog Patterns

### 5.1 Basic Dialog

```
Dialog (28dp radius, 24dp padding, elevation Level 5)
├── Icon (optional) — 24dp, centered, primary color
├── Title — Headline Small, onSurface, centered or start-aligned
│   (16dp below icon if present)
├── Body — Body Medium, onSurfaceVariant
│   (16dp below title)
├── Actions Row — end-aligned
│   (24dp above bottom edge)
│   ├── TextButton (dismiss: "Cancel")
│   └── TextButton or FilledButton (confirm: "OK" / "Delete" / etc.)
```

### 5.2 Dialog Rules
- **Max width**: 560dp
- **Min width**: 280dp
- **Dismissible**: Tapping outside or pressing back dismisses (unless it's a mandatory dialog)
- **Scroll**: If content overflows, body area becomes scrollable; title and actions remain fixed
- **Destructive actions**: Use `error` color for destructive action buttons
- **Stacking buttons**: If button text is too long, stack vertically (confirm on top)
- **Never nest dialogs**: Do not open a dialog from another dialog

### 5.3 Full-Screen Dialog
Use for complex inputs (multi-field forms, editors):
- Takes entire screen
- App bar with close (X) icon on leading, save action on trailing
- No scrim needed
- Animate with full-screen vertical slide or container transform

---

## 6. Bottom Sheet Patterns

### 6.1 Standard (Non-Modal) Bottom Sheet

| Property | Value |
|---|---|
| Corner Radius (top) | 28dp |
| Drag Handle | 32×4dp, centered, `onSurfaceVariant` at 40%, 22dp from top |
| Background | `surfaceContainerLow` |
| Elevation | Level 1 |
| Interaction | Draggable up/down, content beneath is interactive |

### 6.2 Modal Bottom Sheet

| Property | Value |
|---|---|
| Corner Radius (top) | 28dp |
| Drag Handle | 32×4dp, centered |
| Background | `surfaceContainerLow` |
| Elevation | Level 1 |
| Scrim | 32% opacity black |
| Dismiss | Drag down, tap scrim, or back gesture |
| Max Height | 90% of screen height |

### 6.3 Bottom Sheet Content Patterns
- **Action sheets**: List of actions with icons, each item 56dp height
- **Pickers**: Date picker, time picker, color picker
- **Filters**: Filter/sort options with chips or checkboxes
- **Details**: Additional information for a selected item
- **Mini forms**: 1-3 field forms (more fields → use full-screen dialog)

---

## 7. Floating Action Button (FAB)

### 7.1 Placement Rules
- **Default position**: Bottom-right corner, 16dp from edges
- **With bottom nav**: Center-aligned or end-aligned, 16dp above bottom nav
- **Only one FAB per screen**: Multiple FABs create confusion
- **Primary action only**: FAB represents the single most important action on the screen
- **Not every screen needs a FAB**: Only use when there's a clear primary creation/composition action

### 7.2 FAB Behavior
- **Hide on scroll down** (optional): Animate out with scale/fade, return on scroll up
- **Extended FAB**: Use when the action needs a text label for clarity; collapses to standard on scroll
- **No FAB on detail/editing screens**: FAB is for creation/composition, not editing
- **Mini FAB**: Use only in compact UIs or as a secondary action alongside a standard FAB

### 7.3 FAB Sizing

| Variant | Size | Icon | Use |
|---|---|---|---|
| Small | 40dp | 24dp | Compact UIs, secondary FAB |
| Standard | 56dp | 24dp | Default — most screens |
| Large | 96dp | 36dp | High-emphasis primary action |
| Extended | 56dp height | 24dp + text | When icon alone is ambiguous |

---

## 8. Touch Target Requirements

### 8.1 Minimum Sizes

| Element | Minimum Touch Target | Visual Size Can Be Smaller |
|---|---|---|
| Buttons (all types) | 48 × 48dp | Yes — add invisible padding |
| Icon buttons | 48 × 48dp | Icon can be 24dp, target is 48dp |
| List items | 48dp height minimum | — |
| Checkboxes | 48 × 48dp | Visual checkbox can be 18dp |
| Radio buttons | 48 × 48dp | Visual radio can be 20dp |
| Switches | 48dp height | Visual switch is smaller |
| Chips | 32dp height (visual), 48dp target | Add vertical padding for target |
| Text links | 48dp height target zone | — |

### 8.2 Spacing Between Touch Targets
- **Minimum spacing**: 8dp between adjacent touch targets
- **Recommended spacing**: 16dp for important distinct actions
- **Dense layouts** (lists, grids): Targets can be adjacent (0dp gap) if they have clear visual boundaries

---

## 9. Safe Area Handling

### 9.1 System UI Areas

| Area | Handling |
|---|---|
| **Status bar** (top) | Content must not overlap. Use `SafeArea` or `MediaQuery.of(context).padding.top` |
| **Navigation bar** (bottom) | Content must not overlap. Use `SafeArea` or `MediaQuery.of(context).padding.bottom` |
| **Notch / Dynamic Island** (top) | `SafeArea` handles this automatically |
| **Home indicator** (bottom, iOS) | `SafeArea` handles this. Bottom sheets and navigation bars should account for this |
| **Keyboard** | Use `MediaQuery.of(context).viewInsets.bottom` to detect keyboard and adjust layout |

### 9.2 SafeArea Usage Rules

| Scenario | Use SafeArea? |
|---|---|
| Screen with scrollable content | Yes — wrap the body, but NOT the Scaffold |
| Screen with bottom navigation | Bottom nav handles its own safe area |
| Screen with app bar | App bar handles top safe area |
| Screen with FAB | FAB positioning handles safe area |
| Full-screen images/media | Consider: SafeArea for controls, but media can go edge-to-edge |
| Bottom sheets | Add bottom padding equal to `MediaQuery.of(context).padding.bottom` |
| Dialogs | Dialogs are centered; safe area is usually not needed |

### 9.3 Edge-to-Edge Design
Flutter apps should use edge-to-edge design where the content extends behind system bars:
- `SystemChrome.setEnabledSystemUIMode(SystemUiMode.edgeToEdge)` on Android
- System bar colors should be transparent or match app background
- Use `AnnotatedRegion<SystemUiOverlayStyle>` to control status bar icon brightness

---

## 10. Platform-Specific Adaptations

### 10.1 Android vs iOS Differences in Flutter

| Aspect | Android (Material) | iOS (Cupertino) | Flutter Recommendation |
|---|---|---|---|
| **Back navigation** | System back button/gesture | Swipe from left edge | Use `Navigator` + `WillPopScope`. Flutter handles both. |
| **Scroll physics** | `ClampingScrollPhysics` | `BouncingScrollPhysics` | Use platform default (`ScrollPhysics()`) |
| **Page transitions** | Fade through / shared axis | Slide from right | Use `MaterialPageRoute` (adapts per platform) or `CupertinoPageRoute` |
| **Dialogs** | Material dialogs (center) | Cupertino alerts (center) | Use `showDialog` with Material. Consider `showCupertinoDialog` for iOS-native feel. |
| **Date picker** | Material date picker (calendar) | Cupertino date picker (scroll wheel) | Use `showDatePicker` (Material). Consider `CupertinoDatePicker` for iOS. |
| **Bottom sheets** | Material bottom sheets | iOS action sheets | Use `showModalBottomSheet`. Consider `CupertinoActionSheet` on iOS. |
| **Switches** | Material Switch | Cupertino Switch | Use `Switch.adaptive()` |
| **Text selection** | Material handles | iOS magnifying glass | Flutter handles automatically |
| **Haptics** | Basic vibration | Taptic Engine feedback | Use `HapticFeedback` class |

### 10.2 Adaptive Widget Strategy

For the **best cross-platform experience**, use this strategy:

1. **Always Material**: App Bar, Bottom Navigation, Cards, FABs, Chips, Snackbars
2. **Consider Adaptive**: Switches (`Switch.adaptive`), Sliders, Text Fields
3. **Platform-Specific**: Date/Time Pickers, Dialogs (for native feel — optional)
4. **Never Mix**: Don't use Cupertino widgets next to Material widgets on the same screen

### 10.3 Platform-Specific Design Considerations

#### Android-Specific
- Material You / Dynamic Color: Consider supporting `DynamicColorPlugin` for Android 12+
- Predictive back gesture (Android 14+): Ensure `PopScope` is used correctly
- Edge-to-edge: Use `SystemChrome.setEnabledSystemUIMode(SystemUiMode.edgeToEdge)`
- Adaptive icons for launcher

#### iOS-Specific
- Large title navigation bar pattern (optional — using Cupertino)
- Swipe-to-go-back is expected on all screens
- Pull-to-refresh uses Cupertino-style indicator
- Safe area for Dynamic Island and home indicator
- No back button text (Flutter default) — this is fine, Material-style back arrow works on iOS

---

## 11. Loading & Progress Patterns

### 11.1 Loading Indicators

| Type | Use When | Widget |
|---|---|---|
| **Circular indeterminate** | Unknown duration, small area | `CircularProgressIndicator` |
| **Linear indeterminate** | Unknown duration, full-width area | `LinearProgressIndicator` |
| **Circular determinate** | Known progress, small area | `CircularProgressIndicator(value: 0.7)` |
| **Linear determinate** | Known progress, full-width area | `LinearProgressIndicator(value: 0.7)` |
| **Skeleton / Shimmer** | Page loading, preserving layout | Custom shimmer widgets matching content shape |
| **Pull-to-refresh** | Refreshing list content | `RefreshIndicator` |

### 11.2 Shimmer Loading Rules
- Shimmer shapes must match the actual content layout (rectangles for text, circles for avatars, etc.)
- Use `shimmerBase` and `shimmerHighlight` colors from design system
- Animation: Left-to-right gradient sweep, 1.5s duration, infinite repeat
- Show shimmer for minimum 300ms (avoid flash of loading state)
- Transition from shimmer to content with a 200ms cross-fade

### 11.3 Button Loading States
- Replace button text with a `CircularProgressIndicator` (same color as button text, 24dp diameter)
- Disable the button during loading
- Preserve button width to prevent layout shift
- Show loading for minimum 300ms (even if request is faster)

---

## 12. Empty States

### 12.1 Empty State Anatomy

```
Center(
  Column(mainAxisSize: min)
  ├── Illustration or Icon (48-120dp)
  │   — Use outlined Material icon or custom illustration
  │   — Color: onSurfaceVariant or primary at low opacity
  ├── SizedBox(height: 16dp)
  ├── Title — Title Medium, onSurface, center-aligned
  │   — Short, specific: "No messages yet" not "Nothing here"
  ├── SizedBox(height: 8dp)
  ├── Description — Body Medium, onSurfaceVariant, center-aligned
  │   — Explain why empty and suggest action
  ├── SizedBox(height: 24dp)
  └── Action Button (optional) — FilledButton or FilledTonalButton
      — Primary action to resolve empty state: "Compose message"
)
```

### 12.2 Empty State Rules
- Always provide context about WHY it's empty
- Always suggest an action to resolve the empty state
- Use friendly, encouraging tone (not error-like)
- Center vertically in available space
- Use illustration or large icon, not just text
- Different empty states for: first-time empty, search-no-results, filtered-no-results, error-empty

---

## 13. Error States

### 13.1 Error Display Patterns

| Context | Pattern | Duration |
|---|---|---|
| **Form field error** | Inline error text below field | Persistent until fixed |
| **Network/API error** | Full-screen error with retry | Persistent until retry |
| **Submission error** | Snackbar with action | 4-10 seconds |
| **Background sync error** | Banner at top of screen | Until dismissed |
| **Critical error** | Dialog with explanation | Until dismissed |

### 13.2 Error Screen Anatomy

```
Center(
  Column(mainAxisSize: min)
  ├── Icon — error_outline, 48dp, error color
  ├── SizedBox(height: 16dp)
  ├── Title — Title Medium, onSurface
  │   — Specific: "Couldn't load profile" not "Error"
  ├── SizedBox(height: 8dp)
  ├── Description — Body Medium, onSurfaceVariant
  │   — User-friendly: "Check your internet connection and try again"
  │   — NEVER show raw error codes/stack traces to users
  ├── SizedBox(height: 24dp)
  └── FilledButton("Try Again")
)
```

### 13.3 Error Message Rules
- **Never** show technical error messages to users (no "500 Internal Server Error")
- **Always** suggest what the user can do to resolve it
- **Always** provide a retry action for retryable errors
- **Preserve user data** on error (don't clear form fields on submission error)
- **Log detailed errors** for debugging (but show friendly messages to users)

---

## 14. Responsive Design Breakpoints

### 14.1 Window Size Classes (Material Design 3)

| Class | Width Range | Layout | Navigation |
|---|---|---|---|
| **Compact** | < 600dp | Single pane | Bottom navigation |
| **Medium** | 600-839dp | Single pane or list-detail | Navigation rail |
| **Expanded** | ≥ 840dp | List-detail or multi-pane | Navigation rail or drawer |

### 14.2 Flutter Implementation

```dart
// Use LayoutBuilder or MediaQuery
if (constraints.maxWidth < 600) {
  // Compact: phone layout
} else if (constraints.maxWidth < 840) {
  // Medium: tablet layout
} else {
  // Expanded: desktop/large tablet layout
}
```

### 14.3 Responsive Rules
- **Phase 1 (Flutter-only)**: Design primarily for Compact (phone)
- Content max-width on larger screens: 560dp for forms, 840dp for content
- Center content horizontally on larger screens
- Use `LayoutBuilder` not `MediaQuery.of(context).size` for responsive layouts (respects parent constraints)
- Test at: 360dp (small phone), 390dp (standard phone), 428dp (large phone), 768dp (tablet portrait)
