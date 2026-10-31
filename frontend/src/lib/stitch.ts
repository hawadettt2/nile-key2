// Utility to extract the inlined CSS bundle and the root markup from a
// Stitch-exported code.html file, so it can be rendered inside React.
export interface StitchExtract {
  css: string;
  html: string;
}

export function extractStitch(raw: string): StitchExtract {
  // 1. CSS bundle (Tailwind utilities inlined by Stitch)
  const styleMatch = raw.match(/<style[^>]*id="extracted-cssom-bundle"[^>]*>([\s\S]*?)<\/style>/i);
  const css = styleMatch ? styleMatch[1] : '';

  // 2. Body content: everything from the first <div id="root"> ... </body>
  const bodyMatch = raw.match(/<body[^>]*>([\s\S]*?)<\/body>/i);
  let body = bodyMatch ? bodyMatch[1] : raw;

  // Strip leading meta/link/svg-icon noise up to the real root container.
  const rootIdx = body.indexOf('<div id="root">');
  if (rootIdx >= 0) body = body.slice(rootIdx);

  // Drop trailing </body> leftovers already handled by regex.
  // Remove any <script> tags (none expected, but be safe).
  body = body.replace(/<script[\s\S]*?<\/script>/gi, '');

  return { css, html: body };
}
