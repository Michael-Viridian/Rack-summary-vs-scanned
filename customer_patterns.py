# =============================================================================
# Function imports
# =============================================================================

from helpers import _clean_text, _word_boundary_contains

# =============================================================================
# Helper functions
# =============================================================================

def _normalize_keywords(raw_keywords):
    """
    Convert the mixed list (strings, tuples, list-of-tuples) into a uniform structure:
    [
        {
        "alts": [("viridian","nelson"), ("vir","nelson")],  # OR of ANDs
        "label": "Viridian Nelson"                           # canonical group label
        },
        ...
    ]
    Deduplicates by label (case-insensitive) while preserving order.
    """
    patterns = []
    seen_labels = set()

    for item in raw_keywords:
        if item is None:
            continue

        if isinstance(item, str) and ("," in item or "+" in item):
            alts = []

            # OR groups
            for part in item.split(","):
                part = part.strip()
                if not part:
                    continue

                # AND tokens
                tokens = tuple(tok.strip() for tok in part.split("+") if tok.strip())
                if tokens:
                    alts.append(tokens)

            if not alts:
                continue

            # Match Case 3 labeling behavior: first alternative only
            label = " ".join(alts[0])

        # Case 1: single string (e.g., ("Waitaki") -> "Waitaki")
        elif isinstance(item, str):
            alts = [(item,)]
            label = item

        # Case 2: single tuple => AND of tokens in that tuple
        elif isinstance(item, tuple):
            alts = [item]
            label = " ".join(item)

        # Case 3: list => OR of tuples/strings
        elif isinstance(item, list):
            alts = []
            for sub in item:
                if isinstance(sub, tuple):
                    alts.append(sub)
                elif isinstance(sub, str):
                    alts.append((sub,))
                else:
                    # skip invalid
                    continue
            if not alts:
                continue
            label = " ".join(alts[0])

        else:
            # skip invalid
            continue

        # Clean & store
        # Keep the "human" label as-is for display, but base dedupe on a cleaned version
        dedupe_key = _clean_text(label)
        if dedupe_key in seen_labels:
            continue
        seen_labels.add(dedupe_key)

        # Store lowercase alts for matching
        alts_clean = []
        for t in alts:
            alts_clean.append(tuple(_clean_text(x) for x in t if _clean_text(x)))

        patterns.append({
            "alts": alts_clean,
            "label": label.strip()
        })

    return patterns

def deliver_group_key(deliver_to_value: str, patterns, fallback_unknown="(unknown deliver to)"):
    """
    Returns the canonical group label for 'deliver_to_value' using patterns.
    If none match, returns the normalized 'deliver_to_value' (so identical strings group together).
    If empty/None, returns fallback_unknown.
    """
    text = deliver_to_value or ""
    text_clean = _clean_text(text)

    # Try keyword patterns in order; first match wins
    for p in patterns:
        for alt in p["alts"]:
            # AND across tokens in an alt
            if all(_word_boundary_contains(text_clean, tok) for tok in alt):
                return p["label"], True

    # Fallback: group by the actual deliver-to text (normalized)
    return (text.strip(), False) if text_clean else (fallback_unknown, False)

