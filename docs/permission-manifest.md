# Permission Manifest (draft v0.1)

Purpose: declare what a skill/tool is allowed to access before install/use. This is a human/audit-friendly draft; not final.

## Format
YAML or JSON. Fields:

```yaml
schema: permission-manifest/v0.1
name: example-skill
version: 0.1.0
summary: Short description
maintainer: maint@example.com
source:
  repo: https://github.com/example/skill
  commit: abc123
permissions:
  filesystem:
    - path: ~/.config/example
      mode: read
    - path: /tmp/example
      mode: read-write
  network:
    - host: api.example.com
      ports: [443]
      purpose: api
  secrets:
    - name: EXAMPLE_API_KEY
      purpose: external API
  processes:
    - name: ffmpeg
      purpose: media convert
    - name: bash
      purpose: glue
signing:
  hash: sha256:...
  sig: optional-signature-block
  signed_by: maint@example.com
notes: |
  Any extra context.
```

## Minimal rules
- Default deny: if it’s not declared, treat it as disallowed.
- Explicit host/port for net; explicit paths for fs; explicit env var names for secrets.
- Include source provenance (repo + commit) to pin the artifact.
- Optional signing block (hash + signature) for later verification.

## Open questions
- How granular should fs be (dirs vs globs)?
- Do we need execution allow-list (binaries) separate from fs/net? (Included above as `processes`.)
- How to express sandbox preferences (namespaces, seccomp profiles)?
- How to bind audits to manifests (e.g., YARA results)?

## Next steps
- Iterate schema with real skills.
- Add validation + lint tool.
- Integrate into install UX (show manifest, require confirm; default to deny if missing).
