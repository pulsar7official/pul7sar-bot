# PUL7SAR Implementation Guide

Version: 1.0

Status: Official AI Development Workflow

---

# 1. Purpose

This document defines the mandatory workflow for implementing any part of the PUL7SAR platform.

Every AI model or engineer working on the project must follow this workflow before writing, modifying, or deleting any source code.

This document complements the architecture and specifications.

---

# 2. Source of Truth

Before implementing any feature, the implementation order is:

1. README.md
2. 02_ARCHITECTURE.md
3. 04_RENDERING_SPECIFICATION.md
4. Relevant specification document (if available)
5. Current sprint task

If implementation conflicts with documentation, stop and report the conflict.

Never silently choose one over the other.

---

# 3. Sprint Workflow

Each sprint must follow exactly this sequence:

Understand the task

↓

Read the required documentation

↓

Identify affected modules

↓

Explain the implementation plan

↓

Wait for approval (if requested)

↓

Implement

↓

Self-review

↓

Present completed work

No sprint may skip self-review.

---

# 4. Implementation Rules

During implementation:

- Never invent architecture.
- Never bypass documented interfaces.
- Never duplicate existing functionality.
- Never hardcode configuration values.
- Never modify unrelated modules.
- Prefer extension over modification.

---

# 5. Decision Rules

The implementer may decide implementation details only when:

- the architecture already defines the behavior;
- the decision does not change any public contract;
- the decision does not affect another subsystem.

Otherwise, stop and request clarification.

---

# 6. Documentation Before Code

If implementation requires a new architectural concept that is not documented:

Stop.

Document it first.

Only then implement it.

---

# 7. Commit Rules

Every commit must:

- represent one logical unit of work;
- compile independently whenever possible;
- contain a meaningful commit message;
- avoid unrelated changes.

Large commits must be split into smaller logical commits.

---

# 8. Self Review Checklist

Before considering any task complete, verify:

- Architecture respected.
- Interfaces respected.
- No duplicated logic.
- No hidden dependencies.
- No circular imports.
- No hardcoded values.
- Naming follows project standards.
- Public APIs documented.
- Errors handled appropriately.

Only then report completion.

---

# 9. Communication Rules

When reporting progress:

Always distinguish between:

- completed;
- partially completed;
- blocked.

If blocked:

Explain exactly:

- what is missing;
- why implementation cannot continue;
- which document or decision is required.

Do not guess.

---

# 10. Long-Term Principle

The goal is not only to produce working code.

The goal is to build a platform that remains maintainable, scalable, testable, and understandable for many years.

Implementation speed is important.

Architectural integrity is mandatory.
