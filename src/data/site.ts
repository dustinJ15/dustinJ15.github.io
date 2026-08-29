/**
 * Site-wide copy that is not a case study. Project metadata lives in the content
 * collection instead, so the home page and a case study cannot disagree.
 *
 * Copy here has been through the ticket 08 editorial pass. No em-dashes: the
 * verification gate fails the build on one, in body copy and in metadata alike.
 */

export const site = {
  name: 'Dustin Jones',
  role: 'Software engineer',
  location: 'Denver',
  email: 'DBJ2297@gmail.com',
  github: 'https://github.com/dustinJ15',
  githubHandle: 'github.com/dustinJ15',
  linkedin: 'https://www.linkedin.com/in/dustinj15',
  description:
    'Software engineer in Denver. I build full-stack applications and the pipelines that keep them reliable. Available for part-time and contract work.',
} as const;

export const hero = {
  intro: 'I build full-stack applications and the pipelines that keep them reliable.',
  availability: 'Available now for part-time and contract work, Denver or remote.',
  /** Split for lanes that animate the display line word by word or line by line. */
  displayLines: ['Full-stack', 'applications', 'and the pipelines', 'that keep them', 'reliable.'],
} as const;

export const bio = [
  'Last summer I shipped three production tools in eight weeks at Frontage Laboratories, a clinical CRO. The largest replaced a day-and-a-half manual quoting process: intake form, rules engine, Excel and PDF at the end. Tested, containerized, gated behind CI.',
  "I'm finishing a B.S. in Computer Science at MSU Denver, 4.0 GPA, December 2027. Before this I built ETL pipelines for a property management firm, and before that I taught skiing professionally for five seasons.",
] as const;

export const nav = [
  { label: 'Work', href: '/' },
  { label: 'Process', href: '/process/' },
  { label: 'About', href: '/about/' },
] as const;

export const elsewhere = {
  process:
    'How I work is its own page. I use agentic tooling heavily, and the interesting part is the harness that makes what it writes verifiable.',
  code: 'The three tools above were built for an employer and stay private. The writeups describe the engineering without the client’s data.',
} as const;
