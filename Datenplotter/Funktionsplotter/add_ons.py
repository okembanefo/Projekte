import re
import numpy as np
from comp_input import combine_exponents, simplify_funcs
from class_function import functions
from logic_gui import plot_functions
from sympy import symbols, sympify, diff, integrate, fourier_transform, inverse_fourier_transform, pi, exp
from comp_input import parser, rect, tri, handle_error, allowed_funcs, allowed_consts
from plot_logic import conv_to_func
from comp_input import interpreted
from class_function import colors, func_names

x, w, f = symbols('x w f')

def integration(func_obj) -> str:
    expr = func_obj.raw_expr.replace("^", "**")
    expr = parser(expr)
    expr = expr.replace("np.", "")

    try:
        sym_expr = sympify(expr)

        if not sym_expr.has(x):
            result = str(sym_expr * x) + " + C"
        else:
            result = str(integrate(sym_expr, x)) + " + C"

        func_obj.set_integral(result)
        return result

    except Exception as e:
        result = f"Fehler bei der Integration: {e}"
        func_obj.set_integral(result)
        return result

def ableitung(func_obj) -> str:
    expr = func_obj.raw_expr.replace("^", "**")
    expr = parser(expr)
    expr = expr.replace("np.", "")

    try:
        sym_expr = sympify(expr)

        if not sym_expr.has(x):
            result = "0"
        else:
            result = str(diff(sym_expr, x))

        func_obj.set_derivative(result)
        return result

    except Exception as e:
        result = f"Fehler bei der Ableitung: {e}"
        func_obj.set_derivative(result)
        return result

def fourier(func_obj):
    expr = func_obj.raw_expr.replace("^", "**")
    expr = parser(expr)
    expr = expr.replace("np.", "")

    try:
        sym_expr = sympify(expr)

        # Fourier mit w berechnen
        F_w = fourier_transform(sym_expr, x, w)

        # Falls f verwendet wird → substituieren mit w = 2πf
        F_f = F_w.subs(w, 2 * pi * f)

        result = str(F_f)

        func_obj.set_fourier(result)
        return result

    except Exception as e:
        result = f"Fehler bei der Fourier-Transformation: {e}"
        func_obj.set_fourier(result)
        return result

def rfourier(func_obj):
    expr = func_obj.raw_expr.replace("^", "**")
    expr = parser(expr)
    expr = expr.replace("np.", "")

    try:
        sym_expr = sympify(expr)

        # Rücktransformation mit f als Basis
        F_inv = inverse_fourier_transform(sym_expr, w, x)

        # Sicherstellen, dass w = 2πf berücksichtigt wird
        F_inv = F_inv.subs(w, 2 * pi * f)

        result = str(F_inv)

        func_obj.set_fourier_inverse(result)
        return result

    except Exception as e:
        result = f"Fehler bei der Rück-Fourier-Transformation: {e}"
        func_obj.set_fourier_inverse(result)
        return result

def format_number(num):
    if num.is_integer():
        return str(int(num))
    return str(num)

def process_filters(entry_widgets, canvas, ax):
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

        x_vals = np.linspace(-50, 50, 1000)
        y_vals = f(x_vals)

        if x_from_val is not None:
            mask = x_vals >= x_from_val
            x_vals = x_vals[mask]
            y_vals = y_vals[mask]

        if x_to_val is not None:
            mask = x_vals <= x_to_val
            x_vals = x_vals[mask]
            y_vals = y_vals[mask]

        if y_from_val is not None:
            mask = y_vals >= y_from_val
            x_vals = x_vals[mask]
            y_vals = y_vals[mask]

        if y_to_val is not None:
            mask = y_vals <= y_to_val
            x_vals = x_vals[mask]
            y_vals = y_vals[mask]

        if not hide:
            ax.plot(
                x_vals,
                y_vals,
                label=f"{func_name}(x) = {interpreted(func_obj.raw_expr)}",
                color=colors[func_names.index(func_name)]
            )

        func_obj.set_filter({
            "x_from": x_from_val,
            "x_to": x_to_val,
            "y_from": y_from_val,
            "y_to": y_to_val,
            "hidden": hide
        })

    ax.legend(fontsize=12)
    canvas.draw()

