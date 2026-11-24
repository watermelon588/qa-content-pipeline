// Checks for the admin login cookie. Run from web/:  node --test lib/session.test.mjs
import assert from "node:assert/strict";
import { test } from "node:test";
import { checkToken, makeToken, MAX_AGE, sameText } from "./session.ts";

const KEY = "admin:correct horse";
const NOW = 1_000_000;

test("a cookie we made is accepted until it expires", async () => {
  const token = await makeToken(KEY, NOW);
  assert.equal(await checkToken(token, KEY, NOW + 1000), true);
  assert.equal(await checkToken(token, KEY, NOW + MAX_AGE * 1000 + 1), false); // a week and a second later
});

test("a changed password, a stretched expiry or junk are refused", async () => {
  const token = await makeToken(KEY, NOW);
  assert.equal(await checkToken(token, "admin:other password", NOW), false); // password changed: everyone logged out
  const [, signature] = token.split(".");
  assert.equal(await checkToken(`${NOW + 10 * MAX_AGE * 1000}.${signature}`, KEY, NOW), false); // expiry edited
  for (const junk of [undefined, "", "abc", "123.", "x.y", ".sig"]) assert.equal(await checkToken(junk, KEY, NOW), false);
});

test("sameText compares whole strings", () => {
  assert.equal(sameText("abc", "abc"), true);
  assert.equal(sameText("abc", "abd"), false);
  assert.equal(sameText("abc", "abcd"), false);
});
