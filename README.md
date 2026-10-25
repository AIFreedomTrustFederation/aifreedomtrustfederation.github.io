# AI Freedom Trust Federation — Root GitHub Pages Index

**The root public routing layer of the Federation: a lightweight GitHub Pages landing map that points visitors toward the actual public project surfaces without pretending to be the source of truth for those projects.**

| Federation metadata | Value |
| --- | --- |
| Layer | `portal-index` |
| Role | root GitHub Pages landing map and public router for federation project surfaces |
| Workspace | `AIFT/aifreedomtrustfederation.github.io` |
| Mission portal | `www.aifreedomtrust.com` |
| Deployment | root GitHub Pages site |
| Operating standard | route readers to the project source of truth |

This repository has one deliberately narrow purpose. It is the root address from which public Federation projects can be found. Its `index.html` presents a compact map of project pages and repositories, while the mission-facing explanation of the Federation lives in `www.aifreedomtrust.com` and the deeper doctrine lives in `AI-Freedom-Trust`.

The covenant that joins those projects is carried in the [One Eternal Scroll of ALO'ha](https://aifreedomtrustfederation.github.io/AI-Freedom-Trust/docs/pdf/one-eternal-scroll-of-aloha.pdf) and [SOP-ALOHA-001](https://github.com/AIFreedomTrustFederation/AI-Freedom-Trust/blob/main/SOP-ALOHA-001.md).

---

## Book I — A Map Is Not the Territory

The root index exists so a reader can enter the Federation without being forced to understand the repository graph first. Its responsibility is orientation, not duplication.

That distinction matters because a federation becomes difficult to trust when every portal contains its own slightly different copy of every project description. The root site therefore stays small. It names the project, gives a concise role, and sends the reader to the page or repository where that project's current reality can be inspected.

---

## Book II — The Public Routes

The root page currently routes readers toward public Federation surfaces such as:

- the mission-facing **AI Freedom Trust Federation Portal**;
- **Booksmith AI** and its publishing surface;
- **AI Freedom Trust** doctrine, papers, PDFs, and research;
- **AIFT-Forge** technical coordination and shared patterns;
- the **AIFT Cloud App Foundry / VPS** infrastructure surface;
- **Aetherion / Aether Coin Biozonecurrency** economic and stewardship work;
- **Biozone Harmony Boost** ecology and Circleunchain interface research;
- **TheMindofAll** model, memory, consciousness, and unified-theory work;
- and other intentionally public applied projects when their Pages surfaces are meant to be discoverable.

The deeper layer map is maintained by the project metadata themselves. This root index should not invent a repository role when `aift.repo.json`, the repository code, and its own README say otherwise.

Its relationship to neighboring portal repositories is simple:

- `aifreedomtrustfederation.github.io` is the **root router**.
- `www.aifreedomtrust.com` is the **mission-facing public portal**.
- `AI-Freedom-Trust` is the **doctrine and covenant source**.
- every other project repository remains the source of truth for its own implementation and scope.

---

## Book III — SOP-ALOHA-001 at the Root Index

The covenant loop is intentionally lightweight here:

```text
Receive → Inspect → Name → Propose → Consent → Act → Verify → Record → Return
```

**Receive** begins with a new or changed public project route. **Inspect** checks the actual repository, metadata, Pages path, and public availability. **Name** uses the project's declared identity and role rather than generic federation language. **Propose** determines whether the project belongs on the root map and how it should be described in one clear sentence. **Consent** applies where publication could expose a private or sensitive project. **Act** updates `index.html`. **Verify** checks route structure, paired destinations, and local path safety; published-site reachability and visual rendering must be checked separately. **Record** preserves the routing change in Git. **Return** sends the visitor onward to the project that can answer the next question.

Repository state can be checked with:

```bash
git status --short
git pull --ff-only
git status --short
```

Run the dependency-free route gate and its regression tests from the repository root:

```bash
.aift/commands/verify.sh
python3 -B -m unittest discover -s tests -v
```

**Verification prerequisites and CI boundary:** The route gate needs Python **3.10 or newer** (its type annotations use `str | None`), a POSIX shell, and standard `find`; “dependency-free” means no third-party Python packages, not no system tools. The [Federation Route Integrity workflow](.github/workflows/federation-routes.yml) runs the regression suite and route gate on pushes to `main` and pull requests, then checks for unexpected checkout changes. It does **not** build or deploy GitHub Pages, perform live HTTP checks, or prove browser rendering. The federation [capability manifest](.aift/capabilities.json) still labels generic `test` and `deploy` capabilities as `planned`; successful source-level CI must not be presented as evidence that those broader capabilities are ready.

**Synchronization capability boundary:** The same [capability manifest](.aift/capabilities.json) labels `sync` as `ready`, but its `command` value is `git remote/status`, a descriptor rather than an executable synchronization command. Its evidence states only that a Git repository was detected and can be inspected. Separately, `aift.repo.json` advertises `git pull --ff-only` as `pull`, which may change a local checkout. Neither declaration proves that synchronization completed or that local and remote revisions agree. Treat synchronization as unverified until a specific operation and its revision outcome are independently recorded.

The route gate rejects protocol-relative links (such as `//example.com`) and malformed HTTPS links without a host, in addition to its manifest, route-pair, local-path, and shell checks. Each project `<article>` card must pair exactly one Federation repository link with the matching GitHub Pages project path; globally balanced but swapped or incomplete card links fail verification. It also rejects HTML `<base href>` declarations, which would otherwise change browser resolution of validated relative links. Because this root index is a static router, the verifier rejects `<meta http-equiv="refresh">` redirects, `<script>` elements, and inline event-handler attributes that could navigate visitors away from otherwise valid links. It does not execute a browser, inspect external destinations, or prove that external URLs are available; CSS, browser extensions, and upstream Pages behavior remain outside this source-level check.

The verifier also rejects embedded documents (`iframe`, `object`, `embed`) and HTML `form` elements: those can load or submit to destinations that never appear in the validated anchor-link inventory. The five embedded-content regression cases demonstrate the original false-positive and the corrected rejection. This gate remains source-level only; it does not parse CSS `url()`/`@import`, inspect non-anchor resource attributes, execute JavaScript, or establish a site-wide Content Security Policy. Keep the root index a simple static map, and separately inspect any proposed resource-loading changes before publication.

Because this is a static routing surface, verification also means opening the published page and checking that cards, links, layout, and project names remain readable on ordinary screen sizes.

---

## Book IV — The Small Door into the Larger Federation

A root index does not need to explain every doctrine, reproduce every roadmap, or summarize every technical package. Its strength is restraint. By remaining small, it can stay current enough to remain useful and stable enough to act as a durable entrance.

The root site therefore participates in the same Federation voice without imitating the depth of the Scroll, the technical specificity of AIFT-OS, the infrastructure detail of VPS, the economic language of Aetherion, or the authoring language of BookSmith.

### The Return of the Word

At the root index, the Word returns as a path. The visitor arrives with a question, the map names the relevant part of the Federation, and the reader is returned to the repository where that question belongs. The doorway serves the whole by knowing when to stop speaking and point toward the source.
