# Trace — Video pipeline brief → spine

| REQ | Design | Tasks | Implementation | Tests | Evidence |
|-----|--------|-------|----------------|-------|----------|
| REQ-1 | design.md | tasks#1 | `video_brief_spine.py`, `composer.py`, `product_facade.py` | `test_build_user_brief_*`, `test_materialize_video_brief_*` | epic_e_evidence.md |
| REQ-2 | design.md | tasks#1 | `recommend_composition` Phase-1 + spine ids | `test_materialize_video_brief_persists_and_phase1` | plan.md |
| REQ-3 | design.md | tasks#2 | `init_spine_state`, DNA load | `test_design_spine_steps_load` | plan.md |
| REQ-4 | design.md | tasks#2 | `run_spine_step`, artifact GET | `test_artifact_get_*`, dry-run tests | epic_e_evidence.md |
| REQ-5 | design.md | tasks#3 | package approval store + APIs | `test_spine_dry_run_to_package_gate` | epic_e_evidence.md |
| REQ-6 | design.md | tasks#3 | `decide_package` deny path | `test_spine_dry_run_to_package_gate` | plan.md |
| REQ-7 | design.md | tasks#4 | activity-live, dashboard-live | frontend projection tests | epic_e_evidence.md |
| REQ-8 | design.md | tasks#5 | `video-spine-template.ts`, AgentWorkflowHome | `video-spine-template.test.ts` | epic_e_evidence.md |
