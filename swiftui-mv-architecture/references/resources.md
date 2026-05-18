# Resources

## Purpose

`Resources` is a root-level folder for raw non-Swift app files.

It may contain:

```text
asset catalogs
images
icons
illustrations
audio files
video files
JSON files
local data files
markdown files
text files
graphics
PDF files
SVG files
fonts
external/static app files
```

Example:

```text
Resources
├── Assets
│   ├── Icons.xcassets
│   ├── Images.xcassets
│   └── Illustrations.xcassets
├── Audio
│   └── success_sound.mp3
├── Data
│   └── onboarding_questions.json
├── Graphics
│   └── background.svg
├── Videos
│   └── onboarding_loop.mp4
├── Fonts
│   └── CustomFont.otf
└── Files
    └── terms.md
```

## Rules

Resources must not contain:

```text
Swift source files
Views
Models
Enums
Services
DesignSystem Swift files
Utils
Business logic
```

## Resources vs DesignSystem

`Resources` stores physical files and raw assets.

`DesignSystem/Foundation` stores SwiftUI-native access layers and design tokens.

Example:

```text
Resources/Assets/Icons.xcassets -> actual icon assets
DesignSystem/Foundation/Icons/Icons.swift -> Image extension
```

Raw icon assets belong in `Resources`. Custom Swift accessors for those icons belong in `DesignSystem/Foundation/Icons`.
