"""MathSense-ID equation builder templates.

Menyediakan fungsi build_equation sesuai 5 template:
- T1: Harga satuan (N*x=P)
- T2: Total penjumlahan (x=A+B)
- T3: Sisa pengurangan (x=A-B)
- T4: Total perkalian (x=A*B)
- T5: Harga sejumlah (x=(P/N)*M)
"""
from typing import List, Any, Optional, Dict


class _NormalizedEntity:
    def __init__(self, text: str, value: float, unit: str, role: str, confidence: float):
        self.text = text
        self.value = float(value)
        self.unit = unit
        self.role = role
        self.confidence = float(confidence)


def _normalize_entity(e: Any) -> Optional[_NormalizedEntity]:
    if e is None:
        return None
    if hasattr(e, "role") and hasattr(e, "value"):
        return _NormalizedEntity(
            text=getattr(e, "text", ""),
            value=getattr(e, "value", 0.0),
            unit=getattr(e, "unit", ""),
            role=getattr(e, "role", ""),
            confidence=getattr(e, "confidence", 1.0)
        )
    if isinstance(e, dict):
        return _NormalizedEntity(
            text=e.get("text", ""),
            value=float(e.get("value", 0.0)),
            unit=e.get("unit", ""),
            role=e.get("role", ""),
            confidence=float(e.get("confidence", 1.0))
        )
    return None


def _num_str(val: float) -> str:
    """Format angka: integer jika tidak ada desimal, float jika ada desimal."""
    try:
        f = float(val)
        if f.is_integer():
            return str(int(f))
        return str(f)
    except Exception:
        return str(val)


def build_equation(
    entities: List[Any],
    relations: Optional[List[Any]] = None,
    q_type: Optional[str] = None,
    **kwargs: Any
) -> Optional[str]:
    """Membangun persamaan kanonikal dari entities, relations, dan q_type.

    Mengembalikan string persamaan kanonikal atau None jika out-of-scope/invalid.
    """
    if relations is None and "rels" in kwargs:
        relations = kwargs["rels"]

    if not entities:
        return None

    norm_ents = [_normalize_entity(e) for e in entities]
    norm_ents = [e for e in norm_ents if e is not None]

    if not norm_ents:
        return None

    quantities = [e for e in norm_ents if e.role == "quantity"]
    prices = [e for e in norm_ents if e.role == "price"]
    variables = [e for e in norm_ents if e.role == "variable"]
    all_quantities = [e for e in norm_ents if e.role in ("quantity", "variable")]

    # Smart dispatch / inference:
    # Jika memiliki 2 kuantitas dan 1 harga, ini merupakan problem rasio/proporsi T5
    if (q_type in ("T1", "T2", "UNKNOWN") or not q_type) and len(all_quantities) >= 2 and len(prices) == 1:
        q_type = "T5"

    # Infer q_type dari relations jika q_type tidak diberikan atau UNKNOWN
    if not q_type or q_type == "UNKNOWN":
        if relations:
            for r in relations:
                op = getattr(r, "operation", None) if hasattr(r, "operation") else (r.get("operation") if isinstance(r, dict) else None)
                if op == "+":
                    q_type = "T2"
                    break
                elif op == "-":
                    q_type = "T3"
                    break
                elif op == "*":
                    if len(all_quantities) >= 2 and prices:
                        q_type = "T5"
                    elif quantities and prices:
                        q_type = "T1"
                    break
    if q_type == "T1":
        if quantities and prices:
            q_val = _num_str(quantities[0].value)
            p_val = _num_str(prices[0].value)
            return f"{q_val}*x={p_val}"
        return None

    elif q_type == "T2":
        if len(quantities) >= 2:
            return f"x={_num_str(quantities[0].value)}+{_num_str(quantities[1].value)}"
        elif len(all_quantities) >= 2:
            return f"x={_num_str(all_quantities[0].value)}+{_num_str(all_quantities[1].value)}"
        elif len(prices) >= 2:
            return f"x={_num_str(prices[0].value)}+{_num_str(prices[1].value)}"
        return None

    elif q_type == "T3":
        if len(quantities) >= 2:
            return f"x={_num_str(quantities[0].value)}-{_num_str(quantities[1].value)}"
        elif len(all_quantities) >= 2:
            return f"x={_num_str(all_quantities[0].value)}-{_num_str(all_quantities[1].value)}"
        elif len(prices) >= 2:
            return f"x={_num_str(prices[0].value)}-{_num_str(prices[1].value)}"
        return None

    elif q_type == "T4":
        if quantities and prices:
            return f"x={_num_str(quantities[0].value)}*{_num_str(prices[0].value)}"
        return None

    elif q_type == "T5":
        # T5 membutuhkan base quantity, base price, dan target quantity
        if not prices:
            return None
        base_price = prices[0]
        base_qty = quantities[0] if quantities else (all_quantities[0] if all_quantities else None)
        target_qty = None
        if variables:
            target_qty = variables[0]
        elif len(quantities) >= 2:
            target_qty = quantities[1]
        elif len(all_quantities) >= 2:
            target_qty = all_quantities[1]

        if base_qty is not None and target_qty is not None and base_price is not None:
            # Pencegahan dini pembagian dengan nol
            if base_qty.value == 0:
                return None
            return f"x=({_num_str(base_price.value)}/{_num_str(base_qty.value)})*{_num_str(target_qty.value)}"
        return None

    return None
