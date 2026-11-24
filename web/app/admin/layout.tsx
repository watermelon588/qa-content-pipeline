import type { Metadata } from "next";
import Link from "next/link";
import { Toaster } from "sonner";
import { logout } from "../login/actions";
import "./admin.css";

// Admin screens: password-protected by proxy.ts, never indexed, no public header or footer.
export const metadata: Metadata = { title: "Answer desk", robots: { index: false, follow: false } };

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="adm">
      <header className="band--ink adm-top">
        <div className="wrap adm-top__bar">
          <Link href="/admin" className="adm-top__name">AI Atlas India</Link>
          <span className="adm-top__chip">GPU and cloud</span>
          <nav className="adm-top__nav" aria-label="Desk">
            <Link href="/admin" className="adm-top__desk">Answers</Link>
            <Link href="/admin?view=social" className="adm-top__desk">Bluesky</Link>
            <Link href="/admin?view=results" className="adm-top__desk">Results</Link>
            <form action={logout}>
              <button type="submit" className="adm-top__desk adm-top__out">Sign out</button>
            </form>
          </nav>
        </div>
      </header>
      {children}
      {/* Every button's result pops up here (see ActionForm). Errors stay until you close them. */}
      <Toaster position="bottom-right" closeButton toastOptions={{ className: "adm-toast" }} />
    </div>
  );
}
