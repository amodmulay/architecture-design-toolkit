---
name: architecture-review
description: Review an existing or proposed software, cloud, data, integration, or AI architecture for quality, risks, gaps, and trade-offs.
---

# Architecture Review

Perform an evidence-based architecture review. Start by inspecting diagrams, source code, specifications, ADRs, infrastructure definitions, and operational documentation available in the repository.

## Review dimensions

- Functional fit and requirement coverage
- Modularity, coupling, cohesion, and domain boundaries
- Scalability, performance, throughput, and capacity assumptions
- Availability, resilience, recovery, and failure isolation
- Security, identity, secrets, network boundaries, and threat exposure
- Privacy, data residency, retention, lineage, and regulatory obligations
- Observability, operations, deployment, and supportability
- Cost drivers, vendor lock-in, portability, and exit strategy
- AI-specific concerns: grounding, evaluation, model routing, prompt/data security, human oversight, and auditability

## Output

Provide:
1. Executive assessment and scope.
2. Findings ranked Critical / High / Medium / Low.
3. Evidence and impact for each finding.
4. Recommended remediation with priority and dependencies.
5. Open questions and assumptions.
6. A target-state view when requested.

Do not invent evidence. Distinguish confirmed issues from risks and unanswered questions. Avoid generic best-practice lists that are not tied to the actual system.
