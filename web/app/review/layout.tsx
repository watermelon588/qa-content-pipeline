import type { Metadata } from "next";
import { Toaster } from "sonner";
import Footer from "@/components/Footer";
import Header from "@/components/Header";
import "../admin/admin.css"; // same fact list, buttons and toasts as the admin desk

// The expert's page. Public (no admin password: the one-time code in the address is the permission), so:
// - never indexed by search engines;
// - no Google Analytics here, unlike app/(site)/layout.tsx, so the secret address is never sent to Google;
// - "no-referrer", so opening a source link doesn't tell that site the secret address either.
export const metadata: Metadata = {
  title: "Expert review",
  robots: { index: false, follow: false },
  referrer: "no-referrer",
};

export default function ReviewLayout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <Header />
      <main id="main" className="adm">{children}</main>
      <Footer />
      <Toaster position="bottom-right" closeButton toastOptions={{ className: "adm-toast" }} />
    </>
  );
}
