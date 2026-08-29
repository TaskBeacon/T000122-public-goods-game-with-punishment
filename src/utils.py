from __future__ import annotations

from dataclasses import asdict, dataclass
import random
import re
from typing import Any, Iterable, Mapping, Sequence


PEER_PROFILES: tuple[tuple[int, int, int], ...] = (
    (18, 10, 2),
    (20, 12, 4),
    (15, 15, 5),
    (20, 5, 0),
)


@dataclass(frozen=True)
class TrialPlan:
    condition_id: str
    communication: bool
    peer_summary_visible: bool
    contribution_rule: str
    communication_label: str
    visibility_label: str
    contribution_label: str
    round_in_block: int
    peer_names: tuple[str, str, str]
    peer_contributions: tuple[int, int, int]


@dataclass(frozen=True)
class RoundOutcome:
    own_contribution: int
    peer_contributions: tuple[int, int, int]
    total_contribution: int
    multiplied_pool: int
    pool_share: int
    punishment_target_index: int | None
    punishment_units: int
    punishment_cost_total: int
    punishment_target_loss: int
    own_round_payoff: int
    peer_round_payoffs: tuple[int, int, int]
    group_welfare: int


def subject_seed(subject_id: Any, base_seed: int) -> int:
    digits = re.sub(r"\D", "", str(subject_id or ""))
    return int(base_seed) + (int(digits) if digits else 0)


def ordered_conditions(condition_ids: Sequence[str], seed: int) -> list[str]:
    values = [str(value) for value in condition_ids]
    rng = random.Random(int(seed))
    rng.shuffle(values)
    return values


def make_block_plans(
    *,
    condition_id: str,
    profile: Mapping[str, Any],
    block_idx: int,
    rounds: int,
    peer_names: Sequence[str],
    seed: int,
) -> list[TrialPlan]:
    if len(peer_names) != 3:
        raise ValueError("The standalone four-person task requires exactly three peer names")
    plans: list[TrialPlan] = []
    offset = (int(seed) + int(block_idx) * 3) % len(PEER_PROFILES)
    for round_idx in range(int(rounds)):
        contributions = PEER_PROFILES[(offset + round_idx) % len(PEER_PROFILES)]
        plans.append(
            TrialPlan(
                condition_id=str(condition_id),
                communication=bool(profile["communication"]),
                peer_summary_visible=bool(profile["peer_summary_visible"]),
                contribution_rule=str(profile["contribution_rule"]),
                communication_label=str(profile["communication_label"]),
                visibility_label=str(profile["visibility_label"]),
                contribution_label=str(profile["contribution_label"]),
                round_in_block=round_idx + 1,
                peer_names=tuple(str(name) for name in peer_names),
                peer_contributions=tuple(int(value) for value in contributions),
            )
        )
    return plans


def contribution_from_response(
    response: Any,
    *,
    rule: str,
    variable_values: Mapping[str, Any],
    binary_values: Mapping[str, Any],
    default: int,
) -> int:
    mapping = variable_values if str(rule) == "variable" else binary_values
    key = str(response or "")
    return int(mapping.get(key, default))


def punishment_choice(
    target_response: Any,
    amount_response: Any,
    *,
    target_keys: Sequence[str],
    amount_values: Mapping[str, Any],
) -> tuple[int | None, int]:
    target_key = str(target_response or "")
    target_index = list(target_keys).index(target_key) if target_key in target_keys else None
    amount = int(amount_values.get(str(amount_response or ""), 0)) if target_index is not None else 0
    return target_index, max(0, amount)


def compute_round_outcome(
    *,
    own_contribution: int,
    peer_contributions: Sequence[int],
    endowment: int,
    multiplier: float,
    punishment_target_index: int | None,
    punishment_units: int,
    punishment_cost: int,
    punishment_impact: int,
    available_balance: float,
) -> RoundOutcome:
    peers = tuple(int(value) for value in peer_contributions)
    if len(peers) != 3:
        raise ValueError("Expected three peer contributions")
    own = min(int(endowment), max(0, int(own_contribution)))
    total = own + sum(peers)
    multiplied = int(round(total * float(multiplier)))
    share = int(round(multiplied / 4))
    max_affordable = int(max(0.0, float(available_balance)) // max(1, int(punishment_cost)))
    units = min(max(0, int(punishment_units)), max_affordable) if punishment_target_index is not None else 0
    target_index = punishment_target_index if punishment_target_index in (0, 1, 2) and units > 0 else None
    cost_total = units * int(punishment_cost)
    target_loss = units * int(punishment_impact)
    own_payoff = int(endowment) - own + share - cost_total
    peer_payoffs = [int(endowment) - contribution + share for contribution in peers]
    if target_index is not None:
        peer_payoffs[target_index] -= target_loss
    welfare = own_payoff + sum(peer_payoffs)
    return RoundOutcome(
        own_contribution=own,
        peer_contributions=peers,
        total_contribution=total,
        multiplied_pool=multiplied,
        pool_share=share,
        punishment_target_index=target_index,
        punishment_units=units,
        punishment_cost_total=cost_total,
        punishment_target_loss=target_loss,
        own_round_payoff=own_payoff,
        peer_round_payoffs=tuple(peer_payoffs),
        group_welfare=welfare,
    )


def outcome_dict(outcome: RoundOutcome) -> dict[str, Any]:
    return asdict(outcome)


def summarize_rounds(rows: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    scored = [row for row in rows if "own_contribution" in row]
    n = len(scored)
    contributed = sum(int(row.get("own_contribution", 0)) for row in scored)
    punished = sum(int(row.get("punishment_units", 0)) for row in scored)
    welfare = sum(int(row.get("group_welfare", 0)) for row in scored)
    final_balance = float(scored[-1].get("cumulative_balance", 0.0)) if scored else 0.0
    return {
        "rounds": n,
        "mean_contribution": contributed / n if n else 0.0,
        "total_punishment_units": punished,
        "mean_group_welfare": welfare / n if n else 0.0,
        "final_balance": final_balance,
    }
