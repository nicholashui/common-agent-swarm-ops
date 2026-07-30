# Rubric — `video.rubric.cameraoperator.v1`

```json
{
  "schema_version": "1.0",
  "rubric_id": "video.rubric.cameraoperator.v1",
  "agent_id": "video.cameraoperator",
  "title": "L2 craft rubric for CameraOperatorAgent",
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
          "name": "Frame steadiness, focus-hit %, action centering",
          "description": "Frame steadiness, focus-hit %, action centering",
          "weight": 1.0,
          "threshold_hint": null,
          "score_min": 0,
          "score_max": 100
        }
      ]
    },
    "L3_preference": {
      "description": "Optional pairwise/arena preference when human or synthetic preference data exists",
      "surpass_signal_design": "Focus-pull accuracy >99% vs SOC ~97% baseline",
      "note": "Do not claim surpass until measured baseline exists"
    }
  },
  "refine_policy": {
    "max_refinement_count": 3,
    "on_fail": "refine_or_escalate_hitl"
  },
  "sources": {
    "agents_md_self_quality_criteria": "Frame steadiness, focus-hit %, action centering",
    "research": [
      "LLM-as-Judge",
      "Self-Refine",
      "Constitutional AI"
    ]
  }
}
```
