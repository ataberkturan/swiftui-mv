# Core Architecture

## Folder Responsibilities

Use these root-level source folders when the app needs them:

```text
Views
Models
Enums
Services
DataStore
DesignSystem
Resources
Utils
```

- `Views`: SwiftUI screens and view-specific files.
- `Models`: data models, API models, persistence models, domain models, DTO-like types, and shared configuration models.
- `Enums`: shared/global enum types, routes, modes, categories, domain enums, and service-level shared enums.
- `Services`: business logic and external system interaction.
- `DataStore`: app-level observable state and global source of truth.
- `DesignSystem`: reusable UI components, styles, visual modifiers, colors, typography, icons, spacing, and native SwiftUI style systems.
- `Resources`: non-Swift files such as assets, images, audio, video, JSON, graphics, fonts, markdown, and static files.
- `Utils`: general helper code, extensions, utility types, and non-design-system modifiers.

Unused folders do not need to be created just to satisfy the structure.

## Boundary Rule

```text
Local UI state stays in Views.
Business logic stays in Services.
Global app state stays in DataStore.
```

Views draw UI, hold screen-local state, handle simple user interactions, call services, read DataStore, and react to observable state changes.

Services perform work: fetching, saving, networking, auth, subscriptions, remote config, storage, notifications, payments, image generation, database operations, Keychain access, file storage, backend communication, and domain actions. Load `references/services.md` for detailed service rules.

DataStore holds app-wide state, exposes global values to SwiftUI, coordinates app-level state updates, uses services for actual work, and keeps app behavior consistent. Load `references/datastore.md` for detailed DataStore rules.

## No Default ViewModels

Do not introduce ViewModels by default. This architecture is MV with services and app state:

```text
View -> local UI state and layout
Service -> business logic and external systems
DataStore -> global observable app state
Model -> data shape
```

Only use a ViewModel when the user explicitly asks, the existing app already depends on one, or a compatibility refactor requires it.

## Reference Routing

- Load `references/services.md` when designing services, moving business logic out of views, or deciding how views consume dependencies.
- Load `references/datastore.md` when designing global state, app-level source of truth, credits, subscriptions, remote config, persistence, or DataStore/service coordination.
- Load `references/observation-environment.md` before writing `@Observable`, `.environment(_:)`, `@Environment(Type.self)`, optional environment reads, or `@Bindable` code.
