// A review code is what Python's secrets.token_urlsafe(32) makes: 43 letters, digits, "-" or "_".
// Checking the shape before using it in an API address means nothing like "../" can ever reach the API.
export const isCode = (s: string) => /^[A-Za-z0-9_-]{20,100}$/.test(s);
