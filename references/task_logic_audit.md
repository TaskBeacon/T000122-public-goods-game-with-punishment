# Task Logic Audit

This audit was extracted from the cited papers and the public Alsobay et al. OSF configuration/source bundle before task code was written.

## 1. Paradigm Intent

- Task: Public Goods Game with Punishment.
- Primary construct: cooperation in a social dilemma and costly peer punishment.
- Manipulated factors: communication availability (`chat`), visibility of peer round summaries (`showOtherSummaries`), and contribution rule (`allOrNothing`).
- Held constant in the TaskBeacon profile: four-person group, 20-coin endowment, pool multiplier 1.6, punishment enabled, punishment cost 1, target deduction 3, reward disabled.
- Dependent measures: contribution amount/proportion, whether and whom the participant punishes, punishment units/cost, round payoff, cumulative balance, group welfare, and phase-level response times.
- Key citations: `ALSOBAY2026` primary; `FEHR2000` and `FEHR2002` for the standard four-person linear game and 1:3 punishment technology.

## 2. Block/Trial Workflow

### Block Structure

- Total blocks: 8 in the human profile; one block for each `communication × visibility × contribution rule` combination.
- Trials per block: 2 rounds (16 main rounds total). QA and simulation use one round per block while retaining all eight combinations.
- Randomization/counterbalancing: the eight condition profiles are deterministically rotated from a subject-ID-derived seed. Peer contribution vectors are preplanned and rotated by block and round so all decisions are reproducible.
- Condition weight policy: `task.condition_weights` is `null`; conditions are not sampled by weight because each factorial cell must appear exactly once as a block.
- Condition generation method: custom `make_session_plan(...)` in `src/utils.py`.
  - Simple labels cannot represent the required cross-trial block membership, within-block round number, and preplanned peer contribution vector.
  - Each dict passed to `run_trial()` contains `condition_id`, `communication`, `peer_summary_visible`, `contribution_rule`, `round_in_block`, `peer_names`, and `peer_contributions`.
- Runtime-generated trial values: no experimental factor is randomly chosen inside `run_trial.py`. Participant-dependent payoffs and punishment effects are calculated after responses using pure functions in `src/utils.py`.

### Trial State Machine

1. `communication` or `no_communication`
   - Onset trigger: `communication_onset` / `no_communication_onset`.
   - Stimuli shown: when chat is enabled, a peer message and three preset participant reply options; otherwise a notice that chat is unavailable.
   - Valid keys: `f/j/k` for chat; none for no-chat notice.
   - Timeout behavior: no participant message is recorded.
   - Next state: contribution.
2. `contribution`
   - Onset trigger: `contribution_variable_onset` or `contribution_binary_onset`.
   - Stimuli shown: 20-coin endowment, multiplier 1.6, equal division rule, and concrete contribution choices.
   - Valid keys: `1/2/3/4/5` for 0/5/10/15/20 in variable blocks; `f/j` for 0/20 in all-or-nothing blocks.
   - Timeout behavior: default contribution is 0, matching the opt-in default profile.
   - Next state: pool outcome.
3. `pool_outcome`
   - Onset trigger: `pool_outcome_onset`.
   - Stimuli shown: named member contributions, total pot, multiplied return, and equal group share.
   - Valid keys: none.
   - Timeout behavior: fixed display expires.
   - Next state: punishment target.
4. `punishment_target`
   - Onset trigger: `punishment_target_onset`.
   - Stimuli shown: three peers and their contributions, sanction cost/impact rule, and no-punishment option.
   - Valid keys: `f/j/k` for the three peers, `space` for none.
   - Timeout behavior: no punishment.
   - Next state: punishment amount if a peer was selected, otherwise summary.
5. `punishment_amount` (conditional)
   - Onset trigger: `punishment_amount_onset`.
   - Stimuli shown: selected peer and concrete 1/2/3-unit cost and deduction choices.
   - Valid keys: `1/2/3`, `space` to cancel.
   - Timeout behavior: zero units.
   - Next state: summary.
6. `summary`
   - Onset trigger: `summary_visible_onset` or `summary_hidden_onset`.
   - Stimuli shown: own contribution, pool share, sanction cost, round payoff, cumulative balance, and group welfare. Visible blocks additionally show peer outcomes; hidden blocks state that peer summaries are unavailable.
   - Valid keys: `space`.
   - Timeout behavior: continues after 45 seconds.
   - Next state: inter-round interval.
7. `inter_round_interval`
   - Onset trigger: `iti_onset`.
   - Stimuli shown: fixation cross.
   - Valid keys: none.
   - Timeout behavior: fixed interval expires.
   - Next state: next round or block transition.

## 3. Condition Semantics

Each internal condition combines three participant-visible factors. Static wording and response options live in `config/*.yaml`; labels are formatted into block-introduction and trial stimuli without displaying raw condition tokens.

| Condition ID | Communication | Peer summary | Contribution rule | Participant-facing realization |
|---|---|---|---|---|
| `chat_visible_variable` | available | visible | 0/5/10/15/20 | Chat reply screen, five contribution options, detailed peer summary |
| `chat_visible_binary` | available | visible | 0 or 20 | Chat reply screen, two contribution options, detailed peer summary |
| `chat_hidden_variable` | available | hidden | 0/5/10/15/20 | Chat reply screen, five contribution options, own-only summary |
| `chat_hidden_binary` | available | hidden | 0 or 20 | Chat reply screen, two contribution options, own-only summary |
| `silent_visible_variable` | unavailable | visible | 0/5/10/15/20 | No-chat notice, five contribution options, detailed peer summary |
| `silent_visible_binary` | unavailable | visible | 0 or 20 | No-chat notice, two contribution options, detailed peer summary |
| `silent_hidden_variable` | unavailable | hidden | 0/5/10/15/20 | No-chat notice, five contribution options, own-only summary |
| `silent_hidden_binary` | unavailable | hidden | 0 or 20 | No-chat notice, two contribution options, own-only summary |

- Outcome rule for every condition: `round payoff = 20 − own contribution + round(total contribution × 1.6 / 4) − punishment units × 1`.
- Group welfare subtracts the punisher's cost and the target's deduction from the four players' pre-punishment total.
- Localization: all participant copy and option text is Chinese in YAML with `SimHei`; logic code contains only internal identifiers and numeric formatting.

## 4. Response and Scoring Rules

- Response mapping: config fields `chat_keys`, `variable_contribution_keys`, `binary_contribution_keys`, `punishment_target_keys`, `punishment_amount_keys`, and `continue_key`.
- Missing contribution response: 0 coins (opt-in default); missing chat: no message; missing/cancelled punishment: zero units.
- Correctness logic: there is no objectively correct social choice. The task records valid response, amount, and RT rather than accuracy.
- Reward/penalty updates: equal pool return follows the primary source code; punishment costs and target deductions follow the cited configured technology.
- Running metrics: participant cumulative balance begins at 20, then adds each round payoff; group welfare, contribution total, and punishment cost/deduction are stored per round.

## 5. Stimulus Layout Plan

- Instructions: one centered text region, `pos [0,0]`, height 25–29 px, wrap width 1080 px.
- Block introduction: heading at `y=320`, factor summary in a centered body at `y=30`, continue prompt at `y=-320`; spacing exceeds 80 px.
- Communication: header at `y=320`, peer message card centered near `y=90`, three reply options in one wrapped region near `y=-150`.
- Contribution: header at `y=320`, rule/calculation body at `y=80`, response option row at `y=-210`; separate templates for variable and binary choices.
- Pool outcome: header at `y=330`; aligned four-member roster and calculation in a monospaced-like centered body at `y=40`; no option text.
- Punishment target: header at `y=330`, roster at `y=80`, sanction rule and keys at `y=-230`; peers are ordered consistently as Fox/Owl/Bear.
- Punishment amount: header at `y=300`, selected target at `y=80`, amount options at `y=-120`.
- Summary: header at `y=330`, own outcome block at `y=100`, visibility-dependent peer block at `y=-170`, continue prompt at `y=-340`.
- Readability/overlap checks: all screens use explicit positions, heights, and wrap widths; QA screenshots and the final task-flow diagram are reviewed at 1280×800 and 1024×768.

## 6. Trigger Plan

| Event | Code | Semantics |
|---|---:|---|
| experiment start/end | 1 / 2 | session lifecycle |
| block start/end | 10 / 11 | factorial block lifecycle |
| communication/no communication | 20 / 21 | communication factor realization |
| chat response/timeout | 22 / 23 | preset message choice |
| variable/binary contribution | 30 / 31 | contribution rule realization |
| contribution response/timeout | 32 / 33 | allocation event |
| pool outcome | 40 | public-pool calculation revealed |
| punishment target | 50 | peer sanction screen |
| target selected/none/timeout | 51 / 52 / 53 | sanction targeting event |
| punishment amount | 54 | sanction intensity screen |
| amount response/timeout | 55 / 56 | sanction units event |
| visible/hidden summary | 60 / 61 | outcome visibility manipulation |
| summary continue/timeout | 62 / 63 | summary completion |
| ITI | 70 | inter-round fixation |

## 7. Architecture Decisions (Auditability)

- `main.py`: one mode-aware flow, with instructions followed by eight explicit factorial blocks.
- `utils.py`: yes; only for deterministic session plans, payoff calculation, display formatting, and summary aggregation.
- Custom controller: no.
- Custom condition planning: required to preserve factorial block membership, round indexes, and preplanned peer behavior in each condition dict before `run_trial()`.
- `run_trial.py`: thin orchestration over PsyFlow `StimUnit` phases; no condition generation, timing sampling, manual drawing, persistence, or participant wording.
- Legacy/backward-compatibility branches: none.

## 8. Inference Log

- Decision: use three deterministic simulated peers.
  - Why: the canonical TaskBeacon runtime is single-participant, but the source task is synchronous multiplayer.
  - Rationale: preserves the participant's contribution/punishment decisions and exact payoff structure while making QA and web parity possible.
- Decision: serialize chat and punishment controls into dedicated screens.
  - Why: the source web interface embeds chat concurrently and uses multi-click controls; PsyFlow needs auditable response phases.
  - Rationale: all participant-visible information and payoff semantics remain present.
- Decision: preset chat messages.
  - Why: free text cannot be reliably simulated across QA and web-port gates.
  - Rationale: communication remains available/unavailable as a manipulable information channel and has no hard-coded payoff effect.
- Decision: 8 blocks × 2 rounds, with 8 × 1 for QA/sim.
  - Why: the primary study assigns one configuration between groups and ranges from 1–30 rounds; a standalone demonstration must cover the requested factor manipulations within one session.
  - Rationale: mechanism-complete but shorter than the 360-condition integrative experiment.
- Decision: 5-point variable contribution menu.
  - Why: the source interface permits each integer 0–20, but 21 keyboard options are impractical.
  - Rationale: retains graded allocation and endpoints while using evenly spaced levels.

