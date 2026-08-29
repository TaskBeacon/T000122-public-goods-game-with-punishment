Use case: infographic-diagram
Asset type: TaskBeacon task flow diagram
Primary request: Create a clean, publication-ready task flow diagram as a timeline collection for the behavioral task described below.

Task: Public Goods Game with Punishment
Construct: cooperation / costly punishment
Rows/conditions:
- Chat conditions — peer message and F/J/K reply; includes variable or all-or-nothing contribution and visible or hidden peer-summary variants.
- Silent conditions — 2 s no-communication notice; includes variable or all-or-nothing contribution and visible or hidden peer-summary variants.

Timeline phases:
- Chat conditions: Group chat (45 s response; peer asks for at least 15 coins; F/J/K reply choices) -> Contribution (45 s response; 20-coin endowment; variable 0/5/10/15/20 or all-or-nothing 0/20) -> Pool outcome (3 s; four contributions, total × 1.6, equal share) -> Punishment (target within 45 s, then amount within 45 s if a target is chosen; F/J/K target or SPACE none; 1–3 units, each costs 1 and removes 3) -> Round summary (45 s response; own payoff and welfare; peer details visible or hidden) -> Fixation (0.5 s; +)
- Silent conditions: No communication (2 s; notice that chat is unavailable) -> Contribution (45 s response; 20-coin endowment; variable 0/5/10/15/20 or all-or-nothing 0/20) -> Pool outcome (3 s; four contributions, total × 1.6, equal share) -> Punishment (target within 45 s, then amount within 45 s if a target is chosen; F/J/K target or SPACE none; 1–3 units, each costs 1 and removes 3) -> Round summary (45 s response; own payoff and welfare; peer details visible or hidden) -> Fixation (0.5 s; +)

Visual requirements:
- White background, landscape orientation, crisp dark text, restrained condition accent colors.
- One horizontal row per condition or representative trial type.
- Each row contains 3-7 participant-screen snapshots connected by a subtle arrow.
- Each screen snapshot shows the visible stimulus or feedback, not internal variable names.
- Use gray participant-screen boxes, thin black arrows, consistent row spacing, and subtle row separators.
- Place timing labels under each screen in compact text.
- Place condition labels at the left of each row.
- Use short labels only; avoid paragraphs inside the image.
- Make all text legible at normal document preview size.
- Leave a clean blank header band across the top 15-18% of the image. This band is reserved for a fixed title, `Construct: ...` subtitle, and TaskBeacon logo lockup that will be added after generation.
- Collapse equivalent conditions into representative rows and show variants as small parenthetical notes in the row label.
- Use exactly six screen snapshots per row: communication, contribution, pool outcome, punishment, summary, fixation.
- Keep each snapshot the same size and align both rows to the same six-column grid.

Accuracy constraints:
- Do not invent phases, stimuli, condition names, keys, rewards, or timings.
- Do not add people, lab equipment, decorative scenes, logos, or unrelated icons.
- Do not draw the task title, construct subtitle, any logo, watermark, brand mark, or `TaskBeacon` text inside the generated image.
- Draw only the timeline content below the blank header band.
- If a detail is unknown, omit it rather than guessing.
- Preserve these exact terms where used: Chat conditions, Silent conditions, Group chat, No communication, Contribution, Pool outcome, Punishment, Round summary, Fixation, 45 s, 3 s, 2 s, 0.5 s, 20 coins, × 1.6, F/J/K, SPACE, 0/5/10/15/20, 0/20, visible or hidden, costs 1, removes 3.

Style:
TaskBeacon scientific infographic style: clean vector-like raster image, organized spacing, gray screen boxes, restrained color accents, and a blank header-safe area.

Revision request (round 2):
Keep the same task and overall timeline-collection structure.
Fix only these issues:
1. Make the entire canvas, including the blank header band and margins, pure white with no dark vignette, glow, or gradient.
2. In each Round summary screen, remove invented example numbers such as 28 and 96. Show only short participant-facing labels such as `Your payoff`, `Group welfare`, and `Peers: visible or hidden`, with no made-up values.
3. In each Pool outcome roster, use the task's peer names `Fox`, `Owl`, and `Bear` plus `You`; do not use F/J/K as member names. F/J/K remain valid only as response keys in the punishment screen.
Do not add new conditions, phases, stimuli, people, devices, logos, or decorative scenery.
Leave a clean blank top header band; the fixed title, `Construct: ...` subtitle, and TaskBeacon logo lockup will be added after generation.
Preserve the exact condition labels and timing labels from the prompt.
