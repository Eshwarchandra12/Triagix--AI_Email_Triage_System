from typing import Dict, Any
from env.models import Action, Observation, Reward, Transition
import importlib


class EmailTriageEnv:
    def __init__(self):
        self.current_task_id = "easy"
        self.task_module = None
        self.state = None
        self.step_count = 0
        self.max_steps = 8

    # RESET
    def reset(self, task_id: str = "easy") -> Observation:
        self.current_task_id = task_id
        self.step_count = 0

        try:
            self.task_module = importlib.import_module(f"tasks.{task_id}")
        except ModuleNotFoundError:
            raise ValueError(f"Task {task_id} not found.")

        self.state = self.task_module.init_state()
        print("STATE AFTER INIT:", self.state)
        return self._get_obs()

        # safety check
        required_keys = ["current_email", "queue", "previous_actions"]
        for key in required_keys:
            if key not in self.state:
                raise ValueError(f"Missing key in state: {key}")

        return self._get_obs()

    # STEP
    def step(self, action: Action) -> Transition:
        if self.state is None:
            raise RuntimeError("Environment must be reset before taking a step.")

        self.step_count += 1

        reward_value, step_info = self.task_module.grade_step(self.state, action)

        queue_empty = (
            len(self.state.get("queue", [])) == 0
            and self.state.get("current_email") is None
        )

        done = queue_empty or self.step_count >= self.max_steps

        reward = Reward(value=reward_value, info=step_info)
        obs = self._get_obs()

        return Transition(
            observation=obs,
            reward=reward,
            done=done,
            info={"step_count": self.step_count}
        )

    # SERIALIZE EMAIL
    def _serialize_email(self, email):
        if email is None:
            return None

        # support both dict and object
        if isinstance(email, dict):
            return {
                "id": email.get("id", "email_1"),
                "sender": email.get("sender", ""),
                "subject": email.get("subject", ""),
                "body": email.get("body", ""),
                "timestamp": email.get("timestamp", "2026-01-01T00:00:00"),
                "sla_deadline": email.get("sla_deadline", None),
            }
        else:
            return {
                "id": getattr(email, "id", "email_1"),
                "sender": getattr(email, "sender", ""),
                "subject": getattr(email, "subject", ""),
                "body": getattr(email, "body", ""),
                "timestamp": getattr(email, "timestamp", "2026-01-01T00:00:00"),
                "sla_deadline": getattr(email, "sla_deadline", None),
            }

    # OBSERVATION
    def _get_obs(self) -> Observation:
        queue = self.state.get("queue", [])
        current = self.state.get("current_email", None)

        # count SLA emails
        active_slas = sum(
            1 for e in queue
            if isinstance(e, dict)
            and e.get("sla_deadline") is not None
            and e.get("sla_deadline") < 3
        )

        if isinstance(current, dict):
            if current.get("sla_deadline") is not None and current.get("sla_deadline") < 3:
                active_slas += 1

        return Observation(
            current_email=self._serialize_email(current),
            queue_length=len(queue),
            active_slas=active_slas,
            previous_actions=self.state.get("previous_actions", [])
        )

    def get_state(self) -> Dict[str, Any]:
        return self.state