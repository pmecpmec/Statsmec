/**
 * Developer-only UI: env-var names, sync tooling, and config warnings.
 *
 * - `astro dev` → true (local work).
 * - `astro build` (e.g. GitHub Pages from `main`) → false.
 * - Optional: set `PUBLIC_DEV_UI=true` when building to force dev copy (avoid on public deploys).
 */
export const showDevSetupHints =
  import.meta.env.DEV || import.meta.env.PUBLIC_DEV_UI === 'true';
