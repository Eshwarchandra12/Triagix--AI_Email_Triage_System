from env.models import Action
from typing import Dict, Any, Tuple


def init_state():
    return {
        "current_email": {
            "id": "email_001_payment_issue",
            "sender": "billing@client.com",
            "subject": "Duplicate charge on my account",
            "body": "I was charged twice for my subscription.",
            "timestamp": "2026-01-01T10:00:00",
            "sla_deadline": 2
        },
        "queue": [],
        "previous_actions": []
    }


def grade_step(state: Dict[str, Any], action: Action) -> Tuple[float, dict]:
    if state["current_email"] is None:
        return -0.2, {"error": "no email to process"}

    reward = 0.0
    info = {"category_correct": False, "priority_correct": False}

    current = state["current_email"]

    # category
    if action.category == "billing":
        reward += 0.5
        info["category_correct"] = True
    else:
        reward -= 0.3

    # priority
    if action.priority in ["medium", "high"]:
        reward += 0.5
        info["priority_correct"] = True
    else:
        reward -= 0.3

    # log
    email_id = current.get("id", "unknown")
    state["previous_actions"].append(
        f"Processed {email_id}: {action.category}, {action.priority}"
    )

    state["current_email"] = None

    reward = round(min(1.0, reward), 2)
    return reward, info