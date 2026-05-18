---
name: swiftui-mv
description: Build, refactor, or review SwiftUI apps using a native-first MV architecture with local view state, service-owned business logic, an Observation-based DataStore for global app state, reusable DesignSystem code, Resources, and Utils. Use when working on SwiftUI project structure, replacing default ViewModels, organizing Views/Models/Enums/Services/DataStore/DesignSystem/Resources/Utils, injecting services through Environment, creating @Observable app state, or auditing architecture boundaries.
---

# SwiftUI MV

## Operating Workflow

1. Inspect the project structure before changing or judging it. Identify the app source root, existing SwiftUI conventions, service/state patterns, and whether the target is a new feature, refactor, or review.
2. Apply the architecture as `MV + Services + DataStore + DesignSystem`, without adding ViewModels by default.
3. Keep local UI state in views, business logic in services, and app-wide state in DataStore.
4. Preserve existing project patterns unless they conflict with the architecture boundaries.
5. Load only the reference needed for the current task:
   - `references/core-architecture.md` for root folders, high-level boundaries, no-default-ViewModel rule, and reference routing.
   - `references/services.md` for service responsibilities, business logic boundaries, service injection, and service-specific Observation requirements.
   - `references/datastore.md` for global app state, DataStore scope, credits, persistence, remote config, subscriptions, and DataStore/service coordination.
   - `references/observation-environment.md` for Apple-documented `@Observable`, typed environment injection, optional environment reads, `@Bindable`, and migration away from `ObservableObject` patterns.
   - `references/view-organization.md` for screen folders, local components, view extensions, and view-specific state.
   - `references/design-system.md` for reusable UI, native SwiftUI style APIs, styles, tokens, components, and visual modifiers.
   - `references/resources.md` for raw non-Swift app files and the Resources vs DesignSystem boundary.
   - `references/utils.md` for general helpers, extensions, technical modifiers, and the Utils vs DesignSystem boundary.
   - `references/examples.md` for canonical trees and correct/wrong examples.
6. For reviews or larger refactors, run `scripts/audit_swiftui_mv.py <project-root>` to catch obvious structure violations. Treat results as prompts for code inspection, not as a complete Swift semantic analysis.

## When Not To Use

- Do not use this skill for generic SwiftUI styling, layout fixes, animation work, or bug fixes that do not involve architecture boundaries.
- Do not use it to introduce a new architecture into a project when the user only asked for a narrow compatibility fix.

## Architecture Defaults

- Use root folders: `Views`, `Models`, `Enums`, `Services`, `DataStore`, `DesignSystem`, `Resources`, and `Utils`.
- Do not create a global `States` folder.
- Do not introduce a ViewModel layer unless the user explicitly asks or the existing codebase already depends on one and the refactor scope requires compatibility.
- Use Swift Observation for app state by default: `@MainActor @Observable final class AppDataStore`.
- Inject services and stores from the app root or another composition layer; views consume them through SwiftUI `@Environment`.
- Use `.environment(appDataStore)` / `.environment(service)` for Observation objects and read them with `@Environment(AppDataStore.self)`.
- Services read with `@Environment(Service.self)` must conform to `Observable`; otherwise use a custom environment value or initializer injection.
- Use `@Bindable` only when a view needs a `Binding` to a mutable property of an `@Observable` object.
- Keep `DesignSystem` independent from services, DataStore, screen-specific state, and business logic.
- Store non-Swift files under `Resources`; never place Swift source there.
- Put general helpers in `Utils`, not design tokens or business logic.

## Refactor Rules

- Move small screen-specific UI fragments into `ViewName+Components.swift` as extensions on the parent view.
- Use `private var ...: some View` for tiny parameterless local fragments and `private func ... -> some View` for small parameterized fragments.
- Use private nested `View` structs inside `extension ViewName` for larger screen-specific sections with inputs, bindings, local UI state, complex animations, or meaningful identity; place them in files like `ViewName+ComponentName.swift` under the view's `Extensions` folder.
- Move reusable, standalone, UI-focused components to `DesignSystem`, initialized with explicit inputs instead of reading services or app state directly.
- Move networking, persistence, authentication, subscriptions, remote config, storage, notifications, payments, and domain actions to `Services`.
- Keep DataStore small and app-level. It may coordinate services or smaller stores, but it should not directly implement networking, database, Keychain, image generation, secret handling, or screen-specific UI logic.

## Code Marking

- When writing or refactoring Swift code, always add short `// MARK: - ...` sections for real groups that exist in the type.
- Use `// MARK: - Properties` before stored or computed properties, `@Environment`, `@State`, inputs, bindings, constants, or dependencies.
- Use `// MARK: - Body` before SwiftUI `var body`, `makeBody(configuration:)`, ViewModifier `body(content:)`, and grouped view-building computed properties.
- Use `// MARK: - Initialization` before custom initializers.
- Use `// MARK: - Methods` before regular methods, action handlers, helpers, async wrappers, service methods, or utility methods.
- Use `// MARK: - Preview` before `#Preview`.
- Use `// MARK: - <Type> Extension` before concrete type extensions, such as `Color Extension`.
- Use `// MARK: - Extensions` before generic convenience extensions, such as style static-member extensions.
- Keep marks grouped and short: one `Methods` mark for a method group, no empty sections, and no long explanatory comments around marks.
- Put declaration-level marks directly above the declaration they label: no blank line and no unrelated comment between `// MARK: - Body` and `var body`/`makeBody`, between `// MARK: - Extensions` and `extension`, or between `// MARK: - Preview` and `#Preview`.
- Do not add internal lint-suppression comments such as `// swiftlint:disable:next identifier_name` just to make generated code pass style checks. If a temporary suppression comment is used during debugging, remove it after the build/tests pass unless the existing project explicitly requires it.
- Keep `///` documentation comments for public API behavior; `// MARK:` is only for navigation and grouping.

## Audit Helper

Run:

```bash
python3 /path/to/swiftui-mv/scripts/audit_swiftui_mv.py <project-root>
```

Optional flags:

```bash
python3 /path/to/swiftui-mv/scripts/audit_swiftui_mv.py <project-root> --json
python3 /path/to/swiftui-mv/scripts/audit_swiftui_mv.py <project-root> --strict
```

Use `--strict` when architecture conformance should fail on warnings. The script is intentionally read-only and dependency-free.

## Tooling Policy

- Use `audit_swiftui_mv.py` for SwiftUI MV architecture checks.
- Use `swift build` or `xcodebuild` for compile correctness.
- Use SwiftLint or SwiftFormat only when already present in the target app or explicitly requested.
- Do not add linters to user apps just to satisfy this skill.
