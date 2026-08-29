from __future__ import annotations

from dataclasses import dataclass
import random as _py_random
from typing import Any

from psyflow.sim.contracts import Action, Feedback, Observation, SessionInfo


@dataclass
class TaskSamplerResponder:
    cooperation_probability: float = 0.7
    punishment_probability: float = 0.65
    rt_mean_s: float = 0.12
    rt_sd_s: float = 0.02
    rt_min_s: float = 0.05

    def __post_init__(self) -> None:
        self.cooperation_probability = min(1.0, max(0.0, float(self.cooperation_probability)))
        self.punishment_probability = min(1.0, max(0.0, float(self.punishment_probability)))
        self.rt_sd_s = max(1e-6, float(self.rt_sd_s))
        self.rt_min_s = max(0.0, float(self.rt_min_s))
        self._rng: Any = None

    def start_session(self, session: SessionInfo, rng: Any) -> None:
        self._rng = rng

    def on_feedback(self, fb: Feedback) -> None:
        return None

    def end_session(self) -> None:
        self._rng = None

    def _random(self) -> float:
        return float(self._rng.random()) if hasattr(self._rng, "random") else float(_py_random.random())

    def _normal(self) -> float:
        if hasattr(self._rng, "normal"):
            return float(self._rng.normal(self.rt_mean_s, self.rt_sd_s))
        return float(_py_random.gauss(self.rt_mean_s, self.rt_sd_s))

    def act(self, obs: Observation) -> Action:
        valid = [str(key) for key in (obs.valid_keys or [])]
        if not valid:
            return Action(key=None, rt_s=None, meta={"source": "task_sampler", "reason": "no_valid_keys"})

        phase = str(obs.phase or "")
        if phase == "communication":
            key = "j" if "j" in valid else valid[0]
            policy = "neutral_message"
        elif phase == "contribution":
            cooperate = self._random() < self.cooperation_probability
            if valid == ["f", "j"]:
                key = "j" if cooperate else "f"
            else:
                preferred = "4" if cooperate else "2"
                key = preferred if preferred in valid else valid[-1 if cooperate else 0]
            policy = "stochastic_contribution"
        elif phase == "punishment_target":
            if self._random() >= self.punishment_probability and "space" in valid:
                key = "space"
                policy = "no_punishment"
            else:
                peers = list((obs.task_factors or {}).get("peer_contributions", []))
                target_keys = [key for key in valid if key != "space"]
                target_idx = peers.index(min(peers)) if peers and target_keys else 0
                key = target_keys[min(target_idx, len(target_keys) - 1)] if target_keys else valid[0]
                policy = "punish_lowest_contributor"
        elif phase == "punishment_amount":
            key = "2" if "2" in valid else valid[0]
            policy = "moderate_punishment"
        elif "space" in valid:
            key = "space"
            policy = "continue"
        else:
            key = valid[0]
            policy = "first_valid"

        return Action(
            key=key,
            rt_s=max(self.rt_min_s, self._normal()),
            meta={"source": "task_sampler", "policy": policy},
        )

