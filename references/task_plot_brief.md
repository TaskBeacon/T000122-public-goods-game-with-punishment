# Task Plot Brief

## Evidence basis

- Canonical task: `T000122-public-goods-game-with-punishment`
- Runtime sequence: `src/run_trial.py`
- Parameters and participant-facing copy: `config/config.yaml`
- Task summary: `README.md`

## Construct and design

- Task: Public Goods Game with Punishment
- Construct: cooperation / costly punishment
- Design: 2 × 2 × 2 crossing of communication (chat / silent), contribution rule (variable / all-or-nothing), and peer-summary visibility (visible / hidden).
- The eight cells share the same post-contribution sequence, so the figure should collapse them into two representative rows keyed by communication. Contribution-rule and summary-visibility variants must appear as compact notes inside the relevant screen snapshots.

## Representative rows

1. **Chat conditions** — peer proposes contributing at least 15 coins; participant replies with F/J/K. Contribution can be variable (`1–5` → `0/5/10/15/20`) or all-or-nothing (`F/J` → `0/20`).
2. **Silent conditions** — a 2 s notice states that communication is unavailable. The same contribution-rule and peer-summary-visibility variants apply.

## Shared round sequence

1. Communication screen: chat reply within 45 s, or silent notice for 2 s.
2. Contribution screen: choose contribution within 45 s from a 20-coin endowment.
3. Pool outcome: show all four contributions, multiply total by 1.6, divide equally among four members; 3 s.
4. Punishment target: choose one peer with F/J/K or choose no punishment with Space; within 45 s.
5. Punishment amount, only after choosing a target: choose 1–3 units or cancel with Space; within 45 s. Each unit costs the participant 1 coin and removes 3 coins from the target.
6. Summary: show own contribution, pool share, punishment cost, round payoff, balance, and group welfare; within 45 s. Peer details are either visible or hidden by condition.
7. Inter-round interval: fixation cross for 0.5 s.

## Visual guardrails

- Landscape scientific workflow, white background, blank top header band.
- Two horizontal representative rows with six participant-screen snapshots each; combine the conditional target/amount decision into one compact punishment snapshot and show the 0.5 s fixation as a small terminal tile.
- No human figures, laboratory equipment, decorative scenes, generated title, logo, watermark, or invented rewards.
- Keep screen content short and participant-facing. All timing labels must be below their corresponding screens.
- Show the factor note `Contribution: variable or 0/20` at the contribution snapshot and `Peer summary: visible or hidden` at the summary snapshot so all eight cells are represented without eight cramped rows.

