#!/usr/bin/env python3
"""Validate plugin packaging before publishing SwiftUI MV Skill."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

JSON_FILES = [
    ".claude-plugin/plugin.json",
    ".claude-plugin/marketplace.json",
    ".codex-plugin/plugin.json",
    ".agents/plugins/marketplace.json",
]


def load_json(relative_path: str) -> Any:
    path = ROOT / relative_path
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        raise AssertionError(f"{relative_path} is missing")
    except json.JSONDecodeError as error:
        raise AssertionError(f"{relative_path} is invalid JSON: {error}") from error


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate_claude_manifests() -> None:
    plugin = load_json(".claude-plugin/plugin.json")
    marketplace = load_json(".claude-plugin/marketplace.json")
    entries = marketplace.get("plugins", [])

    require("version" not in plugin, "Claude plugin.json must omit version for commit-SHA updates")
    require(isinstance(entries, list) and entries, "Claude marketplace must list plugins")

    swiftui_mv = next((entry for entry in entries if entry.get("name") == "swiftui-mv"), None)
    require(swiftui_mv is not None, "Claude marketplace must include swiftui-mv")
    require(
        "version" not in swiftui_mv,
        "Claude marketplace swiftui-mv entry must omit version for commit-SHA updates",
    )
    require(swiftui_mv.get("source") == "./", "Claude marketplace should point at repo root")


def validate_codex_manifests() -> None:
    plugin = load_json(".codex-plugin/plugin.json")
    marketplace = load_json(".agents/plugins/marketplace.json")
    entries = marketplace.get("plugins", [])

    require(plugin.get("name") == "swiftui-mv", "Codex plugin name must be swiftui-mv")
    require(plugin.get("version"), "Codex plugin.json must keep an explicit version")
    require(isinstance(entries, list) and entries, "Codex marketplace must list plugins")

    swiftui_mv = next((entry for entry in entries if entry.get("name") == "swiftui-mv"), None)
    require(swiftui_mv is not None, "Codex marketplace must include swiftui-mv")
    require(swiftui_mv.get("category") == "Development", "Codex marketplace category must be Development")

    policy = swiftui_mv.get("policy", {})
    require(policy.get("installation") == "AVAILABLE", "Codex policy.installation must be AVAILABLE")
    require(policy.get("authentication") == "ON_INSTALL", "Codex policy.authentication must be ON_INSTALL")

    source = swiftui_mv.get("source", {})
    require(source.get("source") == "url", "Codex marketplace source must be a Git URL source")
    require(
        source.get("url") == "https://github.com/ataberkturan/swiftui-mv-skill.git",
        "Codex marketplace source URL must point at this repository",
    )
    require(source.get("ref") == "main", "Codex marketplace source should track main")


def run_unittests() -> None:
    subprocess.run(
        [
            sys.executable,
            "-m",
            "unittest",
            "tests.test_audit_swiftui_mv",
            "tests.test_audit_swiftui_mv_architecture",
        ],
        cwd=ROOT,
        check=True,
    )


def main() -> int:
    try:
        for relative_path in JSON_FILES:
            load_json(relative_path)
        validate_claude_manifests()
        validate_codex_manifests()
        run_unittests()
    except AssertionError as error:
        print(f"release validation failed: {error}", file=sys.stderr)
        return 1
    except subprocess.CalledProcessError as error:
        print(f"release validation failed: tests exited with {error.returncode}", file=sys.stderr)
        return error.returncode

    print("release validation passed")
    print("Reminder: bump .codex-plugin/plugin.json version whenever Codex plugin content changes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
