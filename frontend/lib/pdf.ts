import puppeteer, { type Browser } from "puppeteer";
import { marked } from "marked";

let browserPromise: Promise<Browser> | null = null;

async function getBrowser(): Promise<Browser> {
  if (browserPromise) {
    try {
      const existing = await browserPromise;
      if (existing.connected) return existing;
    } catch {
      // launch failed previously — fall through to relaunch
    }
    browserPromise = null;
  }
  browserPromise = puppeteer.launch({ headless: true });
  try {
    return await browserPromise;
  } catch (err) {
    browserPromise = null;
    throw err;
  }
}

const css = `
  @page { margin: 1in; }
  html, body { font-family: "Times New Roman", Times, serif; line-height: 1.6; color: #1a1a1a; font-size: 11pt; }
  h1 { font-size: 18pt; margin-top: 0; }
  h2 { font-size: 14pt; margin-top: 1.4em; }
  h3 { font-size: 12pt; margin-top: 1.2em; }
  hr { border: 0; border-top: 1px solid #999; margin: 2em 0; }
  p { margin: 0.6em 0; }
  ul, ol { padding-left: 1.5em; }
  table { border-collapse: collapse; width: 100%; }
  td, th { border: 1px solid #999; padding: 0.4em 0.6em; }
  strong { font-weight: 600; }
  .meta { color: #555; font-size: 9pt; margin-top: 2em; }
`;

export type PdfRenderInput = {
  title: string;
  versionNumber: number;
  markdown: string;
};

export async function renderPdf(input: PdfRenderInput): Promise<Buffer> {
  const html = await marked.parse(input.markdown);
  const fullHtml = `<!doctype html><html><head><meta charset="utf-8"><title>${escapeHtml(
    input.title,
  )}</title><style>${css}</style></head><body>${html}<p class="meta">Document: ${escapeHtml(
    input.title,
  )} — Version ${input.versionNumber}</p></body></html>`;

  let browser: Browser;
  try {
    browser = await getBrowser();
  } catch (err) {
    browserPromise = null;
    throw err;
  }

  const page = await browser.newPage();
  try {
    await page.setContent(fullHtml, { waitUntil: "domcontentloaded" });
    const pdf = await page.pdf({ format: "Letter", printBackground: true });
    return Buffer.from(pdf);
  } catch (err) {
    // The browser may be in a bad state — invalidate the cached instance so
    // the next request relaunches a fresh Chromium rather than reusing a
    // crashed one.
    browserPromise = null;
    throw err;
  } finally {
    await page.close().catch(() => {});
  }
}

function escapeHtml(s: string): string {
  return s.replace(/[&<>"']/g, (c) =>
    c === "&" ? "&amp;" : c === "<" ? "&lt;" : c === ">" ? "&gt;" : c === '"' ? "&quot;" : "&#39;",
  );
}
