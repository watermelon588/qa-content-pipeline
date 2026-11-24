import type { Metadata } from "next";
import { Toaster } from "sonner";
import "../admin/admin.css"; // same buttons, inputs and toasts as the desk

// The admin sign-in page: never indexed, no public header or footer.
export const metadata: Metadata = { title: "Admin sign in", robots: { index: false, follow: false } };

export default function LoginLayout({ children }: { children: React.ReactNode }) {
  return (
    <main className="adm">
      {children}
      <Toaster position="bottom-right" closeButton toastOptions={{ className: "adm-toast" }} />
    </main>
  );
}
