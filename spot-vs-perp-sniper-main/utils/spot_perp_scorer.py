# utils/spot_perp_scorer.py

def score_spot_perp_confluence_multi(deltas: dict):
    """
    Scores 5m, 15m, 1h CVD delta behavior to assign confluence bias and confidence.
    """

    score = 0
    notes = []

    tf_weights = {
        "5m": 1.0,
        "15m": 1.5,
        "1h": 1.0
    }

    for tf, delta in deltas.items():
        weight = tf_weights.get(tf, 1.0)

        cb = delta.get("cb_cvd", 0)
        spot = delta.get("bin_spot", 0)
        perp = delta.get("bin_perp", 0)

        # Bullish confluence
        if cb > 1 and spot > 1:
            score += 2 * weight
            notes.append(f"{tf}: Spot & CB strong")

        # Perp weakness
        if perp < -1:
            score += 1 * weight
            notes.append(f"{tf}: Perp fading")

        # Perp-led conflict
        if perp > 1 and spot < -1:
            score -= 2 * weight
            notes.append(f"{tf}: Perp up, Spot down")

        # Flat/uncertain → minor penalty
        if abs(cb) < 0.3 and abs(spot) < 0.3 and abs(perp) < 0.3:
            score -= 0.5 * weight
            notes.append(f"{tf}: Market flat")

    # === Final bias label ===
    label = "neutral"
    if score >= 6:
        label = "spot_dominant"
    elif score >= 3:
        label = "spot_advantage"
    elif score <= 0:
        label = "perp_dominant"
    elif score <= 2:
        label = "perp_advantage"

    return {
        "score": round(score, 1),
        "label": label,
        "notes": notes
    }
