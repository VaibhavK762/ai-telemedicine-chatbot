def calculate_confidence(
    alias_matches: int,
    extracted: int,
    duplicates: int
) -> float:
    if alias_matches == 0:
        return 0.0

    extraction_score = extracted / alias_matches
    duplicate_penalty = duplicates / alias_matches

    confidence = extraction_score - (duplicate_penalty * 0.5)

    return round(
        max(
            0.0,
            min(confidence, 1.0)
        ),
        2
    )
