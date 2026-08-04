# Evidence — Video pipeline brief → spine

## Commands (representative)

```text
cd backend
python -m pytest tests/unit/api/test_video_brief_spine.py tests/unit/api/test_product_facade_routes.py -q

cd frontend
node --import tsx --test src/lib/projections/video-spine-template.test.ts src/lib/projections/activity-live.test.ts src/lib/projections/dashboard-live.test.ts
```

## Notes

- Process-local façade: restart clears drafts/approvals/artifacts.
- Honesty: stub run · not production media; production_ready remains false.
- Residual risk: package gates are façade-authoritative unless mirrored into control-plane approval repository (fallback read/decision on `/approvals/{id}` when package id is present).
