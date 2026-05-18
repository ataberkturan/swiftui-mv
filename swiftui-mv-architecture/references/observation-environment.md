# Observation and Environment

This reference follows Apple's Observation and SwiftUI environment APIs for iOS 17+, iPadOS 17+, macOS 14+, tvOS 17+, watchOS 10+, and visionOS 1+.

Sources checked:

- Apple `Observable()` macro documentation: <https://developer.apple.com/documentation/observation/observable()>
- Apple `View.environment(_:)` documentation: <https://developer.apple.com/documentation/swiftui/view/environment(_:)>
- Apple `Scene.environment(_:)` documentation: <https://developer.apple.com/documentation/swiftui/scene/environment(_:)>
- Apple `Environment.init(_:)` documentation: <https://developer.apple.com/documentation/swiftui/environment/init(_:)-7pint>
- Apple optional `Environment.init(_:)` documentation: <https://developer.apple.com/documentation/swiftui/environment/init(_:)-8slkf>
- Apple `Bindable` documentation: <https://developer.apple.com/documentation/swiftui/bindable>
- Apple migration guide: <https://developer.apple.com/documentation/swiftui/migrating-from-the-observable-object-protocol-to-the-observable-macro>

## Observable Types

Use the `@Observable` macro for DataStore and shared service/store state in this architecture.

Apple documents `@Observable` as the macro that adds observation support to a custom type and conforms it to the `Observable` protocol.

```swift
import Observation

@MainActor
@Observable
final class AppDataStore {
    var isUserCompletedOnboarding = false
    var currentCredits = 0
    var isSubscribed = false
}
```

Typed `@Environment(Type.self)` and `.environment(object)` require the injected object to conform to `Observable`. In this architecture, any service consumed with `@Environment(AuthService.self)` should be an `@Observable` reference type, even if it mostly exposes methods.

Do not add `@Published` to observable properties. Apple's migration guide says Observation does not require property wrappers for observable properties.

Use `@ObservationIgnored` for accessible properties that should not be tracked.

```swift
import Observation

@Observable
final class GenerationService {
    var cachedResults: [GenerationResult] = []

    @ObservationIgnored
    private let apiClient: APIClient

    init(apiClient: APIClient) {
        self.apiClient = apiClient
    }
}
```

If a dependency should not be observable, do not read it with `@Environment(Type.self)`. Use a custom `EnvironmentKey` / `EnvironmentValues` entry or inject it through an initializer instead.

## App Root Ownership

Own long-lived app state and services at the app root or another composition boundary.

For `@Observable` reference types, Apple's migration guide shows using `@State` instead of `@StateObject` after adopting Observation.

```swift
import SwiftUI

@main
struct WallpaperApp: App {
    @State private var appDataStore = AppDataStore()
    @State private var authService = AuthService()
    @State private var generationService = GenerationService()

    var body: some Scene {
        WindowGroup {
            RootView()
                .environment(appDataStore)
                .environment(authService)
                .environment(generationService)
        }
    }
}
```

Use `.environment(_:)` to place an `Observable` object into a scene or view hierarchy. Apple documents both `Scene.environment(_:)` and `View.environment(_:)` for objects that conform to `Observable`.

## Reading From Environment

Read injected Observation objects with typed `@Environment`.

```swift
struct HomeView: View {
    @Environment(AppDataStore.self) private var appDataStore
    @Environment(GenerationService.self) private var generationService

    @State private var prompt = ""
    @State private var state: HomeState = .idle

    var body: some View {
        VStack {
            Text("Credits: \(appDataStore.currentCredits)")

            Button("Generate") {
                handleGenerateTap()
            }
        }
    }
}
```

Apple documents that SwiftUI automatically updates the parts of a view that depend on the environment object when that object changes.

Important: non-optional `@Environment(Type.self)` crashes when accessed if no object of that type has been set in the environment.

Use optional typed environment when the dependency is truly optional or when fallback behavior is needed.

```swift
struct DebugBannerView: View {
    @Environment(RemoteConfigService.self) private var remoteConfig: RemoteConfigService?

    var body: some View {
        if remoteConfig?.isDebugBannerEnabled == true {
            Text("Debug")
        }
    }
}
```

## Bindings With @Bindable

Use `@Bindable` when a view needs a `Binding` to a mutable property of an `@Observable` object.

Apple documents `Bindable` as the property wrapper that creates bindings to mutable properties of observable objects.

Direct read, no binding needed:

```swift
struct CreditBadge: View {
    @Environment(AppDataStore.self) private var appDataStore

    var body: some View {
        Text("\(appDataStore.currentCredits)")
    }
}
```

Binding needed for controls:

```swift
struct SettingsView: View {
    @Environment(AppDataStore.self) private var appDataStore

    var body: some View {
        @Bindable var appDataStore = appDataStore

        Toggle("NSFW checker disabled", isOn: $appDataStore.nsfwCheckerDisabled)
    }
}
```

For a direct observable input:

```swift
struct ProfileEditorView: View {
    @Bindable var profile: UserProfile

    var body: some View {
        TextField("Display name", text: $profile.displayName)
    }
}
```

Do not use `@Bindable` just to read values or call methods. Use it only where SwiftUI requires a binding, such as `TextField`, `Toggle`, `Picker`, or a child view that accepts `Binding`.

## Local State vs Observable State

Use `@State` for local UI state owned by a view:

```swift
@State private var email = ""
@State private var isSheetPresented = false
@State private var focusedField: Field?
@State private var state: LoginState = .idle
```

Use `@Observable` for shared app/domain state that multiple views or services need:

```swift
@Observable
final class CreditStore {
    var currentCredits = 0
    var dailyUsageLimit = 0
    var lastCreditResetDate: Date?
}
```

Use environment injection for app-level stores/services that descendants should consume:

```swift
RootView()
    .environment(appDataStore)
    .environment(creditStore)
```

## Migration Defaults

When adopting this architecture, prefer these replacements:

```text
ObservableObject -> @Observable
@Published -> plain stored property
@StateObject -> @State at the owner boundary
@ObservedObject -> plain property, @Bindable only if bindings are needed
@EnvironmentObject -> @Environment(Type.self)
.environmentObject(object) -> .environment(object)
```

Apple's migration guide says apps can migrate incrementally and can mix Observation and `ObservableObject` during transition. Still, new SwiftUI MV code should use Observation by default.

## Correct Pattern

```swift
import Observation
import SwiftUI

@MainActor
@Observable
final class AppDataStore {
    var currentCredits = 3
    var isSubscribed = false
}

@MainActor
@Observable
final class GenerationService {
    func generate(prompt: String) async throws -> GenerationResult {
        // business logic
    }
}

@main
struct WallpaperApp: App {
    @State private var appDataStore = AppDataStore()
    @State private var generationService = GenerationService()

    var body: some Scene {
        WindowGroup {
            HomeView()
                .environment(appDataStore)
                .environment(generationService)
        }
    }
}

struct HomeView: View {
    @Environment(AppDataStore.self) private var appDataStore
    @Environment(GenerationService.self) private var generationService

    @State private var prompt = ""
    @State private var state: HomeState = .idle

    var body: some View {
        VStack {
            TextField("Prompt", text: $prompt)
            Text("Credits: \(appDataStore.currentCredits)")
        }
    }
}
```

## Avoid By Default

Avoid this for new code in the SwiftUI MV architecture:

```swift
final class AppDataStore: ObservableObject {
    @Published var currentCredits = 3
}

struct WallpaperApp: App {
    @StateObject private var appDataStore = AppDataStore()

    var body: some Scene {
        WindowGroup {
            HomeView()
                .environmentObject(appDataStore)
        }
    }
}

struct HomeView: View {
    @EnvironmentObject private var appDataStore: AppDataStore
}
```

Use this older pattern only for compatibility with existing `ObservableObject` code, older OS targets, or APIs that still require it.
