# Rubric — `video.rubric.colorist.v1`

```json
{
  "schema_version": "1.0",
  "rubric_id": "video.rubric.colorist.v1",
  "agent_id": "video.colorist",
  "title": "L2 craft rubric for ColoristAgent",
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
          "name": "ΔE drift <2",
          "description": "ΔE drift <2",
          "weight": 0.3333,
          "threshold_hint": "<2",
          "score_min": 0,
          "score_max": 100
        },
        {
          "id": "d2",
          "name": "skin-tone IT8 alignment",
          "description": "skin-tone IT8 alignment",
          "weight": 0.3333,
          "threshold_hint": null,
          "score_min": 0,
          "score_max": 100
        },
        {
          "id": "d3",
          "name": "mood vector match",
          "description": "mood vector match",
          "weight": 0.3334,
          "threshold_hint": null,
          "score_min": 0,
          "score_max": 100
        }
      ]
    },
    "L3_preference": {
      "description": "Optional pairwise/arena preference when human or synthetic preference data exists",
      "surpass_signal_design": "Beats junior colorist in blind preference; matches senior within ΔE",
      "note": "Do not claim surpass until measured baseline exists"
    }
  },
  "refine_policy": {
    "max_refinement_count": 3,
    "on_fail": "refine_or_escalate_hitl"
  },
  "sources": {
    "agents_md_self_quality_criteria": "ΔE drift <2; skin-tone IT8 alignment; mood vector match",
    "research": [
      "LLM-as-Judge",
      "Self-Refine",
      "Constitutional AI"
    ]
  }
}
```
