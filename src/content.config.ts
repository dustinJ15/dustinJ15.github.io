import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

// One case study per markdown file. The schema is the single source of truth for
// project metadata: the home page work list, the project header and the <head>
// description all read from here, so `stack` can no longer disagree with itself
// the way the old front matter did against a hand-written list on the home page.
const projects = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/projects' }),
  schema: ({ image }) =>
    z.object({
    title: z.string(),
    /** Display order on the home page. Lower is higher. */
    order: z.number().int(),
    year: z.number().int(),
    role: z.string(),
    stack: z.array(z.string()).nonempty(),
    /** Either a public repo, or an honest statement that the code is not public. */
    code: z.object({
      label: z.string(),
      href: z.string().url().optional(),
    }),
    /** Long form. Used as the project page lede and the meta description. */
    summary: z.string(),
    /** Short form. Used in the home page work list. */
    tagline: z.string(),
    /** The before/after pair, structured so it can be designed rather than hand-rolled in HTML. */
    outcome: z
      .object({ before: z.string(), after: z.string() })
      .optional(),
    /**
     * Render a chapter rail under the outcome band: one card per `##`, carrying
     * that section's first screenshot, or its pull quote where it has none.
     * Opt-in, for a study long enough to need a way in.
     */
    chapters: z.boolean().default(false),
    /**
     * The picture on the home page card. Optional: a study with nothing to
     * screenshot (a pipeline) sets the card as type alone. Synthetic data only,
     * like everything else under src/assets/img.
     */
    thumb: image().optional(),
    /** Small, verifiable figures. Never invented, always traceable to the case study text. */
    metrics: z
      .array(z.object({ value: z.string(), label: z.string() }))
      .default([]),
    }),
});

export const collections = { projects };
