import re
import numpy as np
from comp_input import combine_exponents
from comp_input import simplify_funcs

abl_map = {
    "sinc(x)": "(pi*x*cos(pi*x)-sin(pi*x))/(pi*x^2)",
    "sin(x)": "cos(x)",
    "cos(x)": "-sin(x)",
    "tan(x)": "1/cos(x)**2",
    "exp(x)": "exp(x)",
    "log(x)": "1/x",
    "ln(x)": "1/x",
    "sqrt(x)": "1/2*x^(-1/2)",
    "1/x": "-1/x**2"
}

def simplify_funcs(expr: str) -> str:
    expr = expr.strip()

    def sqrt_replace(match):
        factor = match.group(1) or ""  # Vorfaktor: 3*, -, + oder leer
        inner = match.group(2)         # Inhalt der sqrt
        factor = factor.rstrip("*")    # Entferne ggf. * am Ende
        if factor in ("", "+"):
            return f"({inner})^(1/2)"
        elif factor == "-":
            return f"-({inner})^(1/2)"
        else:
            return f"{factor}*({inner})^(1/2)"

    # Suche nach optionalem Vorfaktor und sqrt
    expr = re.sub(r"([+-]?\d*\*?)?sqrt\((.*?)\)", sqrt_replace, expr)

    # --- trigonometrische Funktionen unverändert lassen ---
    trig_funcs = ["sin", "cos", "tan", "exp", "ln", "log"]
    for f in trig_funcs:
        pattern = rf"([+-]?\d*\.?\d*)\*?{f}\((.*?)\)"
        def func_replace(match, func=f):
            coeff = match.group(1)
            inner = match.group(2)
            if coeff in ("", "+", None):
                coeff = ""
            elif coeff == "-":
                coeff = "-"
            return f"{coeff}{func}({inner})"
        expr = re.sub(pattern, func_replace, expr)

    return expr

def format_number(num):
    if num.is_integer():
        return str(int(num))
    return str(num)

def integration(func, a, b, steps=1000):
    x = np.linspace(a, b, steps)
    y = func(x)
    return np.trapz(y, x)

def ableitung(expr: str) -> str:
    expr = expr.replace(" ", "")
    expr = simplify_funcs(expr)
    terms = re.split(r'(?=[+-])', expr)
    result_terms = []

    for term in terms:
        if term == "":
            continue

        # --- Potenzen x^(n) (inkl. negative) ---
        power_match = re.match(r'([+-]?\d*\.?\d*)\*?\(?(.+?)\)?\^([+-]?\d*\.?\d+)', term)
        if power_match:
            coeff_str, base, power_str = power_match.groups()
            coeff = float(coeff_str) if coeff_str not in ("", "+", "-") else (-1.0 if coeff_str == "-" else 1.0)
            power = float(power_str)
            new_coeff = coeff * power
            new_power = power - 1
            coeff_out = "" if new_coeff == 1 else "-" if new_coeff == -1 else format_number(new_coeff)
            if new_power == 1:
                result_terms.append(f"{coeff_out}{base}")
            elif new_power == 0:
                result_terms.append(f"{coeff_out}")
            else:
                result_terms.append(f"{coeff_out}{base}^{format_number(new_power)}")
            continue

        # --- lineare Terme k*x ---
        linear_match = re.match(r'([+-]?\d*\.?\d*)x$', term)
        if linear_match:
            coeff_str = linear_match.group(1)
            coeff = float(coeff_str) if coeff_str not in ("", "+", "-") else (-1.0 if coeff_str == "-" else 1.0)
            result_terms.append(format_number(coeff))
            continue

        # --- trigonometrische Funktionen mit Kettenregel ---
        trig_match = re.match(r'([+-]?\d*\.?\d*)?(sin|cos|tan)\((.+)\)', term)
        if trig_match:
            coeff_str, func, inner = trig_match.groups()
            coeff = float(coeff_str) if coeff_str not in ("", "+", "-") else (-1.0 if coeff_str == "-" else 1.0)
            inner_deriv = ableitung(inner)  # Kettenregel
            base_deriv = abl_map[func]
            # Vorfaktor multiplizieren
            if inner_deriv == "1":
                result_terms.append(f"{format_number(coeff)}{base_deriv}({inner})" if coeff != 1 else f"{base_deriv}({inner})")
            else:
                result_terms.append(f"{format_number(coeff)}*({inner_deriv})*{base_deriv}({inner})" if coeff != 1 else f"({inner_deriv})*{base_deriv}({inner})")
            continue

        # --- ln(kx) ---
        ln_match = re.match(r'([+-]?\d*\.?\d*)?ln\((.+)\)', term)
        if ln_match:
            coeff_str, inner = ln_match.groups()
            coeff = float(coeff_str) if coeff_str not in ("", "+", "-") else (-1.0 if coeff_str == "-" else 1.0)
            inner_deriv = ableitung(inner)
            result_terms.append(f"{format_number(coeff)}*({inner_deriv})/({inner})" if coeff != 1 else f"({inner_deriv})/({inner})")
            continue

        # --- exp(...) ---
        exp_match = re.match(r'([+-]?\d*\.?\d*)?exp\((.+)\)', term)
        if exp_match:
            coeff_str, inner = exp_match.groups()
            coeff = float(coeff_str) if coeff_str not in ("", "+", "-") else (-1.0 if coeff_str == "-" else 1.0)
            inner_deriv = ableitung(inner)
            if inner_deriv == "1":
                inner_part = ""
            else:
                inner_part = f"({inner_deriv})*"
            result_terms.append(f"{format_number(coeff)}*{inner_part}exp({inner})" if coeff != 1 else f"{inner_part}exp({inner})")
            continue

        # --- x einzeln ---
        if term in ("x", "+x"):
            result_terms.append("1")
            continue
        if term == "-x":
            result_terms.append("-1")
            continue

        # --- Konstanten ---
        if re.fullmatch(r'[+-]?\d+\.?\d*', term):
            result_terms.append("0")
            continue

        # fallback
        result_terms.append(term)

    result = "+".join(result_terms)
    result = result.replace("+-", "-").replace("--", "+").replace("+ -", "-")
    return result