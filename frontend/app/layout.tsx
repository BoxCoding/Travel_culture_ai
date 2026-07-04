import type { Metadata } from "next";
import "./globals.css";
import Navbar from "@/components/Navbar";

export const metadata: Metadata = {
  title: "Wayfare — Travel & Culture Discovery",
  description:
    "Discover destinations, hidden gems, heritage stories, and authentic cultural experiences — guided by AI.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen font-sans antialiased">
        <Navbar />
        <main className="min-h-[calc(100vh-4rem)]">{children}</main>
        <footer className="border-t border-sand-200 bg-white py-8 text-center text-sm text-ink-700/60">
          Wayfare — travel and culture discovery, guided by AI. Verify
          AI-generated details before you travel.
        </footer>
      </body>
    </html>
  );
}
