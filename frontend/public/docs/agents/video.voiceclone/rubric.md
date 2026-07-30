# Rubric — `video.rubric.voiceclone.v1`

```json
{
  "schema_version": "1.0",
  "rubric_id": "video.rubric.voiceclone.v1",
  "agent_id": "video.voiceclone",
  "title": "L2 craft rubric for VoiceCloneAgent / LipSyncSpecialist",
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
          "name": "Voice MOS ≥4.2",
          "description": "Voice MOS ≥4.2",
          "weight": 0.3333,
          "threshold_hint": "≥4.2",
          "score_min": 0,
          "score_max": 100
        },
        {
          "id": "d2",
          "name": "phoneme-viseme error <40ms",
          "description": "phoneme-viseme error <40ms",
          "weight": 0.3333,
          "threshold_hint": "<40",
          "score_min": 0,
          "score_max": 100
        },
        {
          "id": "d3",
          "name": "consent verified",
          "description": "consent verified",
          "weight": 0.3334,
          "threshold_hint": null,
          "score_min": 0,
          "score_max": 100
        }
      ]
    },
    "L3_preference": {
      "description": "Optional pairwise/arena preference when human or synthetic preference data exists",
      "surpass_signal_design": "Wins blind MOS vs professional ADR",
      "note": "Do not claim surpass until measured baseline exists"
    }
  },
  "refine_policy": {
    "max_refinement_count": 3,
    "on_fail": "refine_or_escalate_hitl"
  },
  "sources": {
    "agents_md_self_quality_criteria": "Voice MOS ≥4.2; phoneme-viseme error <40ms; consent verified",
    "research": [
      "LLM-as-Judge",
      "Self-Refine",
      "Constitutional AI"
    ]
  }
}
```
