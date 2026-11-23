# Git and GitHub workflow

Use `main` for stable releases, `develop` for integration, and short-lived `feature/*` branches for focused work. Open pull requests from feature branches to `develop`; merge tested `develop` to `main` for a release. Use Conventional Commit prefixes such as `feat(leads): ...`, `test(backend): ...`, `ci: ...`, and `docs: ...`.

Suggested GitHub settings after pushing:

1. In **Settings → Branches**, add a ruleset or protection rule for `main`.
2. Require pull requests before merging and require at least one approval if the team has reviewers.
3. Require the Backend CI and Frontend CI checks, and require branches to be up to date.
4. Block force pushes and branch deletion.
5. Enable secret scanning and push protection where available. Rotate any credentials that were exposed; history rewriting alone is not sufficient.

The repository is initialized locally when possible, but no remote, GitHub repository, branch protection, or CI execution is implied unless explicitly verified.
