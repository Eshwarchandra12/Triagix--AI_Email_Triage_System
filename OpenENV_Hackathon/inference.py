import os

import requests
from openai import OpenAI

ENV_BASE_URL = os.getenv("ENV_BASE_URL", "http://127.0.0.1:7860")
API_BASE_URL = os.environ["API_BASE_URL"]
API_KEY = os.environ["API_KEY"]
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
TIMEOUT = int(os.getenv("TIMEOUT", "60"))

client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)


def post_json(path: str, *, json_body=None, params=None):
    response = requests.post(
        f"{ENV_BASE_URL}{path}",
        json=json_body,
        params=params,
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    return response.json()


def call_llm(email: dict) -> str:
    prompt = (
        "You are helping with enterprise email triage.\n"
        "Return one short line with category, priority, team, and reply tone.\n\n"
        f"Subject: {email.get('subject', '')}\n"
        f"Body: {email.get('body', '')}\n"
        f"SLA: {email.get('sla_deadline')}\n"
    )
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    return response.choices[0].message.content or ""


def decide_action(email: dict, llm_hint: str) -> dict:
    text = f"{email.get('subject', '')} {email.get('body', '')}".lower()
    sla = email.get("sla_deadline")

    if any(word in text for word in ["invoice", "refund", "payment", "charge", "billing"]):
        category = "billing"
        assign_to = "support"
    elif any(word in text for word in ["login", "bug", "error", "issue", "down", "crash"]):
        category = "technical"
        assign_to = "engineering"
    elif any(word in text for word in ["pricing", "demo", "quote", "plan", "sales"]):
        category = "sales"
        assign_to = "sales"
    elif any(word in text for word in ["unsubscribe", "winner", "lottery", "free money"]):
        category = "spam"
        assign_to = "ignore"
    else:
        category = "other"
        assign_to = "support"

    if sla is not None and sla <= 1:
        priority = "urgent"
    elif sla is not None and sla <= 3:
        priority = "high"
    elif "urgent" in text or "asap" in text:
        priority = "high"
    else:
        priority = "medium"

    draft_reply = (
        "Hello, thanks for reaching out. "
        "We have reviewed your request and routed it to the right team. "
        "We will follow up shortly."
    )

    if "refund" in text or "charge" in text:
        draft_reply = (
            "Hello, thanks for contacting billing support. "
            "We are reviewing the charge and will update you shortly."
        )
    elif category == "technical":
        draft_reply = (
            "Hello, thanks for reporting this issue. "
            "Our engineering team is investigating and will get back to you soon."
        )

    if llm_hint:
        draft_reply = draft_reply[:400]

    return {
        "category": category,
        "priority": priority,
        "assign_to": assign_to,
        "draft_reply": draft_reply,
    }


def run_task(task_id: str):
    observation = post_json("/reset", params={"task_id": task_id})
    total_reward = 0.0
    steps = 0

    while True:
        email = observation.get("current_email")
        if email is None:
            break

        llm_hint = call_llm(email)
        action = decide_action(email, llm_hint)

        result = post_json("/step", json_body=action)
        total_reward += float(result.get("reward", 0.0))
        steps += 1

        if result.get("done", False):
            break

        observation = result.get("observation", {})

    avg_reward = total_reward / max(steps, 1)
    print(f"[RESULT] task={task_id} steps={steps} avg_reward={avg_reward:.3f}")


def main():
    for task_id in ["easy", "medium", "hard"]:
        run_task(task_id)


if __name__ == "__main__":
    main()
