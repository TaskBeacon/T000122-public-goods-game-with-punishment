# Extracted Primary Protocol

## Source bundle

- Paper: Alsobay et al. (2026), *Science*, DOI `10.1126/science.aeb5280`.
- Public reproducibility package: `https://osf.io/2d56w`.
- Exact protocol evidence inspected: `data/exp_config_files/{learning,validation}.{csv,yaml}`, `code/pgg_empirica/server/callbacks.js`, `client/game/{Contribution,Outcome,Summary,Chat}.jsx`, and the 17-image PGG interface walkthrough.

## Primary study design

The study crossed public-goods-game parameters across 360 configurations and paired punishment-enabled games with otherwise matched controls. The released configuration schema varies group size, game length, whether game length is disclosed, pool multiplier, variable versus all-or-nothing contributions, chat availability, contribution default, punishment availability/cost/magnitude, reward availability/cost/magnitude, visibility of other-player summaries, and identity visibility for received punishment/reward. All released configurations use a 20-coin round endowment. Contribution, outcome, and summary stages each allow up to 45 seconds.

## Exact round state machine in the released platform

1. `contribution`: Each player allocates from a 20-coin endowment. Variable games permit any amount up to the endowment; all-or-nothing games permit zero or the full endowment. The on-screen copy states that the pot is multiplied and divided equally among the group.
2. `outcome`: The platform reveals own contribution, others' aggregate contribution, total contribution, multiplied return, and equal per-player pool payoff. When punishment is enabled, the participant can purchase deduction units for other players. Each unit costs `punishmentCost` to the punisher and removes `punishmentMagnitude` from the target. Spending cannot exceed the participant's current cumulative balance.
3. `summary`: The participant sees own contribution, round gains/losses, punishment spent, and punishment received. `showOtherSummaries` controls whether corresponding peer details are visible. `showPunishmentId` controls whether the source of received punishment is visible.

The server computes equal pool share as `round(total contributions × multiplier / active players)`. Individual round payoff is private remainder plus equal pool share plus received rewards, minus punishment received and the costs of punishment/reward assigned.

## Standalone TaskBeacon adaptation

The published task is a synchronous multiplayer Empirica experiment, whereas a PsyFlow task runs one local participant. This port therefore presents three deterministic, seed-controlled simulated group members. Their preplanned contributions and punishment decisions are data-generating context, not an additional experimental factor. The participant still makes genuine contribution and costly-punishment decisions and receives the cited payoff calculation.

Eight blocks cross the three requested manipulable factors: chat available versus unavailable, peer summary visible versus hidden, and variable versus all-or-nothing contribution. Punishment is enabled in every block. To preserve the standard four-person linear public-goods benchmark, the default group has four members, a 20-coin endowment, multiplier 1.6 (marginal per-capita return 0.4), punishment cost 1, and target loss 3. Communication is implemented as a choice among neutral preset group messages because free text cannot be reliably driven by the task's automated QA/simulation responders. Chat has no mechanical effect on payoffs or simulated peer actions.

The released interface keeps chat concurrent with the main stages and combines pool feedback with sanction controls. The standalone port serializes these elements into `communication/no_communication → contribution → pool_outcome → punishment_target → punishment_amount → summary → inter_round_interval` so that each interaction has an auditable response event. This serialization preserves participant-visible information and payoff semantics while adapting the synchronous interface to PsychoPy.
