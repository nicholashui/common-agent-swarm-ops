import type { Metadata } from "next";
import type { ReactNode } from "react";

import "./globals.css";

export const metadata: Metadata = {
  title: "Generic Swarm Ops",
  description: "Redacted workflow operations console",
};

export function RootLayout({ children }: Readonly<{ children: ReactNode }>): ReactNode {
  return <html lang="en"><body>{children}</body></html>;
}

export default RootLayout;
