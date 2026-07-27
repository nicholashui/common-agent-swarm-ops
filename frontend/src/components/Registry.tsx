/**
 * @duty Registry — legacy export alias for registry hub screen
 * @role Re-export RegistryHome for compatibility imports.
 * @controls None inherent; prefer RegistryHome + BoundScreenHome for routes.
 * @mustnot Add alternate authority paths outside Homes.
 * @redesign docs/frontend_redesign/ui_07_registry_hub.md
 */
export { RegistryHome as Registry } from "./RegistryHome";
