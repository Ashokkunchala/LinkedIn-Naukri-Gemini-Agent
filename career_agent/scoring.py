def score_job(description: str, skills: list[str]) -> tuple[int, list[str]]:
    """Transparent keyword score; this is not a hiring prediction."""
    normalized = list(dict.fromkeys(s.strip().lower() for s in skills if s.strip()))
    text = description.lower()
    matches = [skill for skill in normalized if skill in text]
    return (round(100 * len(matches) / len(normalized)) if normalized else 0, matches)
