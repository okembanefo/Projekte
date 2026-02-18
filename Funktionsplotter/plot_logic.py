import ast
import numpy as np

from comp_input import rect
from comp_input import tri

user_funcs = []

allowed_funcs = {
    "sin": np.sin,
    "cos": np.cos,
    "tan": np.tan,
    "exp": np.exp,
    "log": np.log,
    "ln" : np.log,
    "sqrt": np.sqrt,
    "arcsin": np.arcsin,
    "arccos": np.arccos,
    "arctan": np.arctan,
    "sinc": np.sinc,
    "rect": rect,
    "tri": tri
}

allowed_consts = {
    "pi": np.pi,
    "e": np.e,
    "tau": 2*np.pi
}


class SafeEvaluator(ast.NodeVisitor):
    def __init__(self, x):
        self.x = x

    def visit_Expression(self, node):
        return self.visit(node.body)

    def visit_Name(self, node):
        if node.id == "x":
            return self.x
        if node.id in allowed_consts:
            return allowed_consts[node.id]
        raise ValueError(f"Unbekannte Variable: {node.id}")

    def visit_Constant(self, node):
        return node.value

    def visit_Num(self, node):
        return node.n

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Div):
            return left / right
        if isinstance(node.op, ast.Pow):
            return left ** right
        raise ValueError("Operator nicht erlaubt")

    def visit_UnaryOp(self, node):
        operand = self.visit(node.operand)
        if isinstance(node.op, ast.UAdd):
            return +operand
        if isinstance(node.op, ast.USub):
            return -operand
        raise ValueError("Unary Operator nicht erlaubt")

    def visit_Call(self, node):
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in dir(np):
                func = getattr(np, node.func.attr)
                args = [self.visit(a) for a in node.args]
                return func(*args)
        elif isinstance(node.func, ast.Name):
            fname = node.func.id
            if fname in allowed_funcs:
                func = allowed_funcs[fname]
                args = [self.visit(a) for a in node.args]
                return func(*args)
        raise ValueError("Funktion nicht erlaubt")

    def generic_visit(self, node):
        raise ValueError(f"Nicht erlaubter Ausdruck: {type(node).__name__}")


def eval_ast(expr, x):
    tree = ast.parse(expr, mode="eval")
    evaluator = SafeEvaluator(x)
    return evaluator.visit(tree)


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


def conv_to_func(expr):
    def func(x):
        return eval_ast(expr, x)
    return func


def gen_funcs(expr, allow_compl=False, start=-10, end=10, count=1000):
    x = np.linspace(start, end, count)
    try:
        y = eval_ast(expr, x)
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
    except Exception as e:
        raise ValueError(f"Fehler bei der Auswertung: {e}")
    valid_mask = np.isfinite(y)
    x = x[valid_mask]
    y = y[valid_mask]
    return x, y
