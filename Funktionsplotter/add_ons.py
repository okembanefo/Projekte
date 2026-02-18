import re
import numpy as np
from comp_input import combine_exponents, simplify_funcs
from class_function import functions
from logic_gui import plot_functions


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

def integration(func, a, b, steps=1000):
    x = np.linspace(a, b, steps)
    y = func(x)
    return np.trapz(y, x)

def ableitung(expr: str) -> str:
    expr = expr.replace(" ", "")
    expr = simplify_funcs(expr)
    expr = combine_exponents(expr)

    # Split into additive terms
    terms = re.split(r'(?=[+-])', expr)
    deriv_terms = []

    for term in terms:
        if term == "":
            continue

        # --- Potenzterm: c*x^n ---
        m = re.match(r'([+-]?\d*\.?\d*)\*?x\^([+-]?\d+(\.\d+)?)', term)
        if m:
            c_str, n_str, _ = m.groups()
            c = float(c_str) if c_str not in ("", "+", "-") else (-1.0 if c_str == "-" else 1.0)
            n = float(n_str)
            new_c = c * n
            new_n = n - 1
            coeff_out = "" if new_c == 1 else "-" if new_c == -1 else format_number(new_c)
            if new_n == 1:
                deriv_terms.append(f"{coeff_out}x")
            elif new_n == 0:
                deriv_terms.append(f"{coeff_out}")
            else:
                deriv_terms.append(f"{coeff_out}x^{format_number(new_n)}")
            continue

        # --- Lineare Terme: c*x ---
        m = re.match(r'([+-]?\d*\.?\d*)x$', term)
        if m:
            c_str = m.group(1)
            c = float(c_str) if c_str not in ("", "+", "-") else (-1.0 if c_str == "-" else 1.0)
            deriv_terms.append(format_number(c))
            continue

        # --- Funktionen in allowed_funcs ---
        for f in allowed_funcs:
            if term.startswith(f):
                inner = term[len(f):].strip("()")
                inner_deriv = ableitung(inner)
                base_deriv = allowed_funcs[f]
                if inner_deriv == "1":
                    deriv_terms.append(f"{base_deriv}({inner})")
                else:
                    deriv_terms.append(f"({inner_deriv})*{base_deriv}({inner})")
                break
        else:
            # fallback
            deriv_terms.append(term)

    result = "+".join(deriv_terms)
    result = result.replace("+-", "-").replace("-+", "-").replace("--", "+").replace("++", "+")
    return result

def format_number(num):
    if num.is_integer():
        return str(int(num))
    return str(num)

def process_filters(entry_widgets, canvas, ax):
    for func_name, widgets in entry_widgets.items():
        x_from = widgets["x_from"].get().strip()
        x_to = widgets["x_to"].get().strip()
        y_from = widgets["y_from"].get().strip()
        y_to = widgets["y_to"].get().strip()
        hide = widgets["hide"].get()
        def parse_value(val):
            if val == "":
                return None
            try:
                return float(val.replace(",", "."))
            except:
                return None
        x_from_val = parse_value(x_from)
        x_to_val = parse_value(x_to)
        y_from_val = parse_value(y_from)
        y_to_val = parse_value(y_to)
        functions[func_name].set_filter([x_from_val, x_to_val, y_from_val, y_to_val, hide])
    plot_functions(canvas, ax)
