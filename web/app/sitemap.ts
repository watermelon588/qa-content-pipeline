import type { MetadataRoute } from "next";
import { api } from "@/lib/api";
import { SITE_URL } from "@/lib/site";

// The list of pages we hand to Google: the two fixed pages plus every published answer.
export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const pages = await api<{ slug: string; published_at: string }[]>("/pages").catch(() => []); // API down: fixed pages only
  return [
    ...["", "/about"].map((path) => ({ url: `${SITE_URL}${path}` })),
    ...pages.map((p) => ({ url: `${SITE_URL}/q/${p.slug}`, lastModified: p.published_at })),
  ];
}
