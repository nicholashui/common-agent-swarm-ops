"use client";

import { LoginScreen } from "../../components/LoginScreen";
import { useScreenParameters } from "../../lib/projections/use-screen-parameters";

/**
 * Login copy is loaded from stored screen parameters (not hardcoded in the page).
 */
export default function LoginPage(): JSX.Element {
  const view = useScreenParameters("login");
  return <LoginScreen view={view} />;
}
