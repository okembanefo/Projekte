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

def conv_to_func(expr):

    expr = parser(expr)  

    def func(x):
        local_dict = {'x': x, 'np': np, 'rect': rect, 'tri': tri}
        return eval(expr, {}, local_dict)

    return func


def gen_funcs(expr, allow_compl=False, start=-10, end=10, count=1000):
    x = np.linspace(start, end, count)
    local_dict = {'np': np, 'x': x, 'rect': rect, 'tri': tri}

    try:
        # Prüfen, ob die Funktion x enthält
        if 'x' not in expr:
            # Konstante Funktion: eval einmal, dann auf x ausweiten
            y_val = eval(expr, {}, local_dict)
            y = np.full_like(x, y_val, dtype=float)
        else:
            # Normale Funktion, x im Ausdruck vorhanden
            y = eval(expr, {}, local_dict)
            y = np.array(y)

            # Falls y ein Skalar entsteht, auf x ausweiten
            if np.isscalar(y):
                y = np.full_like(x, y, dtype=float)

            # Komplexwerte behandeln
            if np.iscomplexobj(y):
                if allow_compl:
                    y = np.real(y)
                else:
                    valid_mask = np.imag(y) == 0
                    x = x[valid_mask]
                    y = np.real(y[valid_mask])

    except Exception as e:
        raise ValueError(f"Fehler bei der Auswertung: {e}")

    # Endgültig nur finite Werte behalten
    valid_mask = np.isfinite(y)
    x = x[valid_mask]
    y = y[valid_mask]

    return x, y
