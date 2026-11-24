// A review code is what Python's secrets.token_urlsafe(32) makes: 43 letters, digits, "-" or "_".
// Checking the shape before using it in an API address means nothing like "../" can ever reach the API.
export const isCode = (s: string) => /^[A-Za-z0-9_-]{20,100}$/.test(s);

// The expert's personal reviewer code is kept in this cookie after they type it once, so they aren't asked again.
// The page only forwards it; the API checks it on every request (api/review/router.py).
export const EXPERT_COOKIE = "atlas_expert";

// What they typed, as the API compares it: letters and digits only, capitals ("k7qm-4xrt" -> "K7QM4XRT").
export const cleanCode = (s: string) => s.toUpperCase().replace(/[^A-Z0-9]/g, "").slice(0, 20);
