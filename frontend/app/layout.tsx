import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "LearnGraph AI — Find the concept behind the mistake",
  description:
    "An explainable learning-diagnostics prototype with prerequisite graphs and targeted practice. Explore the first infrastructure preview.",
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
