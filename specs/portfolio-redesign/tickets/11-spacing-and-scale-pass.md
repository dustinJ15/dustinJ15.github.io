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

**Status:** done

- [x] The gap between the work rail and the contact block is deliberate at 1440, 768 and 375, and
      is the scrub distance rather than an accident. At 1440 the pin spacer was already exactly
      the scrub distance (1311 - 900 = 411px = track overhang); what was not deliberate was the
      rail filling only 590px of a 900px viewport while pinned, leaving 310px of empty page under
      it for the whole of that scroll, and 176px of stacked padding between the last card and the
      word "Contact" at every width. The rail now fills the viewport at lg and centres in it, and
      the two paddings no longer stack: 176px of unmarked ground becomes 105px with a rule
      through it.
- [x] The hero fills the viewport at 375 the way it does at 1440, with no display line wrapping.
      Below lg the five rows break into seven lines, which changes the line the size is bound by
      from "and the pipelines" to "applications" and takes the type from 35px to 50px: the display
      block goes from 224px of a 716px hero to 345px, and the dead space around it from 382px to
      220px. The gate checks the wrap at 375, 768 and 1440; both lanes were also swept by hand from
      320px to 2200px, including either side of the 1024px switch.
- [x] The about portrait no longer reads as small and stranded at 1440. It goes from four
      columns to five and runs out through the left gutter to the page edge, 404 x 481 to
      577 x 687, and the paragraph beside it lands on its foot instead of stopping a third of the
      way down.
- [x] The one-line display title has a stated rule for where the accent falls, applied site wide.
      The accent marks the END of a title, and only where there is an end to mark: the last line
      of a title that has more than one, and nothing on a title that has one. It is a rule about
      line count, not about which page, so `/about/` is not special-cased and a title that grows
      a second line picks the accent up on its own. Stated in full on `PageTitle` and applied
      there and on the case-study title.
- [x] The portrait's accent wash is kept or dropped as a decision, not by default. Dropped,
      after looking at it: on a grayscale, darkened photograph the desaturation and the dissolve
      at the foot already stop it reading as a hole punched in the page, and the wash's only
      remaining visible effect was an olive cast on skin.
- [x] The gate passes, and gained whatever coverage of empty trailing space it can hold without
      false positives. `MAX_TRAILING_EMPTY` caps the gap between the last painted thing in `main`
      and the footer. Trailing, not biggest-anywhere, which is what keeps the pinned rail's spacer
      out of it. Real gaps across eight routes at three viewports run 64px to 187px; the budget
      is 260px.
