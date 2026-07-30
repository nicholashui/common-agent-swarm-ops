# Rubric — `video.rubric.lipsync.v1`

```json
{
  "schema_version": "1.0",
  "rubric_id": "video.rubric.lipsync.v1",
  "agent_id": "video.lipsync",
  "title": "L2 craft rubric for LipSyncAgent",
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
          "name": "Sync error below threshold, correction specificity, low false positives",
          "description": "Sync error below threshold, correction specificity, low false positives",
          "weight": 1.0,
          "threshold_hint": null,
          "score_min": 0,
          "score_max": 100
        }
      ]
    },
    "L3_preference": {
      "description": "Optional pairwise/arena preference when human or synthetic preference data exists",
      "surpass_signal_design": "Finds sync drift more precisely than general QC review",
      "note": "Do not claim surpass until measured baseline exists"
    }
  },
  "refine_policy": {
    "max_refinement_count": 3,
    "on_fail": "refine_or_escalate_hitl"
  },
  "sources": {
    "agents_md_self_quality_criteria": "Sync error below threshold, correction specificity, low false positives",
    "research": [
      "LLM-as-Judge",
      "Self-Refine",
      "Constitutional AI"
    ]
  }
}
```
