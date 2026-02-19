import numpy as np
from comp_input import parser, interpreted, handle_error


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

functions = {}
filter_funcs = {}  
entry_widgets = {}


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
    id_counter = 0 

    def __init__(self, name, raw_expr):
        self.id = Funktion.id_counter  
        Funktion.id_counter += 1

        self.name = name
        self.raw_expr = raw_expr
        self.parsed_expr = parser(raw_expr)  
        self.interpreted_expr = interpreted(raw_expr)  

        self.derivative_raw = None
        self.integral_raw = None   
        self.filter_values = None

    def update(self, new_raw):
        self.raw_expr = new_raw
        self.interpreted_expr = interpreted(new_raw)
        self.parsed_expr = parser(new_raw)

        self.derivative_raw = None
        self.integral_raw = None

    def set_derivative(self, deriv_raw):
        self.derivative_raw = deriv_raw

    def set_integral(self, integral_raw):   
        self.integral_raw = integral_raw

    def set_filter(self, values):
        self.filter_values = values

    def __repr__(self):
        return (
            f"Funktion(name='{self.name}', raw_expr='{self.raw_expr}', "
            f"interpreted_expr='{self.interpreted_expr}', parsed_expr='{self.parsed_expr}', "
            f"derivative_raw='{self.derivative_raw}', integral_raw='{self.integral_raw}', "
            f"filter_values={self.filter_values}, id={self.id})"
        )

