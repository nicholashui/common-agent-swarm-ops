# LQR / Consistency Rubric (Video Pack)

**Wave:** 3  
**Pack:** `business/video`  
**Related golden:** `evals/golden/video-lqr-consistency.json`

## Purpose

Human-readable rubric for Look-Quality-Review (LQR) and cross-frame consistency checks on video archetype DNA. Used as provenance for sandbox fitness; offline unit evals remain structural (gates, tools, no auto-promote).

## Dimensions

| Dimension | Pass signal (proxy) |
|-----------|---------------------|
| **LQR** | QC step present (`video_qc_stub` / aiqa agent); publish remains human-gated |
| **Consistency** | Same agent_id / genome lineage for aesthetics QC across generations; no unrestricted tools |
| **Aesthetics** | Hook/script steps use namespaced video tools only |
| **Psychological alignment** | No deception flags; golden input stays curiosity-framed |

## Sandbox rules

- Never auto-promote variants that only “pass” this rubric.
- Production DNA mutation forbidden; use evolution canary/promote APIs.
- Lessons that improve LQR utility must carry `agent_id` (ALC).

## Provenance

- `improvements.md` Wave 3  
- Wave 2 spine / viral-hook DNA baseline  
- va-agent-swarm LQR process family (pack-retained under N3)
