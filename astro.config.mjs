// @ts-check
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

// Static site. GitHub Pages serves it from the repo root, so no `base` is needed
// for a <user>.github.io repo. Do not add one without checking every relative link.
export default defineConfig({
  site: 'https://dustinJ15.github.io',
  output: 'static',
  trailingSlash: 'always',
  vite: {
    plugins: [tailwindcss()],
  },
  build: {
    inlineStylesheets: 'auto',
  },
});
