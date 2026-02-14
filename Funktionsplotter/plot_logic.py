#!/usr/bin/python3
import numpy as np
from comp_input import parser
from comp_input import rect
from comp_input import tri

user_funcs = []

def gen_werte(func, allow_compl=False, start=-10, end=10, count=1000):
    x = np.linspace(start, end, count)
    with np.errstate(divide='ignore', invalid='ignore', over='ignore'):
        y = eval(func, {"np": np}, {"x": x})

        if np.isscalar(y):
            y = np.full_like(x, y, dtype=float)

        y = np.array(y)

        if np.iscomplexobj(y):
            if allow_compl:
                y = np.real(y)
            else:
                valid_mask = np.imag(y) == 0
                x = x[valid_mask]
                y = np.real(y[valid_mask])

        y = y.astype(float)

        valid_mask = np.isfinite(y)
        x = x[valid_mask]
        y = y[valid_mask]

    return x, y


def gen_funcs(expr, allow_compl=False, start=-10, end=10, count=1000):
    x = np.linspace(start, end, count)

    # Überprüfe, ob der Ausdruck eine Konstante ist
    if 'x' not in expr:
        try:
            const_value = float(eval(expr, {"__builtins__": None}, {'np': np, 'e': np.e}))
            y = np.full_like(x, const_value, dtype=float)
        except Exception as e:
            raise ValueError(f"Fehler bei der Auswertung der Konstanten: {e}")
    else:
        eval_namespace = {
            'np': np,
            'x': x,
            'rect': rect,
            'tri': tri,
            'e': np.e
        }

        try:
            y = eval(expr, {"__builtins__": None}, eval_namespace)
        except Exception as e:
            raise ValueError(f"Fehler bei der Auswertung: {e}")

    y = np.array(y)

    if np.isscalar(y):
        y = np.full_like(x, y, dtype=float)

    if np.iscomplexobj(y):
        if allow_compl:
            y = np.real(y)
        else:
            valid_mask = np.isreal(y)
            x = x[valid_mask]
            y = np.real(y[valid_mask])

    y = y.astype(float)

    # Entferne unendliche Werte und NaNs
    valid_mask = np.isfinite(y)
    x = x[valid_mask]
    y = y[valid_mask]

    return x, y