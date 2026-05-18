# DataStore

## Purpose

DataStore is the central app-level state source. It answers:

```text
What is the current global state of the app?
```

DataStore is not:

```text
a screen-specific model
a UI component
a backend service
a networking layer
a database layer
a place for all business logic
```

It acts as a shared state layer between:

```text
Views
Services
App root
Persistent storage
Remote configuration
```

## Observation Default

Use Swift Observation by default:

```swift
import Observation

@MainActor
@Observable
final class AppDataStore {
    var isUserCompletedOnboarding = false
    var isFirstLaunch = true
    var currentCredits = 0
    var dailyUsageLimit = 0
    var isSubscribed = false
    var nsfwCheckerDisabled = false
    var isPaywallDismissButtonActive = false
}
```

Prefer `@Observable` over `ObservableObject` unless project compatibility requires the older model.

Read `references/observation-environment.md` before implementing DataStore ownership, `.environment(appDataStore)`, `@Environment(AppDataStore.self)`, optional environment reads, or `@Bindable`.

## What Belongs in DataStore

DataStore should hold small but important global app state used across multiple screens:

```text
whether the user completed onboarding
whether this is the first app launch
whether the user has free credits left
whether the user is subscribed
whether remote-controlled features are enabled or disabled
whether the paywall dismiss button should be shown
whether NSFW checking is enabled or disabled
current daily usage limit
current credits
```

These values are not temporary screen state. They affect multiple screens or the whole app.

## What Does Not Belong in DataStore

DataStore must not hold temporary UI state:

```text
isButtonPressed
selectedTabAnimationProgress
currentTextFieldFocus
temporaryImagePreviewOffset
isSheetPresented
searchText
localLoadingState
```

DataStore must not become a God Object. It should not directly contain:

```text
direct Supabase query logic
direct Keychain implementation details
direct API key handling logic
detailed Superwall business logic
image generation logic
gallery database logic
screen-specific UI logic
animation state
networking implementation details
every service in the app
```

Keep DataStore small, focused, and app-level. Split larger domains into smaller stores or services, such as `CreditStore` or `FeatureFlagStore`.

## DataStore and Services

DataStore coordinates with services; it does not replace them.

Example split:

```text
AppDataStore -> exposes app-level values to UI
CreditStore -> manages credits and daily resets
SubscriptionService -> talks to Superwall, RevenueCat, StoreKit, or equivalent
RemoteConfigService -> fetches remote flags/settings
KeychainService -> handles secure local storage
```

Preferred data flow:

```text
Views
  ↓
DataStore
  ↓
Services / Smaller Stores
  ↓
Supabase, Superwall, Keychain, UserDefaults, External APIs
```

Views should not directly ask Supabase for remote settings, check Superwall subscription status, or manage credits.

## Persistence

Persist global values through `UserDefaults`, `AppStorage`, a custom persistence helper, or a storage service. Keep persistence details out of DataStore when they become complex.

Good split:

```text
DataStore -> exposes state
StorageService / persistence helper -> saves and loads values
```

Credit reset logic should use real dates, such as `lastCreditResetDate`, not device uptime.

## Credit System

Credit system behavior may be coordinated by DataStore, but detailed credit logic should usually live in a dedicated store or service, such as `CreditStore`.

Credit logic may include:

```text
storing current free credits
knowing the daily free limit
resetting credits after one day
not reducing credits for subscribed users
checking whether the user can continue generating
decreasing credits when needed
```

Credit reset should be based on real dates, not device uptime.

## Remote Config, Subscriptions, and Security

Remote config belongs in a service. DataStore consumes remote values and exposes simple state to UI.

Subscription details belong in `SubscriptionService`; DataStore exposes simple subscription-related state.

Do not manage secrets in DataStore. Prefer:

```text
iOS App -> Supabase Edge Function -> External API
```

If client-side API key handling remains necessary, isolate it in a dedicated service such as `APIKeyService`.

## Final Scope

DataStore should be responsible for:

```text
holding app-wide state
exposing global values to SwiftUI
coordinating app-level stores/services
keeping simple persistent values
providing a clean source of truth for views
```

DataStore should not be responsible for:

```text
direct networking details
direct database queries
direct Keychain implementation
image generation logic
screen-specific UI state
animation state
large business logic
every service in the app
secret API key management
```
