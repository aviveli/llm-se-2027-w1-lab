from pathlib import Path
import subprocess
import sys

import pytest


@pytest.mark.parametrize("prefix", ["Review \u201d\n".encode("utf-8"), b"PK\x00\x9d\xff\n"])
@pytest.mark.parametrize("has_secret", [False, True])
def test_scanner_handles_staged_text_and_binary(
    tmp_path: Path, prefix: bytes, has_secret: bool
) -> None:
    subprocess.run(["git", "init", "--quiet", str(tmp_path)], check=True)
    content = prefix + (("sk-" + "a" * 40).encode("ascii") if has_secret else b"safe")
    (tmp_path / "sample.dat").write_bytes(content)
    subprocess.run(["git", "add", "sample.dat"], cwd=tmp_path, check=True)

    scanner = Path(__file__).resolve().parents[1] / "tools" / "check_secrets.py"
    result = subprocess.run(
        [sys.executable, str(scanner)], cwd=tmp_path, capture_output=True, check=False
    )

    assert result.returncode == (1 if has_secret else 0)
    assert result.stderr == b""
    if has_secret:
        assert b"sample.dat:2  OpenAI key" in result.stdout
