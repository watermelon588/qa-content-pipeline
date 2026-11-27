// Checks for the home page's answer preview and search. Run from web/:  node --test lib/answers.test.mjs
import assert from "node:assert/strict";
import { test } from "node:test";
import { matches, previewOf } from "./answers.ts";

test("the preview is the first plain paragraph, without markers or bold marks", () => {
  const body = "## Short answer\r\n\r\n| a | b |\r\n|---|---|\r\n\r\n- a bullet\r\n\r\nRent **per hour** first [1].\r\nThen compare [12].\r\n\r\nMore.";
  assert.equal(previewOf(body), "Rent per hour first. Then compare.");
  assert.equal(previewOf("## Only a heading"), "");
});

test("search needs every word, ignores case and also looks at providers", () => {
  const card = { slug: "x", title: "Fine-tuning on GPU clouds", preview: "Compare hourly prices.", trust: "", providers: ["E2E Networks"] };
  assert.equal(matches(card, ""), true);
  assert.equal(matches(card, "  e2e PRICES "), true);
  assert.equal(matches(card, "prices aws"), false);
});
