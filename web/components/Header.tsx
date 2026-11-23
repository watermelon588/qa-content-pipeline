import Image from "next/image";
import { CONTACT, HUB_URL, NAV, SECTION_TITLE, SITE_URL, THIS_SECTION } from "@/lib/site";

// Copied from the kit's header.html (aiatlasindia.com/kit/), which says to use it unchanged.

export default function Header() {
  const links = [...NAV, CONTACT];
  return (
    <header className="atlas-header">
      <div className="atlas-header__strip">
        <svg aria-hidden="true" width="10" height="10" viewBox="0 0 10 10"><path d="M5 0 L10 5 L5 10 L0 5 Z" fill="#F4C430" /></svg>
        <span>Owned and run by Vyohm AI Private Limited.</span>
        <a href={`${HUB_URL}/disclosures/`}>Ownership and disclosures</a>
      </div>
      <div className="atlas-header__bar">
        <div className="atlas-header__lockup">
          {/* Required by the guide: "AI Atlas India" linking to aiatlasindia.com, then the section name. */}
          <a className="atlas-header__brand" href={HUB_URL}>
            <Image src="/favicon.svg" alt="" width={34} height={34} />
            <span className="atlas-header__name">AI Atlas India</span>
          </a>
          <a className="atlas-header__section" href={SITE_URL} aria-label={`${SECTION_TITLE} section home`}>
            <span>{THIS_SECTION}</span>{/* the kit's lockup: "AI Atlas India GPU" */}
          </a>
        </div>
        <nav className="atlas-header__nav" aria-label="Main">
          {NAV.map((l) => (
            <a key={l.href} href={l.href}>{l.label}</a>
          ))}
          <a className="atlas-header__contact" href={CONTACT.href}>{CONTACT.label}</a>
        </nav>
        <details className="atlas-header__menu">
          <summary aria-label="Menu">
            <svg width="20" height="14" viewBox="0 0 20 14" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M0 1h20M0 7h20M0 13h20" />
            </svg>
          </summary>
          <nav aria-label="Main menu">
            {links.map((l) => (
              <a key={l.href} href={l.href}>{l.label}</a>
            ))}
          </nav>
        </details>
      </div>
    </header>
  );
}
