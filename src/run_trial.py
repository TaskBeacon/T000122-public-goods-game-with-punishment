from __future__ import annotations

from functools import partial
from dataclasses import asdict
from typing import Any, MutableMapping

from psyflow import StimUnit, next_trial_id, set_trial_context

from .utils import (
    compute_round_outcome,
    contribution_from_response,
    outcome_dict,
    punishment_choice,
    TrialPlan,
)


def _response(unit: StimUnit) -> tuple[str, float | None]:
    key = str(unit.get_state("response", "") or "")
    rt = unit.get_state("rt", None)
    return key, float(rt) if isinstance(rt, (int, float)) else None


def run_trial(
    win,
    kb,
    settings,
    condition,
    stim_bank,
    trigger_runtime,
    session_state: MutableMapping[str, Any],
    block_id=None,
    block_idx=None,
):
    """Run one public-goods round using a preplanned condition dictionary."""
    if not isinstance(condition, TrialPlan):
        raise TypeError("Public-goods trials require preplanned TrialPlan conditions")

    plan = asdict(condition)
    trial_id = next_trial_id()
    block_name = str(block_id or "block_0")
    block_index = int(block_idx or 0)
    condition_id = str(plan["condition_id"])
    peer_names = tuple(str(value) for value in plan["peer_names"])
    peer_contributions = tuple(int(value) for value in plan["peer_contributions"])
    make_unit = partial(StimUnit, win=win, kb=kb, runtime=trigger_runtime)
    base_factors = {
        "communication": bool(plan["communication"]),
        "peer_summary_visible": bool(plan["peer_summary_visible"]),
        "contribution_rule": str(plan["contribution_rule"]),
        "round_in_block": int(plan["round_in_block"]),
        "block_idx": block_index,
    }
    trial_data: dict[str, Any] = {
        "trial_id": int(trial_id),
        "block_id": block_name,
        "block_idx": block_index,
        "condition": condition_id,
        "condition_id": condition_id,
        **base_factors,
        "peer_1_name": peer_names[0],
        "peer_2_name": peer_names[1],
        "peer_3_name": peer_names[2],
        "peer_1_contribution": peer_contributions[0],
        "peer_2_contribution": peer_contributions[1],
        "peer_3_contribution": peer_contributions[2],
    }

    if bool(plan["communication"]):
        chat_keys = [str(key) for key in settings.chat_keys]
        communication = make_unit(unit_label="communication")
        communication.add_stim(stim_bank.get("communication_heading"))
        communication.add_stim(
            stim_bank.get_and_format(
                "peer_message",
                speaker=peer_names[0],
                message=str(settings.peer_chat_message),
            )
        )
        communication.add_stim(stim_bank.get("chat_options"))
        set_trial_context(
            communication,
            trial_id=trial_id,
            phase="communication",
            deadline_s=float(settings.communication_response_s),
            valid_keys=chat_keys,
            block_id=block_name,
            condition_id=condition_id,
            task_factors={**base_factors, "stage": "communication"},
            stim_id="peer_message+chat_options",
        )
        communication.capture_response(
            keys=chat_keys,
            duration=float(settings.communication_response_s),
            onset_trigger=settings.triggers.get("communication_onset"),
            response_trigger={key: settings.triggers.get("chat_response") for key in chat_keys},
            timeout_trigger=settings.triggers.get("chat_timeout"),
            terminate_on_response=True,
        ).to_dict(trial_data)
        chat_key, chat_rt = _response(communication)
    else:
        no_chat = make_unit(unit_label="no_communication")
        no_chat.add_stim(stim_bank.get("no_communication_heading"))
        no_chat.add_stim(stim_bank.get("no_chat_notice"))
        set_trial_context(
            no_chat,
            trial_id=trial_id,
            phase="no_communication",
            deadline_s=float(settings.no_communication_s),
            valid_keys=[],
            block_id=block_name,
            condition_id=condition_id,
            task_factors={**base_factors, "stage": "no_communication"},
            stim_id="no_chat_notice",
        )
        no_chat.show(
            duration=float(settings.no_communication_s),
            onset_trigger=settings.triggers.get("no_communication_onset"),
        ).to_dict(trial_data)
        chat_key, chat_rt = "", None

    rule = str(plan["contribution_rule"])
    if rule == "variable":
        contribution_keys = [str(key) for key in settings.variable_contribution_keys]
        rule_stim_id, option_stim_id = "contribution_rule_variable", "variable_options"
        onset_trigger = settings.triggers.get("contribution_variable_onset")
    elif rule == "binary":
        contribution_keys = [str(key) for key in settings.binary_contribution_keys]
        rule_stim_id, option_stim_id = "contribution_rule_binary", "binary_options"
        onset_trigger = settings.triggers.get("contribution_binary_onset")
    else:
        raise ValueError(f"Unsupported contribution rule: {rule}")

    contribution = make_unit(unit_label="contribution")
    contribution.add_stim(stim_bank.get("contribution_heading"))
    contribution.add_stim(
        stim_bank.get_and_format(
            rule_stim_id,
            endowment=int(settings.endowment),
            multiplier=float(settings.pool_multiplier),
            group_size=int(settings.group_size),
        )
    )
    contribution.add_stim(stim_bank.get(option_stim_id))
    set_trial_context(
        contribution,
        trial_id=trial_id,
        phase="contribution",
        deadline_s=float(settings.contribution_response_s),
        valid_keys=contribution_keys,
        block_id=block_name,
        condition_id=condition_id,
        task_factors={**base_factors, "stage": "contribution"},
        stim_id=f"{rule_stim_id}+{option_stim_id}",
    )
    contribution.capture_response(
        keys=contribution_keys,
        duration=float(settings.contribution_response_s),
        onset_trigger=onset_trigger,
        response_trigger={key: settings.triggers.get("contribution_response") for key in contribution_keys},
        timeout_trigger=settings.triggers.get("contribution_timeout"),
        terminate_on_response=True,
    ).to_dict(trial_data)
    contribution_key, contribution_rt = _response(contribution)
    own_contribution = contribution_from_response(
        contribution_key,
        rule=rule,
        variable_values=dict(settings.variable_contribution_values),
        binary_values=dict(settings.binary_contribution_values),
        default=int(settings.default_contribution),
    )

    preliminary = compute_round_outcome(
        own_contribution=own_contribution,
        peer_contributions=peer_contributions,
        endowment=int(settings.endowment),
        multiplier=float(settings.pool_multiplier),
        punishment_target_index=None,
        punishment_units=0,
        punishment_cost=int(settings.punishment_cost),
        punishment_impact=int(settings.punishment_impact),
        available_balance=float(session_state["balance"]),
    )
    pool_outcome = make_unit(unit_label="pool_outcome")
    pool_outcome.add_stim(stim_bank.get("pool_outcome_heading"))
    pool_outcome.add_stim(
        stim_bank.get_and_format(
            "pool_roster",
            own=own_contribution,
            peer1_name=peer_names[0],
            peer1=peer_contributions[0],
            peer2_name=peer_names[1],
            peer2=peer_contributions[1],
            peer3_name=peer_names[2],
            peer3=peer_contributions[2],
        )
    )
    pool_outcome.add_stim(
        stim_bank.get_and_format(
            "pool_calculation",
            total=preliminary.total_contribution,
            multiplier=float(settings.pool_multiplier),
            multiplied=preliminary.multiplied_pool,
            group_size=int(settings.group_size),
            share=preliminary.pool_share,
        )
    )
    set_trial_context(
        pool_outcome,
        trial_id=trial_id,
        phase="pool_outcome",
        deadline_s=float(settings.pool_outcome_s),
        valid_keys=[],
        block_id=block_name,
        condition_id=condition_id,
        task_factors={**base_factors, "stage": "pool_outcome", "pool_share": preliminary.pool_share},
        stim_id="pool_roster+pool_calculation",
    )
    pool_outcome.show(
        duration=float(settings.pool_outcome_s),
        onset_trigger=settings.triggers.get("pool_outcome_onset"),
    ).to_dict(trial_data)

    target_keys = [str(key) for key in settings.punishment_target_keys]
    none_key = str(settings.no_punishment_key)
    target_unit = make_unit(unit_label="punishment_target")
    target_unit.add_stim(stim_bank.get("punishment_heading"))
    target_unit.add_stim(
        stim_bank.get_and_format(
            "punishment_roster",
            key1=target_keys[0].upper(),
            peer1_name=peer_names[0],
            peer1=peer_contributions[0],
            key2=target_keys[1].upper(),
            peer2_name=peer_names[1],
            peer2=peer_contributions[1],
            key3=target_keys[2].upper(),
            peer3_name=peer_names[2],
            peer3=peer_contributions[2],
        )
    )
    target_unit.add_stim(
        stim_bank.get_and_format(
            "punishment_rule",
            cost=int(settings.punishment_cost),
            impact=int(settings.punishment_impact),
        )
    )
    set_trial_context(
        target_unit,
        trial_id=trial_id,
        phase="punishment_target",
        deadline_s=float(settings.punishment_target_response_s),
        valid_keys=[*target_keys, none_key],
        block_id=block_name,
        condition_id=condition_id,
        task_factors={
            **base_factors,
            "stage": "punishment_target",
            "peer_contributions": list(peer_contributions),
        },
        stim_id="punishment_roster+punishment_rule",
    )
    target_unit.capture_response(
        keys=[*target_keys, none_key],
        duration=float(settings.punishment_target_response_s),
        onset_trigger=settings.triggers.get("punishment_target_onset"),
        response_trigger={
            **{key: settings.triggers.get("punishment_target_selected") for key in target_keys},
            none_key: settings.triggers.get("no_punishment_selected"),
        },
        timeout_trigger=settings.triggers.get("punishment_target_timeout"),
        terminate_on_response=True,
    ).to_dict(trial_data)
    target_key, target_rt = _response(target_unit)
    target_index = target_keys.index(target_key) if target_key in target_keys else None

    amount_key, amount_rt = "", None
    if target_index is not None:
        amount_keys = [str(key) for key in settings.punishment_amount_keys]
        amount_unit = make_unit(unit_label="punishment_amount")
        amount_unit.add_stim(stim_bank.get("punishment_amount_heading"))
        amount_unit.add_stim(
            stim_bank.get_and_format("selected_target", target_name=peer_names[target_index])
        )
        amount_unit.add_stim(
            stim_bank.get_and_format(
                "punishment_amount_options",
                cost=int(settings.punishment_cost),
                impact=int(settings.punishment_impact),
            )
        )
        set_trial_context(
            amount_unit,
            trial_id=trial_id,
            phase="punishment_amount",
            deadline_s=float(settings.punishment_amount_response_s),
            valid_keys=[*amount_keys, none_key],
            block_id=block_name,
            condition_id=condition_id,
            task_factors={
                **base_factors,
                "stage": "punishment_amount",
                "punishment_target_index": target_index,
            },
            stim_id="selected_target+punishment_amount_options",
        )
        amount_unit.capture_response(
            keys=[*amount_keys, none_key],
            duration=float(settings.punishment_amount_response_s),
            onset_trigger=settings.triggers.get("punishment_amount_onset"),
            response_trigger={key: settings.triggers.get("punishment_amount_response") for key in amount_keys},
            timeout_trigger=settings.triggers.get("punishment_amount_timeout"),
            terminate_on_response=True,
        ).to_dict(trial_data)
        amount_key, amount_rt = _response(amount_unit)

    target_index, punishment_units = punishment_choice(
        target_key,
        amount_key,
        target_keys=target_keys,
        amount_values=dict(settings.punishment_amount_values),
    )
    outcome = compute_round_outcome(
        own_contribution=own_contribution,
        peer_contributions=peer_contributions,
        endowment=int(settings.endowment),
        multiplier=float(settings.pool_multiplier),
        punishment_target_index=target_index,
        punishment_units=punishment_units,
        punishment_cost=int(settings.punishment_cost),
        punishment_impact=int(settings.punishment_impact),
        available_balance=float(session_state["balance"]),
    )
    session_state["balance"] = float(session_state["balance"]) + outcome.own_round_payoff
    target_losses = [0, 0, 0]
    if outcome.punishment_target_index is not None:
        target_losses[outcome.punishment_target_index] = outcome.punishment_target_loss

    summary = make_unit(unit_label="summary")
    summary.add_stim(stim_bank.get("summary_heading"))
    summary.add_stim(
        stim_bank.get_and_format(
            "summary_own",
            contribution=outcome.own_contribution,
            pool_share=outcome.pool_share,
            punishment_cost=outcome.punishment_cost_total,
            round_payoff=outcome.own_round_payoff,
            balance=float(session_state["balance"]),
            welfare=outcome.group_welfare,
        )
    )
    if bool(plan["peer_summary_visible"]):
        summary.add_stim(
            stim_bank.get_and_format(
                "summary_peer_visible",
                peer1_name=peer_names[0],
                peer1_contribution=peer_contributions[0],
                peer1_payoff=outcome.peer_round_payoffs[0],
                peer1_loss=target_losses[0],
                peer2_name=peer_names[1],
                peer2_contribution=peer_contributions[1],
                peer2_payoff=outcome.peer_round_payoffs[1],
                peer2_loss=target_losses[1],
                peer3_name=peer_names[2],
                peer3_contribution=peer_contributions[2],
                peer3_payoff=outcome.peer_round_payoffs[2],
                peer3_loss=target_losses[2],
            )
        )
        summary_trigger = settings.triggers.get("summary_visible_onset")
        summary_stim_id = "summary_own+summary_peer_visible"
    else:
        summary.add_stim(stim_bank.get("summary_peer_hidden"))
        summary_trigger = settings.triggers.get("summary_hidden_onset")
        summary_stim_id = "summary_own+summary_peer_hidden"
    summary.add_stim(stim_bank.get("continue_prompt"))
    continue_key = str(settings.continue_key)
    set_trial_context(
        summary,
        trial_id=trial_id,
        phase="summary",
        deadline_s=float(settings.summary_response_s),
        valid_keys=[continue_key],
        block_id=block_name,
        condition_id=condition_id,
        task_factors={
            **base_factors,
            "stage": "summary",
            "own_round_payoff": outcome.own_round_payoff,
            "group_welfare": outcome.group_welfare,
        },
        stim_id=summary_stim_id,
    )
    summary.capture_response(
        keys=[continue_key],
        duration=float(settings.summary_response_s),
        onset_trigger=summary_trigger,
        response_trigger={continue_key: settings.triggers.get("summary_continue")},
        timeout_trigger=settings.triggers.get("summary_timeout"),
        terminate_on_response=True,
    ).to_dict(trial_data)
    summary_key, summary_rt = _response(summary)

    iti = make_unit(unit_label="inter_round_interval").add_stim(stim_bank.get("fixation"))
    set_trial_context(
        iti,
        trial_id=trial_id,
        phase="inter_round_interval",
        deadline_s=float(settings.iti_s),
        valid_keys=[],
        block_id=block_name,
        condition_id=condition_id,
        task_factors={**base_factors, "stage": "inter_round_interval"},
        stim_id="fixation",
    )
    iti.show(duration=float(settings.iti_s), onset_trigger=settings.triggers.get("iti_onset")).to_dict(
        trial_data
    )

    trial_data.update(outcome_dict(outcome))
    trial_data.update(
        {
            "chat_response_key": chat_key,
            "chat_response_rt": chat_rt,
            "chat_message": str(dict(settings.chat_response_labels).get(chat_key, "")),
            "contribution_response_key": contribution_key,
            "contribution_response_rt": contribution_rt,
            "punishment_target_response_key": target_key,
            "punishment_target_response_rt": target_rt,
            "punishment_target_name": peer_names[target_index] if target_index is not None else "",
            "punishment_amount_response_key": amount_key,
            "punishment_amount_response_rt": amount_rt,
            "summary_response_key": summary_key,
            "summary_response_rt": summary_rt,
            "cumulative_balance": float(session_state["balance"]),
        }
    )
    return trial_data
