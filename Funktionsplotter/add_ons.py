import re
import numpy as np
from comp_input import combine_exponents, simplify_funcs
from class_function import functions
from logic_gui import plot_functions
from sympy import symbols, sympify, diff
from comp_input import parser, rect, tri, handle_error, allowed_funcs, allowed_consts

x = symbols('x')

def integration(func, a, b, steps=1000):
    x = np.linspace(a, b, steps)
    y = func(x)
    return np.trapz(y, x)

def ableitung(expr: str) -> str:
    expr = expr.replace("^", "**")
    expr = parser(expr)

    expr = expr.replace("np.", "")

    try:
        sym_expr = sympify(expr)
        deriv = diff(sym_expr, x)
        return str(deriv)
    except Exception as e:
        return f"Fehler bei der Ableitung: {e}"


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
