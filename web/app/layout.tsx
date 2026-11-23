import type { Metadata } from "next";
import { Bricolage_Grotesque, IBM_Plex_Mono, IBM_Plex_Sans } from "next/font/google";
import { SECTION_LEDE, SECTION_NAME, SITE_NAME, SITE_URL } from "@/lib/site";
import "./globals.css";

// The three typefaces of the AI Atlas India kit. next/font downloads them at build time and serves
// them from our own domain, so the page makes no request to Google when someone visits.
const display = Bricolage_Grotesque({ variable: "--font-display", subsets: ["latin"] });
const body = IBM_Plex_Sans({ variable: "--font-body", subsets: ["latin"], weight: ["400", "500", "600"] });
const mono = IBM_Plex_Mono({ variable: "--font-mono", subsets: ["latin"], weight: ["400", "500"] });

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: { default: `${SECTION_NAME} | ${SITE_NAME}`, template: `%s | ${SITE_NAME}` },
  description: SECTION_LEDE,
  icons: { icon: "/favicon.svg" },
  openGraph: { siteName: SITE_NAME, type: "website", locale: "en_IN" },
  twitter: { card: "summary" },
};

// The shell every page shares. The public header and footer live in app/(site)/layout.tsx,
// so the admin screens (app/admin) don't carry them.
export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className={`${display.variable} ${body.variable} ${mono.variable}`}>
      <body data-section="gpu">{children}</body>
    </html>
  );
}
