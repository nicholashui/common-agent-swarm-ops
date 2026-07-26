import type { Metadata } from "next";
import type { ReactNode } from "react";
import { Inter } from "next/font/google";

import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "common-agent-swarm-ops",
  description:
    "Common-first control plane for reusable agent swarms and production operations.",
};

function RootLayout({ children }: Readonly<{ children: ReactNode }>): ReactNode {
  return (
    <html lang="en" className={inter.variable}>
      <body className={inter.className}>{children}</body>
    </html>
  );
}

export default RootLayout;
