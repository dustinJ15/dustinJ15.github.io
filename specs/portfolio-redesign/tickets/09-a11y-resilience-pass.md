# 09: Keyboard, screen-reader and no-JS pass across every route

**What to build:** The whole site works for someone not using a mouse, not seeing the screen, or
not running the JavaScript. Each page ticket asserted this for its own route as it landed; this
ticket covers what a per-route gate row cannot see, and sweeps the finished site as one thing.

What the gate cannot see, and this ticket has to check by hand:

- **Focus and hover states.** Every interactive element shows a visible focus ring, including
  the ones the design leans on: the magnetic contact button, the work rail cards, the marquee if
  anything in it is focusable. Focus order follows reading order. Nothing traps focus.
- **How it actually reads aloud.** The custom cursor and the decorative half of the duplicated
  marquee are hidden from assistive technology so nothing is announced twice or announced at all
  when it is a dot following the pointer. Landmarks are present and the page reads coherently
  top to bottom.
- **The pinned rail with a keyboard.** Tabbing to a card inside a pinned, scrubbed section must
  not leave the user looking at nothing.

What the gate does check, now extended to every route rather than route by route: AA contrast
including the mono metadata at its rendered size, no horizontal scroll from 375 up, reduced
motion leaving nothing invisible, and every route rendering with JavaScript disabled.

`--ink-faint` sits at the AA floor deliberately and must not be darkened to fix anything found
here.

**Blocked by:** 03, 04, 05, 06, 07.

**Status:** done

- [x] Every interactive element on every route has a visible focus ring, verified by tabbing
      through each page.
- [x] Focus order follows reading order and no element traps focus, including inside the pinned
      work rail.
- [x] The skip link works on every route and moves focus to the main content.
- [x] Decorative elements, including the custom cursor and the duplicated marquee content, are
      hidden from assistive technology.
- [x] Each page reads coherently through a screen reader, with landmarks present and every
      figure carrying real alt text.
- [x] All text meets WCAG AA at its rendered size and weight on every route at every viewport,
      with `--ink-faint` unchanged.
- [x] With reduced motion forced, every route shows all its content and nothing is stuck
      invisible.
- [x] With JavaScript disabled, every route renders its content.
- [x] No route scrolls horizontally at 375, 768 or 1440.
- [x] The gate passes with every route in the table.
