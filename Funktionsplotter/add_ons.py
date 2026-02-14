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

def simplify_funcs(expr: str) -> str:
    expr = expr.strip()
    expr = re.sub(r"([+-]?\d*\.?\d*)?\*?sqrt\((x)\)", lambda m: (m.group(1) or "") + "x^(1/2)", expr)
    funcs = ["sin", "cos", "tan", "exp", "ln", "log"]
    for f in funcs:
        pattern = rf"([+-]?\d*\.?\d*)?\*?{f}\((x)\)"
        expr = re.sub(pattern, lambda m, func=f: (m.group(1) or "") + f"{func}(x)", expr)
    return expr

def ableitung(expr: str) -> str:

    expr = expr.replace(" ", "")
    terms = re.split(r'(?=[+-])', expr)

    result_terms = []

    for term in terms:
        if term == "":
            continue

        # --- x^n ---
        power_match = re.match(r'([+-]?\d*\.?\d*)x\^(\d+)', term)
        if power_match:
            coeff_str, power_str = power_match.groups()

            coeff = float(coeff_str) if coeff_str not in ("", "+", "-") else (
                -1.0 if coeff_str == "-" else 1.0
            )
            power = int(power_str)

            new_coeff = coeff * power
            new_power = power - 1

            if new_coeff == 1:
                coeff_out = ""
            elif new_coeff == -1:
                coeff_out = "-"
            else:
                coeff_out = str(int(new_coeff) if new_coeff.is_integer() else new_coeff)

            if new_power == 1:
                result_terms.append(f"{coeff_out}x")
            elif new_power == 0:
                result_terms.append(f"{coeff_out}")
            else:
                result_terms.append(f"{coeff_out}x^{new_power}")

            continue

        # --- kx ---
        linear_match = re.match(r'([+-]?\d*\.?\d*)x$', term)
        if linear_match:
            coeff_str = linear_match.group(1)

            coeff = float(coeff_str) if coeff_str not in ("", "+", "-") else (
                -1.0 if coeff_str == "-" else 1.0
            )

            if coeff == 1:
                result_terms.append("1")
            elif coeff == -1:
                result_terms.append("-1")
            else:
                coeff_out = str(int(coeff) if coeff.is_integer() else coeff)
                result_terms.append(coeff_out)

            continue

        # --- ln(kx) ---
        ln_match = re.match(r'([+-]?\d*\.?\d*)?ln\((\d*)x\)', term)
        if ln_match:
            coeff_str, inner_coeff_str = ln_match.groups()

            coeff = float(coeff_str) if coeff_str not in ("", "+", "-") else (
                -1.0 if coeff_str == "-" else 1.0
            )
            inner_coeff = float(inner_coeff_str) if inner_coeff_str != "" else 1.0

            new_coeff = coeff * inner_coeff
            denom = "x" if inner_coeff == 1 else f"{int(inner_coeff)}x"

            if new_coeff == 1:
                result_terms.append(f"1/{denom}")
            elif new_coeff == -1:
                result_terms.append(f"-1/{denom}")
            else:
                coeff_out = str(int(abs(new_coeff))) if abs(new_coeff).is_integer() else str(abs(new_coeff))
                sign = "-" if new_coeff < 0 else ""
                if denom == "x":
                    result_terms.append(f"{sign}{coeff_out}/x")
                else:
                    result_terms.append(f"{sign}{coeff_out}/({denom})")

            continue

        # --- exp(allgemein) ---
        exp_match = re.match(r'([+-]?\d*\.?\d*)?exp\((.+)\)', term)
        if exp_match:
            coeff_str, inner = exp_match.groups()

            coeff = float(coeff_str) if coeff_str not in ("", "+", "-") else (
                -1.0 if coeff_str == "-" else 1.0
            )

            inner_deriv = ableitung(inner)

            # nur Klammern setzen, wenn inner_deriv mehr als 1 Zeichen enthält
            if inner_deriv == "1":
                inner_part = ""
            elif len(inner_deriv) > 1:
                inner_part = f"({inner_deriv})*"
            else:
                inner_part = f"{inner_deriv}*"

            if coeff == 1:
                coeff_out = ""
            elif coeff == -1:
                coeff_out = "-"
            else:
                coeff_out = str(int(coeff) if coeff.is_integer() else coeff)

            result_terms.append(f"{coeff_out}{inner_part}exp({inner})")
            continue

        # --- trig ---
        func_match = re.match(r'([+-]?\d*\.?\d*)?(sin|cos|tan)\((\d*)x\)', term)
        if func_match:
            coeff_str, func, inner_coeff_str = func_match.groups()

            coeff = float(coeff_str) if coeff_str not in ("", "+", "-") else (
                -1.0 if coeff_str == "-" else 1.0
            )
            inner_coeff = float(inner_coeff_str) if inner_coeff_str != "" else 1.0

            new_coeff = coeff * inner_coeff
            base_deriv = abl_map[f"{func}(x)"]

            if base_deriv.startswith("-"):
                base_deriv = base_deriv[1:]
                new_coeff *= -1

            if new_coeff == 1:
                coeff_out = ""
            elif new_coeff == -1:
                coeff_out = "-"
            else:
                coeff_out = str(int(new_coeff) if new_coeff.is_integer() else new_coeff)

            result_terms.append(f"{coeff_out}{base_deriv}")
            continue

        # --- x ---
        if term in ("x", "+x"):
            result_terms.append("1")
            continue
        if term == "-x":
            result_terms.append("-1")
            continue

        # --- Konstante ---
        if re.fullmatch(r'[+-]?\d+\.?\d*', term):
            result_terms.append("0")
            continue

        result_terms.append(term)

    result = " + ".join(result_terms)
    result = result.replace("+ -", "- ")
    result = result.replace("+-", "-")
    result = result.replace("++", "+")
    result = result.replace("--", "+")

    return result
