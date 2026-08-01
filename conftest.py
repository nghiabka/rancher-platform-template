"""Keep root pytest runs focused on repo-level tests.

The sample-api package has its own dependency/setup flow and is exercised from
apps/sample-api/ in CI. Root-level pytest should not collect that tree because
this workspace does not install the sample app's Flask dependency globally.
"""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent
SAMPLE_API_TESTS = REPO_ROOT / "apps" / "sample-api" / "tests"


def pytest_ignore_collect(collection_path, config):
    if Path.cwd() != REPO_ROOT:
        return False

    path = Path(str(collection_path))
    return path.is_relative_to(SAMPLE_API_TESTS)
