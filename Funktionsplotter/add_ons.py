import re
import numpy as np
from comp_input import combine_exponents, simplify_funcs
from class_function import functions
from logic_gui import plot_functions
from sympy import symbols, sympify, diff, integrate
from comp_input import parser, rect, tri, handle_error, allowed_funcs, allowed_consts
from plot_logic import conv_to_func
from comp_input import interpreted
from class_function import colors, func_names

x = symbols('x')

def integration(expr: str) -> str:
    expr = expr.replace("^", "**")
    expr = parser(expr)

    expr = expr.replace("np.", "")

    try:
        sym_expr = sympify(expr)
        integral = integrate(sym_expr, x)
        return str(integral) + " + C"
    except Exception as e:
        return f"Fehler bei der Integration: {e}"


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
    # --- Alte Funktionsplots löschen, Achsen bleiben ---
    for line in ax.lines:
        line.remove()

    for func_name, widgets in entry_widgets.items():
        x_from_str = widgets["x_from"].get().strip()
        x_to_str = widgets["x_to"].get().strip()
        y_from_str = widgets["y_from"].get().strip()
        y_to_str = widgets["y_to"].get().strip()
        hide = widgets["hide"].get()

        def parse_value(val):
            if val == "":
                return None
            try:
                return float(interpreted(val))
            except:
                return None

        x_from_val = parse_value(x_from_str)
        x_to_val = parse_value(x_to_str)
        y_from_val = parse_value(y_from_str)
        y_to_val = parse_value(y_to_str)

        func_obj = functions[func_name]
        f = conv_to_func(func_obj.parsed_expr)

        x = np.linspace(-50, 50, 1000)
        y = f(x)

        # --- Filter anwenden ---
        if x_from_val is not None:
            mask = x >= x_from_val
            x = x[mask]
            y = y[mask]
        if x_to_val is not None:
            mask = x <= x_to_val
            x = x[mask]
            y = y[mask]
        if y_from_val is not None:
            mask = y >= y_from_val
            x = x[mask]
            y = y[mask]
        if y_to_val is not None:
            mask = y <= y_to_val
            x = x[mask]
            y = y[mask]

        if not hide:
            ax.plot(x, y, label=f"{func_name} = {interpreted(func_obj.raw_expr)}", color=colors[func_names.index(func_name)])

    # Achsenlinien, Ticks etc. bleiben erhalten, nur Legend aktualisieren
    ax.legend(fontsize=12)
    canvas.draw()

