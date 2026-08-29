# Task Plot Review

## Review outcome

- Status: **PASS**
- Selected generation: round 2
- Regeneration count: 1 (two total generation rounds; within the user limit of five)
- Final image: `task_flow.png`
- Preserved raw selected timeline: `references/task_plot_timeline_raw.png`
- Preserved rejected draft for audit: `references/task_plot_timeline_raw_v1.png`

## Evidence match

- Task name matches `T000122-public-goods-game-with-punishment`.
- The two representative rows correctly collapse the eight 2 × 2 × 2 factor cells by communication status while retaining contribution-rule and peer-summary variants.
- Phase order matches `src/run_trial.py`: communication → contribution → pool outcome → punishment target/amount → summary → fixation.
- Timing labels match `config/config.yaml`: chat 45 s, no communication 2 s, contribution 45 s, pool outcome 3 s, punishment target plus conditional amount up to 45 s each, summary 45 s, and fixation 0.5 s.
- Participant-facing content is shown. F/J/K are response keys only; the pool roster uses Fox, Owl, Bear, and You.
- Contribution choices, 20-coin endowment, 1.6 multiplier, and punishment cost/impact all match the canonical config.
- The final summary panels do not invent payoff or welfare values.

## Visual quality

- Text is legible at normal preview size; no garbled or misspelled labels were observed.
- Both rows use a consistent six-column grid with clear left-to-right arrows.
- No screen, arrow, condition label, or timing label overlaps another element.
- Screen ratios and visual scale are consistent across rows.
- The background and header-safe area are white, with restrained blue/purple accents.
- The fixed title is centered; the subtitle begins with `Construct:` and separates the two constructs with ` / `.
- The borderless TaskBeacon logo lockup is in the top-right and does not overlap the title or timeline.
- The image generator did not add a title, subtitle, logo, watermark, people, equipment, or decorative scene.

## Iteration record

1. Round 1 had a dark gradient/vignette, invented summary values, and F/J/K shown as member names in the pool roster. It was rejected.
2. Round 2 changed only those issues. The final watermarked image passed evidence, overlap, stimulus, ratio, and scale review.

## README embed

- `README.md` contains `## 2. Task Flow`.
- The first image under that heading is exactly `![Task Flow](task_flow.png)`.
- The image exists at the task root as `task_flow.png`.
