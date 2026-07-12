# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) and other AI assistants when working with code in this repository.

## Repository status

This repository is in an **initial / bootstrap state**. As of this writing it contains no application source code — only the GitHub Actions integration described below. Treat it as a greenfield project: when the first real code lands, this file should be updated to document the actual architecture, build commands, and conventions.

## Current contents

```
.
├── .github/
│   └── workflows/
│       └── claude.yml   # GitHub Actions workflow: Claude Code Action for @claude mentions
└── CLAUDE.md            # This file
```

## GitHub Actions: Claude Code integration

The only workflow in the repo is `.github/workflows/claude.yml`. It runs the official [`anthropics/claude-code-action`](https://github.com/anthropics/claude-code-action).

- **Triggers:** `issue_comment` (created) and `pull_request_review_comment` (created).
- **Gate:** The job runs only when the comment body contains `@claude` (`if: contains(github.event.comment.body, '@claude')`).
- **Permissions granted to the job:** `contents: write`, `pull-requests: write`, `issues: write`.
- **Authentication:** Uses the `ANTHROPIC_API_KEY` repository secret. This secret must be configured in the repo's Actions settings for the workflow to function.

### How to use it

Mention `@claude` in a comment on an issue or in a pull request review comment, and the action will pick up the request and respond / make changes.

### When editing the workflow

- Keep the `@claude` gate in the `if:` condition — without it the action would attempt to run on every comment.
- If you add new capabilities (e.g. running tests, linting) that require additional permissions, scope them narrowly in the `permissions:` block.
- Pin or review the `claude-code-action` version (`@v1`) when upgrading, and verify the `ANTHROPIC_API_KEY` secret remains available.

## Development workflow

There is no build system, test suite, or linter configured yet. Once code is added, document here:

- How to install dependencies
- How to build the project
- How to run the test suite and linters
- The primary directory layout and module boundaries

## Git conventions

- The default branch is `main`.
- Development is done on feature branches; open a pull request against `main` for review.
- Write clear, descriptive commit messages that explain the *why* of a change, not just the *what*.

## Notes for AI assistants

- This repository currently has almost no content. **Do not fabricate structure, files, or commands that do not exist.** If asked to describe the codebase, describe it accurately as a bootstrap repo.
- When substantial code is introduced, revisit and expand this file so it reflects the real architecture, tooling, and conventions.
