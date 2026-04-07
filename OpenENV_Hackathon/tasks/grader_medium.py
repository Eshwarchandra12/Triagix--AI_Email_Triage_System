def grade(action, observation):
    score = 0.3

    if action.get("category") in ["billing", "technical"]:
        score += 0.25

    if action.get("priority") == "urgent":
        score += 0.25

    if action.get("assign_to") in ["support", "engineering"]:
        score += 0.2

    return max(0.01, min(score, 0.99))
