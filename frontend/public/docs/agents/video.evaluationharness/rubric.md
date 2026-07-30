# Rubric — `video.rubric.evaluationharness.v1`

```json
{
  "schema_version": "1.0",
  "rubric_id": "video.rubric.evaluationharness.v1",
  "agent_id": "video.evaluationharness",
  "title": "L2 craft rubric for EvaluationHarnessAgent",
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
          "name": "Regression precision/recall",
          "description": "Regression precision/recall",
          "weight": 0.5,
          "threshold_hint": null,
          "score_min": 0,
          "score_max": 100
        },
        {
          "id": "d2",
          "name": "alert latency <1h",
          "description": "alert latency <1h",
          "weight": 0.5,
          "threshold_hint": "<1",
          "score_min": 0,
          "score_max": 100
        }
      ]
    },
    "L3_preference": {
      "description": "Optional pairwise/arena preference when human or synthetic preference data exists",
      "surpass_signal_design": "Catches regressions faster than ML-eng rotation",
      "note": "Do not claim surpass until measured baseline exists"
    }
  },
  "refine_policy": {
    "max_refinement_count": 3,
    "on_fail": "refine_or_escalate_hitl"
  },
  "sources": {
    "agents_md_self_quality_criteria": "Regression precision/recall; alert latency <1h",
    "research": [
      "LLM-as-Judge",
      "Self-Refine",
      "Constitutional AI"
    ]
  }
}
```
