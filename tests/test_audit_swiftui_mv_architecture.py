from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "swiftui-mv" / "scripts" / "audit_swiftui_mv.py"
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


def load_audit_module():
    spec = importlib.util.spec_from_file_location("audit_swiftui_mv", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


audit_module = load_audit_module()


class AuditSwiftUIMVTests(unittest.TestCase):
    def make_root(self, tmpdir: str, folders: set[str] | None = None) -> Path:
        root = Path(tmpdir)
        for folder in folders or EXPECTED_ROOT_FOLDERS:
            (root / folder).mkdir(parents=True, exist_ok=True)
        return root

    def write(self, root: Path, relative_path: str, text: str = "") -> Path:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def codes(self, root: Path, strict: bool = False) -> list[str]:
        return [finding.code for finding in audit_module.audit(root, strict=strict)]

    def assert_has_codes(self, root: Path, expected_codes: set[str]) -> None:
        codes = set(self.codes(root))
        self.assertTrue(expected_codes.issubset(codes), f"missing {expected_codes - codes} from {codes}")

    def test_clean_architecture_fixture_returns_no_findings(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = self.make_root(tmpdir)
            self.write(
                root,
                "Views/HomeView/HomeView.swift",
                'import SwiftUI\nstruct HomeView: View { var body: some View { Text("Hi") } }\n',
            )
            (root / "__pycache__").mkdir()
            self.write(root, "Resources/__pycache__/Generated.swift", "struct IgnoredCacheFile {}\n")
            self.write(root, ".DS_Store", "ignored")

            self.assertEqual(self.codes(root), [])

    def test_missing_expected_root_folders(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = self.make_root(tmpdir, folders={"Views"})

            self.assertIn("missing-root-folder", self.codes(root))

    def test_unexpected_root_folder(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = self.make_root(tmpdir)
            (root / "FeatureA").mkdir()

            self.assertIn("unexpected-root-folder", self.codes(root))

    def test_global_states_folder(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = self.make_root(tmpdir)
            (root / "States").mkdir()

            self.assertIn("global-states-folder", self.codes(root))

    def test_swift_files_under_resources(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = self.make_root(tmpdir)
            self.write(root, "Resources/Bad.swift", "struct Bad {}\n")

            self.assertIn("swift-in-resources", self.codes(root))

    def test_missing_main_view_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = self.make_root(tmpdir)
            (root / "Views/FooView").mkdir()

            self.assertIn("missing-main-view-file", self.codes(root))

    def test_nested_struct_view_inside_parent_extension_is_allowed(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = self.make_root(tmpdir)
            self.write(root, "Views/HomeView/HomeView.swift")
            self.write(
                root,
                "Views/HomeView/Extensions/HomeView+PromptDockView.swift",
                (
                    "import SwiftUI\n"
                    "extension HomeView {\n"
                    "    private struct PromptDockView: View {\n"
                    "        @Binding var prompt: String\n"
                    "        var body: some View { TextField(\"Prompt\", text: $prompt) }\n"
                    "    }\n"
                    "}\n"
                ),
            )

            self.assertNotIn("top-level-view-struct-in-extension", self.codes(root))

    def test_top_level_struct_view_inside_extension_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = self.make_root(tmpdir)
            self.write(root, "Views/HomeView/HomeView.swift")
            self.write(
                root,
                "Views/HomeView/Extensions/HomeView+PromptDockView.swift",
                'import SwiftUI\nstruct PromptDockView: View { var body: some View { Text("Prompt") } }\n',
            )

            self.assertIn("top-level-view-struct-in-extension", self.codes(root))

    def test_view_specific_state_in_root_enums(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = self.make_root(tmpdir)
            self.write(root, "Views/HomeView/HomeView.swift")
            self.write(root, "Enums/HomeState.swift", "enum HomeState { case idle }\n")

            self.assertIn("view-state-in-enums", self.codes(root))

    def test_direct_service_creation_in_view(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = self.make_root(tmpdir)
            self.write(
                root,
                "Views/LoginView/LoginView.swift",
                'import SwiftUI\nstruct LoginView: View { private let auth = AuthService()\nvar body: some View { Text("Login") } }\n',
            )

            self.assertIn("direct-service-instantiation-in-view", self.codes(root))

    def test_observable_object_in_datastore(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = self.make_root(tmpdir)
            self.write(root, "DataStore/AppDataStore.swift", "final class AppDataStore: ObservableObject {}\n")

            self.assertIn("observable-object-in-datastore", self.codes(root))

    def test_viewmodel_files_and_types(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = self.make_root(tmpdir)
            self.write(root, "Views/HomeView/HomeViewModel.swift", "final class HomeViewModel {}\n")

            self.assert_has_codes(root, {"viewmodel-file", "viewmodel-type"})

    def test_legacy_observation_wrappers_and_published_properties(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = self.make_root(tmpdir)
            self.write(
                root,
                "Views/HomeView/HomeView.swift",
                "import SwiftUI\nstruct HomeView: View { @EnvironmentObject var store: AppDataStore }\n",
            )
            self.write(
                root,
                "Services/AuthService.swift",
                "final class AuthService: ObservableObject { @Published var isSignedIn = false }\n",
            )

            self.assert_has_codes(root, {"legacy-observation-wrapper", "published-in-observation-area"})

    def test_json_cli_output(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = self.make_root(tmpdir)
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(root), "--json"],
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertEqual(json.loads(result.stdout), [])

    def test_strict_cli_exits_nonzero_and_marks_errors(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = self.make_root(tmpdir, folders={"Views"})
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(root), "--json", "--strict"],
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 1)
            findings = json.loads(result.stdout)
            self.assertTrue(findings)
            self.assertTrue(all(finding["severity"] == "error" for finding in findings))

    def test_invalid_project_root_cli_exits_two(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            missing = Path(tmpdir) / "missing"
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(missing)],
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 2)
            self.assertIn("project root does not exist", result.stderr)


if __name__ == "__main__":
    unittest.main()
