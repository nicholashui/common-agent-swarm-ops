/* AUTO-GENERATED slim catalog for RegistryHome — short descriptions only. */
/* Source: pack-agents.generated.ts. Rebuild: node scripts/build-pack-agents-catalog.mjs */

export interface PackAgentCatalogEntry {
  readonly id: string;
  readonly pack: string;
  readonly name: string;
  readonly role: string;
  readonly status: string;
  readonly description: string;
  readonly versionLabel: string;
  readonly success: string;
  readonly avgTokens: string;
  readonly latency: string;
  readonly usage: string;
  readonly badges: readonly string[];
  readonly domains: readonly string[];
  readonly category: string;
  readonly architecture: string;
  readonly critiqueCompat: string;
}

export const PACK_AGENT_CATALOG_COUNTS = {
  "video": 114,
  "specials": 19,
  "total": 133
} as const;

export const PACK_AGENT_CATALOG: readonly PackAgentCatalogEntry[] = [
  {
    "id": "video.accessibility",
    "pack": "video",
    "name": "Accessibility",
    "role": "AccessibilityAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Owns final accessibility acceptance before release Host role binding: `AccessibilityAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for a…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.accessibilityoptimizer",
    "pack": "video",
    "name": "Accessibilityoptimizer",
    "role": "AccessibilityOptimizerAgent (VA Domain Pack)",
    "status": "registered",
    "description": "WCAG 2.2 contrast, captions, audio description, color-blind safe Host role binding: `AccessibilityOptimizerAgent (VA Domain Pack)`. Design-time VA table content below is historica…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.aiqaconsistency",
    "pack": "video",
    "name": "Aiqaconsistency",
    "role": "AIQAConsistencyAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Catches frame drift, hand/face artifacts, identity breaks Host role binding: `AIQAConsistencyAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-bind…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.analyst",
    "pack": "video",
    "name": "Analyst",
    "role": "AnalystAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Aggregates business, creative, and technical performance telemetry into decision-ready reports Host role binding: `AnalystAgent (VA Domain Pack)`. Design-time VA table content bel…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.animator_2d",
    "pack": "video",
    "name": "Animator 2d",
    "role": "AnimatorAgent (2D/3D) (VA Domain Pack)",
    "status": "registered",
    "description": "Character motion, weight, timing Host role binding: `AnimatorAgent (2D/3D) (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### …",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "network?"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.archivemaster",
    "pack": "video",
    "name": "Archivemaster",
    "role": "ArchiveMasterAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Produces archive-grade masters and preservation packages Host role binding: `ArchiveMasterAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.archiveproducer",
    "pack": "video",
    "name": "Archiveproducer",
    "role": "ArchiveProducerAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Packages archival materials and source assets for reuse-heavy or documentary workflows Host role binding: `ArchiveProducerAgent (VA Domain Pack)`. Design-time VA table content bel…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "network?"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.archiveresearch",
    "pack": "video",
    "name": "Archiveresearch",
    "role": "ArchiveResearchAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Historical / academic / archival deep search Host role binding: `ArchiveResearchAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activ…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.audiencesim",
    "pack": "video",
    "name": "Audiencesim",
    "role": "AudienceSimAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Simulates audience preference, engagement, and drop-off Host role binding: `AudienceSimAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding fo…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.audiobooknarrator",
    "pack": "video",
    "name": "Audiobooknarrator",
    "role": "AudiobookNarratorAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Sustained character + narration Host role binding: `AudiobookNarratorAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### …",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "network?"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.avatardesign",
    "pack": "video",
    "name": "Avatardesign",
    "role": "AvatarDesignAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Synthetic-presenter identity Host role binding: `AvatarDesignAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsi…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.awardsstrategist",
    "pack": "video",
    "name": "Awardsstrategist",
    "role": "AwardsStrategistAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Plans awards submissions and campaign timing Host role binding: `AwardsStrategistAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for acti…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.benchmarkresearch",
    "pack": "video",
    "name": "Benchmarkresearch",
    "role": "BenchmarkResearchAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Monitors VBench, EvalCrafter, MT-Bench, FVD, CLIP-T leaderboards Host role binding: `BenchmarkResearchAgent (VA Domain Pack)`. Design-time VA table content below is historical and…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.brand",
    "pack": "video",
    "name": "Brand",
    "role": "BrandAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Enforces brand voice, claims boundaries, and visual consistency Host role binding: `BrandAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding …",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.brandstrategist",
    "pack": "video",
    "name": "Brandstrategist",
    "role": "BrandStrategistAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Defines audience-value framing and positioning before script and campaign execution Host role binding: `BrandStrategistAgent (VA Domain Pack)`. Design-time VA table content below …",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.cameraoperator",
    "pack": "video",
    "name": "Cameraoperator",
    "role": "CameraOperatorAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Executes framing / focus / move per DoP intent Host role binding: `CameraOperatorAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for acti…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.casting",
    "pack": "video",
    "name": "Casting",
    "role": "CastingAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Voice + likeness selection; audition simulation Host role binding: `CastingAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.channelmanager",
    "pack": "video",
    "name": "Channelmanager",
    "role": "ChannelManagerAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Manages episodic or platform channel operations for cadence and metadata readiness Host role binding: `ChannelManagerAgent (VA Domain Pack)`. Design-time VA table content below is…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.childrensauthor",
    "pack": "video",
    "name": "Childrensauthor",
    "role": "ChildrensAuthorAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Age-appropriate story + safety Host role binding: `ChildrensAuthorAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Res…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.choreography",
    "pack": "video",
    "name": "Choreography",
    "role": "ChoreographyAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Movement design (MVs, dance challenges) Host role binding: `ChoreographyAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. #…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.cinematographer",
    "pack": "video",
    "name": "Cinematographer",
    "role": "CinematographerAgent (DoP) (VA Domain Pack)",
    "status": "registered",
    "description": "Lensing, lighting, composition, look Host role binding: `CinematographerAgent (DoP) (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activat…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.citation",
    "pack": "video",
    "name": "Citation",
    "role": "CitationAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Normalizes sources; grades primary/secondary/tertiary Host role binding: `CitationAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for act…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.colorist",
    "pack": "video",
    "name": "Colorist",
    "role": "ColoristAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Final grade; look consistency Host role binding: `ColoristAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibil…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.comedywriter",
    "pack": "video",
    "name": "Comedywriter",
    "role": "ComedyWriterAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Skits, parody, viral meme writing Host role binding: `ComedyWriterAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Res…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.comms",
    "pack": "video",
    "name": "Comms",
    "role": "CommsAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Coordinates external messaging, disclosure, and public-response posture Host role binding: `CommsAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.community",
    "pack": "video",
    "name": "Community",
    "role": "CommunityAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Captures community response and triages qualitative signals Host role binding: `CommunityAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding …",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.competitorintelligence",
    "pack": "video",
    "name": "Competitorintelligence",
    "role": "CompetitorIntelligenceAgent (VA Domain Pack)",
    "status": "registered",
    "description": "What competitors are shipping Host role binding: `CompetitorIntelligenceAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. #…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.compliance",
    "pack": "video",
    "name": "Compliance",
    "role": "ComplianceAgent (Legal) (VA Domain Pack)",
    "status": "registered",
    "description": "FTC, HIPAA, GDPR, IP, AI-likeness clearance Host role binding: `ComplianceAgent (Legal) (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for act…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.composer",
    "pack": "video",
    "name": "Composer",
    "role": "ComposerAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Original score Host role binding: `ComposerAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA ta…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.conceptartist",
    "pack": "video",
    "name": "Conceptartist",
    "role": "ConceptArtistAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Pre-pro world/character design Host role binding: `ConceptArtistAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Respo…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.continuity",
    "pack": "video",
    "name": "Continuity",
    "role": "ContinuityAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Maintains continuity across character, prop, wardrobe, environment, and time-state Host role binding: `ContinuityAgent (VA Domain Pack)`. Design-time VA table content below is his…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.copywriter",
    "pack": "video",
    "name": "Copywriter",
    "role": "CopywriterAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Scripts, captions, hooks, headlines Host role binding: `CopywriterAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Res…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.corrections",
    "pack": "video",
    "name": "Corrections",
    "role": "CorrectionsAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Coordinates post-publication fixes and correction disclosures Host role binding: `CorrectionsAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-bind…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.costoptimizer",
    "pack": "video",
    "name": "Costoptimizer",
    "role": "CostOptimizerAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Routes between models/providers for $/quality Host role binding: `CostOptimizerAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activa…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.costumedesign",
    "pack": "video",
    "name": "Costumedesign",
    "role": "CostumeDesignAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Character-through-wardrobe Host role binding: `CostumeDesignAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsib…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.creativedirector",
    "pack": "video",
    "name": "Creativedirector",
    "role": "CreativeDirectorAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Campaign concept; cross-discipline taste Host role binding: `CreativeDirectorAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activati…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "network?"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.critic",
    "pack": "video",
    "name": "Critic",
    "role": "CriticAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Simulates reviewer, press, or jury interpretation Host role binding: `CriticAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activatio…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.crm",
    "pack": "video",
    "name": "Crm",
    "role": "CRMAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Delivers audience-targeted or trigger-based campaigns through CRM systems Host role binding: `CRMAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.deepfakedetection",
    "pack": "video",
    "name": "Deepfakedetection",
    "role": "DeepfakeDetectionAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Detects synthetic identity, voice, and provenance deception risks Host role binding: `DeepfakeDetectionAgent (VA Domain Pack)`. Design-time VA table content below is historical an…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.director",
    "pack": "video",
    "name": "Director",
    "role": "DirectorAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Owns vision; issues shot intents, sets pacing, approves takes Host role binding: `DirectorAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.distributor",
    "pack": "video",
    "name": "Distributor",
    "role": "DistributorAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Manages downstream delivery to buyers, platforms, and territories Host role binding: `DistributorAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.dronepilot",
    "pack": "video",
    "name": "Dronepilot",
    "role": "DronePilotAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Aerial cinematography (simulated or real) Host role binding: `DronePilotAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. #…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.editor",
    "pack": "video",
    "name": "Editor",
    "role": "EditorAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Assemble cut; pacing; coverage selection Host role binding: `EditorAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Re…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "network?"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.emotionalarc",
    "pack": "video",
    "name": "Emotionalarc",
    "role": "EmotionalArcAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Maps valence/arousal curve; suggests beats Host role binding: `EmotionalArcAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.ethics",
    "pack": "video",
    "name": "Ethics",
    "role": "EthicsAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Reviews ethical risk, disclosure sufficiency, fairness, and social impact Host role binding: `EthicsAgent (VA Domain Pack)`. Design-time VA table content below is historical and n…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.evaluationharness",
    "pack": "video",
    "name": "Evaluationharness",
    "role": "EvaluationHarnessAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Runs benchmarks (VBench, EvalCrafter, MT-Bench, FVD, CLIP-T); posts regressions Host role binding: `EvaluationHarnessAgent (VA Domain Pack)`. Design-time VA table content below is…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.factchecker",
    "pack": "video",
    "name": "Factchecker",
    "role": "FactCheckerAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Source-grade every claim Host role binding: `FactCheckerAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibilit…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.festivalstrategist",
    "pack": "video",
    "name": "Festivalstrategist",
    "role": "FestivalStrategistAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Positions projects for festivals and submission calendars Host role binding: `FestivalStrategistAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-b…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.finance",
    "pack": "video",
    "name": "Finance",
    "role": "FinanceAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Accurate market / earnings / token facts Host role binding: `FinanceAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### R…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.foodstylist",
    "pack": "video",
    "name": "Foodstylist",
    "role": "FoodStylistAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Camera-ready food, recipe authenticity Host role binding: `FoodStylistAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ###…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.gatekeeper",
    "pack": "video",
    "name": "Gatekeeper",
    "role": "GateKeeperAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Phase transitions; verifies L1/L2/L3 criteria; signs C2PA Host role binding: `GateKeeperAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding f…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.ideation",
    "pack": "video",
    "name": "Ideation",
    "role": "IdeationAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Divergent brainstorm of concepts, hooks, taglines Host role binding: `IdeationAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activat…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.instructionaldesign",
    "pack": "video",
    "name": "Instructionaldesign",
    "role": "InstructionalDesignAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Learning objectives → script → assessment Host role binding: `InstructionalDesignAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for acti…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.interviewsynthesis",
    "pack": "video",
    "name": "Interviewsynthesis",
    "role": "InterviewSynthesisAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Synthesizes practitioner interviews into data Host role binding: `InterviewSynthesisAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for a…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.journalist",
    "pack": "video",
    "name": "Journalist",
    "role": "JournalistAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Reporting + ethical framing Host role binding: `JournalistAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibil…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.judge",
    "pack": "video",
    "name": "Judge",
    "role": "JudgeAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Adjudicates disputes via multi-agent debate; scores against rubric Host role binding: `JudgeAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-bindi…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.labela_r",
    "pack": "video",
    "name": "Labela R",
    "role": "LabelA&RAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Represents label and artist direction for music-specific workflows Host role binding: `LabelA&RAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-bi…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.labeldigital",
    "pack": "video",
    "name": "Labeldigital",
    "role": "LabelDigitalAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Runs label-side digital rollout, metadata, and channel packaging Host role binding: `LabelDigitalAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.latencyoptimizer",
    "pack": "video",
    "name": "Latencyoptimizer",
    "role": "LatencyOptimizerAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Parallelization, caching, speculative decoding, batching Host role binding: `LatencyOptimizerAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-bind…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.learnersim",
    "pack": "video",
    "name": "Learnersim",
    "role": "LearnerSimAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Simulates learner behavior, confusion points, and assessment performance Host role binding: `LearnerSimAgent (VA Domain Pack)`. Design-time VA table content below is historical an…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.legal",
    "pack": "video",
    "name": "Legal",
    "role": "LegalAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Performs final legal review for novel or high-risk publication issues Host role binding: `LegalAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-bi…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.lipsync",
    "pack": "video",
    "name": "Lipsync",
    "role": "LipSyncAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Validates and refines phoneme-viseme alignment as a dedicated gate Host role binding: `LipSyncAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-bin…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.lms",
    "pack": "video",
    "name": "Lms",
    "role": "LMSAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Packages and deploys learning content to LMS environments Host role binding: `LMSAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for acti…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.localizationqa",
    "pack": "video",
    "name": "Localizationqa",
    "role": "LocalizationQAAgent (Linguist) (VA Domain Pack)",
    "status": "registered",
    "description": "Translation + cultural fit Host role binding: `LocalizationQAAgent (Linguist) (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. #…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.marketing",
    "pack": "video",
    "name": "Marketing",
    "role": "MarketingAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Packages content for launch, promotions, and release sequencing Host role binding: `MarketingAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-bind…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.medicalillustrator",
    "pack": "video",
    "name": "Medicalillustrator",
    "role": "MedicalIllustratorAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Anatomy & procedure visuals Host role binding: `MedicalIllustratorAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Res…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.memory",
    "pack": "video",
    "name": "Memory",
    "role": "MemoryAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Episodic + long-term project memory; retrieval for any agent Host role binding: `MemoryAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding fo…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.moodboard",
    "pack": "video",
    "name": "Moodboard",
    "role": "MoodBoardAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Reference boards: visual, sonic, tonal Host role binding: `MoodBoardAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### R…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.motiongraphics",
    "pack": "video",
    "name": "Motiongraphics",
    "role": "MotionGraphicsAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Kinetic typography, lower thirds, infographics Host role binding: `MotionGraphicsAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for acti…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "network?"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.mpa",
    "pack": "video",
    "name": "Mpa",
    "role": "MPAAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Prepares rating-related packaging and release-readiness inputs for feature workflows Host role binding: `MPAAgent (VA Domain Pack)`. Design-time VA table content below is historic…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.mua_makeup",
    "pack": "video",
    "name": "Mua Makeup",
    "role": "MUAAgent (Makeup/Hair/SFX) (VA Domain Pack)",
    "status": "registered",
    "description": "Talent face/hair; prosthetics Host role binding: `MUAAgent (Makeup/Hair/SFX) (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ##…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.musicsupervisor",
    "pack": "video",
    "name": "Musicsupervisor",
    "role": "MusicSupervisorAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Manages music fit, cue usage, rights awareness, and soundtrack packaging Host role binding: `MusicSupervisorAgent (VA Domain Pack)`. Design-time VA table content below is historic…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.musicvideodirector",
    "pack": "video",
    "name": "Musicvideodirector",
    "role": "MusicVideoDirectorAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Visual concept for songs Host role binding: `MusicVideoDirectorAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Respon…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.narrativearc",
    "pack": "video",
    "name": "Narrativearc",
    "role": "NarrativeArcAgent (VA Domain Pack)",
    "status": "registered",
    "description": "3-act / Save-the-Cat / Hero's Journey structure Host role binding: `NarrativeArcAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activ…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.novelty",
    "pack": "video",
    "name": "Novelty",
    "role": "NoveltyAgent / Anti-Cliché Critic (VA Domain Pack)",
    "status": "registered",
    "description": "Flags tropes, clichés, over-fit outputs Host role binding: `NoveltyAgent / Anti-Cliché Critic (VA Domain Pack)`. Design-time VA table content below is historical and non-binding f…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.orchestrator",
    "pack": "video",
    "name": "Orchestrator",
    "role": "OrchestratorAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Runs CrewAI/AutoGen/LangGraph DAG; retries, timeouts, fan-out/fan-in Host role binding: `OrchestratorAgent (VA Domain Pack)`. Design-time VA table content below is historical and …",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "network?"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.performancemarketer",
    "pack": "video",
    "name": "Performancemarketer",
    "role": "PerformanceMarketerAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Optimize ads for ROAS Host role binding: `PerformanceMarketerAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsi…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.personalizationengineer",
    "pack": "video",
    "name": "Personalizationengineer",
    "role": "PersonalizationEngineerAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Variable templates (name/face/voice swap) Host role binding: `PersonalizationEngineerAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for …",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.planner",
    "pack": "video",
    "name": "Planner",
    "role": "PlannerAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Decomposes brief into phased DAG with assignments + critic gates Host role binding: `PlannerAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-bindi…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.producer",
    "pack": "video",
    "name": "Producer",
    "role": "ProducerAgent / EP (VA Domain Pack)",
    "status": "registered",
    "description": "Budget, schedule, hiring, delivery; greenlights phase gates Host role binding: `ProducerAgent / EP (VA Domain Pack)`. Design-time VA table content below is historical and non-bind…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.productiondesign",
    "pack": "video",
    "name": "Productiondesign",
    "role": "ProductionDesignAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Sets, locations, world look Host role binding: `ProductionDesignAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Respo…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.promptengineer",
    "pack": "video",
    "name": "Promptengineer",
    "role": "PromptEngineerAgent / GeneratorOperator (VA Domain Pack)",
    "status": "registered",
    "description": "Crafts prompts; steers Sora/Veo/Runway/Kling Host role binding: `PromptEngineerAgent / GeneratorOperator (VA Domain Pack)`. Design-time VA table content below is historical and no…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "network?"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.promptoptimizer",
    "pack": "video",
    "name": "Promptoptimizer",
    "role": "PromptOptimizerAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Auto-improves prompts via OPRO/APE/DSPy/Promptbreeder Host role binding: `PromptOptimizerAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding …",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.realestatephoto",
    "pack": "video",
    "name": "Realestatephoto",
    "role": "RealEstatePhotoAgent / 3D Scan (VA Domain Pack)",
    "status": "registered",
    "description": "Wide interiors; Matterport scans Host role binding: `RealEstatePhotoAgent / 3D Scan (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activat…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.retentionoptimizer",
    "pack": "video",
    "name": "Retentionoptimizer",
    "role": "RetentionOptimizerAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Tunes hook, pacing, structure for AVD/hold-rate Host role binding: `RetentionOptimizerAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.roasoptimizer",
    "pack": "video",
    "name": "Roasoptimizer",
    "role": "ROASOptimizerAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Optimizes ad creatives for performance Host role binding: `ROASOptimizerAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. #…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.router",
    "pack": "video",
    "name": "Router",
    "role": "RouterAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Picks right specialist agent (and model) for each subtask Host role binding: `RouterAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for a…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.safetyredteam",
    "pack": "video",
    "name": "Safetyredteam",
    "role": "SafetyRedTeamAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Adversarially attacks for deepfake, bias, jailbreak, defamation Host role binding: `SafetyRedTeamAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.sales",
    "pack": "video",
    "name": "Sales",
    "role": "SalesAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Handles buyer-facing sales packaging for distributors and outlets Host role binding: `SalesAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-bindin…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.screenwriter",
    "pack": "video",
    "name": "Screenwriter",
    "role": "ScreenwriterAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Treatment → screenplay; dialogue; structure Host role binding: `ScreenwriterAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activatio…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.seo",
    "pack": "video",
    "name": "Seo",
    "role": "SEOAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Optimizes discoverability through titles, descriptions, metadata, and search intent Host role binding: `SEOAgent (VA Domain Pack)`. Design-time VA table content below is historica…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.showrunner",
    "pack": "video",
    "name": "Showrunner",
    "role": "ShowrunnerAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Cross-episode arc, writers'-room orchestration Host role binding: `ShowrunnerAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activati…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.signlanguageinterpreter",
    "pack": "video",
    "name": "Signlanguageinterpreter",
    "role": "SignLanguageInterpreterAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Accurate ASL/BSL interpretation Host role binding: `SignLanguageInterpreterAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.sme",
    "pack": "video",
    "name": "Sme",
    "role": "SMEAgent (Subject-Matter Expert) (VA Domain Pack)",
    "status": "registered",
    "description": "Domain accuracy in target field Host role binding: `SMEAgent (Subject-Matter Expert) (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activa…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.socialmediastrategist",
    "pack": "video",
    "name": "Socialmediastrategist",
    "role": "SocialMediaStrategistAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Platform-native distribution, timing, trends Host role binding: `SocialMediaStrategistAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.sounddesign",
    "pack": "video",
    "name": "Sounddesign",
    "role": "SoundDesignAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Ambience, foley, SFX Host role binding: `SoundDesignAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (f…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "network?"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.soundmixer",
    "pack": "video",
    "name": "Soundmixer",
    "role": "SoundMixerAgent (Re-recording) (VA Domain Pack)",
    "status": "registered",
    "description": "Final mix; deliverables (5.1/Atmos) Host role binding: `SoundMixerAgent (Re-recording) (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for acti…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.sportsanalyst",
    "pack": "video",
    "name": "Sportsanalyst",
    "role": "SportsAnalystAgent / TelestratorOp (VA Domain Pack)",
    "status": "registered",
    "description": "Tactical breakdowns + diagrams Host role binding: `SportsAnalystAgent / TelestratorOp (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activ…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.standardseditor",
    "pack": "video",
    "name": "Standardseditor",
    "role": "StandardsEditorAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Enforces editorial standards, sourcing discipline, and corrections policy Host role binding: `StandardsEditorAgent (VA Domain Pack)`. Design-time VA table content below is histori…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.storyboard",
    "pack": "video",
    "name": "Storyboard",
    "role": "StoryboardAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Script → shot panels Host role binding: `StoryboardAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (fr…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.styletransfer",
    "pack": "video",
    "name": "Styletransfer",
    "role": "StyleTransferAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Applies named aesthetic consistently across shots Host role binding: `StyleTransferAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for ac…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "network?"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.talent",
    "pack": "video",
    "name": "Talent",
    "role": "TalentAgent (On-camera) (VA Domain Pack)",
    "status": "registered",
    "description": "AI-rendered performance Host role binding: `TalentAgent (On-camera) (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Respons…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.templatedesign",
    "pack": "video",
    "name": "Templatedesign",
    "role": "TemplateDesignAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Designs reusable and safe personalization templates Host role binding: `TemplateDesignAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.trailereditor",
    "pack": "video",
    "name": "Trailereditor",
    "role": "TrailerEditorAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Hook-driven trailer cuts Host role binding: `TrailerEditorAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibil…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.travelcine",
    "pack": "video",
    "name": "Travelcine",
    "role": "TravelCineAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Destination cinematography Host role binding: `TravelCineAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibili…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.trendintelligence",
    "pack": "video",
    "name": "Trendintelligence",
    "role": "TrendIntelligenceAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Detects emerging memes, sounds, formats Host role binding: `TrendIntelligenceAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activati…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.trustsafety",
    "pack": "video",
    "name": "Trustsafety",
    "role": "TrustSafetyAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Screens outputs for impersonation, abuse, or harmful misuse Host role binding: `TrustSafetyAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-bindin…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.ugccreator",
    "pack": "video",
    "name": "Ugccreator",
    "role": "UGCCreatorAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Authentic-feel ads in creator voice Host role binding: `UGCCreatorAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Res…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.ux",
    "pack": "video",
    "name": "Ux",
    "role": "UXAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Reviews clarity and usability of personalized or interactive outputs Host role binding: `UXAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-bindin…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.vfxsupervisor",
    "pack": "video",
    "name": "Vfxsupervisor",
    "role": "VFXSupervisorAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Plans + supervises VFX pipeline Host role binding: `VFXSupervisorAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Resp…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.voiceclone",
    "pack": "video",
    "name": "Voiceclone",
    "role": "VoiceCloneAgent / LipSyncSpecialist (VA Domain Pack)",
    "status": "registered",
    "description": "Voice cloning + lip-sync Host role binding: `VoiceCloneAgent / LipSyncSpecialist (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "network?"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.voiceover",
    "pack": "video",
    "name": "Voiceover",
    "role": "VoiceOverAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Narration, character VO, ad reads Host role binding: `VoiceOverAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Respon…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "network?"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.webresearch",
    "pack": "video",
    "name": "Webresearch",
    "role": "WebResearchAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Live web search, source ranking, citation extraction Host role binding: `WebResearchAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for a…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "video.worldbuilding",
    "pack": "video",
    "name": "Worldbuilding",
    "role": "WorldBuildingAgent (VA Domain Pack)",
    "status": "registered",
    "description": "Lore, rules, geography, factions, magic/tech systems Host role binding: `WorldBuildingAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for…",
    "versionLabel": "video · registered · schema 1.0",
    "success": "—",
    "avgTokens": "1024",
    "latency": "local",
    "usage": "Pack `video` · self-contained folder",
    "badges": [
      "video",
      "registered",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "video"
    ],
    "category": "video",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"video.critic\"],\"outputs\":[\"video.judge\"]}"
  },
  {
    "id": "specials.aesthetics-agent",
    "pack": "specials",
    "name": "Aesthetics Agent",
    "role": "Special_Agent data-only configuration",
    "status": "draft",
    "description": "Owns the specials-domain aesthetics agent design outcome as a **draft, data-only** agent representation. Host role string: `Special_Agent data-only configuration`. This is the **d…",
    "versionLabel": "specials · draft · schema 1.0",
    "success": "—",
    "avgTokens": "1",
    "latency": "local",
    "usage": "Pack `specials` · self-contained folder",
    "badges": [
      "specials",
      "draft",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "specials"
    ],
    "category": "specials",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"spagent.aesthetics-agent-input\"],\"outputs\":[\"spagent.aesthetics-age…"
  },
  {
    "id": "specials.agent-loop-creator",
    "pack": "specials",
    "name": "Agent Loop Creator",
    "role": "Special_Agent data-only configuration",
    "status": "draft",
    "description": "Owns the specials-domain agent loop creator design outcome as a **draft, data-only** agent representation. Host role string: `Special_Agent data-only configuration`. Actionable re…",
    "versionLabel": "specials · draft · schema 1.0",
    "success": "—",
    "avgTokens": "1",
    "latency": "local",
    "usage": "Pack `specials` · self-contained folder",
    "badges": [
      "specials",
      "draft",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "specials"
    ],
    "category": "specials",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"spagent.agent-loop-creator-input\"],\"outputs\":[\"spagent.agent-loop-c…"
  },
  {
    "id": "specials.agentic-rag-agent",
    "pack": "specials",
    "name": "Agentic Rag Agent",
    "role": "Special_Agent data-only configuration",
    "status": "draft",
    "description": "Owns the specials-domain agentic rag agent design outcome as a **draft, data-only** agent representation. Host role string: `Special_Agent data-only configuration`. ** Initial Pro…",
    "versionLabel": "specials · draft · schema 1.0",
    "success": "—",
    "avgTokens": "1",
    "latency": "local",
    "usage": "Pack `specials` · self-contained folder",
    "badges": [
      "specials",
      "draft",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "specials"
    ],
    "category": "specials",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"spagent.agentic-rag-agent-input\"],\"outputs\":[\"spagent.agentic-rag-a…"
  },
  {
    "id": "specials.autotelic-agent",
    "pack": "specials",
    "name": "Autotelic Agent",
    "role": "Special_Agent data-only configuration",
    "status": "draft",
    "description": "Owns the specials-domain autotelic agent design outcome as a **draft, data-only** agent representation. Host role string: `Special_Agent data-only configuration`. **Filename**: `a…",
    "versionLabel": "specials · draft · schema 1.0",
    "success": "—",
    "avgTokens": "1",
    "latency": "local",
    "usage": "Pack `specials` · self-contained folder",
    "badges": [
      "specials",
      "draft",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "specials"
    ],
    "category": "specials",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"spagent.autotelic-agent-input\"],\"outputs\":[\"spagent.autotelic-agent…"
  },
  {
    "id": "specials.complex-problem-solution-process-model",
    "pack": "specials",
    "name": "Complex Problem Solution Process Model",
    "role": "Special_Agent data-only configuration",
    "status": "draft",
    "description": "Owns the specials-domain complex problem solution process model design outcome as a **draft, data-only** agent representation. Host role string: `Special_Agent data-only configura…",
    "versionLabel": "specials · draft · schema 1.0",
    "success": "—",
    "avgTokens": "1",
    "latency": "local",
    "usage": "Pack `specials` · self-contained folder",
    "badges": [
      "specials",
      "draft",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "specials"
    ],
    "category": "specials",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"spagent.complex-problem-solution-process-model-input\"],\"outputs\":[\"…"
  },
  {
    "id": "specials.controller-agent",
    "pack": "specials",
    "name": "Controller Agent",
    "role": "Special_Agent data-only configuration",
    "status": "draft",
    "description": "Owns the specials-domain controller agent design outcome as a **draft, data-only** agent representation. Host role string: `Special_Agent data-only configuration`. Specialized age…",
    "versionLabel": "specials · draft · schema 1.0",
    "success": "—",
    "avgTokens": "1",
    "latency": "local",
    "usage": "Pack `specials` · self-contained folder",
    "badges": [
      "specials",
      "draft",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "specials"
    ],
    "category": "specials",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"spagent.controller-agent-input\"],\"outputs\":[\"spagent.controller-age…"
  },
  {
    "id": "specials.general-creative-agent",
    "pack": "specials",
    "name": "General Creative Agent",
    "role": "Special_Agent data-only configuration",
    "status": "draft",
    "description": "Owns the specials-domain general creative agent design outcome as a **draft, data-only** agent representation. Host role string: `Special_Agent data-only configuration`. This is t…",
    "versionLabel": "specials · draft · schema 1.0",
    "success": "—",
    "avgTokens": "1",
    "latency": "local",
    "usage": "Pack `specials` · self-contained folder",
    "badges": [
      "specials",
      "draft",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "specials"
    ],
    "category": "specials",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"spagent.general-creative-agent-input\"],\"outputs\":[\"spagent.general-…"
  },
  {
    "id": "specials.intent-analysis-agent",
    "pack": "specials",
    "name": "Intent Analysis Agent",
    "role": "Special_Agent data-only configuration",
    "status": "draft",
    "description": "Owns the specials-domain intent analysis agent design outcome as a **draft, data-only** agent representation. Host role string: `Special_Agent data-only configuration`. The **Deep…",
    "versionLabel": "specials · draft · schema 1.0",
    "success": "—",
    "avgTokens": "1",
    "latency": "local",
    "usage": "Pack `specials` · self-contained folder",
    "badges": [
      "specials",
      "draft",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "specials"
    ],
    "category": "specials",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"spagent.intent-analysis-agent-input\"],\"outputs\":[\"spagent.intent-an…"
  },
  {
    "id": "specials.knowledge-router-agent",
    "pack": "specials",
    "name": "Knowledge Router Agent",
    "role": "Special_Agent data-only configuration",
    "status": "draft",
    "description": "Owns the specials-domain knowledge router agent design outcome as a **draft, data-only** agent representation. Host role string: `Special_Agent data-only configuration`. The **Kno…",
    "versionLabel": "specials · draft · schema 1.0",
    "success": "—",
    "avgTokens": "1",
    "latency": "local",
    "usage": "Pack `specials` · self-contained folder",
    "badges": [
      "specials",
      "draft",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "specials"
    ],
    "category": "specials",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"spagent.knowledge-router-agent-input\"],\"outputs\":[\"spagent.knowledg…"
  },
  {
    "id": "specials.llm-usage",
    "pack": "specials",
    "name": "Llm Usage",
    "role": "Special_Agent data-only configuration",
    "status": "draft",
    "description": "Owns the specials-domain llm usage design outcome as a **draft, data-only** agent representation. Host role string: `Special_Agent data-only configuration`. The user currently has…",
    "versionLabel": "specials · draft · schema 1.0",
    "success": "—",
    "avgTokens": "1",
    "latency": "local",
    "usage": "Pack `specials` · self-contained folder",
    "badges": [
      "specials",
      "draft",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "specials"
    ],
    "category": "specials",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"spagent.llm-usage-input\"],\"outputs\":[\"spagent.llm-usage-output\"]}"
  },
  {
    "id": "specials.optimization-agent",
    "pack": "specials",
    "name": "Optimization Agent",
    "role": "Special_Agent data-only configuration",
    "status": "draft",
    "description": "Owns the specials-domain optimization agent design outcome as a **draft, data-only** agent representation. Host role string: `Special_Agent data-only configuration`. Deliver a des…",
    "versionLabel": "specials · draft · schema 1.0",
    "success": "—",
    "avgTokens": "1",
    "latency": "local",
    "usage": "Pack `specials` · self-contained folder",
    "badges": [
      "specials",
      "draft",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "specials"
    ],
    "category": "specials",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"spagent.optimization-agent-input\"],\"outputs\":[\"spagent.optimization…"
  },
  {
    "id": "specials.planner-agent",
    "pack": "specials",
    "name": "Planner Agent",
    "role": "Special_Agent data-only configuration",
    "status": "draft",
    "description": "Owns the specials-domain planner agent design outcome as a **draft, data-only** agent representation. Host role string: `Special_Agent data-only configuration`. SIPA is a hierarch…",
    "versionLabel": "specials · draft · schema 1.0",
    "success": "—",
    "avgTokens": "1",
    "latency": "local",
    "usage": "Pack `specials` · self-contained folder",
    "badges": [
      "specials",
      "draft",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "specials"
    ],
    "category": "specials",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"spagent.planner-agent-input\"],\"outputs\":[\"spagent.planner-agent-out…"
  },
  {
    "id": "specials.podcast-agent",
    "pack": "specials",
    "name": "Podcast Agent",
    "role": "Special_Agent data-only configuration",
    "status": "draft",
    "description": "Owns the specials-domain podcast agent design outcome as a **draft, data-only** agent representation. Host role string: `Special_Agent data-only configuration`. The workflow of a …",
    "versionLabel": "specials · draft · schema 1.0",
    "success": "—",
    "avgTokens": "1",
    "latency": "local",
    "usage": "Pack `specials` · self-contained folder",
    "badges": [
      "specials",
      "draft",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "specials"
    ],
    "category": "specials",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"spagent.podcast-agent-input\"],\"outputs\":[\"spagent.podcast-agent-out…"
  },
  {
    "id": "specials.psychological-profile-agent",
    "pack": "specials",
    "name": "Psychological Profile Agent",
    "role": "Special_Agent data-only configuration",
    "status": "draft",
    "description": "Owns the specials-domain psychological profile agent design outcome as a **draft, data-only** agent representation. Host role string: `Special_Agent data-only configuration`. Prov…",
    "versionLabel": "specials · draft · schema 1.0",
    "success": "—",
    "avgTokens": "1",
    "latency": "local",
    "usage": "Pack `specials` · self-contained folder",
    "badges": [
      "specials",
      "draft",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "specials"
    ],
    "category": "specials",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"spagent.psychological-profile-agent-input\"],\"outputs\":[\"spagent.psy…"
  },
  {
    "id": "specials.psychological-recommendation-agent",
    "pack": "specials",
    "name": "Psychological Recommendation Agent",
    "role": "Special_Agent data-only configuration",
    "status": "draft",
    "description": "Owns the specials-domain psychological recommendation agent design outcome as a **draft, data-only** agent representation. Host role string: `Special_Agent data-only configuration…",
    "versionLabel": "specials · draft · schema 1.0",
    "success": "—",
    "avgTokens": "1",
    "latency": "local",
    "usage": "Pack `specials` · self-contained folder",
    "badges": [
      "specials",
      "draft",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "specials"
    ],
    "category": "specials",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"spagent.psychological-recommendation-agent-input\"],\"outputs\":[\"spag…"
  },
  {
    "id": "specials.research-agent",
    "pack": "specials",
    "name": "Research Agent",
    "role": "Special_Agent data-only configuration",
    "status": "draft",
    "description": "Owns the specials-domain research agent design outcome as a **draft, data-only** agent representation. Host role string: `Special_Agent data-only configuration`. ` and `## Source …",
    "versionLabel": "specials · draft · schema 1.0",
    "success": "—",
    "avgTokens": "1",
    "latency": "local",
    "usage": "Pack `specials` · self-contained folder",
    "badges": [
      "specials",
      "draft",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "specials"
    ],
    "category": "specials",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"spagent.research-agent-input\"],\"outputs\":[\"spagent.research-agent-o…"
  },
  {
    "id": "specials.screenwriter-strategic-goal-achievement-agent",
    "pack": "specials",
    "name": "Screenwriter Strategic Goal Achievement Agent",
    "role": "Special_Agent data-only configuration",
    "status": "draft",
    "description": "Owns the specials-domain screenwriter strategic goal achievement agent design outcome as a **draft, data-only** agent representation. Host role string: `Special_Agent data-only co…",
    "versionLabel": "specials · draft · schema 1.0",
    "success": "—",
    "avgTokens": "1",
    "latency": "local",
    "usage": "Pack `specials` · self-contained folder",
    "badges": [
      "specials",
      "draft",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "specials"
    ],
    "category": "specials",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"spagent.screenwriter-strategic-goal-achievement-agent-input\"],\"outp…"
  },
  {
    "id": "specials.strategic-goal-achievement-agent",
    "pack": "specials",
    "name": "Strategic Goal Achievement Agent",
    "role": "Special_Agent data-only configuration",
    "status": "draft",
    "description": "Owns the specials-domain strategic goal achievement agent design outcome as a **draft, data-only** agent representation. Host role string: `Special_Agent data-only configuration`.…",
    "versionLabel": "specials · draft · schema 1.0",
    "success": "—",
    "avgTokens": "1",
    "latency": "local",
    "usage": "Pack `specials` · self-contained folder",
    "badges": [
      "specials",
      "draft",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "specials"
    ],
    "category": "specials",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"spagent.strategic-goal-achievement-agent-input\"],\"outputs\":[\"spagen…"
  },
  {
    "id": "specials.techology-advisor-agent",
    "pack": "specials",
    "name": "Techology Advisor Agent",
    "role": "Special_Agent data-only configuration",
    "status": "draft",
    "description": "Owns the specials-domain techology advisor agent design outcome as a **draft, data-only** agent representation. Host role string: `Special_Agent data-only configuration`. --- At r…",
    "versionLabel": "specials · draft · schema 1.0",
    "success": "—",
    "avgTokens": "1",
    "latency": "local",
    "usage": "Pack `specials` · self-contained folder",
    "badges": [
      "specials",
      "draft",
      "self-contained",
      "no-network"
    ],
    "domains": [
      "specials"
    ],
    "category": "specials",
    "architecture": "pack agent folder",
    "critiqueCompat": "{\"inputs\":[\"spagent.techology-advisor-agent-input\"],\"outputs\":[\"spagent.techolo…"
  }
];
