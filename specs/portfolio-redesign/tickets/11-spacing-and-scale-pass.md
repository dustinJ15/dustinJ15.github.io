# 11: Spacing and scale pass

**What to build:** The site stops carrying dead vertical space it did not earn, and the display
scale holds up on a phone as well as it does on a desktop. Four specific faults, all found by
reading the gate's own screenshots at 1440 and 375 after ticket 08 landed. None of them is a
redesign. The direction is right and is not up for revisiting here.

- **A screen of empty space between the work rail and the contact block.** Present at 1440 and
  also at 375. Part of it at desktop width is the pin spacer the scrub legitimately needs, but it
  is also there at 375 where nothing is pinned, so the spacer is not the whole story. Measure it
  before changing it, and make the desktop spacer exactly as tall as the scrub distance requires
  and no taller.
- **The hero underfills at 375.** The display lines sit in the top third of the viewport and the
  rest is empty before the availability line. At 1440 the type owns the screen. It should own the
  screen on a phone too, which means the narrow-width display scale, the line breaks, or both.
- **The about portrait is small and stranded.** At 1440 it is a modest rectangle inside a large
  empty block, with a long gap before the prose resumes. Give it a size and a position that earn
  the space around it, or close the space.
- **The about H1 renders entirely in the accent.** `PageTitle` accents the last line, which on a
  one-line title is the whole heading. On the home page the accent is one line out of five and
  works. Decide the rule for a one-line title and apply it everywhere, rather than special-casing
  `/about/`.

Also settle, while in here, whether the accent wash on the portrait should stay. It stops the
photo reading as a hole punched in the near-black page, which is why it exists, but it puts an
olive cast on skin. If it stays, it stays because someone looked at it and chose it.

The gate cannot see any of this, which is why it survived seven tickets. It can, however, be
taught to see part of it: a route that ends in more than some threshold of empty pixels before
its footer is almost always a bug. Add that check if it can be made to not false-positive on the
pinned rail.

**Blocked by:** 07, 09.

**Status:** ready-for-agent

- [ ] The gap between the work rail and the contact block is deliberate at 1440, 768 and 375, and
      is the scrub distance rather than an accident.
- [ ] The hero fills the viewport at 375 the way it does at 1440, with no display line wrapping.
- [ ] The about portrait no longer reads as small and stranded at 1440.
- [ ] The one-line display title has a stated rule for where the accent falls, applied site wide.
- [ ] The portrait's accent wash is kept or dropped as a decision, not by default.
- [ ] The gate passes, and gained whatever coverage of empty trailing space it can hold without
      false positives.
