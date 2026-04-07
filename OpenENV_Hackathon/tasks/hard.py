from env.models import Action
from typing import Dict, Any, Tuple


def init_state():
    return {
        "current_email": {
            "id": "email_001_outage",
            "sender": "enterprise@client.com",
            "subject": "System down",
            "body": "Critical outage",
            "timestamp": "2026-01-01T07:00:00",
            "sla_deadline": 1
        },
        "queue": [
            {
                "id": "email_002_login",
                "sender": "user@gmail.com",
                "subject": "Login issue",
                "body": "Cannot login",
                "timestamp": "2026-01-01T06:30:00",
                "sla_deadline": 3
            },
            {
                "id": "email_003_invoice",
                "sender": "billing@company.com",
                "subject": "Invoice help",
                "body": "Need invoice",
                "timestamp": "2026-01-01T06:00:00",
                "sla_deadline": 5
            }
        ],
        "previous_actions": []
    }


def process_slas(state: Dict[str, Any]) -> int:
    v = 0
    current = state["current_email"]

    if current and current.get("sla_deadline") is not None:
        current["sla_deadline"] -= 1
        if current["sla_deadline"] < 0:
            v += 1

    for e in state["queue"]:
        if e.get("sla_deadline") is not None:
            e["sla_deadline"] -= 1
            if e["sla_deadline"] < 0:
                v += 1

    return v


def grade_step(state: Dict[str, Any], action: Action) -> Tuple[float, dict]:
    if state["current_email"] is None:
        return -0.2, {"error": "no email"}

    reward = 0.0
    violations = process_slas(state)

    current = state["current_email"]
    email_id = current.get("id")

    info = {
        "sla_violations": violations,
        "category_correct": False,
        "routing_correct": False,
        "priority_correct": False
    }

    # SLA
    if violations > 0:
        reward -= 0.4 * violations
    else:
        reward += 0.2

    # urgency
    if current.get("sla_deadline") <= 1:
        if action.priority != "urgent":
            reward -= 0.6
        else:
            reward += 0.3
            info["priority_correct"] = True

    # enterprise pressure
    if "enterprise" in current.get("sender", ""):
        if action.priority != "urgent":
            reward -= 0.3

    # outage
    if email_id == "email_001_outage":
        if action.category == "technical":
            reward += 0.2
            info["category_correct"] = True
        else:
            reward -= 0.2

        if action.assign_to == "engineering":
            reward += 0.2
            info["routing_correct"] = True
        else:
            reward -= 0.2

    # login
    elif email_id == "email_002_login":
        if action.category == "technical":
            reward += 0.2
        else:
            reward -= 0.2

    # invoice
    elif email_id == "email_003_invoice":
        if action.category == "billing":
            reward += 0.2
        else:
            reward -= 0.2

    # queue awareness
    if len(state["queue"]) > 0 and current.get("sla_deadline") <= 1:
        reward += 0.1

    state["previous_actions"].append(f"Processed {email_id}")

    if state["queue"]:
        state["current_email"] = state["queue"].pop(0)
    else:
        state["current_email"] = None

    reward = round(min(1.0, reward), 2)
    return reward, info