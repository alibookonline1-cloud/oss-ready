from dataclasses import dataclass
from pathlib import Path
import subprocess


@dataclass
class CheckResult:
    key: str
    name: str
    passed: bool
    weight: int
    message: str
    suggestion: str


class RepoChecker:
    def __init__(self, path: str = "."):
        self.path = Path(path).resolve()
        if not self.path.exists():
            raise FileNotFoundError(f"Path not found: {self.path}")

    def _exists(self, *names):
        return any((self.path / name).exists() for name in names)

    def _run_git(self, *args):
        try:
            result = subprocess.run(
                ["git", "-C", str(self.path)] + list(args),
                capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None

    def check_readme(self) -> CheckResult:
        passed = self._exists("README.md", "README.rst", "README.txt")
        return CheckResult(
            key="readme",
            name="README",
            passed=passed,
            weight=10,
            message="README found" if passed else "README missing",
            suggestion="Create a README.md with project description, installation, and usage."
        )

    def check_license(self) -> CheckResult:
        passed = self._exists("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING")
        return CheckResult(
            key="license",
            name="LICENSE",
            passed=passed,
            weight=10,
            message="LICENSE found" if passed else "LICENSE missing",
            suggestion="Add an open source license (e.g., MIT, Apache-2.0). See choosealicense.com."
        )

    def check_gitignore(self) -> CheckResult:
        passed = self._exists(".gitignore")
        return CheckResult(
            key="gitignore",
            name=".gitignore",
            passed=passed,
            weight=8,
            message=".gitignore found" if passed else ".gitignore missing",
            suggestion="Create a .gitignore to avoid committing unnecessary files."
        )

    def check_contributing(self) -> CheckResult:
        passed = self._exists("CONTRIBUTING.md", "CONTRIBUTING.rst", "CONTRIBUTING.txt")
        return CheckResult(
            key="contributing",
            name="CONTRIBUTING",
            passed=passed,
            weight=7,
            message="CONTRIBUTING found" if passed else "CONTRIBUTING missing",
            suggestion="Add CONTRIBUTING.md to guide new contributors."
        )

    def check_code_of_conduct(self) -> CheckResult:
        passed = self._exists("CODE_OF_CONDUCT.md", "CODE_OF_CONDUCT.rst", "CODE_OF_CONDUCT.txt")
        return CheckResult(
            key="code_of_conduct",
            name="CODE_OF_CONDUCT",
            passed=passed,
            weight=5,
            message="CODE_OF_CONDUCT found" if passed else "CODE_OF_CONDUCT missing",
            suggestion="Add CODE_OF_CONDUCT.md to set community expectations."
        )

    def check_changelog(self) -> CheckResult:
        passed = self._exists("CHANGELOG.md", "CHANGELOG.rst", "CHANGELOG.txt")
        return CheckResult(
            key="changelog",
            name="CHANGELOG",
            passed=passed,
            weight=5,
            message="CHANGELOG found" if passed else "CHANGELOG missing",
            suggestion="Add CHANGELOG.md to track notable changes."
        )

    def check_security(self) -> CheckResult:
        passed = self._exists("SECURITY.md", "SECURITY.rst", "SECURITY.txt")
        return CheckResult(
            key="security",
            name="SECURITY",
            passed=passed,
            weight=5,
            message="SECURITY found" if passed else "SECURITY missing",
            suggestion="Add SECURITY.md to explain how to report vulnerabilities."
        )

    def check_git(self) -> CheckResult:
        passed = (self.path / ".git").exists()
        return CheckResult(
            key="git",
            name="Git repository",
            passed=passed,
            weight=5,
            message="Git repository initialized" if passed else "Not a git repository",
            suggestion="Run `git init` to initialize a repository."
        )

    def check_remote(self) -> CheckResult:
        remote = self._run_git("remote", "get-url", "origin")
        passed = bool(remote and "github.com" in remote)
        return CheckResult(
            key="remote",
            name="GitHub remote",
            passed=passed,
            weight=5,
            message=f"Remote: {remote}" if remote else "No GitHub remote",
            suggestion="Add a GitHub remote: `git remote add origin https://github.com/USER/REPO.git`"
        )

    def check_sensitive(self) -> CheckResult:
        env_file = self.path / ".env"
        if not env_file.exists():
            return CheckResult(
                key="sensitive",
                name="Sensitive files",
                passed=True,
                weight=10,
                message="No .env file found",
                suggestion=""
            )
        gitignore = self.path / ".gitignore"
        ignored = False
        if gitignore.exists():
            content = gitignore.read_text(errors="ignore")
            ignored = any(line.strip() == ".env" for line in content.splitlines())
        passed = ignored
        return CheckResult(
            key="sensitive",
            name="Sensitive files",
            passed=passed,
            weight=10,
            message=".env is gitignored" if passed else ".env is NOT gitignored",
            suggestion="Add .env to .gitignore and remove it from git history if already committed."
        )

    def check_workflow(self) -> CheckResult:
        workflows = self.path / ".github" / "workflows"
        passed = workflows.exists() and (
            any(workflows.glob("*.yml")) or any(workflows.glob("*.yaml"))
        )
        return CheckResult(
            key="workflow",
            name="CI workflow",
            passed=passed,
            weight=10,
            message="GitHub Actions workflow found" if passed else "No GitHub Actions workflow",
            suggestion="Add a CI workflow in .github/workflows/ci.yml to run tests automatically."
        )

    def check_tests(self) -> CheckResult:
        tests_dir = self.path / "tests"
        passed = tests_dir.exists() or any(self.path.glob("test_*.py")) or any(self.path.glob("**/test_*.py"))
        return CheckResult(
            key="tests",
            name="Tests",
            passed=passed,
            weight=10,
            message="Tests found" if passed else "No tests found",
            suggestion="Add tests to ensure code quality and catch regressions."
        )

    def run_all(self):
        checks = [
            self.check_readme,
            self.check_license,
            self.check_gitignore,
            self.check_contributing,
            self.check_code_of_conduct,
            self.check_changelog,
            self.check_security,
            self.check_git,
            self.check_remote,
            self.check_sensitive,
            self.check_workflow,
            self.check_tests,
        ]
        return [check() for check in checks]

    def score(self, results):
        total_weight = sum(r.weight for r in results)
        earned = sum(r.weight for r in results if r.passed)
        return (earned / total_weight) * 100 if total_weight else 0
