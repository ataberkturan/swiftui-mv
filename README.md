# SwiftUI MV Skill

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/Platform-iOS%20|%20macOS-000000.svg?logo=apple)](https://developer.apple.com/swift/)
[![Swift](https://img.shields.io/badge/Swift-5.10+-F05138.svg?logo=swift&logoColor=white)](https://swift.org)
[![Codex](https://img.shields.io/badge/Codex-Skill-111111.svg)](https://openai.com/codex/)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-blueviolet.svg)](https://claude.ai/code)

SwiftUI MV Skill is an agent skill for building, refactoring, and reviewing
SwiftUI apps with a clean `MV + Services + DataStore + DesignSystem`
architecture.

It helps Agents make consistent architecture decisions while working inside
SwiftUI projects. Instead of creating ViewModels by default, it keeps UI, state,
business logic, reusable components, resources, and utilities in clear ownership
boundaries.

## Who This Is For

- Developers who want SwiftUI features organized without defaulting to MVVM.
- Teams standardizing app folders around Views, Models, Enums, Services,
  DataStore, DesignSystem, Resources, and Utils.
- Agent workflows that need repeatable guidance for Swift Observation,
  service injection, reusable UI boundaries, and architecture reviews.
- SwiftUI projects that need a lightweight audit before refactors or code
  review.

## How To Use This Skill

### Option A: Using skills.sh

Install this skill with the open `skills` CLI:

```bash
npx skills add https://github.com/ataberkturan/swiftui-mv-skill --skill swiftui-mv
```

For Codex:

```bash
npx skills add https://github.com/ataberkturan/swiftui-mv-skill --skill swiftui-mv -a codex -g
```

For Claude Code:

```bash
npx skills add https://github.com/ataberkturan/swiftui-mv-skill --skill swiftui-mv -a claude-code -g
```

Then ask your agent to use the skill, for example:

> Use the SwiftUI MV skill and review this app's architecture boundaries.

Update standalone `skills.sh` installs with:

```bash
npx skills update swiftui-mv
```

### Option B: Claude Code Plugin

This repository includes a Claude Code marketplace at
`.claude-plugin/marketplace.json` and a plugin manifest at
`.claude-plugin/plugin.json`.

Add the marketplace:

```text
/plugin marketplace add ataberkturan/swiftui-mv-skill
```

Install the plugin:

```text
/plugin install swiftui-mv@swiftui-mv-skill
```

After installation, the skill is available as a namespaced plugin skill:

```text
/swiftui-mv:swiftui-mv
```

Claude Code can auto-update installed marketplace plugins at startup. Enable it
from `/plugin` -> Marketplaces -> `swiftui-mv-skill` -> Enable auto-update.
This repository intentionally omits Claude plugin version pins, so Claude Code
uses the Git commit SHA as the update key and can receive every committed
marketplace update. When Claude reports that plugins were updated, run:

```text
/reload-plugins
```

For a team repository, project settings can prompt collaborators to add this
marketplace and enable startup updates:

```json
{
  "extraKnownMarketplaces": {
    "swiftui-mv-skill": {
      "source": {
        "source": "github",
        "repo": "ataberkturan/swiftui-mv-skill"
      },
      "autoUpdate": true
    }
  },
  "enabledPlugins": {
    "swiftui-mv@swiftui-mv-skill": true
  }
}
```

### Option C: Codex Plugin

This repository includes a Codex marketplace at
`.agents/plugins/marketplace.json` and a Codex plugin manifest at
`.codex-plugin/plugin.json`. Add the marketplace with the official Codex CLI:

```bash
codex plugin marketplace add ataberkturan/swiftui-mv-skill
```

If `codex plugin marketplace` is not available, update Codex to a version that
supports plugin marketplace subcommands.

Then open the Codex plugin directory and install or enable `SwiftUI MV`.

Refresh the Git-backed marketplace later with:

```bash
codex plugin marketplace upgrade swiftui-mv-skill
```

Codex currently documents marketplace refresh/upgrade rather than a third-party
startup auto-update toggle. Keep `.codex-plugin/plugin.json` versioned and bump
that version whenever Codex plugin content changes so Codex refreshes its
versioned plugin cache correctly.

### Option D: Codex / OpenAI-Compatible Tools

This repository includes an `agents/openai.yaml` manifest. Copy or symlink the
`swiftui-mv/` folder into your Codex skills directory:

```bash
cp -R swiftui-mv/ "$CODEX_HOME/skills/swiftui-mv"
```

You can also install from inside Codex with Skill Installer:

```text
$skill-installer install https://github.com/ataberkturan/swiftui-mv-skill/tree/main/swiftui-mv
```

### Option E: Manual Install

Clone this repository and copy the same `swiftui-mv/` skill folder into your
agent's skills directory:

```bash
git clone https://github.com/ataberkturan/swiftui-mv-skill.git
mkdir -p ~/.codex/skills ~/.claude/skills
cp -R swiftui-mv-skill/swiftui-mv ~/.codex/skills/
cp -R swiftui-mv-skill/swiftui-mv ~/.claude/skills/
```

Restart your agent if the skill does not appear immediately.

## Keeping Installs Updated

Standalone skills and marketplace plugins update through different mechanisms:

- Standalone `skills.sh` installs: run `npx skills update swiftui-mv`, or
  `npx skills update -g` for global installs.
- Manual folder installs: pull or copy the latest `swiftui-mv/` folder from the
  GitHub repository into your local skills directory.
- Claude Code plugin installs: enable marketplace auto-update in `/plugin`.
  Claude Code refreshes the marketplace at startup and prompts for
  `/reload-plugins` when an installed plugin changes.
- Codex plugin installs: run `codex plugin marketplace upgrade
  swiftui-mv-skill`, then restart or reload Codex if the updated skill does not
  appear immediately.

For standalone Claude Code skills, an optional `SessionStart` hook can run
`npx skills update -g -y` at the beginning of each session:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup",
        "hooks": [
          {
            "type": "command",
            "command": "npx skills update -g -y >/tmp/swiftui-mv-skills-update.log 2>&1 || true"
          }
        ]
      }
    ]
  }
}
```

Only use automatic standalone updates for repositories and package sources you
trust. This hook runs network code on session startup and may silently pull new
skill instructions before you begin work.

## What's Inside

SwiftUI MV Skill guides an AI coding agent to:

- inspect the existing SwiftUI project structure before making changes
- keep screen-local state inside SwiftUI views
- move business logic, networking, persistence, auth, subscriptions, and domain
  actions into services
- keep global app state in an Observation-based DataStore
- organize reusable UI code inside a DesignSystem
- separate raw app assets and files into Resources
- place general-purpose helpers and extensions inside Utils
- avoid creating ViewModels unless the project already uses them or the user
  explicitly asks for that architecture
- run a read-only architecture audit with the bundled helper script

This skill is opinionated about ownership boundaries, not about visual style.
It does not try to replace native SwiftUI design guidance, animation guidance,
or app-specific product decisions.

## Architecture Model

The skill prefers this root-level SwiftUI app structure when the app needs those
areas:

```text
Project
├── Views
├── Models
├── Enums
├── Services
├── DataStore
├── DesignSystem
├── Resources
└── Utils
```

Folder responsibilities:

- `Views`: SwiftUI screens, screen-local state, local view fragments, and
  screen-specific extensions.
- `Models`: data models, domain models, API models, persistence models, and
  DTO-like types.
- `Enums`: shared app, route, mode, category, domain, and service-level enum
  types.
- `Services`: business logic and external systems such as networking,
  authentication, storage, subscriptions, remote config, notifications,
  payments, and backend communication.
- `DataStore`: app-wide observable state and global source of truth, preferably
  using Swift Observation with `@Observable`.
- `DesignSystem`: reusable UI components, button styles, visual modifiers,
  colors, typography, icons, spacing, and native SwiftUI style extensions.
- `Resources`: raw non-Swift files such as asset catalogs, images, icons, JSON,
  audio, video, fonts, markdown, PDFs, and SVGs.
- `Utils`: general helper code, Swift extensions, technical view modifiers,
  validators, date helpers, and other non-design-system utilities.

Unused folders do not need to be created just to satisfy the structure.

## Architecture Audit

The bundled audit helper performs a read-only structural check for common
SwiftUI MV boundary violations:

```bash
python3 swiftui-mv/scripts/audit_swiftui_mv.py /path/to/SwiftUI/project
```

Use JSON output for automation:

```bash
python3 swiftui-mv/scripts/audit_swiftui_mv.py /path/to/SwiftUI/project --json
```

Use strict mode when warnings should fail the audit:

```bash
python3 swiftui-mv/scripts/audit_swiftui_mv.py /path/to/SwiftUI/project --strict
```

The audit is intentionally conservative. Treat its findings as prompts for code
inspection, not as a complete Swift semantic analysis.

## Skill Structure

```text
swiftui-mv/
  SKILL.md
  references/
    core-architecture.md - Root folders, high-level boundaries, routing, and the no-default-ViewModel rule
    services.md - Service responsibilities, business logic boundaries, injection, and Observation requirements
    datastore.md - Global app state, app-level source of truth, persistence coordination, and store/service boundaries
    observation-environment.md - @Observable, SwiftUI Environment injection, @Bindable, and ObservableObject migration
    view-organization.md - Screen folders, local components, view extensions, and screen-specific state
    design-system.md - Reusable UI components, native SwiftUI styles, tokens, and visual modifiers
    resources.md - Raw non-Swift app files and the Resources vs DesignSystem boundary
    utils.md - General helpers, extensions, validators, and the Utils vs DesignSystem boundary
    examples.md - Canonical folder trees and correct/wrong architecture examples
  scripts/
    audit_swiftui_mv.py - Read-only structural audit for SwiftUI MV boundary violations
```

`swiftui-mv/` is the canonical skill folder. It contains the required
`SKILL.md`, optional UI metadata, references, and the read-only audit helper.

## Publishing

This repository is prepared for multiple distribution paths:

- `skills.sh`: install with `npx skills add ... --skill swiftui-mv`.
- Claude Code plugin marketplace: `.claude-plugin/marketplace.json` points to
  this repository as a plugin source and uses Git commit SHA updates.
- Codex plugin marketplace: `.agents/plugins/marketplace.json` exposes the
  plugin to Codex, and `.codex-plugin/plugin.json` describes the plugin bundle.
- Codex/OpenAI-compatible tools: `agents/openai.yaml` lists the skill metadata.
- `pi`: `package.json` declares the skill folder under `pi.skills`.

Before publishing a release, validate local discovery:

```bash
python3 scripts/validate_release.py
npx skills add . --skill swiftui-mv --list
```

When Codex plugin files change, bump `.codex-plugin/plugin.json` because Codex
uses that version for its plugin cache. Claude Code intentionally has no plugin
version pin in this repository, so Git-backed installs can update on every
commit.

## Contributing

Contributions should keep `SKILL.md` concise and move detailed guidance into
topic-specific files under `swiftui-mv/references/`. The skill should remain
focused on SwiftUI MV architecture boundaries rather than generic SwiftUI
styling, animation, or platform API coverage.

## License

MIT. Created by Ataberk Turan.

## References

- Thomas Ricouard, ["Removing the M from MVVM with SwiftUI"](https://blog.stackademic.com/removing-the-m-from-mvvm-with-swiftui-a58b239e9e3e),
  Stackademic, Apr 8, 2024. This article inspired parts of the service-oriented
  guidance behind this skill.
