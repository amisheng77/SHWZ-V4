---
name: shwz-literary-review
description: Independently review prose chapters in the SHWZ novel project for literary quality, reader engagement and Canon continuity; always read prose before agent self-assessment and produce evidence-backed revision priorities.
---

# SHWZ Literary Review Skill

## Scope

Use for reviews of `《山河无主》` full chapter drafts, revised drafts and CH01—05 combined opening-arc manuscripts. **Do not use as the writing Agent or change locked prose.**

## Inputs

- Draft text or exact `repository/path@commit_sha` (prefer immutable commit URL, never assume main is the draft revision).
- Logical CH number.
- Chapter Contract and prior chapter Delta when available.

## Procedure

1. Read `review/SHWZ_Literary_Review_Protocol_V1.0.md`.
2. Confirm the exact draft content, version, logical chapter, and what material has actually been read. If tools cannot access the text, ask for pasted text; do not invent a review.
3. Independently review prose first, keeping the Agent's self-evaluation aside. Write genuine reader impressions and concrete text evidence before Canon fact checking.
4. Read live main `SHWZ_Current_Context.md` and relevant `docs/00—05` owner(s), registry/terms and targeted chapter contract. Distinguish Canon hard conflicts from legitimate new creative details. Respect `state/legacy_quarantine.json`.
5. Produce `review/templates/Chapter_Review_Report_Template_V1.0.md`: strengths, six literary dimensions, P0/P1/P2, evidence-backed fixes, Canon checks, final verdict. Limit preference-driven revisions.
6. On follow-up, compare drafts and previous P0/P1 before giving fresh suggestions; do CH01—05 holistic opening-arc review only after all five are supplied.
7. Default to **read-only review** and answer in chat. Save under `work/audits/literary/` only upon explicit author request; never automatically modify drafts, Canon, contracts, lock, or `state/chapters.json`.

## Non-negotiables

- Literary engagement first; Canon compliance second. Neither is a substitute for the other.
- **山河可以无主，英雄不可无光；历史可以冷酷，传奇必须炽烈。**
- No formulaic forced moral ambiguity, hero-dimming, suppressing actual supernatural spectacle, or mechanical “AI prose detection.”
- Do not call a ChatGPT skill “installed” just because this Markdown exists in the repository; clients must support/discover it or read the file explicitly.
