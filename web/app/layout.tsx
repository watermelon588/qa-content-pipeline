import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { OWNERSHIP_LINE, SECTION_NAME } from "@/lib/site";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: `${SECTION_NAME} | AI Atlas India`,
  description: "Answers to the questions Indian business owners ask before buying AI, reviewed by a named expert.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">
        <header className="border-b px-4 py-3 flex gap-3 items-baseline">
          <a href="https://aiatlasindia.com" className="font-semibold">AI Atlas India</a>
          <span className="text-sm opacity-70">{SECTION_NAME}</span>
        </header>
        <main className="flex-1 px-4 py-8">{children}</main>
        <footer className="border-t px-4 py-4 text-sm opacity-70">{OWNERSHIP_LINE}</footer>
      </body>
    </html>
  );
}
