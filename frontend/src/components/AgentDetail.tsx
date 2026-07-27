/**
 * @duty AgentDetail — legacy export alias for agent detail screen
 * @role Re-export AgentDetailHome for compatibility imports.
 * @controls None inherent; prefer AgentDetailHome + BoundScreenHome for routes.
 * @mustnot Add alternate authority paths outside Homes.
 * @redesign docs/frontend_redesign/ui_05_agent_detail.md
 */
export { AgentDetailHome as AgentDetail } from "./AgentDetailHome";
