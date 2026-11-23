import Script from "next/script";
import Footer from "@/components/Footer";
import Header from "@/components/Header";
import { GA_ID } from "@/lib/site";

// Public pages only. "(site)" is a route group: the brackets keep it out of the URL,
// so app/(site)/about/page.tsx is still served at /about.
export default function SiteLayout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <a className="skip-link" href="#main">Skip to content</a>
      <Header />
      <main id="main" tabIndex={-1}>{children}</main>
      <Footer />
      {/* Google Analytics 4. Renders only when NEXT_PUBLIC_GA_ID is set, so local dev sends no data. */}
      {GA_ID && (
        <>
          <Script src={`https://www.googletagmanager.com/gtag/js?id=${GA_ID}`} strategy="afterInteractive" />
          <Script id="ga4" strategy="afterInteractive">
            {`window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments)}gtag('js',new Date());gtag('config','${GA_ID}');`}
          </Script>
        </>
      )}
    </>
  );
}
