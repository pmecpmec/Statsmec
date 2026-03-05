import { defineConfig } from 'astro/config';
import svelte from '@astrojs/svelte';
import tailwind from '@astrojs/tailwind';

export default defineConfig({
  site: 'https://stats.pmec.dev',
  integrations: [
    svelte(),
    tailwind({ applyBaseStyles: false }),
  ],
  build: {
    inlineStylesheets: 'auto',
  },
});
