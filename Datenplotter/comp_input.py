import re
import numpy as np
import ast
from typing import Optional

error_display_time = 2

def rect(x, T = 1.0):
    x = np.asarray(x)
    return np.where(np.abs(x) <= T/2, 1.0, 0.0)

def tri(x, T = 1.0):
    x = np.asarray(x)
    return np.where(np.abs(x) <= T, 1.0 - np.abs(x)/T, 0.0)

def delta(expr, x, eps=1e-3):

    x = np.asarray(x)

    scale = 1.0
    shift = 0.0

    scale_match = re.search(r"([\-]?\d*\.?\d+(?:/\d*\.?\d+)?)\s*\*?\s*x", expr)

    if scale_match:
        scale_str = scale_match.group(1)

        if "/" in scale_str:
            num, den = scale_str.split("/")
            scale = float(num) / float(den)
        else:
            scale = float(scale_str)

    elif re.search(r"\bx\b", expr):
        scale = 1.0
    elif re.search(r"-\s*x", expr):
        scale = -1.0

    shift_match = re.search(r"[+\-]\s*([\-]?\d+\.?\d*)\s*$", expr)

    if shift_match:
        shift = float(shift_match.group(1))

        if scale != 0:
            shift = -shift / scale

    height = 1.0 / (abs(scale) * 2 * eps)

    mask = np.abs(scale * (x - shift)) < eps

    return np.where(mask, height, 0.0)


allowed_funcs = {
    "sin": np.sin,
    "cos": np.cos,
    "tan": np.tan,
    "exp": np.exp,  
    "log": np.log10, 
    "ln": np.log,  
    "sqrt": np.sqrt,
    "cosh": np.cosh,
    "sinh": np.sinh,
    "arcsin": np.arcsin,
    "arccos": np.arccos,
    "arctan": np.arctan,
    "sinc": np.sinc,
    "abs": np.abs,
    "rect": rect,
    "tri": tri,
    "delta": delta
}

allowed_consts = {
    "pi": np.pi,
    "tau": 2 * np.pi,
}

numpy_modules = {
    "sin": np.sin,
    "cos": np.cos,
    "tan": np.tan,
    "exp": np.exp,
    "log": np.log,
    "ln": np.log,
    "sqrt": np.sqrt,
    "cosh": np.cosh,
    "sinh": np.sinh,
    "arcsin": np.arcsin,
    "arccos": np.arccos,
    "arctan": np.arctan,
    "abs": np.abs,
    "pi": np.pi,
    "e": np.e,
}


subs_map = {
    "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴",
    "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹",
    "-": "⁻", "+": "⁺", ".": "·",
    "x": "ˣ", "y": "ʸ", "n": "ⁿ",
    "(": "⁽", ")": "⁾"
}

class SafeEvaluator(ast.NodeVisitor):
    def __init__(self, x):
        self.x = x

    def visit_Expression(self, node):
        return self.visit(node.body)

    def visit_Name(self, node):
        if node.id == "x":
            return self.x
        if node.id in allowed_consts:
            return allowed_consts[node.id]
        raise ValueError(f"Unbekannte Variable: {node.id}")


    def visit_Constant(self, node):
        return node.value

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Div):
            return left / right
        if isinstance(node.op, ast.Pow):
            return left ** right
        raise ValueError("Operator nicht erlaubt")

    def visit_UnaryOp(self, node):
        operand = self.visit(node.operand)
        if isinstance(node.op, ast.UAdd):
            return +operand
        if isinstance(node.op, ast.USub):
            return -operand
        raise ValueError("Unary Operator nicht erlaubt")

    def visit_Call(self, node):
        # Falls es sich um np.exp, np.sin, etc. handelt
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name) and node.func.value.id == "np":
                fname = node.func.attr
                if fname in allowed_funcs:
                    func = allowed_funcs[fname]
                    args = [self.visit(arg) for arg in node.args]
                    return func(*args)
                else:
                    raise ValueError(f"Funktion nicht erlaubt: np.{fname}")
            else:
                raise ValueError(f"Unbekannte Funktion: {type(node.func).__name__}")
        # Falls es sich um einfache Funktionen wie sin, cos, etc. handelt
        elif isinstance(node.func, ast.Name):
            fname = node.func.id
            if fname in allowed_funcs:
                func = allowed_funcs[fname]
                args = [self.visit(arg) for arg in node.args]
                return func(*args)
            else:
                raise ValueError(f"Funktion nicht erlaubt: {fname}")
        else:
            raise ValueError(f"Unbekannte Funktion: {type(node).__name__}")

    def generic_visit(self, node):
        raise ValueError(f"Nicht erlaubter Ausdruck: {type(node).__name__}")

def eval_ast(expr, x):
    try:
        tree = ast.parse(expr, mode="eval")
        evaluator = SafeEvaluator(x)
        return evaluator.visit(tree)
    except SyntaxError as e:
        raise ValueError(f"Syntaxfehler: {e}")
    except ValueError as e:
        raise ValueError(f"Fehler bei der Auswertung: {e}")
    except Exception as e:
        raise ValueError(f"Unbekannter Fehler: {e}")


def handle_error(expr: str, error: Exception, func_name: str | None = None, label=None, max_line_length: int = 45) -> None:

    if not label:
        return

    if func_name:
        msg = f"Fehler in '{func_name}': {error}"
    else:
        msg = f"Fehler in '{expr}': {error}"

    if isinstance(error, ValueError):
        if "Unbekannte Variable" in str(error):
            msg += " – Unbekannte Variable."
        elif "Funktion nicht erlaubt" in str(error):
            msg += " – Nicht erlaubte Funktion."
        elif "Nicht erlaubter Ausdruck" in str(error):
            msg += " – Ausdruck nicht unterstützt."
        else:
            msg += " – Ungültiger Ausdruck."
    elif isinstance(error, SyntaxError):
        msg += " – Syntaxfehler."
    else:
        msg += " – Unbekannter Fehler."

    words = msg.split()
    lines = []
    current = ""

    for word in words:
        if len(current) + len(word) + 1 <= max_line_length:
            current += (" " if current else "") + word
        else:
            lines.append(current)
            current = word

    if current:
        lines.append(current)

    wrapped_msg = "\n".join(lines)

    label.config(
        text=wrapped_msg,
        foreground="red"
    )

def simplify_funcs(expr: str) -> str:
    expr = expr.strip()
    def sqrt_replace(match):
        coeff = match.group(1)
        if coeff is None or coeff in ("", "+"):
            coeff = ""
        elif coeff == "-":
            coeff = "-"
        return f"{coeff}x^(1/2)"
    expr = re.sub(r"([+-]?\d*\.?\d*)?\*?sqrt\((x)\)", sqrt_replace, expr)
    trig_funcs = ["sin", "cos", "tan", "exp", "ln", "log"]
    for f in trig_funcs:
        pattern = rf"([+-]?\d*\.?\d*)?\*?{f}\((x)\)"
        def func_replace(match, func=f):
            coeff = match.group(1)
            if coeff is None or coeff in ("", "+"):
                coeff = ""
            elif coeff == "-":
                coeff = "-"
            return f"{coeff}{func}(x)"
        expr = re.sub(pattern, func_replace, expr)
    return expr

def combine_exponents(expr: str) -> str:
    pattern_mul = re.compile(r"x\*\*\(?(-?\d+)\)?\*x\*\*\(?(-?\d+)\)?")
    while True:
        match = pattern_mul.search(expr)
        if not match:
            break
        a, b = map(int, match.groups())
        new_exp = a + b
        if new_exp == 0:
            replacement = "1"
        elif new_exp == 1:
            replacement = "x"
        else:
            replacement = f"x**{new_exp}"
        expr = expr[:match.start()] + replacement + expr[match.end():]
    pattern_div = re.compile(r"x\*\*\(?(-?\d+)\)?/x\*\*\(?(-?\d+)\)?")
    while True:
        match = pattern_div.search(expr)
        if not match:
            break
        a, b = map(int, match.groups())
        new_exp = a - b
        if new_exp == 0:
            replacement = "1"
        elif new_exp == 1:
            replacement = "x"
        else:
            replacement = f"x**{new_exp}"
        expr = expr[:match.start()] + replacement + expr[match.end():]
    return expr

def parser(expr: str) -> str:
    expr = expr.strip().replace(" ", "")
    expr = expr.replace(",", ".")
    expr = re.sub(r"\^(\-?\d+)", r"**\1", expr)
    expr = re.sub(r"\^(\-?[a-zA-Z])", r"**\1", expr)
    expr = expr.replace("^", "**")
    funcs = sorted(allowed_funcs.keys(), key=len, reverse=True)
    for f in funcs:
        expr = re.sub(rf"\b{f}\s*\(", f"np.{f}(", expr)
    expr = re.sub(r"(?<![a-zA-Z0-9_\.])pi(?![a-zA-Z0-9_])", "np.pi", expr)
    expr = re.sub(r"(?<![a-zA-Z0-9_\.])tau(?![a-zA-Z0-9_])", "(2*np.pi)", expr)
    expr = re.sub(r"(\d)\s*\(", r"\1*(", expr)  # 2(x) → 2*(x)
    expr = re.sub(r"(\d)([a-zA-Z])", r"\1*\2", expr)  # 2x → 2*x
    expr = re.sub(r"\)\s*\(", r")*(", expr)  # (x)(y) → (x)*(y)
    expr = re.sub(r"\)\s*([a-zA-Z])", r")*\1", expr)  # (x)y → (x)*y
    return expr


def interpreted(expr: str) -> str:
    expr = expr.strip().replace(" ", "")
    expr = expr.replace(".", ",")
    expr = expr.replace("pi", "π").replace("tau", "τ")
    def to_power(text):
        if not text:
            return ""
        text = re.sub(r"sqrt\((.*?)\)", lambda m: sqrt_replace(m.group(1)), text)
        return "".join(subs_map.get(ch, ch) for ch in text)
    def sqrt_replace(inner):
        inner = inner.replace("*", "")
        if len(inner) == 1:
            return f"√{inner}"
        return f"√({inner})"
    def replace_exp(match):
        inner = match.group(1)
        inner_processed = to_power(inner)
        if len(inner_processed) > 1:
            return f"e⁽{inner_processed}⁾"
        return f"e{inner_processed}"
    def replace_abs(match):
        inner = match.group(1)
        inner_processed = interpreted(inner)
        return f"|{inner_processed}|"
    expr = re.sub(r"exp\((.*?)\)", replace_exp, expr)
    expr = re.sub(r"e\^\((.*?)\)", replace_exp, expr)
    expr = re.sub(r"e\^([0-9a-zA-Zπ√\+\-\.\(\)]+)", replace_exp, expr)
    expr = re.sub(r"sqrt\((.*?)\)", lambda m: sqrt_replace(m.group(1)), expr)
    expr = re.sub(r"(\d+)\*([a-zA-Z\(])", lambda m: m.group(1) + m.group(2), expr)
    expr = re.sub(
        r"([a-zA-Z0-9\)])\*\*(\-?[0-9a-zA-Z\+\-π√\.\(\)]+)",
        lambda m: f"{m.group(1)}{to_power(m.group(2))}",
        expr
    )
    expr = re.sub(
        r"([a-zA-Z0-9\)])\^(\-?[0-9a-zA-Z\+\-π√\.\(\)]+)",
        lambda m: f"{m.group(1)}{to_power(m.group(2))}",
        expr
    )
    expr = re.sub(r"abs\((.*?)\)", replace_abs, expr)
    return expr
