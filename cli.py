#!/usr/bin/env python3
"""
Rivet Lab CLI

Commands:
  validate-manifest <path>   Validate a permission manifest (YAML/JSON).
  append-decision --log logs/YYYY-MM-DD.md --what ... --why ... [--lesson ...] [--when ISO8601]
"""
import argparse
import datetime as dt
import json
import sys
import pathlib
from typing import Any, Dict, List

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None


class ManifestError(Exception):
    pass


def load_manifest(path: pathlib.Path) -> Dict[str, Any]:
    text = path.read_text()
    if path.suffix.lower() in {".json"}:
        return json.loads(text)
    if yaml is None:
        raise ManifestError("PyYAML not installed; cannot parse YAML")
    return yaml.safe_load(text)


def validate_manifest(data: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    required_top = ["schema", "name", "version", "permissions"]
    for k in required_top:
        if k not in data:
            errors.append(f"missing field: {k}")
    if errors:
        return errors

    perms = data.get("permissions", {})
    if not isinstance(perms, dict):
        errors.append("permissions must be a mapping")
        return errors

    fs = perms.get("filesystem", [])
    if not isinstance(fs, list):
        errors.append("permissions.filesystem must be a list")
    else:
        for i, entry in enumerate(fs):
            if not isinstance(entry, dict):
                errors.append(f"filesystem[{i}] must be a mapping")
                continue
            if "path" not in entry:
                errors.append(f"filesystem[{i}] missing path")
            mode = entry.get("mode")
            if mode not in {"read", "read-write"}:
                errors.append(f"filesystem[{i}] mode must be read|read-write")

    net = perms.get("network", [])
    if not isinstance(net, list):
        errors.append("permissions.network must be a list")
    else:
        for i, entry in enumerate(net):
            if not isinstance(entry, dict):
                errors.append(f"network[{i}] must be a mapping")
                continue
            if "host" not in entry:
                errors.append(f"network[{i}] missing host")
            ports = entry.get("ports")
            if not isinstance(ports, list) or not all(isinstance(p, int) for p in ports):
                errors.append(f"network[{i}] ports must be a list of ints")

    secrets = perms.get("secrets", [])
    if not isinstance(secrets, list):
        errors.append("permissions.secrets must be a list")
    else:
        for i, entry in enumerate(secrets):
            if not isinstance(entry, dict):
                errors.append(f"secrets[{i}] must be a mapping")
                continue
            if "name" not in entry:
                errors.append(f"secrets[{i}] missing name")

    procs = perms.get("processes", [])
    if not isinstance(procs, list):
        errors.append("permissions.processes must be a list")
    else:
        for i, entry in enumerate(procs):
            if not isinstance(entry, dict):
                errors.append(f"processes[{i}] must be a mapping")
                continue
            if "name" not in entry:
                errors.append(f"processes[{i}] missing name")

    if not any([fs, net, secrets, procs]):
        errors.append("permissions must declare at least one of filesystem/network/secrets/processes")

    return errors


def cmd_validate_manifest(args: argparse.Namespace) -> int:
    path = pathlib.Path(args.path)
    try:
        data = load_manifest(path)
        errors = validate_manifest(data)
    except Exception as e:  # broad by design for CLI
        print(f"error: {e}", file=sys.stderr)
        return 1
    if errors:
        for err in errors:
            print(f"INVALID: {err}", file=sys.stderr)
        return 1
    print("VALID")
    return 0


def cmd_append_decision(args: argparse.Namespace) -> int:
    log_path = pathlib.Path(args.log)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    when = args.when or dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    entry = (
        f"- when: {when}\n"
        f"  what: {args.what}\n"
        f"  why: {args.why}\n"
        f"  lesson: {args.lesson}\n"
    )
    with log_path.open("a", encoding="utf-8") as f:
        f.write(entry)
        if not log_path.read_text().endswith("\n"):
            f.write("\n")
    print(f"Appended to {log_path}")
    return 0


def main(argv: List[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    v = sub.add_parser("validate-manifest", help="Validate a permission manifest (YAML/JSON)")
    v.add_argument("path")
    v.set_defaults(func=cmd_validate_manifest)

    d = sub.add_parser("append-decision", help="Append a decision log entry")
    d.add_argument("--log", required=True, help="Path to log file, e.g. logs/2026-01-31.md")
    d.add_argument("--what", required=True)
    d.add_argument("--why", required=True)
    d.add_argument("--lesson", default="")
    d.add_argument("--when", help="ISO8601 time; defaults to now UTC")
    d.set_defaults(func=cmd_append_decision)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
