# Rubric — `video.rubric.standardseditor.v1`

```json
{
  "schema_version": "1.0",
  "rubric_id": "video.rubric.standardseditor.v1",
  "agent_id": "video.standardseditor",
  "title": "L2 craft rubric for StandardsEditorAgent",
  "pass_threshold": 85,
  "max_score": 100,
  "layers": {
    "L1_spec": {
      "description": "Machine validators: schema, format, required fields, policy allowlist",
      "must_pass": true
    },
    "L2_rubric": {
      "description": "LLM-as-Judge or scorer against dimensions below",
      "pass_threshold": 85,
      "dimensions": [
        {
          "id": "d1",
          "name": "Standards-compliance rate, attribution accuracy, corrections readiness",
          "description": "Standards-compliance rate, attribution accuracy, corrections readiness",
          "weight": 1.0,
          "threshold_hint": null,
          "score_min": 0,
          "score_max": 100
        }
      ]
    },
    "L3_preference": {
      "description": "Optional pairwise/arena preference when human or synthetic preference data exists",
      "surpass_signal_design": "Reduces standards drift better than late-stage copy edits",
      "note": "Do not claim surpass until measured baseline exists"
    }
  },
  "refine_policy": {
    "max_refinement_count": 3,
    "on_fail": "refine_or_escalate_hitl"
  },
  "sources": {
    "agents_md_self_quality_criteria": "Standards-compliance rate, attribution accuracy, corrections readiness",
    "research": [
      "LLM-as-Judge",
      "Self-Refine",
      "Constitutional AI"
    ]
  }
}
```
