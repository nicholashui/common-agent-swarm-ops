# Rubric — `video.rubric.screenwriter.v1`

```json
{
  "schema_version": "1.0",
  "rubric_id": "video.rubric.screenwriter.v1",
  "agent_id": "video.screenwriter",
  "title": "L2 craft rubric for ScreenwriterAgent",
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
          "name": "Save-the-Cat beat pass",
          "description": "Save-the-Cat beat pass",
          "weight": 0.3333,
          "threshold_hint": null,
          "score_min": 0,
          "score_max": 100
        },
        {
          "id": "d2",
          "name": "dialogue distinctiveness (embedding distance ≥τ)",
          "description": "dialogue distinctiveness (embedding distance ≥τ)",
          "weight": 0.3333,
          "threshold_hint": null,
          "score_min": 0,
          "score_max": 100
        },
        {
          "id": "d3",
          "name": "rewrite delta",
          "description": "rewrite delta",
          "weight": 0.3334,
          "threshold_hint": null,
          "score_min": 0,
          "score_max": 100
        }
      ]
    },
    "L3_preference": {
      "description": "Optional pairwise/arena preference when human or synthetic preference data exists",
      "surpass_signal_design": "Wins ≥50% blind read vs Black List Top-10 (WGA panel emulated)",
      "note": "Do not claim surpass until measured baseline exists"
    }
  },
  "refine_policy": {
    "max_refinement_count": 3,
    "on_fail": "refine_or_escalate_hitl"
  },
  "sources": {
    "agents_md_self_quality_criteria": "Save-the-Cat beat pass; dialogue distinctiveness (embedding distance ≥τ); rewrite delta",
    "research": [
      "LLM-as-Judge",
      "Self-Refine",
      "Constitutional AI"
    ]
  }
}
```
