#!/usr/bin/env python3
"""Read-only structural audit for the SwiftUI MV architecture."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


EXPECTED_ROOT_FOLDERS = {
    "Views",
    "Models",
    "Enums",
    "Services",
    "DataStore",
    "DesignSystem",
    "Resources",
    "Utils",
}

IGNORED_ROOT_DIRS = {
    "__pycache__",
    ".build",
    ".git",
    ".github",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".swiftpm",
    "Build",
    "DerivedData",
    "Docs",
    "Documentation",
    "Frameworks",
    "Packages",
    "Preview Content",
    "Products",
    "Scripts",
    "Sources",
    "Supporting Files",
    "Tests",
    "UITests",
    "UnitTests",
    "fastlane",
    "metadata",
}

SERVICE_INSTANTIATION_RE = re.compile(
    r"=\s*(?:[A-Z][A-Za-z0-9_]*Service|APIClient|KeychainService|StorageService)\s*\("
)
STRUCT_VIEW_RE = re.compile(r"\bstruct\s+[A-Za-z_][A-Za-z0-9_]*\s*:\s*View\b")
OBSERVABLE_OBJECT_RE = re.compile(r"\bObservableObject\b")
VIEWMODEL_TYPE_RE = re.compile(r"\b(?:class|struct|actor|protocol)\s+[A-Za-z_][A-Za-z0-9_]*ViewModel\b")
LEGACY_VIEW_OBSERVATION_RE = re.compile(r"@(EnvironmentObject|StateObject|ObservedObject)\b")
PUBLISHED_RE = re.compile(r"@Published\b")

IGNORED_PATH_PARTS = IGNORED_ROOT_DIRS | {
    ".DS_Store",
    "__MACOSX",
}


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    path: str
    message: str


def relative(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="ignore")


def is_ignored_path(path: Path) -> bool:
    return any(part in IGNORED_PATH_PARTS for part in path.parts)


def swift_files(path: Path) -> list[Path]:
    if not path.exists():
        return []
    return sorted(swift_file for swift_file in path.rglob("*.swift") if not is_ignored_path(swift_file))


def add(findings: list[Finding], strict: bool, code: str, path: Path, root: Path, message: str) -> None:
    findings.append(
        Finding(
            severity="error" if strict else "warning",
            code=code,
            path=relative(path, root),
            message=message,
        )
    )


def matching_brace_index(text: str, open_index: int) -> int | None:
    depth = 0
    for index in range(open_index, len(text)):
        char = text[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return index
    return None


def text_without_parent_view_extensions(text: str, view_name: str) -> str:
    extension_re = re.compile(rf"\bextension\s+{re.escape(view_name)}\b[^{{]*{{")
    chars = list(text)

    for match in extension_re.finditer(text):
        open_index = text.find("{", match.start(), match.end())
        if open_index == -1:
            continue
        close_index = matching_brace_index(text, open_index)
        if close_index is None:
            continue
        for index in range(match.start(), close_index + 1):
            chars[index] = " "

    return "".join(chars)


def screen_extension_files(root: Path) -> list[tuple[Path, str]]:
    views = root / "Views"
    if not views.exists():
        return []

    files: list[tuple[Path, str]] = []
    for swift_file in swift_files(views):
        try:
            parts = swift_file.relative_to(views).parts
        except ValueError:
            continue
        if len(parts) >= 3 and parts[1] == "Extensions":
            files.append((swift_file, parts[0]))
    return files


def root_folder_findings(root: Path, strict: bool) -> list[Finding]:
    findings: list[Finding] = []
    existing = {child.name for child in root.iterdir() if child.is_dir()}

    for folder in sorted(EXPECTED_ROOT_FOLDERS - existing):
        add(
            findings,
            strict,
            "missing-root-folder",
            root / folder,
            root,
            f"Expected root architecture folder '{folder}' is missing.",
        )

    for folder in sorted(existing - EXPECTED_ROOT_FOLDERS - IGNORED_ROOT_DIRS):
        if folder.startswith(".") or folder.endswith((".xcodeproj", ".xcworkspace", ".playground")):
            continue
        add(
            findings,
            strict,
            "unexpected-root-folder",
            root / folder,
            root,
            f"Root folder '{folder}' is outside the SwiftUI MV architecture folders.",
        )

    return findings


def global_states_findings(root: Path, strict: bool) -> list[Finding]:
    states = root / "States"
    if not states.exists():
        return []
    findings: list[Finding] = []
    add(
        findings,
        strict,
        "global-states-folder",
        states,
        root,
        "Do not create a global States folder; view-specific state belongs in the corresponding view group and shared enums belong in Enums.",
    )
    return findings


def resources_findings(root: Path, strict: bool) -> list[Finding]:
    resources = root / "Resources"
    if not resources.exists():
        return []
    findings: list[Finding] = []
    for swift_file in swift_files(resources):
        add(
            findings,
            strict,
            "swift-in-resources",
            swift_file,
            root,
            "Resources must contain non-Swift files only.",
        )
    return findings


def view_folder_findings(root: Path, strict: bool) -> list[Finding]:
    views = root / "Views"
    if not views.exists():
        return []

    findings: list[Finding] = []
    for child in sorted(views.iterdir()):
        if not child.is_dir() or child.name == "Extensions":
            continue
        expected = child / f"{child.name}.swift"
        if not expected.exists():
            add(
                findings,
                strict,
                "missing-main-view-file",
                expected,
                root,
                f"View folder '{child.name}' should contain '{child.name}.swift'.",
            )

    for extension_file, view_name in screen_extension_files(root):
        text = text_without_parent_view_extensions(read_text(extension_file), view_name)
        if STRUCT_VIEW_RE.search(text):
            add(
                findings,
                strict,
                "top-level-view-struct-in-extension",
                extension_file,
                root,
                "Screen-specific View structs in Extensions should be nested inside extension ViewName; move generic or reusable UI to DesignSystem.",
            )

    return findings


def enum_findings(root: Path, strict: bool) -> list[Finding]:
    enums = root / "Enums"
    views = root / "Views"
    if not enums.exists() or not views.exists():
        return []

    view_names = {path.name.removesuffix("View") for path in views.iterdir() if path.is_dir()}
    findings: list[Finding] = []
    for state_file in swift_files(enums):
        if not state_file.name.endswith("State.swift"):
            continue
        stem = state_file.stem
        if stem.endswith("ViewState"):
            prefix = stem.removesuffix("ViewState")
        else:
            prefix = stem.removesuffix("State")
        if prefix in view_names:
            add(
                findings,
                strict,
                "view-state-in-enums",
                state_file,
                root,
                "View-specific state should live in the corresponding view folder, not in root Enums.",
            )
    return findings


def direct_service_creation_findings(root: Path, strict: bool) -> list[Finding]:
    views = root / "Views"
    if not views.exists():
        return []
    findings: list[Finding] = []
    for swift_file in swift_files(views):
        text = read_text(swift_file)
        if SERVICE_INSTANTIATION_RE.search(text):
            add(
                findings,
                strict,
                "direct-service-instantiation-in-view",
                swift_file,
                root,
                "Views should consume services through Environment instead of instantiating services directly.",
            )
    return findings


def datastore_findings(root: Path, strict: bool) -> list[Finding]:
    datastore = root / "DataStore"
    if not datastore.exists():
        return []
    findings: list[Finding] = []
    for swift_file in swift_files(datastore):
        text = read_text(swift_file)
        if OBSERVABLE_OBJECT_RE.search(text):
            add(
                findings,
                strict,
                "observable-object-in-datastore",
                swift_file,
                root,
                "DataStore should use Swift Observation (@Observable) by default instead of ObservableObject.",
            )
    return findings


def viewmodel_findings(root: Path, strict: bool) -> list[Finding]:
    findings: list[Finding] = []
    for swift_file in swift_files(root):
        text = read_text(swift_file)
        if "ViewModel" in swift_file.stem:
            add(
                findings,
                strict,
                "viewmodel-file",
                swift_file,
                root,
                "ViewModel files are not part of SwiftUI MV by default; keep only when the user asks or compatibility requires it.",
            )
        if VIEWMODEL_TYPE_RE.search(text):
            add(
                findings,
                strict,
                "viewmodel-type",
                swift_file,
                root,
                "ViewModel types are not part of SwiftUI MV by default; prefer local view state, services, and DataStore.",
            )
    return findings


def legacy_observation_findings(root: Path, strict: bool) -> list[Finding]:
    findings: list[Finding] = []
    for folder_name in ("Views", "Services", "DataStore"):
        folder = root / folder_name
        for swift_file in swift_files(folder):
            text = read_text(swift_file)
            if LEGACY_VIEW_OBSERVATION_RE.search(text):
                add(
                    findings,
                    strict,
                    "legacy-observation-wrapper",
                    swift_file,
                    root,
                    "New SwiftUI MV code should prefer Observation APIs over @EnvironmentObject, @StateObject, or @ObservedObject.",
                )
            if folder_name in {"Services", "DataStore"} and PUBLISHED_RE.search(text):
                add(
                    findings,
                    strict,
                    "published-in-observation-area",
                    swift_file,
                    root,
                    "Services and DataStore should use @Observable with plain stored properties by default, not @Published.",
                )
    return findings


def audit(root: Path, strict: bool) -> list[Finding]:
    checks = [
        root_folder_findings,
        global_states_findings,
        resources_findings,
        view_folder_findings,
        enum_findings,
        direct_service_creation_findings,
        datastore_findings,
        viewmodel_findings,
        legacy_observation_findings,
    ]
    findings: list[Finding] = []
    for check in checks:
        findings.extend(check(root, strict))
    return findings


def print_text(findings: list[Finding], root: Path) -> None:
    if not findings:
        print(f"No SwiftUI MV audit findings for {root}.")
        return

    print(f"SwiftUI MV audit findings for {root}:")
    for finding in findings:
        print(f"[{finding.severity}] {finding.code}: {finding.path}")
        print(f"  {finding.message}")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Audit SwiftUI MV project structure.")
    parser.add_argument("project_root", help="Path to the SwiftUI app source root to audit.")
    parser.add_argument("--json", action="store_true", help="Print findings as JSON.")
    parser.add_argument("--strict", action="store_true", help="Report findings as errors and exit non-zero.")
    args = parser.parse_args(argv)

    root = Path(args.project_root).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        print(f"error: project root does not exist or is not a directory: {root}", file=sys.stderr)
        return 2

    findings = audit(root, args.strict)

    if args.json:
        print(json.dumps([asdict(finding) for finding in findings], indent=2))
    else:
        print_text(findings, root)

    if args.strict and findings:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
