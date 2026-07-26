/**
 * Local Knowledge Management Hub fixture for ui_10_knowledge.md / .svg.
 * Presentation-only until knowledge projections and contribution workflows connect.
 * External URLs are untrusted refs; promotion requires explicit verification.
 */

export type KnowledgeDetailTab = "sources" | "search" | "config" | "contributions" | "analytics";

export type KnowledgeBindingKind =
  | "rag"
  | "few-shot"
  | "correction"
  | "constitutional"
  | "benchmark"
  | "continuity";

export interface KnowledgeCollectionCard {
  readonly id: string;
  readonly name: string;
  readonly scope: "common" | "business";
  readonly health: "healthy" | "reindexing" | "degraded";
  readonly healthLabel: string;
  readonly chunks: string;
  readonly syncDetail: string;
  readonly bindingKinds: readonly KnowledgeBindingKind[];
}

export interface KnowledgeSourceRow {
  readonly id: string;
  readonly name: string;
  readonly type: string;
  readonly status: string;
  readonly chunks: string;
  readonly license: string;
  readonly bindingKind: KnowledgeBindingKind;
}

export interface KnowledgeSearchHit {
  readonly id: string;
  readonly score: string;
  readonly snippet: string;
  readonly metadata: string;
}

export interface KnowledgeContribution {
  readonly id: string;
  readonly title: string;
  readonly detail: string;
  readonly verification: string;
}

export interface KnowledgeSyncJob {
  readonly id: string;
  readonly label: string;
  readonly status: string;
  readonly note: string;
}

export interface KnowledgeLandingView {
  readonly title: string;
  readonly description: string;
  readonly searchPlaceholder: string;
  readonly facets: readonly string[];
  readonly collections: readonly KnowledgeCollectionCard[];
  readonly selectedCollectionId: string;
  readonly sources: readonly KnowledgeSourceRow[];
  readonly searchQuery: string;
  readonly searchHits: readonly KnowledgeSearchHit[];
  readonly contributions: readonly KnowledgeContribution[];
  readonly syncJobs: readonly KnowledgeSyncJob[];
  readonly chunkingConfig: readonly { readonly label: string; readonly value: string }[];
  readonly retrievalTrace: readonly string[];
  readonly governanceNote: string;
  readonly footerNote: string;
}

export const LOCAL_KNOWLEDGE_LANDING: KnowledgeLandingView = {
  title: "Knowledge Management Hub",
  description:
    "Common + business-scoped RAG sources · seamless contribution from verified runs.",
  searchPlaceholder: "Search collections, chunks…",
  facets: ["All types", "Common", "Business-scoped", "Health"],
  collections: [
    {
      id: "trading-corpus",
      name: "Trading Corpus (Common)",
      scope: "common",
      health: "healthy",
      healthLabel: "Healthy",
      chunks: "12.4k",
      syncDetail: "Last sync 14m ago · embed: text-3-large",
      bindingKinds: ["rag", "few-shot", "benchmark"],
    },
    {
      id: "wuxia-lore",
      name: "Wuxia Lore",
      scope: "business",
      health: "healthy",
      healthLabel: "Healthy",
      chunks: "3.1k",
      syncDetail: "Git sync · bilingual EN/繁",
      bindingKinds: ["rag", "continuity"],
    },
    {
      id: "dse-notes",
      name: "DSE ICT Notes",
      scope: "business",
      health: "reindexing",
      healthLabel: "Reindexing",
      chunks: "8.7k",
      syncDetail: "Strapi sync · reindex 62%…",
      bindingKinds: ["rag", "correction", "constitutional"],
    },
  ],
  selectedCollectionId: "trading-corpus",
  sources: [
    {
      id: "s1",
      name: "market_reports_2026.md",
      type: "markdown",
      status: "indexed",
      chunks: "420",
      license: "licensed reference",
      bindingKind: "rag",
    },
    {
      id: "s2",
      name: "sentiment_dataset.csv",
      type: "dataset",
      status: "indexed",
      chunks: "1.2k",
      license: "validated",
      bindingKind: "benchmark",
    },
    {
      id: "s3",
      name: "strategy_wiki (Git)",
      type: "git",
      status: "synced",
      chunks: "890",
      license: "workspace",
      bindingKind: "rag",
    },
    {
      id: "s4",
      name: "pasted_notes.txt",
      type: "paste",
      status: "pending review",
      chunks: "36",
      license: "untrusted until audited",
      bindingKind: "correction",
    },
  ],
  searchQuery: "bullish divergence patterns",
  searchHits: [
    {
      id: "h1",
      score: "0.94",
      snippet: "Bullish divergence confirmed when price lows lower while RSI higher…",
      metadata: "market_reports_2026.md · chunk 88 · freshness 14m",
    },
    {
      id: "h2",
      score: "0.88",
      snippet: "Divergence filters reduced false positives 12% in verified eval pack…",
      metadata: "sentiment_dataset.csv · few-shot · retention 30d",
    },
  ],
  contributions: [
    {
      id: "c1",
      title: "Distilled insight from run-4421 (verified)",
      detail: "provenance retained · awaiting review · opt-in contribution",
      verification: "verified run · not auto-promoted",
    },
    {
      id: "c2",
      title: "Correction memory from verifier failure cluster",
      detail: "severity major · evidence refs only · approval pending",
      verification: "awaiting human approval",
    },
  ],
  syncJobs: [
    {
      id: "j1",
      label: "Git · Trading Corpus",
      status: "ok",
      note: "Last 14m · schedule hourly",
    },
    {
      id: "j2",
      label: "Strapi · DSE ICT Notes",
      status: "running",
      note: "Reindex 62%",
    },
    {
      id: "j3",
      label: "URL import queue",
      status: "gated",
      note: "URLs submitted as untrusted refs · server-side ingestion only",
    },
  ],
  chunkingConfig: [
    { label: "Size", value: "512 tokens" },
    { label: "Overlap", value: "64 tokens" },
    { label: "Embedding", value: "policy-bound model" },
    { label: "Retention", value: "30d · access policy enforced" },
  ],
  retrievalTrace: [
    "Task/agent version: VerifierNode Common v3.0",
    "Query purpose: groundedness evidence",
    "Selected references: 2 chunks (redacted)",
    "Freshness: 14m · correction-memory: not used",
    "Resulting artifact/run ref: run-4421 · local-preview",
  ],
  governanceNote:
    "Item can't be promoted to Common solely because retrieved/generated — verification state explicit. Contributions retain opt-in, artifact provenance, verification state, and approval outcome.",
  footerNote:
    "Local preview knowledge hub · server-defined type/size/ownership/retention shown before submit · client checks aren't authorization. Distinguishes RAG, few-shot, correction memory, constitutional rules, continuity, and benchmarks.",
};
