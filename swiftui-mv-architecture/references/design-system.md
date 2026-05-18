# DesignSystem

## Purpose

`DesignSystem` is a root-level folder for reusable, standalone, UI-focused Swift code.

It may contain:

```text
reusable UI components
reusable styled views
ButtonStyle implementations
visual ViewModifiers
color tokens
typography tokens
spacing tokens
custom icon/symbol access layers
native SwiftUI style wrappers
```

It must not contain:

```text
business logic
service calls
observable app state
screen-specific UI fragments
screen-specific helper methods
feature-specific domain logic
raw resource files
app icon
normal content images
```

DesignSystem code should receive data through explicit inputs. It should not read app services or DataStore directly.

## Native-First SwiftUI APIs

Prefer APIs that feel native to SwiftUI:

```swift
.buttonStyle(.medium)
.foregroundStyle(.brandOrange)
Image.customSparkle
Color.surfacePrimary
.font(.brandTitle)
```

Avoid unnecessary wrapper namespaces like `AppColors.brandOrange` when a native extension reads better.

## Button Styles

Button appearance must be implemented with `ButtonStyle`, not reusable custom button views.

Wrong:

```swift
struct PrimaryButton: View {
    ...
}
```

Correct:

```swift
struct MediumButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .font(.caption)
            .fontWeight(.semibold)
            .frame(height: 32)
            .padding(.horizontal, 10)
            .foregroundStyle(Color.black)
            .background(Color.white)
            .cornerRadius(999)
            .opacity(configuration.isPressed ? 0.7 : 1.0)
    }
}

extension ButtonStyle where Self == MediumButtonStyle {
    static var medium: MediumButtonStyle { MediumButtonStyle() }
}
```

Usage:

```swift
Button("Continue") {
    ...
}
.buttonStyle(.medium)
```

Folder:

```text
DesignSystem/ButtonStyles/MediumButtonStyle.swift
```

Apply the same native style-extension pattern to other SwiftUI style systems when appropriate:

```text
PickerStyle
ToggleStyle
TextFieldStyle
ProgressViewStyle
```

## Components and Views

Use `DesignSystem/Components` for reusable UI components that are standalone, independent from services, independent from observable app state, independent from a specific screen, and initialized with their own inputs or model/config.

Correct:

```swift
struct StatCard: View {
    let model: StatCardModel
}
```

Wrong:

```swift
struct ProfileCard: View {
    @Environment(UserSession.self) private var session
}
```

Use `DesignSystem/Views` for generic, standalone, UI/styling-focused views that are complex enough to make a parent view extension too large or likely to be reused later. A view does not need to already be used by multiple screens before it can belong there.

## Foundation

Create foundation folders only when needed:

```text
DesignSystem/Foundation/Colors
DesignSystem/Foundation/Typography
DesignSystem/Foundation/Icons
DesignSystem/Foundation/Spacing
```

Create `Colors` only if the app has custom color tokens. Extend `Color`:

```swift
Color.brandOrange
Color.surfacePrimary
Color.textSecondary
```

Create `Typography` only if the app uses custom typography. Prefer native usage:

```swift
.font(.brandTitle)
.font(.brandBody)
```

Create `Icons` only if the app has custom icon or symbol assets. Extend `Image`:

```swift
Image.customSparkle
```

Create `Spacing` only if the app has a custom spacing system.

## View Modifiers

Use `DesignSystem/ViewModifiers` for visual, reusable, design-focused modifiers:

```text
GlassBackgroundModifier
CardSurfaceModifier
PressScaleModifier
ShimmerModifier
```

Do not put technical helper modifiers there. Technical behavior helpers belong in `Utils/ViewModifiers`.
