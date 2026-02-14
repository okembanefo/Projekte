import re
import numpy as np

def rect(x, T = 1.0):
    x = np.asarray(x)
    return np.where(np.abs(x) <= T/2, 1.0, 0.0)

def tri(x, T = 1.0):
    x = np.asarray(x)
    return np.where(np.abs(x) <= T, 1.0 - np.abs(x)/T, 0.0)

spec_funcs = {
    "log10": "np.log10",
    "log2": "np.log2",
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
    "euler": "np.e",
    "tau": "(2*np.pi)"
}

superscript_map = {
    "0": "⁰",
    "1": "¹",
    "2": "²",
    "3": "³",
    "4": "⁴",
    "5": "⁵",
    "6": "⁶",
    "7": "⁷",
    "8": "⁸",
    "9": "⁹",
    "x": "ˣ",
    "-": "⁻",
}

def parser(expr: str) -> tuple:
    expr = expr.strip().replace(" ", "")

    # --- e^... ---
    expr = re.sub(r"e\^\((.*?)\)", r"np.exp(\1)", expr)
    expr = re.sub(r"e\^x\b", r"np.exp(x)", expr)
    expr = re.sub(r"e\^\s*([0-9a-zA-Z\(\)\-]+)", r"np.exp(\1)", expr)

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
        expr = re.sub(rf"\b{f}\b\((.*?)\)", rf"{spec_funcs[f]}(\1)", expr)
        expr = re.sub(rf"\b{f}\b([a-zA-Z0-9\.]+)", rf"{spec_funcs[f]}(\1)", expr)

    # --- Konstanten ---
    for c, npc in spec_cons.items():
        expr = re.sub(rf"\b{c}\b", npc, expr)

    # --- Restliche Potenzen ---
    expr = expr.replace("^", "**")

    return expr



def interpreted(expr: str) -> str:
    expr = expr.strip().replace(" ", "")

    # 1. e^... durch e^... (Basisformat) ersetzen
    def exp_replace(match):
        inner = match.group(1).replace("*", "")
        return f"e^{inner}"

    expr = re.sub(r"e\^\((.*?)\)", exp_replace, expr)
    expr = re.sub(r"e\^([0-9x\-]+)", exp_replace, expr)
    expr = re.sub(r"np\.exp\((.*?)\)", exp_replace, expr)

    # 2. Spezielle Funktionen
    funcs = sorted(spec_funcs.keys(), key=len, reverse=True)
    for f in funcs:
        expr = re.sub(rf"\b{f}\b(?=\s*\()", rf"{f}", expr)

    # 3. Hoch 1 entfernen
    expr = re.sub(r"([a-zA-Z0-9\)])\^1\b", r"\1", expr)
    expr = re.sub(r"([a-zA-Z0-9\)])\*\*1\b", r"\1", expr)

    # 4. Superscript-Formatierung inkl. negative Exponenten
    def sup_replace(match):
        base, power = match.groups()

        # Klammern entfernen bei ^(-2)
        power = power.strip("()")

        sup = "".join(superscript_map.get(ch, ch) for ch in power)
        return f"{base}{sup}"

    expr = re.sub(r"([a-zA-Z0-9\)])\^(\-?\d+|\-?x|\(\-?\d+\))", sup_replace, expr)
    expr = re.sub(r"([a-zA-Z0-9\)])\*\*(\-?\d+|\-?x|\(\-?\d+\))", sup_replace, expr)

    # 5. Multiplikationszeichen entfernen
    expr = re.sub(r"(\d+)(\*([a-zA-Z\(]))", lambda m: m.group(1) + m.group(3), expr)

    # 6. Konstanten
    expr = expr.replace("np.pi", "π").replace("np.e", "e").replace("(2*np.pi)", "τ")

    return expr
