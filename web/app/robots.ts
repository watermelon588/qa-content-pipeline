import type { MetadataRoute } from "next";
import { SITE_URL } from "@/lib/site";

// Everyone may read the public pages, AI crawlers included (we want AI referrals).
// /admin is the login-protected desk (/login is its sign-in page); /review is the expert's one-time pages (also marked noindex).
export default function robots(): MetadataRoute.Robots {
  return {
    rules: { userAgent: "*", allow: "/", disallow: ["/admin", "/login", "/review"] },
    sitemap: `${SITE_URL}/sitemap.xml`,
  };
}
