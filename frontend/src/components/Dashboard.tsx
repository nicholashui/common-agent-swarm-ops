/**
 * @duty Dashboard — legacy export alias for dashboard screen
 * @role Re-export OperationalScreens/DashboardHome for compatibility imports.
 * @controls None inherent; prefer DashboardHome + BoundScreenHome for routes.
 * @mustnot Add alternate authority paths outside Homes.
 * @redesign docs/frontend_redesign/ui_02_dashboard.md; component_duty_catalog.md §3.4
 */
export { Dashboard } from "./OperationalScreens";
export { DashboardHome } from "./DashboardHome";
