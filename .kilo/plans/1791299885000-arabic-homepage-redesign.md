# Arabic Homepage — Authoritative Reconstruction Brief

**Status:** This is the active implementation brief for the homepage. It supersedes the previous public-homepage redesign plans and all older Kilo summaries. It does not authorize changing unrelated routes, backend behavior, or business logic.

## Source of truth

- Use `frontend/public/design-reference/nile-key-export-platform-homepage-ar.png` as the sole visual authority for the public homepage.
- The attached image is a complete composition reference. Rebuild its elements as page markup, styles, code-drawn UI, and independent image assets.
- Never display the full reference, crop sections from it, or use screenshots/design boards as runtime images.
- Do not use the existing `frontend/public/assets/hero-export.jpg`, `about-egypt.jpg`, `products/*.jpg`, or `services/services-bg.jpg` as homepage images. They contain flattened design-board/UI content rather than clean standalone photographs.
- Keep current public routes, authentication destinations, language switcher, translations, and RTL/LTR behavior.

## Exact page sequence

1. **Header over hero:** compact brand at the visual left, navigation and language/auth actions aligned as in the reference. On small screens, keep the current accessible mobile-menu behavior.
2. **Hero:** full-width Egyptian export scene; title and company identity on the opposite side with two account actions. The hero image must be a clean standalone image with no baked-in text, logo, website UI, or buttons.
3. **Our Company:** dark teal two-column section; Arabic/English company copy and three compact capability icons on one side, a standalone cargo-ship photo on the other.
4. **Export Journey:** light, wide scenic band; copy on the visual right and exactly four RTL steps with green circular icons and thin directional arrows: Egyptian farms/factories → port → transport → global markets. Match the reference ordering and spacing.
5. **Digital Platform:** dark section with explanatory copy on the visual left and a monitor-plus-phone illustration on the right. Build the device/dashboard in React/SVG/CSS; do not embed a screenshot. Beneath it, render exactly six outlined feature tiles in a 3-column by 2-row desktop grid, collapsing cleanly on mobile.
6. **Closing CTA:** one wide, light green trade-network image band with centered heading, short supporting line, and one dark rounded contact button.
7. **Footer:** compact dark footer with brand at left, navigation across the right, copyright at lower left, and the reference social marks at lower right. Render social marks as non-interactive unless verified project URLs exist; never link them to `#`.

## Explicit exclusions

- No separate Products tile section.
- No standalone Global Markets metrics/map section.
- No Trusted Partners/quality-badge panel.
- No invented trust marks, statistics, fake dashboard records, empty image placeholders, or screenshot crops.
- Do not alter standalone Products, Markets, Services, About, or Contact routes as part of this task.

## Image assets

Use clean, independent photos for the hero, company ship, export journey, and CTA. Current files live in `frontend/public/assets/home/`: `hero-port-said.jpg`, `hero-pyramids.jpg`, `hero-produce.jpg`, `company-cargo-ship.jpg`, `export-journey-panorama.jpg`, and `global-trade-cta.jpg`. Build the hero and journey scenes from these independent photos with CSS masks and color overlays; do not flatten the design reference into a new composite. Keep all text, brand marks, buttons, diagrams, and responsive overlays in page code. No runtime image may point to the reference or a design-board crop.

## Content and implementation

- Prefer existing approved Arabic/English copy where it matches the reference. Add only the missing homepage-specific strings to both locale files; preserve unrelated locale keys.
- Use semantic sections/headings, accessible controls, actual links, stable React keys, and decorative `aria-hidden` treatment for non-semantic SVG.
- Keep the design palette sampled from the reference: very dark teal, mid teal, vivid green accents, and the near-white scenic section.
- Implement responsive behavior for mobile, tablet, and desktop while preserving the desktop composition.

## Acceptance checks

- At desktop width, the section order, proportions, image placement, light/dark transitions, header, feature grid, CTA, and footer follow the Arabic reference; no extra homepage sections appear.
- No runtime image points to a screenshot, design board, full-page reference, or cropped section.
- Arabic is RTL; English is LTR; both retain working navigation and authentication links.
- No horizontal overflow at 375, 390, 768, 1024, 1280, and 1440 CSS pixels.
- Build and relevant existing checks pass. Compare a full-page browser capture with the supplied Arabic reference before declaring visual completion.
