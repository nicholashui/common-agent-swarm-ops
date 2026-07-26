import type { Metadata } from "next";
import type { ReactNode } from "react";

import "./globals.css";

export const metadata: Metadata = {
  title: "common-agent-swarm-ops",
  description: "Common-first control plane for reusable agent swarms and production operations.",
};

function RootLayout({ children }: Readonly<{ children: ReactNode }>): ReactNode {
  return <html lang="en"><body>{children}</body></html>;
}

export default RootLayout;
