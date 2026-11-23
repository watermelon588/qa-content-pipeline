import type { Metadata } from "next";
import { BLUESKY_URL, BUILDER_NAME, EXPERT_NAME, HUB_URL, OWNERSHIP_LINE, SECTION_NAME } from "@/lib/site";

export const metadata: Metadata = {
  title: "About this section",
  description: `Who builds and reviews the ${SECTION_NAME} section, how AI is used, and who owns the site.`,
  alternates: { canonical: "/about" },
};

// The five marks used across AI Atlas India (same names as the hub).
const MARKS = [
  ["Sourced fact", "Links to its source and shows the date we checked it."],
  ["Not yet sourced", "Left out. We never guess a price, a feature or a data location."],
  ["AI-assisted draft", "AI wrote the first version from the sources listed on the page."],
  ["Reviewed by a named expert", "A real person in the field edited and approved it, with the date."],
  ["Owned by Vyohm, the company that runs this site", "Shown wherever a Vyohm product appears. Same criteria, no special treatment."],
];

export default function About() {
  return (
    <>
      <section className="band--sea band--rule-bottom">
        <div className="wrap wrap--narrow section-pad">
          <h1 className="display">About this section</h1>
          <p className="lede" style={{ marginTop: "var(--atlas-space-4)" }}>
            {SECTION_NAME}: answers to the questions business owners ask before they buy.
          </p>
        </div>
      </section>

      <div className="wrap wrap--narrow section-pad">
        <div className="prose">
          <h2 style={{ marginTop: 0 }}>Who builds it</h2>
          <p>
            This section was built by {BUILDER_NAME} as a candidate for Vyohm AI&rsquo;s internship
            assignment. AI coding tools were used to build it.
          </p>

          <h2>Who reviews it</h2>
          {EXPERT_NAME ? (
            <p>Every answer is checked and approved by {EXPERT_NAME}, who has agreed in writing to be named here.</p>
          ) : (
            <p>
              Our expert reviewer will be named here, with their credentials and any link they have to a
              provider, once they have agreed in writing to be named. Until a named expert has signed an
              answer, it is not published.
            </p>
          )}

          <h2>How we use AI</h2>
          <ul>
            <li>AI helps find the questions people ask, using public question sources through their official APIs.</li>
            <li>AI writes the first draft of an answer, and only from sources we supply. Each fact keeps its source link and the date we checked it.</li>
            <li>A person checks every fact against its source before the expert sees the draft.</li>
            <li>The expert approves, edits or rejects each answer. Only approved answers go live, and every page says it was drafted with AI.</li>
            <li>
              Social posts are written by AI about our own answers only. A person approves every reply
              before it is sent.{BLUESKY_URL && <> Follow us on <a href={BLUESKY_URL}>Bluesky</a> (an automated account, labelled as such).</>}
            </li>
          </ul>

          <h2>Who owns the site</h2>
          <p>{OWNERSHIP_LINE}</p>
          <p>
            There are no paid placements, affiliate links or sponsored rankings. Where a Vyohm product
            fits a question, it is shown next to the alternatives, labelled, and judged by the same criteria.
          </p>

          <h2>How to read a page</h2>
        </div>
        <ul className="rule-list" style={{ maxWidth: "70ch", marginTop: "var(--atlas-space-4)" }}>
          {MARKS.map(([name, text]) => (
            <li key={name}>
              <strong>{name}</strong>
              <span className="muted">{text}</span>
            </li>
          ))}
        </ul>

        <p className="prose" style={{ marginTop: "var(--atlas-space-6)" }}>
          Spotted a mistake? <a href={`${HUB_URL}/contact/`}>Tell us</a> and we will check it against the source.
        </p>
      </div>
    </>
  );
}
