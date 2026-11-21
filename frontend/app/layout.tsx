import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "LearnGraph AI — Find the concept behind the mistake",
  description:
    "Explore twelve connected concepts, evidence-based diagnostics and fresh practice with synthetic learners. Free, anonymous, and browser-local.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
