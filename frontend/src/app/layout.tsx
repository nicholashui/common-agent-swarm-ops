import type { Metadata } from "next";
import type { ReactNode } from "react";

import "./globals.css";

export const metadata: Metadata = {
  title: "common/swarm · Registry and operations",
  description: "Reusable agent swarms, collective improvement, and production operations.",
};

function RootLayout({ children }: Readonly<{ children: ReactNode }>): ReactNode {
  return <html lang="en"><body>{children}</body></html>;
}

export default RootLayout;
