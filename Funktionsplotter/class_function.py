import numpy as np
from comp_input import parser, interpreted

max_funcs = 10
func_names = [
    'f(x)', 'g(x)', 'h(x)', 'j(x)', 'k(x)',
    'l(x)', 'n(x)', 'm(x)', 'r(x)', 't(x)'
]
colors = [
    "springgreen", "coral", "magenta", "gold",
    "mediumslateblue", "turquoise", "indigo",
    "olive", "crimson", "lightpink"
]

x_range_kord = [-10, 10]
y_range_kord = [-10, 10]
count_points = 50000
axis_in_radians = False
show_positive_only = False
is_panning = False
pan_start_x = 0
pan_start_y = 0
pan_x_range = [0, 0]
pan_y_range = [0, 0]

x_ax_min = -1000
x_ax_max = 1000
y_ax_min = -1000
y_ax_max = 1000

pan_sen = 0.3
pan_state = {
    "press": None,
    "xlim": None,
    "ylim": None
}

class Funktion:
    def __init__(self, name, raw_expr):
        self.name = name
        self.raw_expr = raw_expr
        self.interpreted_expr = interpreted(raw_expr)
        self.parsed_expr = parser(raw_expr)
        self.derivative_raw = None
        self.filter_values = None

    def update(self, new_raw):
        self.raw_expr = new_raw
        self.interpreted_expr = interpreted(new_raw)
        self.parsed_expr = parser(new_raw)

    def set_derivative(self, deriv_raw):
        self.derivative_raw = deriv_raw

    def set_filter(self, values):
        self.filter_values = values

    def __repr__(self):
        return (
            f"Funktion(\n"
            f"  name='{self.name}',\n"
            f"  raw='{self.raw_expr}',\n"
            f"  interpreted='{self.interpreted_expr}',\n"
            f"  parsed='{self.parsed_expr}',\n"
            f"  derivative='{self.derivative_raw}',\n"
            f"  filter={self.filter_values}\n"
            f")"
        )

functions = {}
