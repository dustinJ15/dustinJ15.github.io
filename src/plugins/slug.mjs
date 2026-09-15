/**
 * One slug function, used by the markdown plugin to stamp an id on every h2
 * and by the case-study page to link a chapter card to it. They have to agree,
 * so neither keeps a copy.
 */
export const slug = (text) =>
  String(text)
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
