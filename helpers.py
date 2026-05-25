from datetime import datetime, timedelta
import re
from openpyxl.styles import PatternFill, Font
from copy import copy

def safe_to_int(s):
    try:
        f = float(s)
        if f != f:  # NaN check (NaN is not equal to itself)
            return None
        return int(f)
    except:
        return None

def copy_cell(src_cell, dst_cell):
    dst_cell.value = src_cell.value

    if src_cell.has_style:
        dst_cell.font = copy(src_cell.font)
        dst_cell.border = copy(src_cell.border)
        dst_cell.fill = copy(src_cell.fill)
        dst_cell.number_format = copy(src_cell.number_format)
        dst_cell.protection = copy(src_cell.protection)
        dst_cell.alignment = copy(src_cell.alignment)

# ----- robust date parser accepting multiple common formats -----
def _parse_date_any(date_str: str) -> datetime:
    """Try multiple common date formats and normalize to a datetime."""
    if date_str is None:
        raise ValueError("Date string is None")

    s = str(date_str).strip()

    # Common formats to try (ordered by likelihood / minimal ambiguity)
    candidates = [
        "%d/%m/%Y", "%d/%m/%y",
        "%d-%m-%Y", "%d-%m-%y",
        "%d.%m.%Y", "%d.%m.%y",
        "%m/%d/%Y", "%m/%d/%y",  # US
        "%m-%d-%Y", "%m-%d-%y",
        "%Y/%m/%d", "%Y-%m-%d", "%Y.%m.%d",
        "%d %b %Y", "%d %B %Y",
        "%b %d, %Y", "%B %d, %Y",
        "%d %b %y", "%d %B %y",
        "%b %d, %y", "%B %d, %y",
    ]

    last_error = None
    for fmt in candidates:
        try:
            return datetime.strptime(s, fmt)
        except ValueError as e:
            last_error = e

    # Fallback heuristic: disambiguate dd/mm vs mm/dd
    for sep in ("/", "-", "."):
        if sep in s:
            parts = s.split(sep)
            if len(parts) == 3 and all(p.isdigit() for p in parts):
                a, b, c = parts

                def _norm_year(y):
                    if len(y) == 2:
                        yy = int(y)
                        return 2000 + yy if yy <= 69 else 1900 + yy
                    return int(y)

                # Try D/M/Y
                try:
                    day = int(a)
                    month = int(b)
                    year = _norm_year(c)
                    return datetime(year, month, day)
                except Exception:
                    pass

                # Try M/D/Y
                try:
                    month = int(a)
                    day = int(b)
                    year = _norm_year(c)
                    return datetime(year, month, day)
                except Exception:
                    pass

    raise ValueError(f"Unrecognized date format for '{date_str}'. Last parsing error: {last_error}")

def dates_before(end_date_str, start_date_str=None):
    """Return list of date strings (dd/mm/YYYY) for all days before end date from start date."""
    output_format = "%d/%m/%Y"
    start_date = _parse_date_any(start_date_str) if start_date_str else datetime(2026, 1, 1)
    end_date = _parse_date_any(end_date_str)

    if end_date <= start_date:
        return []

    result = []
    current_date = start_date
    while current_date < end_date:
        result.append(current_date.strftime(output_format))
        current_date += timedelta(days=1)
    return result

def highlight_cell(cell, color="FFFF00"):
    """Highlight a cell with the specified color (default is yellow)."""
    fill = PatternFill(start_color=color, end_color=color, fill_type="solid")
    cell.fill = fill

def highlight_text(cell, color="FF0000"):
    """Highlight the text in a cell with the specified color (default is red)."""
    font = Font(color=color)
    cell.font = font

def _clean_text(s: str) -> str:
    """Lowercase, collapse non-alphanumerics to spaces, normalize whitespace."""
    if not s:
        return ""
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def _norm_str(v):
    s = "" if v is None else str(v).strip()
    return s.casefold()

def _slot_as_int_or_inf(v):
    s = "" if v is None else str(v).strip()
    if s == "":
        return float("inf")  # blanks last
    
    # Match an integer at the start of the string (optional sign)
    m = re.match(r"^[\s]*([+-]?\d+)", s)
    if m:
        try:
            return int(m.group(1))
        except ValueError:
            pass  # fall through to inf if something odd happens

    return float("inf")

def _word_boundary_contains(text: str, token: str) -> bool:
    """True if token appears as a word (boundary-aware) in text."""
    if not token:
        return False
    return re.search(rf"\b{re.escape(token.lower())}\b", text) is not None