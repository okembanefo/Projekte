import re
from comp_input import combine_exponents
from comp_input import simplify_funcs

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
    expr = expr.strip().replace(" ", "")

    # --- vereinfachen von sqrt, sinc und Funktionen ---
    expr = simplify_funcs(expr)

    # --- Standardfunktionen mit Vorfaktor ---
    func_pattern = r"^([+-]?\d*\.?\d*)?(sin\(x\)|cos\(x\)|tan\(x\)|exp\(x\)|log\(x\)|ln\(x\)|x\^\(1/2\)|1/x|sin\(x\)/x)$"
    match_func = re.match(func_pattern, expr)

    if match_func:
        coeff_str, func = match_func.groups()
        if coeff_str in ("", "+", None):
            coeff = 1.0
        elif coeff_str == "-":
            coeff = -1.0
        else:
            coeff = float(coeff_str)

        # Ableitung bestimmen
        if func == "x^(1/2)":
            derivative = "1/2x^(-1/2)"
        elif func == "sin(x)/x":
            # Produktregel: (u/v)' = (u'v - uv')/v^2
            derivative = "(cos(x)*x - sin(x))/x^2"
        else:
            derivative = abl_map.get(func, f"d/dx({func})")

        if derivative.startswith("-"):
            coeff *= -1
            derivative = derivative[1:]

        if coeff == 1:
            return derivative
        elif coeff == -1:
            return f"-{derivative}"
        else:
            coeff_out = int(coeff) if coeff.is_integer() else coeff
            return f"{coeff_out}{derivative}"

    # --- Potenzen mit Vorfaktor ---
    match_pow_with_coeff = re.match(r"^([+-]?\d*\.?\d*)x\^\(?([+-]?\d+(\.\d+)?)\)?$", expr)
    if match_pow_with_coeff:
        coeff_str, exponent_str, _ = match_pow_with_coeff.groups()
        coeff = (
            float(coeff_str)
            if coeff_str not in ("+", "-", "")
            else 1.0 if coeff_str in ("", "+") else -1.0
        )
        exponent = float(exponent_str)
        new_coeff = coeff * exponent
        new_exponent = exponent - 1
        if new_exponent == 1:
            return f"{int(new_coeff) if new_coeff.is_integer() else new_coeff}x"
        elif new_exponent == 0:
            return f"{int(new_coeff) if new_coeff.is_integer() else new_coeff}"
        else:
            coeff_out = int(new_coeff) if new_coeff.is_integer() else new_coeff
            return f"{coeff_out}x^{new_exponent}"

    # --- Potenzen ohne Vorfaktor ---
    match_pow = re.match(r"^x\^\(?([+-]?\d+(\.\d+)?)\)?$", expr)
    if match_pow:
        exponent = float(match_pow.group(1))
        new_coeff = exponent
        new_exponent = exponent - 1
        if new_exponent == 1:
            return f"{new_coeff}x"
        elif new_exponent == 0:
            return f"{new_coeff}"
        else:
            return f"{new_coeff}x^{new_exponent}"

    # --- Linear ---
    match_linear = re.match(r"^([+-]?\d*\.?\d*)x$", expr)
    if match_linear:
        coeff_str = match_linear.group(1)
        coeff = (
            float(coeff_str)
            if coeff_str not in ("+", "-", "")
            else 1.0 if coeff_str in ("", "+") else -1.0
        )
        return f"{int(coeff) if coeff.is_integer() else coeff}"

    # --- Konstante ---
    match_const = re.match(r"^[+-]?\d*\.?\d+$", expr)
    if match_const:
        return "0"

    return f"d/dx({expr})"