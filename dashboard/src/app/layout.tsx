import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = { title: "AXION SkillTree", description: "AXION AI operating intelligence map" };

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
