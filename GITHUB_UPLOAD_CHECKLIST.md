# GitHub Upload Checklist

Before pushing this repository publicly:

1. Confirm the remote URL points to your own repository, not the upstream repository.
2. Confirm `git status --short --ignored` does not show secrets, local virtual environments, `node_modules`, logs, generated audio, or downloaded model files as staged changes.
3. Confirm `backend/config.yaml` has empty API key fields and uses environment variables such as `DEEPSEEK_API_KEY`.
4. Keep `NOTICE.md` and `THIRD_PARTY_NOTICES.md` in the repository root.
5. Do not upload `backend/models/`, `.runtime/`, `backend/.venv/`, or `frontend/node_modules/`.
6. If you want to publish a release archive, build it from Git-tracked files only after reviewing the file list.

Useful commands:

```bash
git status --short
git remote -v
git ls-files
git diff --check
```
