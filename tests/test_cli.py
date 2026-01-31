import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
CLI = ROOT / "cli.py"


def run(args):
    cmd = [sys.executable, str(CLI)] + args
    return subprocess.run(cmd, capture_output=True, text=True)


def test_validate_manifest_ok(tmp_path):
    manifest = tmp_path / "m.yaml"
    manifest.write_text(
        """
        schema: permission-manifest/v0.1
        name: example
        version: 0.1.0
        permissions:
          filesystem:
            - path: /tmp
              mode: read
          network:
            - host: api.example.com
              ports: [443]
          secrets:
            - name: EXAMPLE_KEY
          processes:
            - name: bash
        """
    )
    res = run(["validate-manifest", str(manifest)])
    assert res.returncode == 0
    assert "VALID" in res.stdout


def test_validate_manifest_fail(tmp_path):
    manifest = tmp_path / "m.yaml"
    manifest.write_text(
        "schema: permission-manifest/v0.1\n"
        "name: example\n"
        "version: 0.1.0\n"
        "permissions: {}\n"
    )
    res = run(["validate-manifest", str(manifest)])
    assert res.returncode != 0
    assert "filesystem" in res.stderr or "network" in res.stderr


def test_append_decision(tmp_path):
    log = tmp_path / "logs/2026-01-31.md"
    res = run([
        "append-decision",
        "--log", str(log),
        "--what", "test what",
        "--why", "test why",
        "--lesson", "test lesson",
        "--when", "2026-01-31T00:00:00Z",
    ])
    assert res.returncode == 0
    text = log.read_text()
    assert "test what" in text and "test why" in text
