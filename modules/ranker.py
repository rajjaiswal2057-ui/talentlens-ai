"""Ranks scored candidates and assigns a match label."""

def rank_candidates(candidates: list) -> list:
    """candidates: list of dicts each containing a 'score' dict from scorer."""
    ranked = sorted(candidates, key=lambda c: c["score"]["overall"], reverse=True)
    for i, c in enumerate(ranked, start=1):
        c["rank"] = i
        s = c["score"]["overall"]
        c["label"] = "Strong" if s >= 75 else "Good" if s >= 55 else "Partial" if s >= 35 else "Weak"
    return ranked