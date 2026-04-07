def grade(action, observation):
    score = 0.4

    if action.get("category") == "billing":
        score += 0.2

    if action.get("priority") in ["high", "urgent"]:
        score += 0.2

    if action.get("assign_to") == "support":
        score += 0.2

    return max(0.01, min(score, 0.99))
