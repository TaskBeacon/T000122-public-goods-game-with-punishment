from src.utils import (
    PEER_PROFILES,
    compute_round_outcome,
    contribution_from_response,
    make_block_plans,
    ordered_conditions,
    punishment_choice,
    summarize_rounds,
)


def test_all_condition_ids_are_deterministically_preserved():
    conditions = [f"condition_{idx}" for idx in range(8)]
    assert sorted(ordered_conditions(conditions, 122)) == conditions
    assert ordered_conditions(conditions, 122) == ordered_conditions(conditions, 122)


def test_block_plan_contains_factors_and_three_peers():
    profile = {
        "communication": True,
        "peer_summary_visible": False,
        "contribution_rule": "variable",
        "communication_label": "chat",
        "visibility_label": "hidden",
        "contribution_label": "graded",
    }
    plans = make_block_plans(
        condition_id="cell",
        profile=profile,
        block_idx=2,
        rounds=2,
        peer_names=["A", "B", "C"],
        seed=122,
    )
    assert len(plans) == 2
    assert all(len(plan.peer_contributions) == 3 for plan in plans)
    assert all(tuple(plan.peer_contributions) in PEER_PROFILES for plan in plans)
    assert plans[0].round_in_block == 1


def test_contribution_mappings_cover_variable_binary_and_timeout():
    variable = {"1": 0, "2": 5, "3": 10, "4": 15, "5": 20}
    binary = {"f": 0, "j": 20}
    assert contribution_from_response("4", rule="variable", variable_values=variable, binary_values=binary, default=0) == 15
    assert contribution_from_response("j", rule="binary", variable_values=variable, binary_values=binary, default=0) == 20
    assert contribution_from_response(None, rule="variable", variable_values=variable, binary_values=binary, default=0) == 0


def test_payoff_and_welfare_apply_public_share_and_punishment():
    outcome = compute_round_outcome(
        own_contribution=10,
        peer_contributions=[20, 10, 0],
        endowment=20,
        multiplier=1.6,
        punishment_target_index=2,
        punishment_units=2,
        punishment_cost=1,
        punishment_impact=3,
        available_balance=20,
    )
    assert outcome.total_contribution == 40
    assert outcome.multiplied_pool == 64
    assert outcome.pool_share == 16
    assert outcome.own_round_payoff == 24
    assert outcome.peer_round_payoffs == (16, 26, 30)
    assert outcome.group_welfare == 96


def test_punishment_choice_and_affordability():
    target, units = punishment_choice("k", "3", target_keys=["f", "j", "k"], amount_values={"1": 1, "2": 2, "3": 3})
    assert (target, units) == (2, 3)
    outcome = compute_round_outcome(
        own_contribution=0,
        peer_contributions=[0, 0, 0],
        endowment=20,
        multiplier=1.6,
        punishment_target_index=target,
        punishment_units=units,
        punishment_cost=1,
        punishment_impact=3,
        available_balance=1,
    )
    assert outcome.punishment_units == 1
    assert outcome.punishment_target_loss == 3


def test_summary_metrics():
    summary = summarize_rounds(
        [
            {"own_contribution": 10, "punishment_units": 2, "group_welfare": 100, "cumulative_balance": 44},
            {"own_contribution": 20, "punishment_units": 0, "group_welfare": 120, "cumulative_balance": 70},
        ]
    )
    assert summary == {
        "rounds": 2,
        "mean_contribution": 15.0,
        "total_punishment_units": 2,
        "mean_group_welfare": 110.0,
        "final_balance": 70.0,
    }
