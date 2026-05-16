---
name: commit
description: Generate a conventional commit message and commit staged changes locally. Use when the user asks to commit, create a git commit, or wants to commit their changes. Does not push.
---

# Git Commit

Analyze staged changes, compose a conventional commit message, and commit locally. Do not push.

## Commit Message Format

```
<type>(<scope>): <short summary>

- bullet point describing a specific change
- bullet point describing another change
```

## Guidelines

- The summary line captures the **overall purpose** of the changes.
- Use bullet points in the body to detail specific modifications.
- Non-code changes (e.g., dependencies, docs) belong in bullet points only, not the summary line.
- Do not push after committing.

## Workflow

1. Run `git diff --staged` to inspect staged changes.
2. If nothing is staged, run `git status` to see what's available and stage relevant files.
3. Compose the commit message following the format above.
4. Commit using a HEREDOC to preserve formatting:

```bash
git commit -m "$(cat <<'EOF'
<type>(<scope>): <short summary>

- change 1
- change 2
EOF
)"
```

5. Confirm success with `git status`.
