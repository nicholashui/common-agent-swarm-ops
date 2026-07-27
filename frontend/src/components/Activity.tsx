/**
 * @duty Activity — legacy export alias for activity screen
 * @role Re-export ActivityHome for compatibility imports.
 * @controls None inherent; prefer ActivityHome + BoundScreenHome for routes.
 * @mustnot Add alternate authority paths outside Homes.
 * @redesign docs/frontend_redesign/ui_06_activity.md
 */
export { ActivityHome as Activity } from "./ActivityHome";
