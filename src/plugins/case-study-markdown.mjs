/**
 * The one Markdown transform the case studies need.
 *
 * Authoring stays plain markdown, which is the point of the ticket: adding a
 * case study is dropping one `.md` in. A screenshot is written as
 *
 *     ![alt text](../../assets/img/thing.png "The caption.")
 *
 * so the file goes through Astro's own image pipeline (a relative path in a
 * content-collection markdown file is resolved and optimised by it) instead of
 * being a raw <img> pointed at a public URL. This plugin turns that image into
 * the captioned, browser-chromed figure the design calls for, so no presentation
 * markup lives in the content. The Jekyll pages hand-rolled a <figure> in raw
 * HTML around a Liquid URL; that could not be optimised and it put layout in the
 * prose.
 *
 * This is a Sätteri hast plugin, not a rehype one. Sätteri is Astro's default
 * Markdown processor now, and `markdown.rehypePlugins` is a deprecated shim that
 * pulls the whole unified pipeline back in as an extra dependency.
 *
 * Astro registers its own image-marker plugin AFTER the user's, so the plain
 * `src` written below is still picked up and optimised.
 */
import { defineHastPlugin } from 'satteri';
import { slug } from './slug.mjs';

const isBlank = (node) => node.type === 'text' && !node.value.trim();

/** The lone <img> inside this node, or null if it is not an image-only paragraph. */
function soleImage(node) {
  const kids = (node.children ?? []).filter((c) => !isBlank(c));
  if (kids.length !== 1) return null;
  const only = kids[0];
  return only.type === 'element' && only.tagName === 'img' ? only : null;
}

function figureFor(img) {
  // The markdown title becomes the caption, so it must not also survive as a
  // tooltip repeating the caption on hover.
  const { title, ...properties } = img.properties ?? {};
  const caption = typeof title === 'string' ? title : '';

  // The frame is a child of the figure rather than the figure itself, so the
  // caption can sit outside the pictured window and still be inside the figure
  // that it captions.
  const children = [
    {
      type: 'element',
      tagName: 'div',
      properties: { className: ['shot-frame'] },
      children: [
        {
          type: 'element',
          tagName: 'div',
          properties: { className: ['shot-chrome'], 'aria-hidden': 'true' },
          children: [],
        },
        {
          type: 'element',
          tagName: 'div',
          properties: { className: ['shot-body'] },
          children: [{ type: 'element', tagName: 'img', properties, children: [] }],
        },
      ],
    },
  ];

  if (caption) {
    children.push({
      type: 'element',
      tagName: 'figcaption',
      properties: {},
      children: [{ type: 'text', value: caption }],
    });
  }

  return {
    type: 'element',
    tagName: 'figure',
    properties: { className: ['shot'], 'data-reveal': '' },
    children,
  };
}

/**
 * Blocks allowed to arrive on scroll. Deliberately NOT `p` or `li`: a case study
 * exists to be read, so body copy is painted at full opacity before anything
 * scroll-triggered runs. Only the designed moments animate.
 */
const REVEALS = ['h2', 'h3', 'blockquote'];

/** The heading's visible text, for its id. */
const textOf = (node) =>
  (node.children ?? [])
    .map((c) => (c.type === 'text' ? c.value : c.type === 'element' ? textOf(c) : ''))
    .join('');

const plugin = defineHastPlugin({
  name: 'case-study',
  element: [
    {
      filter: ['p'],
      visit(node, ctx) {
        const img = soleImage(node);
        if (img) ctx.replaceNode(node, figureFor(img));
      },
    },
    {
      filter: REVEALS,
      visit(node, ctx) {
        ctx.setProperty(node, 'data-reveal', '');
        // Chapter cards on the study page link to `#<slug>`; the slug is shared
        // so the two cannot drift.
        if (node.tagName === 'h2') ctx.setProperty(node, 'id', slug(textOf(node)));
      },
    },
  ],
});

/**
 * Scoped to the case studies, and it has to be.
 *
 * `data-reveal` is a contract with a page's own motion script: the CSS that
 * hides it is armed by ANY page calling `withMotion`, so a heading marked here
 * on a page whose script has no reveal loop would be hidden and never brought
 * back. Case studies are the only markdown this applies to, and stamping every
 * markdown document site-wide would hand that trap to whoever writes the next
 * page as markdown.
 */
const CASE_STUDIES = '/src/content/projects/';

export default function caseStudyMarkdown(ctx) {
  return ctx.fileURL?.pathname.includes(CASE_STUDIES) ? plugin : null;
}
