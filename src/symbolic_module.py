"""MathSense-ID symbolic solver module.

Menyediakan:
- solve_symbolic: solver berbasis SymPy dengan fallback manual_solve
- _manual_solve: rule-based solver untuk T1-T5 dan persamaan linear umum
"""
import ast
import re
from typing import Optional, Tuple

try:
    from equation_templates import build_equation
except ImportError:
    try:
        from src.equation_templates import build_equation
    except ImportError:
        build_equation = None


def solve_symbolic(equation: Optional[str], variable: str = "x") -> Optional[float]:
    """Menyelesaikan persamaan menggunakan SymPy dengan fallback ke _manual_solve."""
    if not equation or not isinstance(equation, str) or not equation.strip():
        return None

    clean_eq = (
        equation.replace(" ", "")
        .replace("×", "*")
        .replace("÷", "/")
        .replace("X", "x")
    )

    try:
        from sympy import symbols, Eq, solve, sympify
        x = symbols(variable)
        if "=" in clean_eq:
            left_str, right_str = clean_eq.split("=", 1)
            eq = Eq(sympify(left_str.strip()), sympify(right_str.strip()))
            sols = solve(eq, x)
        else:
            sols = solve(sympify(clean_eq.strip()), x)

        if sols:
            sol = sols[0]
            val = float(sol.evalf() if hasattr(sol, "evalf") else sol)
            return val
    except Exception:
        pass

    return _manual_solve(equation, variable)


def _parse_linear_ast(node: ast.AST, var_name: str = "x") -> Optional[Tuple[float, float]]:
    """Mengevaluasi node AST menjadi tuple linear (koefisien_x, konstanta).

    Mengembalikan (a, b) sehingga ekspresi = a * var + b.
    Mengembalikan None jika non-linear atau invalid.
    Sesuai batasan SCOPE.md, operator non-linear seperti Pow (**), Mod (%),
    FloorDiv (//) secara sengaja dianggap out-of-scope dan menghasilkan None.
    """
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return (0.0, float(node.value))
    elif isinstance(node, ast.Name):
        if node.id.lower() == var_name.lower():
            return (1.0, 0.0)
        return None
    elif isinstance(node, ast.UnaryOp):
        operand_res = _parse_linear_ast(node.operand, var_name)
        if operand_res is None:
            return None
        a, b = operand_res
        if isinstance(node.op, ast.USub):
            return (-a, -b)
        elif isinstance(node.op, ast.UAdd):
            return (a, b)
        return None
    elif isinstance(node, ast.BinOp):
        left_res = _parse_linear_ast(node.left, var_name)
        right_res = _parse_linear_ast(node.right, var_name)
        if left_res is None or right_res is None:
            return None
        a1, b1 = left_res
        a2, b2 = right_res

        if isinstance(node.op, ast.Add):
            return (a1 + a2, b1 + b2)
        elif isinstance(node.op, ast.Sub):
            return (a1 - a2, b1 - b2)
        elif isinstance(node.op, ast.Mult):
            # Perkalian hanya linear jika salah satu sisi murni konstanta (a == 0)
            if a1 != 0 and a2 != 0:
                return None
            return (a1 * b2 + a2 * b1, b1 * b2)
        elif isinstance(node.op, ast.Div):
            # Pembagian hanya valid jika penyebut adalah konstanta non-zero
            if a2 != 0 or b2 == 0:
                return None
            return (a1 / b2, b1 / b2)
        else:
            # Operator non-linear (Pow, Mod, FloorDiv) out-of-scope by design (SCOPE.md)
            return None

    return None


def _manual_solve(equation: Optional[str], variable: str = "x") -> Optional[float]:
    """Rule-based solver WAJIB cover T1-T5 + general linear ax+b=c."""
    if not equation or not isinstance(equation, str) or not equation.strip():
        return None

    eq = (
        equation.replace(" ", "")
        .replace("×", "*")
        .replace("÷", "/")
        .replace("X", "x")
        .lower()
    )
    var = variable.lower()

    if "=" not in eq:
        return None

    left, right = eq.split("=", 1)

    # Pastikan variable berada di sisi kiri untuk pola regex standar jika hanya satu sisi
    if var not in left and var in right:
        left, right = right, left

    full = f"{left}={right}"

    # T1: N*x=P atau x*N=P
    m1 = re.match(rf"^(-?\d+(?:\.\d+)?)\*{var}=(-?\d+(?:\.\d+)?)$", full)
    if m1:
        a, b = float(m1.group(1)), float(m1.group(2))
        return b / a if a != 0 else None

    m1_rev = re.match(rf"^{var}\*(-?\d+(?:\.\d+)?)=(-?\d+(?:\.\d+)?)$", full)
    if m1_rev:
        a, b = float(m1_rev.group(1)), float(m1_rev.group(2))
        return b / a if a != 0 else None

    # T2, T3, T4: x=A op B
    m_op = re.match(rf"^{var}=(-?\d+(?:\.\d+)?)([\+\-\*/])(-?\d+(?:\.\d+)?)$", full)
    if m_op:
        a, op_sym, b = float(m_op.group(1)), m_op.group(2), float(m_op.group(3))
        if op_sym == "+":
            return a + b
        if op_sym == "-":
            return a - b
        if op_sym == "*":
            return a * b
        if op_sym == "/":
            return a / b if b != 0 else None

    # T5: x=(A/B)*C atau x=(A*C)/B
    m5 = re.match(
        rf"^{var}=\((-?\d+(?:\.\d+)?)/(-?\d+(?:\.\d+)?)\)\*(-?\d+(?:\.\d+)?)$",
        full,
    )
    if m5:
        a, b, c = float(m5.group(1)), float(m5.group(2)), float(m5.group(3))
        return (a / b) * c if b != 0 else None

    m5_alt = re.match(
        rf"^{var}=\((-?\d+(?:\.\d+)?)\*(-?\d+(?:\.\d+)?)\)/(-?\d+(?:\.\d+)?)$",
        full,
    )
    if m5_alt:
        a, c, b = float(m5_alt.group(1)), float(m5_alt.group(2)), float(m5_alt.group(3))
        return (a * c) / b if b != 0 else None

    # General Linear 1: A*x+B=C atau A*x-B=C
    m_gen = re.match(
        rf"^(-?\d+(?:\.\d+)?)\*{var}([\+\-])(-?\d+(?:\.\d+)?)=(-?\d+(?:\.\d+)?)$",
        full,
    )
    if m_gen:
        a, op_sym, b, c = (
            float(m_gen.group(1)),
            m_gen.group(2),
            float(m_gen.group(3)),
            float(m_gen.group(4)),
        )
        if a == 0:
            return None
        if op_sym == "+":
            return (c - b) / a
        if op_sym == "-":
            return (c + b) / a

    # General Linear 2: x+B=C atau x-B=C
    m_gen2 = re.match(
        rf"^{var}([\+\-])(-?\d+(?:\.\d+)?)=(-?\d+(?:\.\d+)?)$",
        full,
    )
    if m_gen2:
        op_sym, b, c = m_gen2.group(1), float(m_gen2.group(2)), float(m_gen2.group(3))
        if op_sym == "+":
            return c - b
        if op_sym == "-":
            return c + b

    # General AST Linear Equation Fallback
    try:
        l_node = ast.parse(left, mode="eval").body
        r_node = ast.parse(right, mode="eval").body
        l_res = _parse_linear_ast(l_node, var)
        r_res = _parse_linear_ast(r_node, var)
        if l_res is not None and r_res is not None:
            a_l, b_l = l_res
            a_r, b_r = r_res
            A = a_l - a_r
            B = b_r - b_l
            if A != 0:
                return float(B / A)
    except Exception:
        pass

    return None
