// @ts-check
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';
import { satteri } from '@astrojs/markdown-satteri';
import caseStudyMarkdown from './src/plugins/case-study-markdown.mjs';

// Static site. GitHub Pages serves it from the repo root, so no `base` is needed
// for a <user>.github.io repo. Do not add one without checking every relative link.
export default defineConfig({
  site: 'https://dustinJ15.github.io',
  output: 'static',
  trailingSlash: 'always',
  markdown: {
    // Case-study markdown stays plain markdown: an image with a title becomes a
    // captioned figure in browser chrome, and the designed moments are tagged
    // for the reveal. See src/plugins/case-study-markdown.mjs.
    processor: satteri({ hastPlugins: [caseStudyMarkdown] }),
  },
  vite: {
    plugins: [tailwindcss()],
  },
  image: {
    // Markdown images are the case-study screenshots, and they were shipping a
    // single 2400px master with an empty srcset: a phone downloaded the full
    // file to paint it in a ~335px column. `constrained` makes Astro generate
    // srcset and sizes for every optimised image, markdown ones included, and
    // never upscales past the source. The styles that go with it are left off
    // because the two places an image renders already size it in CSS, and the
    // injected `:where()` rules would be one more thing to reason about.
    layout: 'constrained',
    responsiveStyles: false,
  },
  build: {
    inlineStylesheets: 'auto',
  },
});
