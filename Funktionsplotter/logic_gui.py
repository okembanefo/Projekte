import numpy as np
import re
import time
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from collections import deque, defaultdict
from comp_input import parser
from comp_input import interpreted
from plot_logic import gen_funcs

# Globale Variablen für die Logik
colors = ["green", "blue", "red", "yellow", "purple"]
x_range = [-10, 10]
y_range = [-10, 10]
count_points = 1000
axis_in_radians = False
show_positive_only = False
is_panning = False
pan_start_x = 0
pan_start_y = 0
pan_x_range = [0, 0]
pan_y_range = [0, 0]
func_dict = {}

x_ax_min = -15
x_ax_max = 15
y_ax_min = -15
y_ax_max = 15

pan_sen = 0.3  
pan_state = {
    "press": None,
    "xlim": None,
    "ylim": None
}

# Fehlerverwaltung
input_errors = defaultdict(lambda: {"timestamp": 0, "count": 0})

def handle_input_errors(error_message):
    current_time = time.time()

    if error_message in input_errors:
        if current_time - input_errors[error_message]["timestamp"] < 3:
            input_errors[error_message]["count"] += 1
            return None
        else:
            input_errors[error_message]["count"] += 1
            return error_message
    else:
        input_errors[error_message]["timestamp"] = current_time
        input_errors[error_message]["count"] = 1
        return None

def auto_adjust_axis(x, y):
    global x_range, y_range
    x_min, x_max = min(x), max(x)
    y_min, y_max = min(y), max(y)
    x_pad = (x_max - x_min) * 0.1
    y_pad = (y_max - y_min) * 0.1
    x_range = [x_min - x_pad, x_max + x_pad]
    if show_positive_only:
        y_range = [0, y_max + y_pad]
    else:
        y_range = [y_min - y_pad, y_max + y_pad]

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
    global x_range, y_range

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

    x_range = [
        xdata - new_width * (1 - relx),
        xdata + new_width * relx
    ]

    y_range = [
        ydata - new_height * (1 - rely),
        ydata + new_height * rely
    ]

    ax.set_xlim(x_range)
    ax.set_ylim(y_range)
    canvas.draw_idle()

def lighter_color(color):
    """Erzeugt eine hellere Variante einer Farbe."""
    import matplotlib.colors as mc
    import colorsys
    rgb = mc.to_rgb(color)
    hls = colorsys.rgb_to_hls(*rgb)
    return mc.to_hex(colorsys.hls_to_rgb(hls[0], 1 - 0.5*(1 - hls[1]), hls[2]))

def plot_functions(canvas, ax, error_label=None):

    ax.clear()

    initial_x_range = list(x_range)
    initial_y_range = list(y_range)

    for i, func_name in enumerate(['f(x)', 'g(x)', 'h(x)', 'i(x)', 'j(x)']):

        if func_name not in func_dict:
            continue

        func_list = func_dict[func_name]

        base_color = colors[i]
        deriv_color = lighter_color(base_color)

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

                # Originalfunktion
                if j == 0:
                    ax.plot(
                        x,
                        y,
                        color=base_color,
                        label=f"{func_name} = {interpreted(func_str)}"
                    )

                # Ableitung(en)
                else:
                    ax.plot(
                        x,
                        y,
                        color=deriv_color,
                        linestyle="--",
                        label=f"{func_name}' = {interpreted(func_str)}"
                    )

            except ZeroDivisionError:
                continue

            except Exception as e:
                error_message = f"Fehler bei Funktion {func_name}: {str(e)}"
                return handle_input_errors(error_message)

    # Achsen beibehalten
    ax.set_xlim(initial_x_range)
    ax.set_ylim(initial_y_range)

    # Ticks
    x_ticks = np.arange(int(x_ax_min), int(x_ax_max) + 1, 1)
    y_ticks = np.arange(int(y_ax_min), int(y_ax_max) + 1, 1)

    ax.set_xticks(x_ticks)
    ax.set_yticks(y_ticks)

    ax.set_xlabel("x")
    ax.set_ylabel("y")

    ax.grid(True, which="both", linestyle='-')
    ax.legend()

    canvas.draw()

    return True
