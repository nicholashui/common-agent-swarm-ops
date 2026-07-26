/**
 * Specials pack presentation for Registry Hub.
 * Aligns to docs/special_agents_redesign/agents/*.md as draft catalog only.
 */

import type { ScreenLabels } from "./screen-labels";

import {
  SPECIALS_PACK_DISCLAIMER,
  SPECIAL_AGENT_CATALOG,
  type SpecialAgentCatalogEntry,
} from "../specials/specials-catalog";

export interface SpecialsLandingView {
  readonly labels: ScreenLabels;
  readonly title: string;
  readonly subtitle: string;
  readonly disclaimer: string;
  readonly agents: readonly SpecialAgentCatalogEntry[];
  readonly emptyLabel: string;
}

export const LOCAL_SPECIALS_LANDING: SpecialsLandingView = {
  labels: {
    "specials_pack_draft": "SPECIALS PACK · DRAFT",
    "search_special_agents": "Search special agents",
    "draft_non_active": "draft · non-active",
    "search_specials_by_id_or_title": "Search specials by id or title…",
    "special_agents_pack_catalog": "Special agents pack catalog",
  },
  title: "Special Agents Pack",
  subtitle:
    "Checked-in specials.* draft catalog (19). Inspect provenance only — not runtime-active commons.",
  disclaimer: SPECIALS_PACK_DISCLAIMER,
  agents: SPECIAL_AGENT_CATALOG,
  emptyLabel: "No special agent drafts are available in this presentation.",
};
