# Design System Template

This document is the **template** the Designer agent uses to define a project's design system. When designing for a feature, the agent fills this out and saves the result to `pipeline_output/design/design_system.md`.

---

## Colour Palette

### Philosophy
Choose a harmonious, modern colour palette. Avoid generic primaries (plain red #FF0000, blue #0000FF). Use HSL-based selections with intentional saturation and lightness.

### Light Mode

| Token | Hex | HSL | Usage |
|-------|-----|-----|-------|
| `primary` | #XXXX | hsl(X, X%, X%) | Brand primary, key actions, active states |
| `onPrimary` | #XXXX | hsl(X, X%, X%) | Text/icons on primary colour |
| `primaryContainer` | #XXXX | hsl(X, X%, X%) | Lower emphasis primary surface |
| `onPrimaryContainer` | #XXXX | hsl(X, X%, X%) | Text/icons on primaryContainer |
| `secondary` | #XXXX | hsl(X, X%, X%) | Secondary actions, complementary accents |
| `onSecondary` | #XXXX | hsl(X, X%, X%) | Text/icons on secondary |
| `secondaryContainer` | #XXXX | hsl(X, X%, X%) | Secondary surface |
| `onSecondaryContainer` | #XXXX | hsl(X, X%, X%) | Text on secondaryContainer |
| `tertiary` | #XXXX | hsl(X, X%, X%) | Tertiary accents, highlights |
| `onTertiary` | #XXXX | hsl(X, X%, X%) | Text/icons on tertiary |
| `tertiaryContainer` | #XXXX | hsl(X, X%, X%) | Tertiary surface |
| `onTertiaryContainer` | #XXXX | hsl(X, X%, X%) | Text on tertiaryContainer |
| `error` | #B00020 | hsl(350, 100%, 35%) | Error states, destructive actions |
| `onError` | #FFFFFF | hsl(0, 0%, 100%) | Text on error |
| `errorContainer` | #FFDAD6 | hsl(4, 100%, 92%) | Error container surface |
| `onErrorContainer` | #410002 | hsl(358, 100%, 13%) | Text on errorContainer |
| `surface` | #XXXX | hsl(X, X%, X%) | Card backgrounds, sheet surfaces |
| `onSurface` | #XXXX | hsl(X, X%, X%) | Primary text on surfaces |
| `surfaceVariant` | #XXXX | hsl(X, X%, X%) | Alternative surface colour |
| `onSurfaceVariant` | #XXXX | hsl(X, X%, X%) | Secondary text on surfaces |
| `outline` | #XXXX | hsl(X, X%, X%) | Borders, dividers |
| `outlineVariant` | #XXXX | hsl(X, X%, X%) | Subtle borders |
| `background` | #XXXX | hsl(X, X%, X%) | Page/screen background |
| `onBackground` | #XXXX | hsl(X, X%, X%) | Text on background |
| `inverseSurface` | #XXXX | hsl(X, X%, X%) | Snackbar, tooltip backgrounds |
| `onInverseSurface` | #XXXX | hsl(X, X%, X%) | Text on inverseSurface |
| `inversePrimary` | #XXXX | hsl(X, X%, X%) | Primary in dark contexts |
| `shadow` | #000000 | hsl(0, 0%, 0%) | Drop shadows |
| `scrim` | #000000 | hsl(0, 0%, 0%) | Modal overlay scrim |

### Dark Mode

| Token | Hex | Notes |
|-------|-----|-------|
| `primary` (dark) | #XXXX | Lightened primary for dark surfaces |
| `onPrimary` (dark) | #XXXX | |
| `primaryContainer` (dark) | #XXXX | |
| `onPrimaryContainer` (dark) | #XXXX | |
| `surface` (dark) | #XXXX | Dark surface (e.g., #1C1B1F) |
| `background` (dark) | #XXXX | Dark background |
| *(repeat all tokens)* | | |

---

## Typography Scale

Font family: **[Choose from Google Fonts — e.g., Inter, Outfit, DM Sans]**

Import in Flutter:
```dart
// pubspec.yaml
fonts:
  - family: [FontName]
    fonts:
      - asset: fonts/[FontName]-Regular.ttf
      - asset: fonts/[FontName]-Medium.ttf
        weight: 500
      - asset: fonts/[FontName]-SemiBold.ttf
        weight: 600
      - asset: fonts/[FontName]-Bold.ttf
        weight: 700
```

| Style | Font Size | Weight | Line Height | Letter Spacing | Usage |
|-------|-----------|--------|-------------|----------------|-------|
| `displayLarge` | 57sp | 400 (Regular) | 64sp | -0.25 | Hero text, splash screens |
| `displayMedium` | 45sp | 400 | 52sp | 0 | Large headings |
| `displaySmall` | 36sp | 400 | 44sp | 0 | Section headings |
| `headlineLarge` | 32sp | 400 | 40sp | 0 | Page titles |
| `headlineMedium` | 28sp | 400 | 36sp | 0 | Card titles |
| `headlineSmall` | 24sp | 400 | 32sp | 0 | Dialog titles |
| `titleLarge` | 22sp | 500 (Medium) | 28sp | 0 | App bar title |
| `titleMedium` | 16sp | 500 | 24sp | 0.15 | List item titles |
| `titleSmall` | 14sp | 500 | 20sp | 0.1 | Sub-section titles |
| `bodyLarge` | 16sp | 400 | 24sp | 0.5 | Primary body text |
| `bodyMedium` | 14sp | 400 | 20sp | 0.25 | Secondary body text |
| `bodySmall` | 12sp | 400 | 16sp | 0.4 | Captions, footnotes |
| `labelLarge` | 14sp | 500 | 20sp | 0.1 | Button text |
| `labelMedium` | 12sp | 500 | 16sp | 0.5 | Chip text, tab labels |
| `labelSmall` | 11sp | 500 | 16sp | 0.5 | Overline text, badges |

---

## Spacing Scale (4px grid)

| Token | Value | Usage |
|-------|-------|-------|
| `spacing2` | 2px | Micro gaps (icon to label) |
| `spacing4` | 4px | Tight spacing (chip padding) |
| `spacing8` | 8px | Small gaps (list item internal) |
| `spacing12` | 12px | Medium-small gaps |
| `spacing16` | 16px | Standard padding (page margins, card padding) |
| `spacing20` | 20px | Medium-large gaps |
| `spacing24` | 24px | Section spacing |
| `spacing32` | 32px | Large section gaps |
| `spacing40` | 40px | XL gaps |
| `spacing48` | 48px | Touch target minimum height |
| `spacing64` | 64px | Hero spacing |

**Standard page padding**: 16px horizontal, 16px vertical  
**Standard card padding**: 16px all sides  
**Standard list item height**: 56px (with subtitle: 72px)  
**Section header spacing**: 24px top, 8px bottom  

---

## Border Radius

| Token | Value | Usage |
|-------|-------|-------|
| `radiusNone` | 0px | No rounding (dividers) |
| `radiusSmall` | 4px | Subtle rounding (chips) |
| `radiusMedium` | 8px | Standard rounding (cards, buttons small) |
| `radiusLarge` | 12px | Prominent rounding (modal cards) |
| `radiusXLarge` | 16px | Very rounded (bottom sheets) |
| `radiusFull` | 9999px | Fully rounded (FAB, avatar, pills) |

---

## Elevation

Material Design 3 uses tonal surface overlays (colour mixing) rather than drop shadows for elevation on coloured surfaces.

| Level | Usage | Surface tint opacity |
|-------|-------|---------------------|
| Level 0 | Flat surface, background | 0% |
| Level 1 | Cards, raised surfaces | 5% |
| Level 2 | Floating buttons, dropdowns | 8% |
| Level 3 | Navigation drawer | 11% |
| Level 4 | App bar (scrolled) | 12% |
| Level 5 | Bottom sheets | 14% |

For shadow (on non-coloured backgrounds):

| Level | BoxShadow |
|-------|-----------|
| 0 | none |
| 1 | `0 1px 2px rgba(0,0,0,0.15)` |
| 2 | `0 2px 6px rgba(0,0,0,0.15)` |
| 3 | `0 4px 12px rgba(0,0,0,0.15)` |

---

## Component Tokens

| Component | Property | Value |
|-----------|----------|-------|
| **FilledButton** | Height | 40px |
| **FilledButton** | Horizontal padding | 24px |
| **FilledButton** | Border radius | `radiusFull` (20px) |
| **OutlinedButton** | Height | 40px |
| **OutlinedButton** | Border width | 1px |
| **TextButton** | Height | 40px |
| **FAB** | Size | 56×56px |
| **Extended FAB** | Height | 56px |
| **TextField** | Height | 56px |
| **TextField** | Border radius | `radiusMedium` (8px) |
| **Chip** | Height | 32px |
| **Chip** | Horizontal padding | 12px |
| **AppBar** | Height | 64px |
| **Bottom Navigation** | Height | 80px |
| **Bottom Sheet** (min) | Min height | 30% of screen |
| **Dialog** | Width | 280–560px |
| **Dialog** | Padding | 24px |
| **Card** | Border radius | `radiusLarge` (12px) |
| **List Tile** | Min height | 56px (72px with subtitle) |
| **Avatar** | Size (small) | 32×32px |
| **Avatar** | Size (medium) | 40×40px |
| **Avatar** | Size (large) | 56×56px |

---

## Icon System

Library: **Material Icons** (included with Flutter)  
Icon size: 24px (standard), 20px (dense), 28px (prominent)  
Icon colour: Inherit from `onSurface` or `onPrimary` as appropriate

Custom icons (if any): [List here with file paths]

---

## State Colours

| State | Overlay | Opacity |
|-------|---------|---------|
| Hovered | onSurface | 8% |
| Focused | onSurface | 12% |
| Pressed | onSurface | 12% |
| Dragged | onSurface | 16% |
| Disabled (surface) | onSurface | 12% |
| Disabled (content) | onSurface | 38% |
