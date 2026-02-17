import numpy as np
import re
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.colors as mc
import colorsys
from collections import deque, defaultdict
from comp_input import parser
from comp_input import interpreted
from plot_logic import gen_funcs

#Funktionendef.
max_funcs = 7
func_names = ['f(x)', 'g(x)', 'h(x)', 'j(x)', 'k(x)', 'l(x)', 'n(x)', 'm(x)', 'r(x)', 't(x)']

# Globale Variablen für die Logik
colors = ["springgreen", "skyblue", "magenta", "coral", "indigo", "moccasin", "turquoise", "mistyrose"]
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
func_dict = {}

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

def auto_adjust_axis(x, y):
    global x_range_kord, y_range_kord
    x_min, x_max = min(x), max(x)
    y_min, y_max = min(y), max(y)
    x_pad = (x_max - x_min) * 0.1
    y_pad = (y_max - y_min) * 0.1
    x_range_kord = [x_min - x_pad, x_max + x_pad]
    if show_positive_only:
        y_range_kord = [0, y_max + y_pad]
    else:
        y_range_kord = [y_min - y_pad, y_max + y_pad]

def on_press(event, ax, canvas):
    if event.inaxes != ax or event.button != 1:
        return

    pan_state["press"] = (event.x, event.y)
    pan_state["xlim"] = ax.get_xlim()
    pan_state["ylim"] = ax.get_ylim()

def on_motion(event, ax, canvas):
    if pan_state["press"] is None or event.inaxes != ax:
        return

    xpress, ypress = pan_state["press"]
    dx = event.x - xpress
    dy = event.y - ypress

    cur_xlim = pan_state["xlim"]
    cur_ylim = pan_state["ylim"]

    width = cur_xlim[1] - cur_xlim[0]
    height = cur_ylim[1] - cur_ylim[0]

    dx_data = -dx * width / ax.bbox.width * pan_sen
    dy_data = -dy * height / ax.bbox.height * pan_sen

    new_xlim = [cur_xlim[0] + dx_data, cur_xlim[1] + dx_data]
    new_ylim = [cur_ylim[0] + dy_data, cur_ylim[1] + dy_data]

    ax.set_xlim(new_xlim)
    ax.set_ylim(new_ylim)
    canvas.draw_idle()

def on_release(event):
    pan_state["press"] = None

def on_scroll(event, ax, canvas):
    global x_range_kord, y_range_kord

    if event.inaxes != ax:
        return

    base_scale = 1.05

    if event.button == 'up':
        scale_factor = 1 / base_scale
    elif event.button == 'down':
        scale_factor = base_scale
    else:
        return

    cur_xlim = ax.get_xlim()
    cur_ylim = ax.get_ylim()

    xdata = event.xdata
    ydata = event.ydata

    new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
    new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor

    relx = (cur_xlim[1] - xdata) / (cur_xlim[1] - cur_xlim[0])
    rely = (cur_ylim[1] - ydata) / (cur_ylim[1] - cur_ylim[0])

    x_range_kord = [
        xdata - new_width * (1 - relx),
        xdata + new_width * relx
    ]

    y_range_kord = [
        ydata - new_height * (1 - rely),
        ydata + new_height * rely
    ]

    ax.set_xlim(x_range_kord)
    ax.set_ylim(y_range_kord)
    canvas.draw_idle()

def lighter_color(color):
    rgb = mc.to_rgb(color)
    hls = colorsys.rgb_to_hls(*rgb)
    return mc.to_hex(colorsys.hls_to_rgb(hls[0], 1 - 0.5*(1 - hls[1]), hls[2]))

def darker_color(color):
    rgb = mc.to_rgb(color)
    hls = colorsys.rgb_to_hls(*rgb)
    return mc.to_hex(colorsys.hls_to_rgb(hls[0], 0.5 * hls[1], hls[2]))

def plot_functions(canvas, ax, error_label=None):
    ax.clear()

    print(func_dict)

    initial_x_range = list(x_range_kord)
    initial_y_range = list(y_range_kord)

    for i, func_name in enumerate(func_names):
        if func_name not in func_dict:
            continue

        func_list = func_dict[func_name]
        base_color = colors[i]

        for j, func_str in enumerate(func_list):
            try:
                parsed_expr = parser(func_str)

                x, y = gen_funcs(
                    parsed_expr,
                    allow_compl=False,
                    start=x_ax_min,
                    end=x_ax_max,
                    count=count_points
                )

                if j == 0:
                    ax.plot(
                        x,
                        y,
                        color=base_color,
                        label=f"{func_name} = {interpreted(func_str)}"
                    )
                else:
                    label = f"{func_name.split('(')[0]}'(x) = {interpreted(func_str)}"
                    ax.plot(
                        x,
                        y,
                        color=base_color,
                        linestyle="--",
                        label=label
                    )

            except ZeroDivisionError:
                continue
            except Exception as e:
                return f"Fehler: {str(e)}"

    ax.set_xlim(initial_x_range)
    ax.set_ylim(initial_y_range)

    ax.grid(True, which="both", linestyle='-')
    ax.legend(fontsize=12)

    canvas.draw()

    return True
