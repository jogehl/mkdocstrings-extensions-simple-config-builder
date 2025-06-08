"""Test building documentation."""
from pathlib import Path
import subprocess
import os
import shutil
import pytest


@pytest.mark.skipif(
    shutil.which("mkdocs") is None,
    reason="mkdocs missing",
)
def test_build_docs(tmp_path):
    """Build the example docs using mkdocs."""
    docs_dir = Path(__file__).resolve().parents[1]
    env = os.environ.copy()
    env['PYTHONPATH'] = str(docs_dir / 'src') + os.pathsep + str(docs_dir)
    result = subprocess.run(
        ['mkdocs', 'build', '--site-dir', str(tmp_path)],
        cwd=docs_dir,
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert (tmp_path / 'index.html').exists()


