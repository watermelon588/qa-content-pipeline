import Link from "next/link";
import Footer from "@/components/Footer";
import Header from "@/components/Header";

// Lives outside app/(site), so it brings the public header and footer itself.
export default function NotFound() {
  return (
    <>
      <Header />
      <main id="main" tabIndex={-1}>
        <div className="wrap wrap--narrow section-pad">
          <p className="label label--route">Error 404</p>
          <h1 className="display" style={{ marginTop: "var(--atlas-space-3)" }}>Page not found</h1>
          <p className="lede" style={{ marginTop: "var(--atlas-space-4)" }}>
            This page is not on the map. It may have moved, or it was never published.
          </p>
          <p style={{ marginTop: "var(--atlas-space-5)" }}>
            <Link className="btn btn--primary" href="/">Back to the section home</Link>
          </p>
        </div>
      </main>
      <Footer />
    </>
  );
}
