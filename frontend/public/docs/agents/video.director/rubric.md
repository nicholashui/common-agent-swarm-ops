# Rubric — `video.rubric.director.v1`

```json
{
  "schema_version": "1.0",
  "rubric_id": "video.rubric.director.v1",
  "agent_id": "video.director",
  "title": "L2 craft rubric for DirectorAgent",
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
          "name": "Shot-intent fidelity (CLIP-T ≥0.32)",
          "description": "Shot-intent fidelity (CLIP-T ≥0.32)",
          "weight": 0.3333,
          "threshold_hint": "≥0.32",
          "score_min": 0,
          "score_max": 100
        },
        {
          "id": "d2",
          "name": "story-beat coverage 100%",
          "description": "story-beat coverage 100%",
          "weight": 0.3333,
          "threshold_hint": null,
          "score_min": 0,
          "score_max": 100
        },
        {
          "id": "d3",
          "name": "pacing curve matches genre prior",
          "description": "pacing curve matches genre prior",
          "weight": 0.3334,
          "threshold_hint": null,
          "score_min": 0,
          "score_max": 100
        }
      ]
    },
    "L3_preference": {
      "description": "Optional pairwise/arena preference when human or synthetic preference data exists",
      "surpass_signal_design": "Wins ≥55% blind pairwise vs DGA cuts (Arena)",
      "note": "Do not claim surpass until measured baseline exists"
    }
  },
  "refine_policy": {
    "max_refinement_count": 3,
    "on_fail": "refine_or_escalate_hitl"
  },
  "sources": {
    "agents_md_self_quality_criteria": "Shot-intent fidelity (CLIP-T ≥0.32); story-beat coverage 100%; pacing curve matches genre prior",
    "research": [
      "LLM-as-Judge",
      "Self-Refine",
      "Constitutional AI"
    ]
  }
}
```
