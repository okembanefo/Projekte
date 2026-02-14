import re

abl_map = {
    "sin(x)": "cos(x)",
    "cos(x)": "-sin(x)",
    "tan(x)": "1/cos(x)**2",
    "exp(x)": "exp(x)",
    "log(x)": "1/x",
    "ln(x)": "1/x",
    "sqrt(x)": "1/(2*sqrt(x))",
    "1/x": "-1/x**2"
}

def ableitung(expr: str) -> str:
    """Berechnet die Ableitung eines Ausdrucks als String."""
    expr = expr.strip().replace(" ", "")

    # Faktorableitung: x^n -> n*x**(n-1)
    def pow_deriv(match):
        base, exp = match.groups()
        return f"{exp}*{base}**{int(exp)-1}"

    expr = re.sub(r"(x)\*\*(\d+)", pow_deriv, expr)

    if expr in abl_map:
        return abl_map[expr]

    # e^(...) als spezielle Kette
    match_exp = re.match(r"exp\((.*)\)", expr)
    if match_exp:
        inner = match_exp.group(1)
        # Kettenregel: (e^u)' = u'*e^u
        return f"({ableitung(inner)})*exp({inner})" if inner != "x" else "exp(x)"

    # Default: zurückgeben, dass Ableitung unbekannt ist
    return f"d/dx({expr})"
