# Utils

## Purpose

`Utils` is a root-level folder for general-purpose helper code that does not belong to `Views`, `Models`, `Enums`, `Services`, `DataStore`, `DesignSystem`, or `Resources`.

Examples:

```text
Utils
├── Extensions
│   ├── String+Extensions.swift
│   ├── Date+Extensions.swift
│   ├── View+Extensions.swift
│   ├── Collection+Extensions.swift
│   └── Optional+Extensions.swift
├── ViewModifiers
│   ├── KeyboardDismissModifier.swift
│   ├── ReadSizeModifier.swift
│   └── ConditionalModifier.swift
├── Helpers
│   ├── Validator.swift
│   ├── DateFormatterHelper.swift
│   └── HapticsHelper.swift
└── Constants
    └── AppConstants.swift
```

Utils may contain:

```text
general Swift extensions
general SwiftUI extensions
reusable helper functions
utility types
small helper structs/classes
technical ViewModifiers
date formatting helpers
validation helpers
device helpers
keyboard dismiss helpers
conditional view helpers
read size/layout helpers
```

Examples:

```swift
String.isValidEmail
Date.formattedShort
Array[safe: index]
View.if(...)
View.hideKeyboardOnTap()
```

Utils must not contain:

```text
design tokens
ButtonStyles
visual design modifiers
services
DataStore
models
enums
screen-specific code
business logic
raw resource files
```

## Utils/ViewModifiers vs DesignSystem/ViewModifiers

Use `DesignSystem/ViewModifiers` for visual, reusable, design-focused modifiers:

```text
GlassBackgroundModifier
CardSurfaceModifier
PressScaleModifier
ShimmerModifier
```

Use `Utils/ViewModifiers` for technical/helper behavior modifiers:

```text
KeyboardDismissModifier
ReadSizeModifier
ConditionalModifier
```

Decision rule:

```text
Visual/design/styling modifier -> DesignSystem/ViewModifiers
Technical/helper behavior modifier -> Utils/ViewModifiers
```
