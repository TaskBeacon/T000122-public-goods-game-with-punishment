# Parameter Mapping

## Mapping Table

| Parameter ID | Config Path | Implemented Value | Source Paper ID | Evidence (quote/figure/table) | Decision Type | Notes |
|---|---|---|---|---|---|---|
| `group_size` | `task.group_size` | `4` | `FEHR2000` | AER design: groups of `n = 4` | `direct` | Three peers are simulated in the standalone runtime. |
| `endowment` | `task.endowment` | `20` | `ALSOBAY2026` | OSF configuration: `endowment=20` in all learning/validation rows | `direct` | Fresh endowment each round. |
| `pool_multiplier` | `task.pool_multiplier` | `1.6` | `FEHR2002` | 80 contributed units yield 32 per player, implying MPCR 0.4 and group multiplier 1.6 | `direct` | Equal pool share rounded as in the OSF server. |
| `punishment_enabled` | `task.punishment_enabled` | `true` | `ALSOBAY2026` | OSF `punishmentExists` factor | `direct` | Enabled in all TaskBeacon blocks. |
| `punishment_cost` | `task.punishment_cost` | `1` | `FEHR2002` | One punishment point costs one monetary unit | `direct` | Participant can buy 1–3 units. |
| `punishment_impact` | `task.punishment_impact` | `3` | `FEHR2002` | One punishment point reduces target payoff by three units | `direct` | Used in group-welfare calculation. |
| `communication` | `task.factor_profiles.*.communication` | `true/false` | `ALSOBAY2026` | OSF factor `chat` | `direct` | Preset-message interface is an adapted input method. |
| `summary_visibility` | `task.factor_profiles.*.peer_summary_visible` | `true/false` | `ALSOBAY2026` | OSF factor `showOtherSummaries` | `direct` | Contributions are still shown before sanctioning; only post-round peer summaries vary. |
| `contribution_rule` | `task.factor_profiles.*.contribution_rule` | `variable/binary` | `ALSOBAY2026` | OSF factor `allOrNothing` | `direct` | Variable levels are discretized to 0/5/10/15/20. |
| `default_contribution` | `task.default_contribution` | `0` | `ALSOBAY2026` | OSF factor `defaultContribProp=0` (opt-in) | `direct` | Applied on timeout. |
| `stage_deadline` | `timing.*_response_s` | `45 s` | `ALSOBAY2026` | OSF contribution/outcome/summary durations are 45 seconds | `adapted` | Separate serialized response phases each use the source maximum where interaction occurs. |
| `main_rounds` | `task.rounds_per_condition` | `2` | `ALSOBAY2026` | OSF `numRounds` ranges 1–30 | `inferred` | Short factorial demonstration; QA/sim use one. |
| `condition_distribution` | `task.condition_weights` | `null` | `ALSOBAY2026` | Integrative design systematically varies configurations | `adapted` | Every one of the eight selected cells appears exactly once; no weighted sampling. |
| `peer_contributions` | `src.utils.PEER_PROFILES` | rotated `18/10/2`, `20/12/4`, `15/15/5`, `20/5/0` | `ALSOBAY2026` | Other players make independent contribution decisions in the source platform | `inferred` | Deterministic context spanning high/mid/low contributions; not an experimental factor. |
| `chat_input` | `task.chat_messages` | three preset Chinese replies | `ALSOBAY2026` | Source chat permits player messages | `adapted` | Presets enable reproducible keyboard QA; no mechanical payoff effect. |
| `window` | `window.size` | `1280×800 px` | `ALSOBAY2026` | OSF interface walkthrough is a wide desktop layout | `inferred` | Conservative PsychoPy desktop layout. |
| `iti` | `timing.iti_s` | `0.5 s` | `ALSOBAY2026` | No standalone ITI specified | `inferred` | Separates serialized local rounds. |

Decision type values: `direct`, `adapted`, `inferred`.

