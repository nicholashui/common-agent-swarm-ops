# Rubric — `video.rubric.audiobooknarrator.v1`

```json
{
  "schema_version": "1.0",
  "rubric_id": "video.rubric.audiobooknarrator.v1",
  "agent_id": "video.audiobooknarrator",
  "title": "L2 craft rubric for AudiobookNarratorAgent",
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
          "name": "Vocal stamina (no drift 60min)",
          "description": "Vocal stamina (no drift 60min)",
          "weight": 0.5,
          "threshold_hint": null,
          "score_min": 0,
          "score_max": 100
        },
        {
          "id": "d2",
          "name": "character distinction (embedding distance)",
          "description": "character distinction (embedding distance)",
          "weight": 0.5,
          "threshold_hint": null,
          "score_min": 0,
          "score_max": 100
        }
      ]
    },
    "L3_preference": {
      "description": "Optional pairwise/arena preference when human or synthetic preference data exists",
      "surpass_signal_design": "Wins AudioFile blind eval at fraction of studio time",
      "note": "Do not claim surpass until measured baseline exists"
    }
  },
  "refine_policy": {
    "max_refinement_count": 3,
    "on_fail": "refine_or_escalate_hitl"
  },
  "sources": {
    "agents_md_self_quality_criteria": "Vocal stamina (no drift 60min); character distinction (embedding distance)",
    "research": [
      "LLM-as-Judge",
      "Self-Refine",
      "Constitutional AI"
    ]
  }
}
```
