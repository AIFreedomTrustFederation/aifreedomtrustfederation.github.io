# aifreedomtrustfederation.github.io — Proposed Universal AIFT OS Documentation Relationship

> **Informational planning only.** Source architecture and editable infographics appear in [AIFT-OS PR #92](https://github.com/AIFreedomTrustFederation/AIFT-OS/pull/92). All native boot, hosted OS and future physical device support remain separately unverified until exact target evidence exists.

## Current authority

The root public GitHub Pages routing index. It forwards visitors to actual project owners and is not the public OS, native installer, an authenticated hosted desktop or a release host.

## Future relationship

Optionally link to a reviewed architecture explainer in the existing public route map only after publication approval, with explicit planned/unverified state. No new public links/routes are installed by this docs-only PR.

~~~mermaid
flowchart LR
  SOURCE["aifreedomtrustfederation.github.io: current source authority"] --> GUIDE["Proposed informational alignment"]
  GUIDE -. "reference only" .-> OS["AIFT-OS architecture under review"]
  EVIDENCE["Per-repository primary evidence"] --> GUIDE
  REVIEW["Owner and publication approvals"] --> GUIDE
~~~

## Documentation acceptance

1. Preserve the existing README, AGENTS, repository catalog and publication boundary.
2. Confirm the central PR is indeed a draft design proposal, not a released firmware or deployed OS.
3. Never confuse GitHub presence, published roadmap or passing documentation CI with installed, booted or safe hardware.
4. Verification needed: Current public routes, HTTPS links, accessibility, local static verify and external link resolution; release state separately checked at real Pages URL.
5. Do not add secrets, privileged routes, fabricated project achievements, or credentials.

## Restricted changes

Do not change domain, redirects, route coverage, public maturity labels, user data or deployment based on the proposed platform work. Follow owner-specific AGENTS instructions. This document grants no new control, release authority, user permissions, device privileges or auto-merge exemptions.
