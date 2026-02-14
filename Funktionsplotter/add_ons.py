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
    expr = simplify_funcs(expr)

    def split_terms(e):
        terms, bracket_level, current = [], 0, ""
        for i, c in enumerate(e):
            if c == '(':
                bracket_level += 1
            elif c == ')':
                bracket_level -= 1
            if c in '+-' and bracket_level == 0 and i != 0:
                terms.append(current)
                current = c
            else:
                current += c
        terms.append(current)
        return terms

    def parse_factor_and_inner(term):
        match = re.match(r'^([+-]?\d*\.?\d*)?([a-zA-Z]+\(.+\)|x\^\(?[0-9./+-]+\)?|x|1/x)$', term)
        if match:
            coeff_str, inner = match.groups()
            if coeff_str in ("", "+", None):
                coeff = 1.0
            elif coeff_str == "-":
                coeff = -1.0
            else:
                coeff = float(coeff_str)
            return coeff, inner
        return 1.0, term

    def extract_inner_factor(inner):
        match = re.match(r'^([+-]?\d*\.?\d*)\*?x$', inner)
        if match:
            factor_str = match.group(1)
            if factor_str in ("", "+"):
                return 1.0
            elif factor_str == "-":
                return -1.0
            else:
                return float(factor_str)
        match = re.match(r'^x/([+-]?\d*\.?\d+)$', inner)
        if match:
            return 1/float(match.group(1))
        return 1.0

    def derivative_func(inner, coeff=1.0):
        # Potenzen x^n
        match_pow = re.match(r'^x\^\(?([+-]?\d+(\.\d+)?)\)?$', inner)
        if match_pow:
            exp = float(match_pow.group(1))
            total_coeff = coeff * exp
            new_exp = exp - 1
            if new_exp == 0:
                return f"{total_coeff:g}"
            elif new_exp == 1:
                return f"{total_coeff:g}x"
            else:
                exp_str = str(int(new_exp)) if new_exp.is_integer() else f"({new_exp})"
                return f"{total_coeff:g}x^{exp_str}"

        # Standardfunktionen aus abl_map
        if inner in abl_map:
            der = abl_map[inner]
            return f"{coeff:g}*{der}" if coeff != 1 else der

        # Verschachtelte Funktionen f(g(x)) → Kettenregel
        func_match = re.match(r'([a-zA-Z]+)\((.+)\)', inner)
        if func_match:
            f, g = func_match.groups()
            inner_factor = extract_inner_factor(g)
            total_coeff = coeff * inner_factor
            outer = abl_map.get(f"{f}(x)", None)
            if outer:
                outer = outer.replace("x", g)
                return f"{total_coeff:g}*{outer}"  # d_g entfällt, inner_factor ist schon multipliziert
            else:
                return f"{total_coeff:g}*d/dx({inner})"

        if inner == "x":
            return f"{coeff:g}"
        if re.fullmatch(r'[+-]?\d+(\.\d+)?', inner):
            return "0"
        return f"{coeff:g}*d/dx({inner})"

    terms = split_terms(expr)
    derivatives = []
    for term in terms:
        if not term:
            continue
        coeff, inner = parse_factor_and_inner(term)
        derivatives.append(derivative_func(inner, coeff))

    return '+'.join(derivatives).replace('+-','-')