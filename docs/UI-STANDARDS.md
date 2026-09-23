# Interface standards

What the interface is held to, where each rule comes from, and how it is
checked. Written 2026-09-22 alongside the visual rework; the tokens live in
`src/operators_console/ui/theme.py` and the checks in `tests/test_ui_round2.py`.

## Sources consulted

| Source | What was taken from it |
| --- | --- |
| WCAG 2.2, 1.4.3 Contrast (Minimum) and 1.4.11 Non-text Contrast | Text 4.5:1 against its background; large text and the visible boundary of every control 3:1. Both are enforced by tests over every token pair the interface draws. |
| WCAG 2.2, 2.4.11 Focus Appearance, and the CSS `:focus-visible` rules | Keyboard focus changes something visible on every focusable control - and only keyboard focus does. Qt has no `:focus-visible`, so `ui/focus.py` supplies it: a widget is marked `kbd` when the last thing the learner did was press a key, and every ring selector reads `[kbd="true"]:focus`. Text fields are the documented exception and keep their plain `:focus` border - dashed ring on navigation, accent border on fields, a darker ring on filled buttons, a background change on tabs and radios. |
| Radix Colors, *Understanding the scale* | The 12-step ladder: app background, subtle background, element background, hovered, active, subtle border, element border, hovered border, solid, hovered solid, low-contrast text, high-contrast text. The `Palette` tokens map onto these steps. |
| Material Design, *Dark theme* | Dark grey rather than black as the base surface; depth expressed tonally (each layer a step lighter) rather than with shadows; desaturated accents so colour does not vibrate on dark. |
| Apple Human Interface Guidelines, *Dark Mode* and *Color* | Two appearance modes with the same information hierarchy; content legible in both; system-adaptive semantic colours (a `done`, a `warn`, a `bad`, each with a text and a tint variant). |
| Vercel Geist, *Colors* | Two page backgrounds and a three-step component-background ladder; low-contrast versus high-contrast text as separate tokens. |
| Windows 11 design, *Spacing* and *Typography* | The 4-pixel grid; 8 px between controls, 12 px between a control and its label, 16 px from a surface edge to its text; a type ramp with distinct caption, body, subtitle and title sizes. |
| Emil Kowalski, design engineering notes | Press feedback on every pressable; no animation on keyboard-driven actions; ease-out for anything entering, under 300 ms; reduced-motion keeps the change and drops the movement. |

## Tokens

Both themes share one set of names. Every value below was run through a
contrast solver before it was adopted.

| Token | Role | Dark | Light |
| --- | --- | --- | --- |
| `bg` | app background | `#0F1114` | `#F4F5F7` |
| `bg_2` | sidebar, menu bar, status bar | `#141619` | `#EDEEF1` |
| `surface` | card | `#1A1D21` | `#FFFFFF` |
| `surface_2` | hovered element, input field | `#20242A` | `#F7F8FA` |
| `surface_3` | active or selected element, progress track, neutral pill | `#272C33` | `#EEF0F3` |
| `rule` | hairline (card edge, divider) | `#2B3036` | `#E3E6EA` |
| `rule_2` | element border (button, field, menu) | `#353B43` | `#D5D9DF` |
| `rule_strong` | border of an operable control - 3:1 on every surface | `#6E7681` | `#7C838D` |
| `ink` | high-contrast text | `#EDEFF2` | `#15181D` |
| `ink_soft` | secondary text | `#AEB4BC` | `#4A515C` |
| `ink_faint` | muted text and placeholders - still 4.5:1 on every surface | `#8F969F` | `#646C77` |
| `accent` / `accent_hover` / `accent_press` | the one brand colour, as a fill | `#E5793F` `#EE8A55` `#D66C34` | `#B8471C` `#C24B21` `#9E3B15` |
| `accent_text` | the accent as text | `#F2A072` | `#A63F18` |
| `accent_subtle` | the accent as a tint behind `accent_text` | `#36231A` | `#FAE8DF` |
| `on_accent` | text on any solid fill | `#1A1005` | `#FFFFFF` |
| `done` / `done_text` / `done_subtle` | success | `#4FC08D` `#6FD3A3` `#16302A` | `#1F7A4D` `#1F6F46` `#E4F3EA` |
| `warn` / `warn_text` / `warn_subtle` | caution | `#E3A83C` `#F0BC5A` `#332A16` | `#9A6410` `#8A5A0E` `#FBF0D9` |
| `bad` / `bad_text` / `bad_subtle` | failure | `#F0705E` `#F4857A` `#3A1E1B` | `#B8321F` `#A82D1C` `#FBE5E1` |
| `focus` | keyboard focus ring | `#F2A072` | `#B8471C` |
| `tooltip_bg` / `tooltip_ink` | tooltips | `#272C33` / `#EDEFF2` | `#15181D` / `#FFFFFF` |

Measured minimums (the solver's worst pairs): dark `ink_faint` on `surface_3`
4.71:1, light `on_accent` on `accent_hover` 4.86:1, light `rule_strong` on
`bg` 3.51:1. Nothing the interface draws sits below 4.5:1 for text or 3:1
for a control edge.

## Type

System font first (Inter, then Segoe UI Variable, Segoe UI, SF Pro Text);
code in JetBrains Mono, Cascadia Mono, IBM Plex Mono or Consolas.

| Role | Size / weight | Tracking |
| --- | --- | --- |
| Page title | 26 px / 700 | -0.7 px |
| Headline number (stat tile) | 34 px / 700 | -1.2 px |
| Kicker (small caps above a title) | 11 px / 700 | +1.2 px |
| Section title, card title | 13 px / 700 | 0 |
| Body | 13 px / 400 | 0 |
| Secondary body | 12.5 px / 400 | 0 |
| Muted, captions, table headers | 12 px / 400-600 | 0 to +0.3 px |
| Pill | 11 px / 700 | +0.4 px |
| Buttons | 12.5 px / 600 | 0 |

Everything you have to read is 12 px or larger; 11 px is reserved for labels
(a test refuses any other 11 px rule in the sheet). The text-size setting
scales every size in the sheet, not only plain labels.

## Space and shape

- 4 px grid. Card padding 16 px; compact card 12 px; 8 px between controls;
  12 px between a label column and its field; 24 px page margins.
- Corners: 6 px on controls and inputs, 10 px on cards and lists, 8 px on
  menus and code, 4 px on checkboxes.
- Borders: cards use the hairline (`rule`); controls use `rule_2`; anything
  that must be found by eye alone (a checkbox, a radio) uses `rule_strong`.
- Depth is tonal. The sidebar is one step below the page, a card one step
  above it, a hovered element one more, an active element one more. No
  shadows.
- Pills carry a tint and the same hue as text, never a solid fill; solid
  fills are for the primary action of a view.

## Focus

- A ring is drawn for the keyboard and for nothing else. A control the
  mouse has just pressed, or one Qt parked the focus on after a page was
  rebuilt, wore a ring it never earned; on screen that read as damage.
- The mark is consumed by the focus change it causes, so typing a note and
  then having a page rebuilt underneath you cannot ring whatever Qt hands
  the focus to next.
- Rings are solid. Nothing in either theme is dashed, and a test refuses
  the word.
- Text fields keep their border on a click, which is what `:focus-visible`
  itself does: clicking into a field is how you start typing.
- The watching is cheap by design. An application-wide event filter sees
  every event of every object - 31,000 calls to open one phase page, which
  cost more than the page did - so the watcher listens to `focusChanged`
  and `focusWindowChanged` and filters only the window.

## Motion

- Press feedback is colour, never geometry: a pressed control changes
  background and border, and a test refuses any `:pressed` rule that moves
  the control.
- Animation is reserved for state you could otherwise lose track of: the
  disclosure fold (180 ms, ease-out) and the update button's fill. Nothing
  keyboard-driven animates.
- `reduced_motion()` is honoured everywhere something moves: the change
  still happens, instantly.

## How it is checked

- `tests/test_ui_round2.py`: contrast of every body, muted and on-fill pair
  in both palettes; control borders at 3:1; no 11 px body text; every
  pressable state repeats its radius; no pressed rule moves a control.
- A real-font audit harness (Windows platform, off screen) renders every
  page and state in both themes at 940x620, 1024x640, 1366x768 and
  1920x1080, at 150 % scale and at 1.6x text, and measures clipped text,
  overlaps, sideways scrollbars, elided rows, contrast and invisible focus.
  After the learner-view sweep it reports fifteen items at 1366x768, of which four are by design - the code editor scrolls long lines sideways, search rows are elided with the full text in a tooltip, a 170-character scratch path cannot wrap, and the Review page takes the focus itself so its number keys work, which draws no ring because a page is not a control. The rest are sampler artefacts on tinted grounds, recognisable because the reported foreground and background are the same colour. The harness sets the keyboard flag before it focuses a control, since a programmatic `setFocus` deliberately draws nothing.
- The learner walkthrough (`pytest -m walk`) drives every page as a user
  would and fails if fewer than 80 % of the interface's controls were
  pressed.

## The rework, before and after

| Before | After | Why |
| --- | --- | --- |
| Green-grey "paper" light theme, flat charcoal dark theme, 1 px borders on everything | Neutral cool-grey ladders, tonal elevation, hairline card edges | Depth from surface steps reads as premium; heavy borders read as a form |
| Solid pills (`DONE`, `CORE`, `YOU ARE HERE`) in full colour | Tinted pills with the hue as text | Solid colour is reserved for the one primary action per view |
| Text on filled buttons drawn in the card colour (3.7:1 in dark) | `on_accent` token, 6.6:1 dark / 5.2:1 light | WCAG 1.4.3 |
| Wordmark broken over two lines | One line, 14 px / 700 | It is a name, not a heading |
| Full-width nav rows with a 3 px accent bar; focus looked like "selected" | Inset 6 px-radius rows; active = one surface step + 600 weight; focus = dashed ring, Tab only | Two rows no longer look selected at once |
| Search bar the full width of the window | A 520 px field; results in a floating panel wider than the field | A field sized for a query, a panel sized for its answers |
| Today and Roadmap cards with the button alone on a bottom row (145 px cards) | Button on the title row (90 px cards) | Less empty space; the action next to what it acts on |
| Checked items struck through, code included | Prose struck, code spans left whole | A line through monospace text hid the thing the item was about |
| Phase jumps styled as quiet text | Secondary buttons | They are actions and now look like it |
| Spin boxes and dates with no arrows; radios invisible in dark | Arrows drawn in the theme's ink; radios styled | Qt's stock arrows are dark grey in both themes |
| The text-size setting scaled only plain labels | The whole sheet scales; fixed widths became minimums | Headings and buttons must grow with the body |
| Text-only sidebar, eleven items in one column | A brand mark, four captioned sections (Learn, Practise, Track, More), a drawn line icon per item that follows the theme and the open page | The eye finds a page by shape before it reads the word; grouping halves the scan |
| Today: four bordered tiles, a thin bar, then equal cards for every action | A hero (greeting + a progress ring), one stat strip, one "Up next" card with a tinted ground and a 34 px Start, the rest as a compact list | One number and one action per glance; the day's first thing is unmistakable |
| Roadmap: seventeen identical bordered cards | A timeline: a rail with a ticked node, an accent node for "you are here", numbered nodes ahead; each row title, aim, meta, a short bar and its counts on one line | The shape of the whole plan is visible before a word is read |
| Checked items and settings actions as quiet text | Bordered secondary buttons wherever a control acts | An action must look pressable in both themes |
| Theme switch re-polished every widget ever built (3.8 s; 82 s for the text-size spinner) | Pages off screen give up their widgets first; 0.4 s, 0.1 s after | Qt polishes every live widget at ~1 ms; the sheet never sees what is not on screen |
| A long status message widened the window | `ElidedLabel`: ellipsis on screen, whole text in the tooltip | A message must never move the layout |
| Content wider than the page was cut off | The page scrolls sideways when it must | Only at 1.6x text in a 1024 px window; nothing is lost |
| A dashed ring appeared on whatever Qt focused, including after a click | Keyboard-only rings, solid, consumed by the change they mark | Qt has no `:focus-visible`; a ring after a mouse press reads as damage |
| The checked box drew Qt's stock `standardbutton-apply-16.png` | The app's own tick, in `on_accent`, over the `done` fill | A stock bitmap ignores the theme and covered the box whole |
| A folded group said only "4 more to study" | The same line with an OPTIONAL pill | What is folded is the optional half of the group, and a three-word caption is a weak place to say so |
| The setup wizard was four bare form steps | Progress segments, scrolled steps, and selectable cards that take the accent tint | It is the first thing a learner sees, and it looked like a form |
| Every failing check said "Wrong result." | Expected against got, and one sentence saying why | The grader's whole job is telling you what went wrong |

Second-pass sources: Rauno Freiberg's *Web Interface Guidelines* (no dead
zones between list items; decorative layers must not take pointer events;
toggles take effect immediately) and Linear's and Raycast's shipped
interfaces for the sidebar grammar - a mark, captioned groups, icon + label
rows with a single tonal active state.
