# View Organization

## Screen Folder Pattern

Each screen-level SwiftUI view gets its own group under `Views`. The group name matches the view name.

```text
Views
└── HomeView
    ├── HomeView.swift
    ├── HomeState.swift
    └── Extensions
        ├── HomeView+Components.swift
        ├── HomeView+PromptDockView.swift
        └── HomeView+Extensions.swift
```

Repeat this pattern for each screen:

```text
Views
├── HomeView
├── LoginView
└── ProfileView
```

## Main View File

`HomeView.swift` contains:

```text
main view struct
body
high-level layout
local @State properties
@Environment dependencies
top-level screen composition
```

Keep the main file readable and high-level. Move small view fragments to `HomeView+Components.swift`. Move larger view-specific nested subviews to dedicated `HomeView+ComponentName.swift` files. Move local actions and helpers to `HomeView+Extensions.swift`.

## Code Marking

Generated Swift should use compact `// MARK: - ...` sections whenever the group exists:

```text
Properties -> stored or computed properties, inputs, dependencies, @Environment, @State, @Binding
Body -> var body, makeBody(configuration:), body(content:), grouped view-building computed properties
Initialization -> custom init blocks
Methods -> action handlers, helpers, async wrappers, service methods, utility methods
Preview -> #Preview blocks
<Type> Extension -> concrete extensions such as Color Extension
Extensions -> generic convenience extension groups
```

Do not add one mark per function. Group related methods under one `// MARK: - Methods`, skip empty sections, and keep `///` documentation comments for API behavior. Put declaration-level marks directly above what they label: no blank line and no unrelated comment between `// MARK: - Body` and `var body`/`makeBody`, between `// MARK: - Extensions` and `extension`, or between `// MARK: - Preview` and `#Preview`. Do not leave internal lint-suppression comments such as `// swiftlint:disable:next identifier_name` in generated code unless the existing project explicitly requires them.

## Components Extension

`Views/HomeView/Extensions/HomeView+Components.swift` contains small UI fragments that belong only to `HomeView`.

Correct:

```swift
// MARK: - HomeView Extension
extension HomeView {
    // MARK: - Body
    private var headerSection: some View {
        VStack {
            Text("Title")
            Text("Subtitle")
        }
    }

    // MARK: - Methods
    private func optionRow(title: String, isSelected: Bool) -> some View {
        HStack {
            Text(title)
            Spacer()

            if isSelected {
                Image(systemName: "checkmark")
            }
        }
    }
}
```

Use this file for tiny view-local layout helpers. Do not put a large section, independent animation, local `@State`, or a complex interaction flow in a computed property.

## Local Component Rule

```text
Small + no parameters -> computed property
Small + has parameters -> function
Large + view-specific -> private nested View in its own extension file
Generic or reusable -> DesignSystem
```

Examples:

```swift
// MARK: - Body
private var headerSection: some View {
    ...
}

// MARK: - Methods
private func actionButton(title: String) -> some View {
    ...
}
```

Computed properties and helper functions should be small, view-specific, simple, scoped to the parent view, and not complex enough to deserve their own `View` body.

Use a private nested subview when the section is still screen-specific but has inputs, bindings, local transient state, complex animations, meaningful identity, or enough layout to make the parent body hard to scan.

Example file:

```text
Views/HomeView/Extensions/HomeView+PromptDockView.swift
```

Example:

```swift
// MARK: - HomeView Extension
extension HomeView {
    private struct PromptDockView: View {
        // MARK: - Properties
        @Binding var prompt: String
        let isGenerating: Bool
        let onGenerate: () -> Void

        @State private var isExpanded = false

        // MARK: - Body
        var body: some View {
            VStack {
                TextField("Describe a wallpaper", text: $prompt)

                Button("Generate", action: onGenerate)
                    .disabled(isGenerating)
            }
            .scaleEffect(isExpanded ? 1.0 : 0.98)
        }
    }
}
```

The nested view can own transient UI state and animation state. Shared parent state should be passed with `@Binding`. Business logic, networking, persistence, generation, payments, authentication, and storage still belong in `Services`.

If a component becomes too generic, reusable across screens, styling-focused, or useful outside this one view, move it to `DesignSystem`.

Do not create top-level screen-specific `struct View` components in a view extension file:

```swift
struct PromptDockView: View {
    // MARK: - Body
    var body: some View {
        Text("Prompt")
    }
}
```

Scope screen-specific nested views under the parent:

```swift
// MARK: - HomeView Extension
extension HomeView {
    private struct PromptDockView: View {
        // MARK: - Body
        var body: some View {
            Text("Prompt")
        }
    }
}
```

## View Extensions

`Views/HomeView/Extensions/HomeView+Extensions.swift` contains view-specific methods:

```text
button action methods
small helper methods
view-specific interaction logic
small async wrappers
formatting helpers
screen-local behavior
```

Example:

```swift
// MARK: - HomeView Extension
extension HomeView {
    // MARK: - Methods
    func handleGenerateButtonTap() {
        Task {
            await generateWallpaper()
        }
    }

    func resetGenerationState() {
        prompt = ""
        selectedImage = nil
        state = .idle
    }
}
```

Do not put networking, database logic, authentication, payment logic, storage implementation, image generation business logic, or large domain logic in a view extension. Those belong in `Services`.

## View-Specific State

If a state enum belongs only to one view, keep it inside that view group.

Correct:

```text
Views/HomeView/HomeState.swift
```

Wrong:

```text
Enums/HomeState.swift
```

Example:

```swift
enum HomeState {
    case idle
    case loading
    case result
    case failed
}
```

Do not create a global `States` folder.

Rule:

```text
View-specific UI state -> corresponding View folder
Shared/global state enum -> Enums folder
```

Shared/global enums such as `AppRoute`, `GenerationMode`, `AppTheme`, and `PermissionStatus` belong in `Enums`.

## Local vs Reusable UI

Keep UI in `ViewName+Components.swift` when it is:

```text
small
screen-specific
strongly tied to parent view state
not generic
not complex
a simple local UI fragment
```

Keep UI in `ViewName+ComponentName.swift` as a private nested subview when it is:

```text
screen-specific
too large for a computed property
has inputs or bindings
owns local transient state
contains complex animations
has meaningful UI responsibility
not reusable across the app
```

Move UI to `DesignSystem` when it is:

```text
generic
standalone outside one screen
complex in a reusable or generic way
reusable or potentially reusable
useful across screens
UI/styling focused
initialized with its own model/config
```

Simple rule:

```text
Small + screen-specific -> ViewName+Components.swift
Large + screen-specific -> ViewName+ComponentName.swift
Generic + reusable -> DesignSystem
```

## Naming

```text
View group: HomeView
Main view file: HomeView.swift
Components extension file: HomeView+Components.swift
Nested view file: HomeView+PromptDockView.swift
Extensions file: HomeView+Extensions.swift
View state file: HomeState.swift or HomeViewState.swift
```
