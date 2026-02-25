import numpy as np
from comp_input import parser, interpreted, handle_error


max_funcs = 5
func_names = [
    'f', 'g', 'h', 'j', 'k',
    'l', 'm', 'n', 'r', 't',
    'u', 'v', 'w', 'x', 'y', 'z'
]

color_palettes = [
    # Hell 
    [
        "#E0E0E0",
        "#D8C3A5",
        "#D2A679",
        "#C9A0DC",
        "#B0C4FF",
        "#A8E6E6",
        "#A8D8A8",
        "#D8D8A0",
        "#E6C7A0",
        "#CFCFCF"
    ],

    # Dunkel 
    [
        "#2A2A2A",
        "#4A4A4A",
        "#5C4033",
        "#6B3E75",
        "#3A4F7A",
        "#2F6F6F",
        "#2F5F2F",
        "#4F5F2F",
        "#5F4F2F",
        "#3A3A3A"
    ],

    # Pastell 
    [
        "#FF8A8A",
        "#FFB347",
        "#FFD966",
        "#B5EAD7",
        "#C7CEEA",
        "#A8D5BA",
        "#D4A5A5",
        "#CDB4DB",
        "#FFC6FF",
        "#9AD1D4"
    ],

    # Neon 
    [
        "#FF00FF",
        "#FF0066",
        "#FF6600",
        "#FFFF00",
        "#66FF00",
        "#00FF66",
        "#00FFFF",
        "#0066FF",
        "#6600FF",
        "#FF3300"
    ],

    # Natur 
    [
        "#8B5E3C",
        "#A67C52",
        "#C2B280",
        "#556B2F",
        "#2E8B57",
        "#3B6B8F",
        "#6B8E23",
        "#5A4A42",
        "#4B6A4B",
        "#7D5A4A"
    ]
]

color_palette_names = [
    "Hell",
    "Dunkel",
    "Pastell",
    "Neon",
    "Natur"
]

palette_index = 0 

colors = color_palettes[palette_index]
color_circles = []

functions = {}
filter_funcs = {}  
entry_widgets = {}

x_range_kord = [-10, 10]
y_range_kord = [-10, 10]
count_points = 35000
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
        self.fourier_raw = None
        self.rfourier_raw = None
        self.filter_values = None

    def update(self, new_raw):
        self.raw_expr = new_raw
        self.interpreted_expr = interpreted(new_raw)
        self.parsed_expr = parser(new_raw)

        self.derivative_raw = None
        self.integral_raw = None
        self.fourier_raw = None
        self.rfourier_raw = None

    def set_derivative(self, deriv_raw):
        self.derivative_raw = deriv_raw

    def set_integral(self, integral_raw):   
        self.integral_raw = integral_raw

    def set_fourier(self, fourier_raw):
        self.fourier_raw = fourier_raw

    def set_rfourier(self, rfourier_raw):
        self.rfourier_raw = rfourier_raw

    def set_filter(self, values):
        self.filter_values = values

    def __repr__(self):
        return (
            f"Funktion(name='{self.name}', raw_expr='{self.raw_expr}', "
            f"interpreted_expr='{self.interpreted_expr}', parsed_expr='{self.parsed_expr}', "
            f"derivative_raw='{self.derivative_raw}', "
            f"integral_raw='{self.integral_raw}', "
            f"fourier_raw='{self.fourier_raw}', "
            f"rfourier_raw='{self.rfourier_raw}')"
        )