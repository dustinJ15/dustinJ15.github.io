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
  /** This site's own source, linked from the footer. Not the same as `github`,
      which is the profile: this is the repo a reader can check the site against. */
  repo: 'https://github.com/dustinJ15/dustinJ15.github.io',
  /** Built in career-hub with `build_resume.py general --no-phone`, copied into public/. */
  resume: '/Dustin-Jones-Resume.pdf',
  description:
    'Software engineer in Denver. Case studies of a quoting system, a label generator, a billing analyzer and an ETL pipeline.',
} as const;

export const hero = {
  /**
   * The hero display type, as ROWS of PHRASES. Two rows, one word each: the name.
   * A row is one visual line from `lg` up; below `lg` every phrase takes its own
   * line. The size is bound by the widest line, and the gate's wrap check is what
   * says whether a change still fits.
   */
  displayRows: [['Dustin'], ['Jones']],
} as const;

export const nav = [
  { label: 'Work', href: '/' },
  { label: 'Process', href: '/process/' },
  { label: 'About', href: '/about/' },
  { label: 'Resume', href: '/Dustin-Jones-Resume.pdf' },
] as const;
