# AGENTS.md — Federation Public Route Index

## Scope

This repository is the Federation's root GitHub Pages router. It helps visitors find public project surfaces; it does not own or redefine the doctrine, maturity, authority, capabilities, or operating status of those projects.

## Required Behavior

- Route visitors to each project's own source of truth.
- Derive project names and descriptions from that project's current repository evidence.
- Keep Pages and GitHub repository links paired and HTTPS-only.
- Keep local routes inside this repository and reject path traversal.
- Do not claim that a project, deployment, service, or capability is available without verified public evidence.
- Never publish credentials, private endpoints, personal data, internal infrastructure details, or private project routes.

## Human Approval Required

- exposing a project or route that was not already public
- removing or redirecting an established public route
- changing doctrine, governance, security, financial, health, or legal claims
- changing deployment or domain configuration

## Validation

Run the same dependency-free, non-mutating route gate enforced by CI:

```sh
.aift/commands/verify.sh
git diff --check
test -z "$(git status --porcelain)"
```

The gate validates six federation manifests, shell syntax, safe local paths, HTTPS destinations, and matching Pages/repository route pairs. For visible page changes, also inspect the rendered page at ordinary desktop and mobile widths before declaring it ready.
