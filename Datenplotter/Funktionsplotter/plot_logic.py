import ast
import numpy as np
from comp_input import eval_ast, SafeEvaluator, handle_error, rect, tri, delta

user_funcs = []


def gen_werte(func, allow_compl=False, start=-10, end=10, count=1000):
    x = np.linspace(start, end, count)
    with np.errstate(divide='ignore', invalid='ignore', over='ignore'):
        y = eval_ast(func, x)
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

def conv_to_func(expr, allow_compl: bool = False):
    def func(x):
        x = np.asarray(x)

        with np.errstate(divide='ignore', invalid='ignore', over='ignore'):
            y = eval_ast(expr, x)

            if np.isscalar(y):
                y = np.full_like(x, y, dtype=float)
            else:
                y = np.asarray(y)

            if np.iscomplexobj(y):
                if allow_compl:
                    y = np.real(y)
                else:
                    mask = np.imag(y) == 0
                    y = np.where(mask, np.real(y), np.nan)

            y = y.astype(float)

            return y

    return func
    
def gen_funcs(expr: str, allow_compl: bool = False, start: float = -10, end: float = 10, count: int = 1000) -> tuple[np.ndarray, np.ndarray]:

    try:
        x = np.linspace(start, end, count)
        y = eval_ast(expr, x)

        # Skalare y-Werte in Arrays umwandeln
        if np.isscalar(y):
            y = np.full_like(x, y, dtype=float)

        # Komplexe Werte behandeln
        if np.iscomplexobj(y):
            if allow_compl:
                y = np.real(y)
            else:
                valid_mask = np.imag(y) == 0
                x = x[valid_mask]
                y = np.real(y[valid_mask])

        # Ungültige Werte entfernen
        valid_mask = np.isfinite(y)
        x = x[valid_mask]
        y = y[valid_mask]

        return x, y

    except ValueError as e:
        return
    except Exception as e:
        return
