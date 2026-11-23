// Provider pages offered as tick boxes on the draft form, so you don't have to hunt for URLs every time.
// Only add a page after checking that it downloads as readable text (pages drawn by JavaScript don't:
// paste their text instead). Checked on 22 Nov 2026: each of these downloaded with real text.
// Any other page can still be typed into the form.

export const KNOWN_SOURCES = [
  { provider: "E2E Networks", page: "GPU cloud (prices in rupees)", url: "https://www.e2enetworks.com/gpu-cloud" },
  { provider: "E2E Networks", page: "Pricing", url: "https://www.e2enetworks.com/pricing" },
  { provider: "AWS", page: "EC2 P5 instances (H100)", url: "https://aws.amazon.com/ec2/instance-types/p5/" },
  { provider: "Google Cloud", page: "GPU pricing", url: "https://cloud.google.com/compute/gpus-pricing" },
];
