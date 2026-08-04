# Plan samples — video pack only

Load in UI: **Plan** (`/composer`) → **▦** next to Requirements → Load / Load + AI plan.

All samples are **video-domain** (and may mention specials only when relevant).  
They do **not** include trading, COBOL, or other out-of-pack demos.

Source: `frontend/src/lib/projections/composer-landing.ts` (`COMPOSER_SAMPLES`).

Execute board samples: `frontend/src/lib/projections/canvas-samples.ts` (`CANVAS_SAMPLES`) — same rule: **video.* agent ids only**.

| Sample | Kind | Intent |
|--------|------|--------|
| YouTube wuxia short | happy_path | hierarchical + verify |
| Trend research → script | happy_path | webresearch / trend / writers |
| Social under budget | happy_path | lean editor + a11y + sound |
| Cost vs quality | hitl_demo | video production conflict |
| Full feature hierarchy | happy_path | orch → planner → depts |
| Brand spot + compliance | happy_path | brand / creative + gates |
| UGC vs cinematic | hitl_demo | video scope conflict |

Agent inventory lives under:

- `business/video/agents/*`
- `business/specials/agents/*` (optional specials; not used in default Plan/Execute samples)
