import re
import numpy as np

def rect(x, T = 1.0):
    x = np.asarray(x)
    return np.where(np.abs(x) <= T/2, 1.0, 0.0)

def tri(x, T = 1.0):
    x = np.asarray(x)
    return np.where(np.abs(x) <= T, 1.0 - np.abs(x)/T, 0.0)

spec_funcs = {
    "sinc": "np.sinc",
    "sin": "np.sin",
    "cos": "np.cos",
    "tan": "np.tan",
    "exp": "np.exp",
    "log": "np.log",
    "sqrt": "np.sqrt",
    "arcsin": "np.arcsin",
    "arccos": "np.arccos",
    "arctan": "np.arctan",
    "ln": "np.log",
    "rect": "rect",
    "tri": "tri"
}

spec_cons = {
    "pi": "np.pi",
    "e": "np.e",
    "tau": "(2*np.pi)"
}

subs_map = {
    "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴",
    "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹",
    "-": "⁻", "+": "⁺", ".": "·",
    "x": "ˣ", "y": "ʸ", "n": "ⁿ",
    "(": "⁽", ")": "⁾"
}

def simplify_funcs(expr: str) -> str:

    expr = expr.strip()

    # --- 1. sqrt(x) vereinfachen ---
    def sqrt_replace(match):
        coeff = match.group(1)
        if coeff is None or coeff in ("", "+"):
            coeff = ""
        elif coeff == "-":
            coeff = "-"
        return f"{coeff}x^(1/2)"
    expr = re.sub(r"([+-]?\d*\.?\d*)?\*?sqrt\((x)\)", sqrt_replace, expr)

    # --- 2. Trigonometrische Funktionen mit Vorfaktor ---
    trig_funcs = ["sin", "cos", "tan", "exp", "ln", "log"]  # ggf. erweitern
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
    # Multiplikation gleicher Basen: x**a * x**b -> x**(a+b)
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

    # Division gleicher Basen: x**a / x**b -> x**(a-b)
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

    if re.search(r"(^|[^a-zA-Z])e\^", expr):
        raise ValueError("Bitte verwende exp(x) statt e^x oder e^(...).")

    # --- exp(...) schützen → Platzhalter ---
    expr = re.sub(r"\bexp\((.*?)\)", r"__EXP__(\1)", expr)

    # --- Negative Exponenten normalisieren ---
    expr = re.sub(r"\^\(\s*-\s*([0-9a-zA-Z]+)\s*\)", r"**(-\1)", expr)
    expr = re.sub(r"\^\-\s*([0-9a-zA-Z]+)", r"**(-\1)", expr)

    # --- Implizite Multiplikation ---
    expr = re.sub(r"(\d)(x)", r"\1*x", expr)
    expr = re.sub(r"(\d)([a-zA-Z])", r"\1*\2", expr)
    expr = re.sub(r"(x)([a-zA-Z])", r"\1*\2", expr)
    expr = re.sub(r"(\d|x)\(", r"\1*(", expr)
    expr = re.sub(r"\)(\d|x)", r")*\1", expr)

    # --- Funktionen ---
    funcs = sorted(spec_funcs.keys(), key=len, reverse=True)
    for f in funcs:
        if f == "exp":
            continue
        expr = re.sub(rf"\b{f}\b\((.*?)\)", rf"{spec_funcs[f]}(\1)", expr)
        expr = re.sub(rf"\b{f}\b([a-zA-Z0-9\.]+)", rf"{spec_funcs[f]}(\1)", expr)

    # --- Konstanten (e nur isoliert!) ---
    expr = re.sub(r"(?<![a-zA-Z])pi(?![a-zA-Z])", "np.pi", expr)
    expr = re.sub(r"(?<![a-zA-Z])tau(?![a-zA-Z])", "(2*np.pi)", expr)
    expr = re.sub(r"(?<![a-zA-Z])euler(?![a-zA-Z])", "np.e", expr)
    expr = re.sub(r"(?<![a-zA-Z])e(?![a-zA-Z])", "np.e", expr)

    # --- exp Platzhalter zurückwandeln ---
    expr = re.sub(r"__EXP__\((.*?)\)", r"np.exp(\1)", expr)

    # --- Restliche Potenzen ---
    expr = expr.replace("^", "**")

    # --- Exponenten zusammenfassen ---
    expr = combine_exponents(expr)

    return expr


def interpreted(expr: str) -> str:
    expr = expr.strip().replace(" ", "")
    expr = expr.replace(".", ",") 

    # Nur direkte Benutzereingabe: pi → π, tau → τ
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

    # exp(...) und e^(...) in Hochzahlen umwandeln
    expr = re.sub(r"exp\((.*?)\)", replace_exp, expr)
    expr = re.sub(r"e\^\((.*?)\)", replace_exp, expr)
    expr = re.sub(r"e\^([0-9a-zA-Zπ√\+\-\.\(\)]+)", replace_exp, expr)

    # Wurzeln direkt ersetzen
    expr = re.sub(r"sqrt\((.*?)\)", lambda m: sqrt_replace(m.group(1)), expr)

    # Multiplikationszeichen entfernen
    expr = re.sub(r"(\d+)\*([a-zA-Z\(])", lambda m: m.group(1) + m.group(2), expr)

    # Hochzahlen (**) oder ^
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

    return expr