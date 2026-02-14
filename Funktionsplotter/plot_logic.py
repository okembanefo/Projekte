#!/usr/bin/python3
import numpy as np
from funktion_parser import parser
from funktion_parser import rect
from funktion_parser import tri

user_funcs = []

def gen_werte(func, allow_compl=False, start=-10, end=10, count=1000):
    x = np.linspace(start, end, count)

    with np.errstate(divide='ignore', invalid='ignore', over='ignore'):
        y = eval(func, {"__builtins__": None}, {"x": x, "np": np})

        if np.isscalar(y):
            y = np.full_like(x, y, dtype=float)

        y = np.array(y)

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


def gen_funcs(expr, allow_compl=False, start=-10, end=10, count=1000):
    x = np.linspace(start, end, count)

    eval_namespace = {
        'np': np,
        'x': x,
        'rect': rect,
        'tri': tri
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
