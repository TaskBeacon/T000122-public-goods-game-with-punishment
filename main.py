from __future__ import annotations

from contextlib import nullcontext
from functools import partial
from pathlib import Path

import pandas as pd
from psychopy import core
from psyflow import (
    BlockUnit,
    StimBank,
    StimUnit,
    SubInfo,
    TaskRunOptions,
    TaskSettings,
    context_from_config,
    initialize_exp,
    initialize_triggers,
    load_config,
    parse_task_run_options,
    runtime_context,
)

from src import make_block_plans, ordered_conditions, run_trial, subject_seed, summarize_rounds


MODES = ("human", "qa", "sim")
DEFAULT_CONFIG_BY_MODE = {
    "human": "config/config.yaml",
    "qa": "config/config_qa.yaml",
    "sim": "config/config_scripted_sim.yaml",
}


def _continue_screen(bank, stim_id, win, kb, triggers, continue_key):
    StimUnit(stim_id, win, kb, runtime=triggers).add_stim(bank.get(stim_id)).wait_and_continue(
        keys=[continue_key]
    )


def run(options: TaskRunOptions) -> None:
    task_root = Path(__file__).resolve().parent
    config = load_config(str(options.config_path))
    output_dir, scope, context = None, nullcontext(), None
    if options.mode in ("qa", "sim"):
        context = context_from_config(task_dir=task_root, config=config, mode=options.mode)
        output_dir, scope = context.output_dir, runtime_context(context)

    with scope:
        if options.mode == "qa":
            subject_data = {"subject_id": "qa122"}
        elif options.mode == "sim":
            subject_data = {"subject_id": str(context.session.participant_id or "sim122")}
        else:
            subject_data = SubInfo(config["subform_config"]).collect()

        settings = TaskSettings.from_dict(config["task_config"])
        settings.add_subinfo(subject_data)
        if output_dir is not None:
            output_dir.mkdir(parents=True, exist_ok=True)
            settings.save_path = str(output_dir)
            prefix = "qa" if options.mode == "qa" else "sim"
            settings.res_file = str(output_dir / f"{prefix}_trace.csv")
            settings.log_file = str(output_dir / f"{prefix}_psychopy.log")
            settings.json_file = str(output_dir / f"{prefix}_settings.json")

        settings.triggers = config["trigger_config"]
        triggers = (
            initialize_triggers(mock=True)
            if options.mode in ("qa", "sim")
            else initialize_triggers(config)
        )
        win, kb = initialize_exp(settings)
        bank = StimBank(win, config["stim_config"]).preload_all()
        settings.save_to_json()
        continue_key = str(settings.continue_key)

        triggers.send(settings.triggers.get("experiment_start"))
        _continue_screen(bank, "instruction_overview", win, kb, triggers, continue_key)
        _continue_screen(bank, "instruction_punishment", win, kb, triggers, continue_key)
        _continue_screen(bank, "instruction_factors", win, kb, triggers, continue_key)

        seed = subject_seed(subject_data.get("subject_id"), int(settings.overall_seed))
        condition_ids = ordered_conditions(list(settings.conditions), seed)
        rows: list[dict] = []
        session_state = {"balance": float(settings.starting_balance)}
        profiles = dict(settings.factor_profiles)
        for block_idx, condition_id in enumerate(condition_ids):
            profile = dict(profiles[condition_id])
            intro = StimUnit("block_intro", win, kb, runtime=triggers)
            intro.add_stim(
                bank.get_and_format(
                    "block_heading",
                    block_num=block_idx + 1,
                    total_blocks=len(condition_ids),
                )
            )
            intro.add_stim(
                bank.get_and_format(
                    "block_factors",
                    communication=profile["communication_label"],
                    visibility=profile["visibility_label"],
                    contribution=profile["contribution_label"],
                    rounds=int(settings.rounds_per_condition),
                )
            )
            intro.add_stim(bank.get("continue_prompt"))
            intro.wait_and_continue(keys=[continue_key])

            plans = make_block_plans(
                condition_id=condition_id,
                profile=profile,
                block_idx=block_idx,
                rounds=int(settings.rounds_per_condition),
                peer_names=list(settings.peer_names),
                seed=seed,
            )
            (
                BlockUnit(
                    block_id=f"factor_block_{block_idx + 1}",
                    block_idx=block_idx,
                    settings=settings,
                    window=win,
                    keyboard=kb,
                    seed=seed + block_idx,
                )
                .add_condition(plans)
                .on_start(lambda _: triggers.send(settings.triggers.get("block_start")))
                .on_end(lambda _: triggers.send(settings.triggers.get("block_end")))
                .run_trial(
                    partial(
                        run_trial,
                        stim_bank=bank,
                        trigger_runtime=triggers,
                        session_state=session_state,
                        block_id=f"factor_block_{block_idx + 1}",
                        block_idx=block_idx,
                    )
                )
                .to_dict(rows)
            )

            if block_idx < len(condition_ids) - 1:
                StimUnit("block_break", win, kb, runtime=triggers).add_stim(
                    bank.get_and_format(
                        "block_break",
                        completed=block_idx + 1,
                        total=len(condition_ids),
                        balance=float(session_state["balance"]),
                    )
                ).wait_and_continue(keys=[continue_key])

        summary = summarize_rounds(rows)
        StimUnit("final_summary", win, kb, runtime=triggers).add_stim(
            bank.get_and_format("final_summary", **summary)
        ).wait_and_continue(keys=[continue_key], terminate=True)

        result_path = Path(settings.res_file)
        result_path.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(rows).to_csv(result_path, index=False)
        triggers.send(settings.triggers.get("experiment_end"))
        triggers.close()
        win.close()
        core.quit()


def main() -> None:
    run(
        parse_task_run_options(
            task_root=Path(__file__).resolve().parent,
            description="Run the Public Goods Game with Punishment.",
            default_config_by_mode=DEFAULT_CONFIG_BY_MODE,
            modes=MODES,
        )
    )


if __name__ == "__main__":
    main()

