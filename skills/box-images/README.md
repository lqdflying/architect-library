# box-images

Agent skill for bringing up a disposable test container or pod from the public toolbox images on Docker Hub.

| Image | Purpose |
|-------|---------|
| [`lqdflying/osbox`](https://hub.docker.com/r/lqdflying/osbox) | General network troubleshooting: Debian 13, SSH access, network tools, Python 3.13 |
| [`lqdflying/azurebox`](https://hub.docker.com/r/lqdflying/azurebox) | Azure service integration testing, built `FROM lqdflying/osbox`: Azure CLI, PostgreSQL client, protocol-level Python clients |

## Setup

No runtime dependencies in this library. The agent needs `docker` or `kubectl` for the launch, and `curl` plus `jq` to read digests and overviews from Docker Hub.

Installed with the library for Cursor, VS Code Copilot, Claude Code, and Codex:

```bash
bash scripts/install_library.sh all cursor
bash scripts/install_library.sh all copilot
```

## Files

| File | Purpose |
|------|---------|
| `SKILL.md` | Image picker, shared behavior, workflow, limits, delivery checklist |
| `references/osbox.md` | osbox tools and launch commands |
| `references/azurebox.md` | azurebox tooling, AKS workload identity manifest, token scopes, sample checks, troubleshooting |

## Add an image

1. Add a row to the "Pick the image" table in `SKILL.md`.
2. Add `references/<image>.md` with the image facts, launch commands, and cleanup.
3. Add the image to the `description` in `SKILL.md` so agents select the skill for it.
4. Update "Shared behavior" in `SKILL.md` if the new image does not derive from `osbox`.

When an image tag changes, update the versions and sizes in its reference file. Digests are read from the registry at use time and are not stored here.
