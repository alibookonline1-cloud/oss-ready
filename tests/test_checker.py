import tempfile
from pathlib import Path
import unittest
from oss_ready.checker import RepoChecker


class TestRepoChecker(unittest.TestCase):
    def test_missing_readme(self):
        with tempfile.TemporaryDirectory() as tmp:
            checker = RepoChecker(tmp)
            result = checker.check_readme()
            self.assertFalse(result.passed)

    def test_readme_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "README.md").write_text("# Test")
            checker = RepoChecker(tmp)
            result = checker.check_readme()
            self.assertTrue(result.passed)

    def test_license_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "LICENSE").write_text("MIT")
            checker = RepoChecker(tmp)
            result = checker.check_license()
            self.assertTrue(result.passed)

    def test_sensitive_env_not_ignored(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, ".env").write_text("SECRET=123")
            checker = RepoChecker(tmp)
            result = checker.check_sensitive()
            self.assertFalse(result.passed)

    def test_sensitive_env_ignored(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, ".env").write_text("SECRET=123")
            Path(tmp, ".gitignore").write_text(".env\n")
            checker = RepoChecker(tmp)
            result = checker.check_sensitive()
            self.assertTrue(result.passed)


if __name__ == "__main__":
    unittest.main()
