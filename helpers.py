# =============================================================================
# Module imports
# =============================================================================

from datetime import datetime, timedelta
import re
from openpyxl.styles import PatternFill, Font
from copy import copy

# =============================================================================
# Helper functions
# =============================================================================


def _clean_text(s: str) -> str:
    """Lowercase, collapse non-alphanumerics to spaces, normalize whitespace."""
    if not s:
        return ""
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def _word_boundary_contains(text: str, token: str) -> bool:
    """True if token appears as a word (boundary-aware) in text."""
    if not token:
        return False
    return re.search(rf"\b{re.escape(token.lower())}\b", text) is not None