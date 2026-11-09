"""MathSense-ID shared contracts. FROZEN — jangan ubah tanpa Orchestrator."""
from dataclasses import dataclass, asdict
from typing import List, Tuple, Optional
import json
import re


@dataclass
class ExtractedEntity:
    text: str
    value: float
    unit: str
    role: str  # "quantity" | "price" | "subject" | "variable"
    confidence: float


@dataclass
class ExtractedRelation:
    head: str
    tail: str
    relation: str
    operation: str  # "+" | "-" | "*" | "/" | "?" | "="
    confidence: float


@dataclass
class MathSenseOutput:
    original_text: str
    entities: List[ExtractedEntity]
    relations: List[ExtractedRelation]
    equation: Optional[str]
    variable_asked: str
    solution: Optional[float]
    graph_edges: List[Tuple[str, str, str]]
    confidence_overall: float
    warnings: List[str]


def entity_to_dict(e: ExtractedEntity) -> dict:
    return asdict(e)


def entity_from_dict(d: dict) -> ExtractedEntity:
    return ExtractedEntity(**d)


def output_to_json(output: MathSenseOutput) -> str:
    data = asdict(output)
    data['entities'] = [asdict(e) for e in output.entities]
    data['graph_edges'] = [list(t) for t in output.graph_edges]
    return json.dumps(data, ensure_ascii=False, indent=2)


def canonicalize_equation(eq: Optional[str]) -> str:
    """Format canonical: '3*x=15000', 'x=10+5', 'x=(30000/6)*4'."""
    if not eq:
        return ""
    eq = eq.replace(" ", "").replace("×", "*").replace("÷", "/").replace("X", "x")
    if "=" in eq:
        left, right = eq.split("=", 1)
        if "x" not in left and "x" in right:
            left, right = right, left
        return f"{left}={right}"
    return eq


def is_valid_math_problem(text: str) -> bool:
    if not isinstance(text, str) or len(text.strip()) < 10:
        return False
    has_number = bool(re.search(r'\d+', text))
    has_question = '?' in text or 'berapa' in text.lower()
    has_context = len(text.split()) >= 5
    return has_number and has_question and has_context


def has_multiple_questions(text: str) -> bool:
    return len(re.findall(r'\?', text)) > 1


def compute_overall_confidence(entities, relations, equation, solution) -> float:
    if not equation or solution is None:
        return 0.0
    import numpy as np
    avg_e = float(np.mean([e.confidence for e in entities])) if entities else 0.0
    avg_r = float(np.mean([r.confidence for r in relations])) if relations else 0.0
    return 0.4 * avg_e + 0.4 * avg_r + 0.2
