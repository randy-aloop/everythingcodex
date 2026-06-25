# DOC-V03-SYNC-TO-CODE-EXPANDED Recovery Pack

Created: 2026-06-25

This public folder records the recovery metadata for the executed `0.2.0-trial docs V03.1 sync-to-code` patch.

## Contents

- `manifest.json` records the patch id, target branch, target commit, affected files, and baseline availability.
- Full local file-copy payloads are intentionally omitted from the public package.

## Public Payload Policy

The original local recovery folder included copied working-tree files and local audit provenance. Those local payloads are not published because they can preserve machine-specific paths and duplicate private workspace context.

Use the Git commit history plus the file lists in `manifest.json` for public recovery. If a private local recovery bundle is needed, use the Phase 0 backup that was created outside the repository before the version bump.
