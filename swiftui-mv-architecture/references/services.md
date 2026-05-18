# Services

## Purpose

Services own business logic and external system interaction.

Services answer:

```text
How do we perform this action?
How do we fetch this data?
How do we save this value?
How do we talk to this external system?
```

Typical service examples:

```text
APIClient
AuthService
StorageService
SubscriptionService
RemoteConfigService
NotificationService
KeychainService
GenerationService
```

Create services that match the actual app needs. Do not create a fixed service list just to satisfy the architecture.

## Responsibilities

Services may handle:

```text
networking
authentication
storage
subscriptions
remote config
notifications
payments
image generation
database operations
Keychain access
UserDefaults access
file storage
backend communication
domain actions
```

Examples:

```text
AuthService -> login, logout, register, session refresh
APIClient -> HTTP requests, decoding, network errors
StorageService -> UserDefaults, file storage, local cache
KeychainService -> secure local storage
SubscriptionService -> Superwall, RevenueCat, StoreKit
RemoteConfigService -> remote settings from Supabase or backend
GenerationService -> wallpaper/image generation requests
NotificationService -> notification permissions and registration
```

## Services Are Not ViewModels

Services must not hold temporary screen state:

```text
isLoginButtonLoading
selectedTab
isSheetPresented
searchText
focusedField
temporaryErrorMessage
local animation state
isPromptFocused
isButtonPressed
```

Keep those values in views as `@State`.

Services may hold shared domain or app-level state when appropriate:

```text
currentUser
token
subscriptionStatus
remoteConfig
notificationPermissionStatus
cachedProfile
```

## Service Injection

Views consume services. Views do not create services directly.

Wrong:

```swift
struct LoginView: View {
    private let authService = AuthService()
}
```

Correct for an observable service:

```swift
struct LoginView: View {
    @Environment(AuthService.self) private var authService
}
```

Create and own services higher in the app, then inject them into the SwiftUI environment.

## Observation Requirement

Read `references/observation-environment.md` before implementing service injection with typed environment APIs.

Typed `@Environment(AuthService.self)` requires `AuthService` to conform to Swift Observation's `Observable` protocol. In new code, make services injected this way `@Observable` reference types:

```swift
import Observation

@MainActor
@Observable
final class AuthService {
    func signIn(email: String, password: String) async throws {
        ...
    }
}
```

If a service should not be observable, do not use `@Environment(Service.self)`. Use a custom `EnvironmentKey` / `EnvironmentValues` entry or initializer injection instead.

## Boundary Checks

Move code from views into services when it:

```text
talks to external systems
performs domain actions
encodes business rules
persists or fetches values
handles credentials or secure storage
coordinates subscriptions, remote config, or notifications
```

Keep code in views when it is:

```text
local UI state
local formatting for one screen
simple button interaction routing
screen-local animation or focus behavior
small task wrapper calling a service
```
