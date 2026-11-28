// Provider pages offered as tick boxes on the draft form, so you don't have to hunt for URLs every time.
// The public home page uses the same list to turn a source address into a provider's name.
// Only add a page after checking that it downloads as readable text with the API's own downloader (pages drawn
// by JavaScript don't: paste their text instead). Re-checked on 28 Nov 2026 from a laptop: each of these downloaded
// and had GPU prices next to GPU names in its text. Pages change, so the fact check still matters.
// Any other page can still be typed into the form.

export const KNOWN_SOURCES = [
  { group: "India", provider: "E2E Networks", page: "GPU cloud (₹ prices)", url: "https://www.e2enetworks.com/gpu-cloud" },
  { group: "India", provider: "E2E Networks", page: "Full pricing (₹ and $)", url: "https://www.e2enetworks.com/pricing" },
  { group: "India", provider: "JarvisLabs", page: "India GPU prices (₹)", url: "https://jarvislabs.ai/in" },
  { group: "India", provider: "Yotta", page: "Shakti Cloud plans (₹, many are monthly)", url: "https://shakticloud.ai/pricing" },
  { group: "India", provider: "Cyfuture AI", page: "GPU pricing (₹ and $)", url: "https://cyfuture.ai/pricing" },
  { group: "India", provider: "Neysa", page: "GPU pricing ($)", url: "https://neysa.ai/pricing/" },
  { group: "Global", provider: "AWS", page: "Reserved GPU blocks ($, lists Mumbai)", url: "https://aws.amazon.com/ec2/capacityblocks/pricing/" },
  { group: "Global", provider: "Google Cloud", page: "GPU machine prices ($, check the region)", url: "https://cloud.google.com/products/compute/pricing/accelerator-optimized" },
  { group: "Global", provider: "RunPod", page: "GPU prices ($)", url: "https://www.runpod.io/pricing" },
  { group: "Global", provider: "Lambda", page: "GPU prices ($)", url: "https://lambda.ai/pricing" },
  { group: "Global", provider: "CoreWeave", page: "GPU prices ($, check the region)", url: "https://www.coreweave.com/pricing" },
  { group: "Global", provider: "DigitalOcean", page: "GPU Droplet prices ($)", url: "https://www.digitalocean.com/pricing/gpu-droplets" },
  { group: "Global", provider: "Hyperstack", page: "GPU prices ($)", url: "https://www.hyperstack.cloud/gpu-pricing" },
  { group: "Global", provider: "Nebius", page: "GPU prices ($)", url: "https://www.nebius.com/prices" },
];

export const SOURCE_GROUPS = [
  { key: "India", label: "Indian providers" },
  { key: "Global", label: "Global providers" },
];

const hostname = (url: string) => {
  try {
    return new URL(url).hostname.replace(/^www\./, "");
  } catch {
    return url;
  }
};

/** "https://www.e2enetworks.com/x" gives "E2E Networks". A page that isn't in the list gives its host name. */
export const providerOf = (url: string) =>
  KNOWN_SOURCES.find((s) => hostname(s.url) === hostname(url))?.provider ?? hostname(url);
