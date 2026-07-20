export type RunStatus = "running" | "success" | "paused" | "error";

export interface CommonAgent {
  readonly id: string;
  readonly name: string;
  readonly version: string;
  readonly description: string;
  readonly successRate: string;
  readonly usage: string;
  readonly tags: readonly string[];
}

export const COMMON_AGENTS: readonly CommonAgent[] = [
  { id: "market-sentinel", name: "Market Sentinel", version: "2.4", description: "Triages market signals with source-backed confidence.", successRate: "94.8%", usage: "1.2k swarms", tags: ["Trading", "Verified"] },
  { id: "research-verifier", name: "Research Verifier", version: "1.8", description: "Scores claims, requests evidence, and closes quality loops.", successRate: "97.1%", usage: "842 swarms", tags: ["Verification", "Core"] },
  { id: "content-director", name: "Content Director", version: "3.1", description: "Coordinates editorial plans and creative production handoffs.", successRate: "92.4%", usage: "536 swarms", tags: ["Content", "Parallel"] },
  { id: "adaptive-tutor", name: "Adaptive Tutor", version: "1.6", description: "Builds formative lessons and individualized assessment paths.", successRate: "95.2%", usage: "419 swarms", tags: ["Education", "RAG"] },
];

export const PATTERNS = [
  { id: "parallel-verify", name: "Parallel research + verification", version: "1.4", description: "Run independent evidence branches, then synthesize through a verifier.", metrics: "94% success · 23% faster" },
  { id: "supervisor-workers", name: "Supervisor + specialists", version: "2.0", description: "Delegate work to focused agents with a centralized quality handoff.", metrics: "91% success · 8 agents" },
  { id: "map-reduce", name: "Map-reduce with consensus", version: "1.2", description: "Shard large inputs, combine candidate outputs, and vote on a result.", metrics: "89% success · scalable" },
] as const;

export const RECENT_RUNS = [
  { name: "Daily market brief", pattern: "Parallel + verification", status: "success" as const, duration: "4m 12s", cost: "$0.38", commons: "6 linked" },
  { name: "Research digest", pattern: "Supervisor + specialists", status: "running" as const, duration: "12m 08s", cost: "$0.71", commons: "8 linked" },
  { name: "DSE lesson planner", pattern: "Adaptive tutor", status: "paused" as const, duration: "2m 47s", cost: "$0.19", commons: "4 linked" },
];
