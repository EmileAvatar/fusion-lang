# New Fusion Libraries: SourceControl, WorkTracking, Governance

Version 3, 2026-11-19. Replaces the first draft (`newLib.md`). Version 3 adds section 15 (why these libraries are required: real incidents and root causes).
Status: [IDEA / DESIGN] - future project settings, to be investigated and designed by Claude Code (see section 12).

## 1. What changed from the first draft

The first draft treated these as normal API libraries (`repo.commit {...}`, `WorkTracking.get(...)`). That is not the goal. The goal is:

- A **compiler / IDE feature set for corporate customers** with strict change control, where code is linked to business rules, laws, compliance and security requirements, and to the tickets/bugs that required each change.
- The link lives in the source as **metadata only** (references, not logic). The rules and tickets live **outside the source**, as data, because rules change constantly (discounts, for example).
- It is **opt-in per project**. Normal dev work keeps working the traditional way (tasks tracked outside the code). Controlled projects turn the links on.
- Environments may be **restricted and preset**, so a developer cannot deviate from the settings the organisation has locked.

Kept from the first draft, as options only: a shared event mechanism (`Fusion.Events`), and a separate `Fusion.Rules` runtime rules engine (see section 11).

**The reason these libraries must exist** is real-world incidents: source code and credentials leak, build pipelines get tampered with, and unreviewed changes slip in. Section 15 lists the incidents since 2020 (and major earlier ones), their root causes, and the security requirements (SEC-01 to SEC-13) each library has to meet.

## 2. Two working modes (a project setting)

| | Standard mode | Controlled mode |
|---|---|---|
| Who | Normal dev work, hobby, internal tools | Corporate customers with change control, audit, regulation |
| Links in source | Optional, ignored by compiler | Required in governed areas, checked by compiler/IDE |
| Tickets | Tracked in the tracker, not linked in code | Every change linked to a ticket/bug/issue |
| Business rules / law / compliance / security | Not tracked | Governed code is linked to a rule, law, compliance or security requirement |
| Settings | Developer can change | Can be preset and locked by an administrator |
| Audit evidence | None needed | Produced automatically (who, why, approved by, tested, released) |

Each project ticks which capabilities it needs (section 9). Nothing here is forced on a project that doesn't want it.

## 3. Research: how others handle this

I found no mainstream programming language that has compliance/requirement links as a built-in, first-class feature. The work is done by tools around the language, plus one research proposal that is close to Fusion's idea.

| Approach | How it works | What Fusion can learn |
|---|---|---|
| **OpenFastTrace (OFT)** | Requirements written in Markdown; developers put coverage tags in source comments (e.g. `[impl->...]`, `[utest->...]`). OFT traces requirement -> code -> tests and finds orphaned code. A language server and IDE plugins exist. | Comment tags are a proven, simple model. IDE completion for tags is practical. |
| **StrictDoc** | Requirements in plain-text files. Two linking styles: markers in source code pointing at requirements, or forward links from the requirement to source files when the source **cannot be modified**. Source-code traceability is marked experimental in its docs. | The "source can't be touched" style (sidecar links) is useful for locked or legacy code. |
| **Doorstop, Sphinx-Needs, Quarto-Needs** | Requirements as code in the repo; Quarto-Needs adds a graph, "suspect link" detection after changes, and PR reports. | A change to a rule should flag linked code as "suspect" until reviewed. |
| **DO-178C (aerospace)** | Requires two-way traceability: requirements <-> design <-> code <-> tests. Code that cannot be traced to a requirement is treated as a risk. Applies at levels A, B and C (A adds source-to-object-code). Related: ISO 26262 (automotive), IEC 62304 (medical). | "Orphan code" (code with no governing requirement) is a first-class finding. Traceability must run both directions. |
| **ReqToCode (research, arXiv 2603.13999)** | Argues traces kept as external metadata silently go out of date. Proposes referencing requirement facts ("Traceables") directly in code, with links **verified at compile time**, and a graduated lifecycle when requirements change. | Closest to what Fusion could do natively: the compiler itself verifies the links. |
| **Ada / SPARK** | Contracts (pre/post conditions) were first written in comments (SPARK 83/95/2005), then moved into the language itself as aspects (SPARK 2014). | Precedent for starting as comment metadata and promoting it to a language feature later. (These are behaviour contracts, not business traceability.) |
| **Jira Smart Commits / GitHub-Jira** | Issue key in the commit message links the commit to the ticket; can also comment, log time, transition status. Development info shows on the ticket. | Weakness: history rewrites (force push, squash) can duplicate or break the links, and it depends on matching emails. Fusion.SourceControl should keep its own link record, not rely on commit text alone. |
| **GitHub pull requests as audit trail** | A PR is the change request, the evaluation (review + tests) and the approval record, which maps to ISO 27001 change management. | Approval and review evidence should be captured from the PR/provider, not retyped. |
| **ALM tools (Polarion, Codebeamer, Jama, IBM DOORS)** | Traceability matrices linking requirements to work items, code, tests. | Link records live in the tool, so they drift from the code. This is the problem Fusion can avoid by making the compiler check. |
| **Policy as code: Cedar (AWS), OPA/Rego** | Authorization rules written as policies kept **outside** application code, versioned, and evaluated by an engine. Cedar is authorization-only (`permit` / `forbid`); Rego is general-purpose. | Matches the "rules are data, not code" requirement, and the rep/manager permissions example (section 8). |
| **DMN (OMG standard) / Drools** | Business decisions as decision tables, with "knowledge sources" that reference the regulations and policies behind a decision. Drools can execute DMN. | Gives a standard shape for rules and a standard way to attach the law/policy a rule comes from. |

### Evidence auditors ask for (SOX, ISO 27001, SOC 2)

- Auditors sample change tickets and look for the request, approval, testing and deployment records (SOX IT general controls, change management).
- ISO 27001 Annex A 8.32 audits trace an implemented change back to the original request and its authorisation.
- Approvals must come from authorised people ("anyone can approve anything" fails an audit).
- Evidence must be recorded at the time, not reconstructed later.
- Common pain: tickets, commits and approvals live in different tools and are collected by hand (screenshots, CSV exports).

Fusion's opportunity: produce this chain automatically, because the compiler/IDE already knows the code, the links and the project settings.

## 4. Core design idea

Three things are kept separate and joined by **IDs**:

```
Governance store (data)      WorkTracking (tickets)        SourceControl (history)
rule / law / compliance      bug / change / issue          commits / branches / reviews
BR-001 v2                    BUG-1024                      commit abc123
        \                          |                          /
         \________  link tags in source (metadata only) _____/
                              |
                    Fusion compiler + IDE
          (check links, flag orphan/suspect code, build evidence)
```

- Source contains **references only**. No rule values, no ticket content.
- Rule values (e.g. a discount limit) are **data** in the Governance store. Changing a discount creates a new rule version; it does not need a code change unless the logic changes.
- The compiler/IDE resolves the IDs, so these three libraries give the compiler and IDE features that are not normally available.

## 5. Fusion.SourceControl (library 22)

**Purpose:** control how Fusion source is versioned, with any system, including one you build yourself.

- **Provider model**: a small contract that any provider implements. Providers: Git (first), other existing systems (GitHub, GitLab, Bitbucket, Azure DevOps and similar), a **custom Fusion source control**, or **your own**.
- The contract covers: snapshot/commit, history, diff, branch/merge, tags, identity, and events (committed, pushed, merged, review approved).
- **Fusion-aware features** on top of the contract, working with any provider: diff by function/module instead of by line, which links changed, and which governed areas a change touches.
- **Link record owned by Fusion**: the change-to-ticket-to-rule link is stored by Fusion, not only in commit message text, so history rewrites do not silently break it.
- **Integration** with other systems through adapters (code review, CI, release).
- Controlled mode can require: signed commits, verified identity, protected branches, no direct commits to governed areas.

## 6. Fusion.WorkTracking (library 23)

**Purpose:** link the IDE and the source code to external tasks, tickets, bugs and issues. It is **not** a task API for programs to call.

- Source holds **references** in special comments or metadata (see section 10), such as a ticket ID or change ID.
- The IDE resolves the references against the tracker (Jira, Azure DevOps Boards, GitHub/GitLab Issues, Linear, YouTrack, Trello, others via adapters): hover shows the ticket, jump to it, and "show all code linked to this ticket".
- Standard mode: no links required, devs work from tasks as traditionally done.
- Controlled mode can require: a ticket on every change, ticket in an approved state, ticket type matches the change (bug, change request, security fix).
- Two-way: ticket shows its commits/branches/PRs; code shows its tickets.
- Event-driven where possible (a push or merge raises an event the tracker adapter handles), so libraries stay loosely coupled.

## 7. Fusion.Governance (library 24)

**Purpose:** hold the business rules, laws, compliance and security requirements, and govern both the data and the code that implements them. Linked to the IDE and to the other two libraries.

**Rule record (data, not source code):**

| Field | Notes |
|---|---|
| ID, title, type | Business rule / law / regulation / compliance control / security requirement |
| Version, effective date | Rules change over time; old versions are kept |
| Source / reference | The law, policy or standard behind it (DMN calls these knowledge sources) |
| Owner | Responsible person or department |
| Change history | Who requested, who approved, why, when effective |
| Approval workflow | Who may approve which rule changes |
| Linked tickets | Work that implements or changed it |
| Linked code | Found via link tags in source |
| Status | Draft, approved, effective, retired |

**Features:**
- Rule versions with effective dates, so a discount change is a new version, not a code edit.
- Impact analysis: "if BR-001 changes, which code/tests/systems are affected?"
- **Suspect links**: when a rule version changes, linked code is flagged for review until someone confirms it.
- **Orphan code**: governed areas with no link to a rule/requirement are reported (or fail the build in Controlled mode).
- Immutable audit trail, and evidence/report generation (change report for an auditor).
- Compliance mapping: which control (SOX, ISO 27001, SOC 2, PCI DSS, POPIA/GDPR, others) a rule or code area satisfies.
- Rule values read at runtime from the store, when the project chooses that (see section 11).

## 8. Locked environments and permissions

Corporate customers may need a restricted environment where settings are preset and the developer cannot deviate.

**Policy profile:**
- An administrator defines a profile: which mode, which checks are required, which links are mandatory, which branches/areas are protected, who may approve what.
- The profile is locked and signed. The compiler/IDE refuses to build or commit if project settings deviate from it.
- This could become **its own application** (a governance console/server) that controls how the compiler works for a team.

**Roles (example):**
- A sales rep can read pricing and orders but not change prices.
- A manager can change prices up to a set limit.
- Above the limit needs further approval.

This example is a **runtime permission rule**, which is a different thing from "who may change this code". Both are likely needed:

| Level | Question | Precedent |
|---|---|---|
| Development time | Who may change this module, approve this rule change, merge to this branch? | Branch protection, CODEOWNERS-style rules, approval workflows |
| Runtime | Who may read/change this business data, and up to what limit? | Policy-as-code (Cedar, OPA) |

Both can be expressed as data (policies) held in Governance, versioned and audited, not hard-coded.

## 9. Project capability checklist (each project ticks what it needs)

Project settings are checkboxes, not a single fixed design:

- [ ] Link tags in source (section 10 style: ______)
- [ ] Link granularity: [ ] file  [ ] module  [ ] function/type  [ ] line range
- [ ] Every change linked to a ticket/bug/issue
- [ ] Every governed code area linked to a rule / law / compliance / security requirement
- [ ] Orphan code reported as: [ ] info  [ ] warning  [ ] build error
- [ ] Suspect links after a rule change: [ ] flag  [ ] block release until reviewed
- [ ] Approval required before merge / release (who: ______)
- [ ] Signed commits / verified identity
- [ ] Protected branches / areas
- [ ] Test results linked to rules/tickets
- [ ] Audit trail immutable
- [ ] Evidence report for: [ ] SOX  [ ] ISO 27001  [ ] SOC 2  [ ] PCI DSS  [ ] POPIA/GDPR  [ ] other: ______
- [ ] Rule data stored in: [ ] file in repo  [ ] database  [ ] external system  [ ] other: ______
- [ ] Rule values read at runtime from the store
- [ ] Runtime rules engine needed (see `Fusion.Rules`)
- [ ] Runtime role/permission policies
- [ ] Policy profile locked/signed by administrator
- [ ] Settings preset, developer cannot deviate
- [ ] Source cannot be modified (use sidecar links instead of in-source tags)

## 10. How the link could be written (options, not decided)

All examples are illustrative only. Final syntax is for the design task.

**A. Comment tag** (ignored by compiler in Standard mode, checked in Controlled mode). Same idea as OpenFastTrace tags.
```
//@ rule BR-001 v2
//@ ticket BUG-1024
//@ compliance SOX-ITGC-CM
```

**B. Attribute / annotation** (part of the language, always checked).
```
@Governs("BR-001")
@Change("BUG-1024")
function applyDiscount(...)
```

**C. Sidecar link file** (source untouched; link file maps file/function to IDs). Same idea as StrictDoc forward links. Suits locked or legacy code.
```
links/pricing.fusionlinks:
  Pricing.applyDiscount -> BR-001, BUG-1024
```

Path to consider: start with A (comments), later promote to B once the model is proven, as SPARK did with its contracts. C should exist regardless for code that cannot be edited.

What the compiler/IDE does with links in Controlled mode: check the IDs exist, check the rule version is current/approved, check the ticket state, report orphan and suspect code, and write the trace record.

## 11. Runtime rules and `Fusion.Rules` (optional, later)

Two different jobs:

- **Governance** manages rules: ownership, versions, history, approval, compliance, links.
- **Rules** (optional separate library) **executes** rules at runtime: conditions, decisions, policies.

Whether a project needs the second depends on the project (see question 2 below). Possible rule formats to investigate: simple value tables, DMN-style decision tables, policy languages (Cedar/Rego style).

## 12. Questions and answers

| # | Question | Answer (Emile) | Design implication |
|---|---|---|---|
| 1 | Where should rule data live (file in repo, database, external system)? | Can't answer as each project will be different. Treat them all as a checkbox. | Storage is a pluggable provider chosen in project settings. Support several; section 9 has the checkbox. |
| 2 | Should Governance only store/manage rules, or also execute them (a separate `Fusion.Rules`)? | Not sure yet; needs further investigation. Will depend heavily on the project settings. | Keep Governance = manage, Rules = execute, and make Rules optional. Investigate before deciding. |
| 3 | Should the link comments be a language feature (compiler-checked) or an IDE convention? | See answers 1 and 2: it might be, but others also need to be investigated. | Support more than one style (A, B, C in section 10), selectable per project. Research precedent: SPARK moved from comments into the language. |
| 4 | Three libraries, or one IDE/tooling module? | Three libraries that give the compiler/IDE extra features not normally available. Devs may work in a restricted environment where settings are preset to stop deviation from the rules. It might even become its own specific app that governs how the compiler works, e.g. a rep can read pricing and orders but not change price, while a manager can change price up to a limit. | Three libraries, plus a locked policy profile and possibly a standalone governance app (section 8). Includes both dev-time and runtime permissions. |

### New open questions (from this research)

1. Does the runtime rep/manager permission model belong in Governance, or in a separate security/authorization library (`Fusion.Crypto`/`Fusion.Web` or a new one)?
2. Should the compiler ever fail a build in Standard mode, or only in Controlled mode?
3. Which regulations should the first evidence reports target (SOX, ISO 27001, SOC 2, POPIA, PCI DSS)?
4. How is the link kept valid when code is refactored, moved or renamed (the problem ReqToCode describes)?
5. Who owns the Governance store (the customer's compliance team?) and does it need its own login/roles outside the IDE?

## 13. Library list update

Existing: 21 libraries (5 Core + 12 Additional + 4 IDE), see `FusionLibraries.md`. These three would join IDE & Development, making 24.

| # | Library | Purpose |
|---|---|---|
| 22 | Fusion.SourceControl | Pluggable source control (Git, custom, your own) with Fusion-aware diff and owned link records |
| 23 | Fusion.WorkTracking | Links code and IDE to tickets, bugs, issues; metadata references, not a task API |
| 24 | Fusion.Governance | Business rules, laws, compliance and security requirements as versioned data, with traceability, approval and audit |

Note: `FusionLibraries.md` already lists a future idea `fusionlib.IDE` as "(22)". The number will need to be reconciled when these are accepted.

## 14. For Claude Code: investigation tasks

1. Check how the existing spec files (`180`-`183`) describe the IDE tier and where these three modules would fit; reconcile the "(22) fusionlib.IDE" numbering.
2. Design the provider interface for SourceControl (contract, events, link record), starting with Git.
3. Design the link model: ID scheme, the three syntax options (A/B/C), granularity, and what the compiler checks in each mode.
4. Design the Governance rule record and version/approval model; decide a storage-provider interface.
5. Investigate rule formats (value tables, DMN-style decision tables, Cedar/Rego-style policies) and whether `Fusion.Rules` is needed.
6. Design the policy profile (locked/signed settings) and how the compiler enforces it; assess a standalone governance app.
7. Design the dev-time vs runtime permission split (section 8).
8. Define the event mechanism (`Fusion.Events`) shared by the three libraries, `Fusion.Test` and `Fusion.DocWiki`.
9. Define the evidence/report output for one regulation as a pilot.
10. Record the decisions in `Decisions.md` and update the Library Summary in `183-fusionlib-IDE.md`.
11. Turn the SEC-01 to SEC-13 requirements in section 15.3 into design requirements for each library, and decide which are mandatory in Controlled mode.
12. Investigate how to verify that a built/released artifact matches a recorded, approved commit (SEC-04), since SolarWinds, Codecov and xz all tampered with the build or release step, not the repository.
13. Design the managed dev workspace and release gate (SEC-03, SEC-06, SEC-07) and how far the Fusion IDE/compiler can enforce them versus relying on the OS and endpoint tools.

## 15. Why these libraries are required: incidents and root causes

This section is the justification for the three libraries. Each real incident below maps to a cause, and each cause maps to a requirement that SourceControl, WorkTracking or Governance (with the compiler/IDE) has to meet.

Notes on the evidence: details come from company statements, security researchers and press reports. Some causes are alleged or disputed, and are marked. Several 2026 entries are recent and may still be updated.

### 15.1 Incidents since 2020

| Year | Incident | What happened | Root cause | Accidental? |
|---|---|---|---|---|
| 2020 | **SolarWinds** | Attackers inside the development/build environment (from Sept 2019) used a build-time implant to inject a backdoor into Orion source files before compilation. The result was then compiled, signed and shipped to customers. | Compromised build environment; tampering invisible in build logs and to developers | No |
| 2020 | Windows XP SP1 / Server 2003 source depots | Full source depots leaked online and were confirmed genuine. | Not stated in the sources found | Unknown |
| 2021 | **Codecov** | A dev tool's Bash Uploader script was altered from Jan 31 to Apr 1, 2021, and exported customers' CI secrets. Found by a customer who checked the script's hash. | An error in the Docker image build let the attacker extract the credential that could modify the script | No (attacker), build error (cause) |
| 2021 | **Twitch** | About 125GB leaked, including the entire site source with commit history, SDKs and internal tools. | An error in a server configuration change exposed the data, then accessed by a third party | Yes (config error) |
| 2022 | **Lapsus$** (Nvidia, Samsung, Microsoft, others) | Source code stolen and leaked or used for extortion: Samsung Galaxy code (190GB), part of Microsoft's code from its Azure DevOps server (37GB), Nvidia DLSS code. | Social engineering, SIM swapping and stolen employee credentials | No |
| 2022 | **LastPass** | A developer account was used to take source code from the dev environment. A second attack followed: a DevOps engineer's home computer, running a three-year-old vulnerable Plex server, got a keylogger that captured the corporate vault password. Attackers stayed about eight weeks. | Compromised developer account; unpatched personal machine used for corporate access | No |
| 2022 | **Toyota (T-Connect)** | A subcontractor uploaded source code containing a data-server access key to a public GitHub repo in Dec 2017. It stayed public until Sept 2022. 296,019 customer emails were potentially exposed. | Contractor mistake; key hardcoded in code; never rotated; discovered after five years; Toyota could not confirm or rule out use | Yes |
| 2023 | **Yandex** | 44.7GB source repository leaked on a hacker forum. Yandex denied a hack and blamed a former employee; a former Yandex executive described the motive as political. | Insider (ex-employee), per Yandex | No |
| 2023 | **CircleCI** | Infostealer malware on an engineer's laptop (Dec 16, 2022; not detected by antivirus) stole a 2FA-backed SSO session. The attacker reached production data including customers' tokens and keys; about three weeks undetected. | Endpoint malware; session theft bypassed MFA; one engineer had broad privileges | No |
| 2024 | **Mercedes-Benz** | An employee's GitHub token in a public repo exposed from Sept 2023 until Jan 2024. Researchers said it gave access to the whole internal GitHub Enterprise server; Mercedes said it covered a number of repositories, not all. | Human error; token in public repo | Yes |
| 2024 | **xz Utils** | A backdoor was added to a core Linux library after a roughly two-year social-engineering campaign against its maintainer. The malicious build file was in the release tarballs, not in the Git repository. Found by chance in March 2024. | Social engineering of an overloaded maintainer; release artifacts differing from source | No |
| 2024 | **Microsoft (Midnight Blizzard)** | A password spray against a legacy test account without MFA (Nov 2023) led to email theft; secrets found in that email were then used to reach some source repositories. | Weak/legacy authentication (no MFA); secrets shared in email | No |
| 2026 | Claude Code (Anthropic) | Full source shipped in a public npm package via a source map file. | Packaging/build configuration error; missing release checks | Yes |
| 2026 | **GitHub internal repos** | About 3,800 internal repositories accessed after an employee's machine was compromised by a poisoned VS Code extension; GitHub linked it to the TanStack npm compromise. Reports differ in detail. | Poisoned developer tool; stolen credentials | Employee unaware |
| 2026 | CrowdSec, Checkmarx | Source stolen from GitHub repos. CrowdSec says a laptop hit by the TanStack attack was the likely source, and that the employee's GitHub access had been left open. Checkmarx tied it to the Trivy supply-chain attack; Lapsus$ claimed the data. | Developer tool supply chain; stolen tokens; access not revoked | No |
| 2025-26 | npm "Shai-Hulud" family worms | Self-spreading malware steals developer tokens and republishes poisoned packages (for example hundreds of packages in under four hours in Aug 2026). | Stolen publishing tokens; install-time scripts | No |
| 2026 | Exposed `.git` folders | About 5 million web servers exposed Git metadata; 252,733 exposed a config file with live deployment credentials. | Server misconfiguration; secrets in repo metadata | Yes |
| 2026 | Target | About 860GB of code and docs appeared online and were confirmed genuine. | Not disclosed | Unknown |
| 2025 | Hardcoded secrets (GitGuardian report) | 28.65 million new hardcoded secrets in public GitHub commits; internal repos six times more likely to contain secrets; 64% of credentials valid in 2022 were still unrevoked in 2026. | Secrets in code; no rotation | Yes |

### 15.2 Major earlier incidents and insider cases

| Year | Incident | What happened | Root cause |
|---|---|---|---|
| 2003 | Half-Life 2 (Valve) | Complete source stolen by a hacker who had been inside Valve's network for months, using an Outlook security hole. | Network intrusion; unpatched software |
| 2004 | Windows NT 4.0 / Windows 2000 | Large portions leaked online (about 13.5 million lines reported). Microsoft said there was no indication of a breach of its own network; press reported a partner as the likely source. | Not confirmed; possibly a partner |
| 2004 | Cisco IOS | About 800MB of IOS 12.3 source reported stolen (reported by a Russian security site; FBI investigated). | Reported network break-in |
| 2009-2011 | Insider cases (Goldman Sachs, Federal Reserve contractor) | A script copied, compressed, encrypted and uploaded code to an outside server; a contractor copied code to a portable drive and personal computers. | Insider with legitimate access |
| Ongoing | CERT insider-threat research | Insiders emailed code to personal accounts or uploaded it externally, mostly while still employed; theft is hard to detect until the data is leaving. | Insider with legitimate access |

### 15.3 What the incidents have in common (root causes) and the requirement for Fusion

| # | Root cause | Seen in | Requirement | Library |
|---|---|---|---|---|
| R1 | Secrets and tokens inside code or repo metadata | Toyota, Mercedes, `.git` exposure, GitGuardian | SEC-01, SEC-02 | Governance, SourceControl |
| R2 | Tampering with the build or release step, not the repository | SolarWinds, Codecov, xz | SEC-04 | SourceControl, WorkTracking, Governance |
| R3 | Accidental publication of debug/internal files or config | Claude Code, Twitch, `.git` | SEC-03, SEC-10 | SourceControl, Governance, WorkTracking |
| R4 | Stolen developer credentials, sessions or tokens | GitHub, CircleCI, LastPass, CrowdSec, worms, Lapsus$ | SEC-07, SEC-08 | Governance, SourceControl |
| R5 | Insiders and ex-employees copying code | Yandex, CERT cases | SEC-06, SEC-08 | SourceControl, Governance |
| R6 | Weak or exempt authentication | Microsoft (no MFA on a legacy test account), Lapsus$ | SEC-09 | Governance |
| R7 | Unreviewed or socially engineered changes | xz, npm worms | SEC-05 | Governance, SourceControl |
| R8 | Slow detection and revocation | Toyota (five years), CircleCI (three weeks), LastPass (eight weeks), unrevoked secrets | SEC-08, SEC-11 | Governance |
| R9 | Compromised user or machine at run time | CircleCI, LastPass | SEC-12, SEC-13 | Governance policy profile, runtime |

### 15.4 Derived security requirements (proposals, IDs are for tracking)

| ID | When | Requirement | Library |
|---|---|---|---|
| SEC-01 | Dev | In governed projects, a literal secret (key, token, password) in source is a compile error. Secrets are referenced from a secrets store and fetched at runtime. | Governance (rule), compiler |
| SEC-02 | Dev | Commit/push scans for secrets and blocks them; the attempt is logged. Credentials are never stored in repository metadata, and repository history is never deployed to servers. | SourceControl |
| SEC-03 | Release | Release gate with an allowed-artifact manifest: blocks source maps, debug symbols, VCS metadata, config/credential files and unexpected file sizes from anything published. | SourceControl, Governance |
| SEC-04 | Release | Every release artifact traces to a recorded commit and an approved change (ticket, approver). The built output is verified against the source commit; code in a release that has no linked change is flagged as orphan code. | SourceControl, WorkTracking, Governance |
| SEC-05 | Dev | Approvals only from authorised people; governed areas need a second reviewer. Changes to the approver or maintainer list are themselves governed, recorded changes. | Governance |
| SEC-06 | Dev | Read access to source is scoped (by module or project), bulk clone and export are controlled, and reads and clones are logged with alerts on unusual volume. | SourceControl |
| SEC-07 | Dev | Managed dev workspace: IDE loads only signed or allowlisted extensions and dependencies, versions pinned, install scripts blocked, and copy/export/print controls apply. Preferably the code stays on the server. | Governance (policy profile) |
| SEC-08 | Dev | Short-lived credentials bound to the person and device instead of long-lived tokens on laptops; access revoked automatically at offboarding and when a leak is detected. | Governance, SourceControl |
| SEC-09 | Dev | Multi-factor authentication is required for every account that can reach governed code; no exempt legacy or test environments. | Governance (policy profile) |
| SEC-10 | Dev/Ops | Infrastructure and configuration changes need a change record and approval, like code changes (Twitch's leak came from a configuration change). | WorkTracking, Governance |
| SEC-11 | All | Immutable audit trail with alerts on anomalies; the time to detect and to revoke is recorded. | Governance |
| SEC-12 | Runtime | Only signed builds run, and the runtime checks integrity at startup. Each user must log in under the OS/organisation policy, with least privilege and no credentials on disk. | Governance (policy profile), runtime |
| SEC-13 | All | The policy profile (section 8) is locked and signed by an administrator, and the compiler/IDE refuse to build, commit or run if settings deviate from it. | Governance |

### 15.5 Limits (what these libraries cannot do)

- Restricting copying cannot stop someone photographing a screen. The goal is to make leaks hard, logged and attributable.
- A logged-in developer on a compromised machine can still reach what that developer can reach. That is why credentials must be short-lived, access scoped and activity audited. In the CircleCI case the malware was not caught by antivirus, so Fusion tooling does not replace endpoint security.
- Microsoft stated that it does not depend on the secrecy of its source code for security. In these incidents most of the harm came from stolen secrets, build tampering and unreviewed changes, not from the code simply being read. Design priority: integrity and secrets first, code confidentiality second.
- A trusted maintainer or approver who has been socially engineered (xz) cannot be fully stopped. The libraries can make unreviewed, unlinked or unusual changes visible.
- Malware running as the logged-in user inherits that user's rights. Runtime restrictions limit the damage but do not prevent the infection.

### 15.6 Open points from this section

1. Which of SEC-01 to SEC-13 are mandatory in Controlled mode, and which are per-project checkboxes (section 9)?
2. How can the compiler verify a built artifact against a source commit (reproducible builds, signed build records)?
3. How much of SEC-07 (managed workspace, extension allowlist, copy controls) can the Fusion IDE enforce itself, and how much needs the OS, a remote workspace or endpoint tools?
4. Should Fusion ship its own secrets-store interface, or only integrate with existing ones?

## 16. Sources

- OpenFastTrace user guide and repository: https://github.com/itsallcode/openfasttrace
- OpenFastTrace Language Server: https://github.com/fgorke/openfasttrace-language-server
- StrictDoc documentation (traceability between requirements and source code): https://strictdoc.readthedocs.io/
- Quarto-Needs (requirements as code): https://pypi.org/project/quarto-needs/
- DO-178C traceability: https://en.wikipedia.org/wiki/DO-178 and https://www.electronicdesign.com/technologies/embedded/article/21794228/do-178c-enhances-safety-critical-avionics-software-development
- ReqToCode, compile-time verified traceability (research): https://arxiv.org/abs/2603.13999
- SPARK / Ada contracts: https://en.wikipedia.org/wiki/SPARK_(programming_language)
- Jira Smart Commits: https://confluence.atlassian.com/jirasoftwarecloud/processing-issues-with-smart-commits-788960027.html
- GitHub, pull requests as end-to-end traceability: https://github.blog/enterprise-software/governance-and-compliance/demonstrating-end-to-end-traceability-with-pull-requests/
- SOX IT controls and change management evidence: https://safeguard.sh/resources/blog/sox-it-controls-meets-software-controls
- ISO 27001 Annex A 8.32 audit guide: https://hightable.io/how-to-audit-iso-27001-annex-a-8-32/
- Cedar vs Rego: https://aws.amazon.com/blogs/security/migrating-from-open-policy-agent-to-amazon-verified-permissions and Cedar paper https://arxiv.org/pdf/2403.04651
- DMN (OMG): https://www.omg.org/dmn/ and Apache KIE / Drools DMN: https://kie.apache.org/drools/dmn/
