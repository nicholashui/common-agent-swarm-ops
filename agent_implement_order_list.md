# Video agent implementation order

**Date:** 2026-07-13  
**Roster:** `business/video/ROSTER.json` (114 agents)  
**Folder root:** `business/video/agents/`

## Ordering rationale

1. **Spine / control first** — agents needed for orchestrator-down DNA and gates (`orchestrator` → `planner` → `router` → `judge` → `gatekeeper`, then producer/director/screenwriter/research/QC/memory).
2. **Then by craft category** (va order): 1-ATL → 2-Cam → 3-Edit → 4-Snd → 5-Perf → 6-Dist → 7-Edu → 8-AI → 9-Meta (remaining) → 10-Sup.
3. **Within category:** ascending `va_id`.

Use this sequence for L2 activation, deep SPEC polish, tool wiring, or DNA binding — not for deleting later agents (N3 retains all 114).

| order seq | agent id | agent folder path |
|----------:|----------|-------------------|
| 1 | `video.orchestrator` | `business/video/agents/video.orchestrator` |
| 2 | `video.planner` | `business/video/agents/video.planner` |
| 3 | `video.router` | `business/video/agents/video.router` |
| 4 | `video.judge` | `business/video/agents/video.judge` |
| 5 | `video.gatekeeper` | `business/video/agents/video.gatekeeper` |
| 6 | `video.producer` | `business/video/agents/video.producer` |
| 7 | `video.director` | `business/video/agents/video.director` |
| 8 | `video.screenwriter` | `business/video/agents/video.screenwriter` |
| 9 | `video.webresearch` | `business/video/agents/video.webresearch` |
| 10 | `video.aiqaconsistency` | `business/video/agents/video.aiqaconsistency` |
| 11 | `video.memory` | `business/video/agents/video.memory` |
| 12 | `video.showrunner` | `business/video/agents/video.showrunner` |
| 13 | `video.casting` | `business/video/agents/video.casting` |
| 14 | `video.cinematographer` | `business/video/agents/video.cinematographer` |
| 15 | `video.cameraoperator` | `business/video/agents/video.cameraoperator` |
| 16 | `video.dronepilot` | `business/video/agents/video.dronepilot` |
| 17 | `video.editor` | `business/video/agents/video.editor` |
| 18 | `video.colorist` | `business/video/agents/video.colorist` |
| 19 | `video.vfxsupervisor` | `business/video/agents/video.vfxsupervisor` |
| 20 | `video.animator_2d` | `business/video/agents/video.animator_2d` |
| 21 | `video.motiongraphics` | `business/video/agents/video.motiongraphics` |
| 22 | `video.storyboard` | `business/video/agents/video.storyboard` |
| 23 | `video.conceptartist` | `business/video/agents/video.conceptartist` |
| 24 | `video.productiondesign` | `business/video/agents/video.productiondesign` |
| 25 | `video.costumedesign` | `business/video/agents/video.costumedesign` |
| 26 | `video.mua_makeup` | `business/video/agents/video.mua_makeup` |
| 27 | `video.sounddesign` | `business/video/agents/video.sounddesign` |
| 28 | `video.composer` | `business/video/agents/video.composer` |
| 29 | `video.voiceover` | `business/video/agents/video.voiceover` |
| 30 | `video.soundmixer` | `business/video/agents/video.soundmixer` |
| 31 | `video.choreography` | `business/video/agents/video.choreography` |
| 32 | `video.musicvideodirector` | `business/video/agents/video.musicvideodirector` |
| 33 | `video.comedywriter` | `business/video/agents/video.comedywriter` |
| 34 | `video.talent` | `business/video/agents/video.talent` |
| 35 | `video.ugccreator` | `business/video/agents/video.ugccreator` |
| 36 | `video.socialmediastrategist` | `business/video/agents/video.socialmediastrategist` |
| 37 | `video.copywriter` | `business/video/agents/video.copywriter` |
| 38 | `video.creativedirector` | `business/video/agents/video.creativedirector` |
| 39 | `video.performancemarketer` | `business/video/agents/video.performancemarketer` |
| 40 | `video.instructionaldesign` | `business/video/agents/video.instructionaldesign` |
| 41 | `video.sme` | `business/video/agents/video.sme` |
| 42 | `video.factchecker` | `business/video/agents/video.factchecker` |
| 43 | `video.medicalillustrator` | `business/video/agents/video.medicalillustrator` |
| 44 | `video.journalist` | `business/video/agents/video.journalist` |
| 45 | `video.compliance` | `business/video/agents/video.compliance` |
| 46 | `video.finance` | `business/video/agents/video.finance` |
| 47 | `video.foodstylist` | `business/video/agents/video.foodstylist` |
| 48 | `video.travelcine` | `business/video/agents/video.travelcine` |
| 49 | `video.childrensauthor` | `business/video/agents/video.childrensauthor` |
| 50 | `video.audiobooknarrator` | `business/video/agents/video.audiobooknarrator` |
| 51 | `video.signlanguageinterpreter` | `business/video/agents/video.signlanguageinterpreter` |
| 52 | `video.localizationqa` | `business/video/agents/video.localizationqa` |
| 53 | `video.realestatephoto` | `business/video/agents/video.realestatephoto` |
| 54 | `video.promptengineer` | `business/video/agents/video.promptengineer` |
| 55 | `video.avatardesign` | `business/video/agents/video.avatardesign` |
| 56 | `video.voiceclone` | `business/video/agents/video.voiceclone` |
| 57 | `video.personalizationengineer` | `business/video/agents/video.personalizationengineer` |
| 58 | `video.trailereditor` | `business/video/agents/video.trailereditor` |
| 59 | `video.sportsanalyst` | `business/video/agents/video.sportsanalyst` |
| 60 | `video.ideation` | `business/video/agents/video.ideation` |
| 61 | `video.narrativearc` | `business/video/agents/video.narrativearc` |
| 62 | `video.styletransfer` | `business/video/agents/video.styletransfer` |
| 63 | `video.worldbuilding` | `business/video/agents/video.worldbuilding` |
| 64 | `video.moodboard` | `business/video/agents/video.moodboard` |
| 65 | `video.novelty` | `business/video/agents/video.novelty` |
| 66 | `video.emotionalarc` | `business/video/agents/video.emotionalarc` |
| 67 | `video.archiveresearch` | `business/video/agents/video.archiveresearch` |
| 68 | `video.trendintelligence` | `business/video/agents/video.trendintelligence` |
| 69 | `video.competitorintelligence` | `business/video/agents/video.competitorintelligence` |
| 70 | `video.citation` | `business/video/agents/video.citation` |
| 71 | `video.interviewsynthesis` | `business/video/agents/video.interviewsynthesis` |
| 72 | `video.benchmarkresearch` | `business/video/agents/video.benchmarkresearch` |
| 73 | `video.promptoptimizer` | `business/video/agents/video.promptoptimizer` |
| 74 | `video.costoptimizer` | `business/video/agents/video.costoptimizer` |
| 75 | `video.latencyoptimizer` | `business/video/agents/video.latencyoptimizer` |
| 76 | `video.retentionoptimizer` | `business/video/agents/video.retentionoptimizer` |
| 77 | `video.roasoptimizer` | `business/video/agents/video.roasoptimizer` |
| 78 | `video.accessibilityoptimizer` | `business/video/agents/video.accessibilityoptimizer` |
| 79 | `video.evaluationharness` | `business/video/agents/video.evaluationharness` |
| 80 | `video.safetyredteam` | `business/video/agents/video.safetyredteam` |
| 81 | `video.analyst` | `business/video/agents/video.analyst` |
| 82 | `video.audiencesim` | `business/video/agents/video.audiencesim` |
| 83 | `video.accessibility` | `business/video/agents/video.accessibility` |
| 84 | `video.brand` | `business/video/agents/video.brand` |
| 85 | `video.brandstrategist` | `business/video/agents/video.brandstrategist` |
| 86 | `video.marketing` | `business/video/agents/video.marketing` |
| 87 | `video.seo` | `business/video/agents/video.seo` |
| 88 | `video.community` | `business/video/agents/video.community` |
| 89 | `video.templatedesign` | `business/video/agents/video.templatedesign` |
| 90 | `video.ux` | `business/video/agents/video.ux` |
| 91 | `video.trustsafety` | `business/video/agents/video.trustsafety` |
| 92 | `video.crm` | `business/video/agents/video.crm` |
| 93 | `video.legal` | `business/video/agents/video.legal` |
| 94 | `video.festivalstrategist` | `business/video/agents/video.festivalstrategist` |
| 95 | `video.critic` | `business/video/agents/video.critic` |
| 96 | `video.lms` | `business/video/agents/video.lms` |
| 97 | `video.learnersim` | `business/video/agents/video.learnersim` |
| 98 | `video.continuity` | `business/video/agents/video.continuity` |
| 99 | `video.lipsync` | `business/video/agents/video.lipsync` |
| 100 | `video.musicsupervisor` | `business/video/agents/video.musicsupervisor` |
| 101 | `video.labela_r` | `business/video/agents/video.labela_r` |
| 102 | `video.labeldigital` | `business/video/agents/video.labeldigital` |
| 103 | `video.deepfakedetection` | `business/video/agents/video.deepfakedetection` |
| 104 | `video.comms` | `business/video/agents/video.comms` |
| 105 | `video.archiveproducer` | `business/video/agents/video.archiveproducer` |
| 106 | `video.standardseditor` | `business/video/agents/video.standardseditor` |
| 107 | `video.ethics` | `business/video/agents/video.ethics` |
| 108 | `video.channelmanager` | `business/video/agents/video.channelmanager` |
| 109 | `video.corrections` | `business/video/agents/video.corrections` |
| 110 | `video.mpa` | `business/video/agents/video.mpa` |
| 111 | `video.sales` | `business/video/agents/video.sales` |
| 112 | `video.distributor` | `business/video/agents/video.distributor` |
| 113 | `video.awardsstrategist` | `business/video/agents/video.awardsstrategist` |
| 114 | `video.archivemaster` | `business/video/agents/video.archivemaster` |

**Total:** 114 agents.
