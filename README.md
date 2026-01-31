# Rivet Lab

Patterns and notes for trustworthy agent ops.

## Contents
- `docs/permission-manifest.md` — draft schema for declaring an agent skill's permissions (fs/net/secrets) + provenance hooks.
- `samples/permission-manifest.yaml` — example manifest.
- `docs/decision-log.md` — tiny decision-log pattern for preserving identity through context compression.

## Goals
- Safer skill installs: declare what a skill can touch; enable audits and signing later.
- Reliable agents: use small, structured logs of choices and lessons; ship small, reversible changes.

PRs/issues welcome.
