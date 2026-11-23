import Link from "next/link";
import { BUILDER_NAME, FOOTER_GUIDE, FOOTER_SITE, OWNERSHIP_LINE, SECTIONS, THIS_SECTION } from "@/lib/site";

// Copied from the kit's footer.html (aiatlasindia.com/kit/), plus "Built by" and an About link as the kit shows.

export default function Footer() {
  return (
    <footer className="atlas-footer">
      <div className="atlas-footer__inner">
        <div className="atlas-footer__cols">
          <div className="atlas-footer__about">
            <div className="atlas-footer__brand">
              {/* The logo "on ink", from the kit: white lines, yellow marker. Never recolour it. */}
              <svg aria-hidden="true" width="30" height="30" viewBox="0 0 32 32">
                <g fill="none" stroke="#FFFFFF" strokeWidth="2">
                  <rect x="1.5" y="1.5" width="29" height="29" />
                  <path d="M11 2C7 10 7 22 11 30" />
                  <path d="M21 2c4 8 4 20 0 28" />
                  <path d="M2 16h28" />
                  <circle cx="19.5" cy="10.5" r="3.2" fill="#F4C430" stroke="none" />
                </g>
              </svg>
              <span className="atlas-footer__name">AI Atlas India</span>
            </div>
            {/* The kit's ownership sentence word for word, then the guide's exact line (D16). Never reword either. */}
            <div className="atlas-footer__ownership">
              <p className="atlas-footer__label atlas-footer__label--signal">Ownership</p>
              <p>
                <strong>AI Atlas India is owned and run by Vyohm AI Private Limited.</strong> Vyohm&#39;s own products
                (wotbot.ai, shotbot.ai) are judged by the same criteria as every other provider and are labelled wherever
                they appear.
              </p>
              <p>{OWNERSHIP_LINE}</p>
            </div>
            <p className="atlas-footer__built">Built by {BUILDER_NAME}</p>
          </div>

          <nav className="atlas-footer__col atlas-footer__col--sections" aria-label="Sections">
            <h2 className="atlas-footer__label">Sections</h2>
            <ul>
              {SECTIONS.map((s, i) => (
                <li key={s} className={s === THIS_SECTION ? "atlas-footer__current" : undefined}>
                  {String(i + 1).padStart(2, "0")} {s}
                </li>
              ))}
            </ul>
          </nav>

          <nav className="atlas-footer__col" aria-label="The guide">
            <h2 className="atlas-footer__label">The guide</h2>
            <ul>
              {FOOTER_GUIDE.map((l) => (
                <li key={l.href}><a href={l.href}>{l.label}</a></li>
              ))}
            </ul>
          </nav>

          <nav className="atlas-footer__col" aria-label="The site">
            <h2 className="atlas-footer__label">The site</h2>
            <ul>
              <li><Link href="/about">About this section</Link></li>
              {FOOTER_SITE.map((l) => (
                <li key={l.href}><a href={l.href}>{l.label}</a></li>
              ))}
            </ul>
          </nav>
        </div>

        <div className="atlas-footer__base">
          <p>&copy; 2026 Vyohm AI Private Limited</p>
          <p>Every fact sourced and dated. Tell us if something is wrong.</p>
        </div>
      </div>
    </footer>
  );
}
