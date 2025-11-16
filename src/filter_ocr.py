from .ocr_extractor import *

from typing import List, Dict

KEYWORDS = {
    "name", "signature", "title", "date", "address",
    "phone", "email", 'mail', "company", "id", "ssn", "dob", 'sign', 'sum',
    'contact', 'number'
    # 'total'
}

SUBSTRINGS = {"[", "]", ":", "__", "…", "-"}  

def should_filter(item: Dict, next_item: Dict | None) -> bool:
    """
    Return True if this `item` should be filtered out (i.e. rejected).
    """
    text = item.get("text", "")
    low = text.lower()

    for kw in KEYWORDS:
        if kw in low: return True

    for sub in SUBSTRINGS:
        if sub in text: return True
    
    if next_item is not None:
        nxt = next_item.get("text", "")
        if nxt.strip() in {":", "-"}: return True
    return False

def filter_items(lst: List[Dict]) -> List[Dict]:
    """
    Return a new list, excluding items that should be filtered.
    """
    out = []
    n = len(lst)
    for i, itm in enumerate(lst):
        nxt = lst[i + 1] if i + 1 < n else None
        if should_filter(itm, nxt):
            out.append(itm)
    return out

