import numpy as np
import re
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.colors as mc
import colorsys
from collections import deque, defaultdict
from comp_input import eval_ast, interpreted, parser, handle_error
from plot_logic import gen_funcs
import class_function
from class_function import functions, func_names, colors, x_range_kord, y_range_kord, count_points, axis_in_radians, show_positive_only, pan_sen, pan_state, x_ax_min, x_ax_max, y_ax_min, y_ax_max



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

def plot_functions(canvas, ax, error_label=None, func_obj=None):
    import re

    ax.clear()

    initial_x_range = list(x_range_kord)
    initial_y_range = list(y_range_kord)

    plotted_something = False  # Flag, um zu prüfen, ob etwas geplottet wurde

    for func_name, func in functions.items():
        if func_name not in func_names:
            continue

        color = class_function.colors[func_names.index(func_name)]

        try:
            expr_lower = func.raw_expr.lower()

            if "delta" in expr_lower:
                match_inner = re.search(r"delta\((.*)\)", func.raw_expr, re.DOTALL)

                if not match_inner:
                    continue

                inner_expr = match_inner.group(1)

                x_vals = np.linspace(x_ax_min, x_ax_max, count_points)

                y_vals = delta(inner_expr, x_vals)

                if len(y_vals) == 0:
                    continue

                height = float(np.max(y_vals))

                pos = 0.0

                shift_match = re.search(r"x\s*-\s*([0-9\.\-]+)", inner_expr)

                if shift_match:
                    try:
                        pos = float(shift_match.group(1))
                    except:
                        pos = 0.0

                ax.vlines(
                    pos,
                    0,
                    height,
                    color=color,
                    linewidth=3
                )

                ax.annotate(
                    "",
                    xy=(pos, height),
                    xytext=(pos, height * 0.7),
                    arrowprops=dict(
                        arrowstyle="->",
                        color=color,
                        linewidth=3
                    )
                )

                continue

            x, y = gen_funcs(
                func.parsed_expr,
                allow_compl=False,
                start=x_ax_min,
                end=x_ax_max,
                count=count_points
            )

            if len(x) == 0 or len(y) == 0:
                continue

            # Filter anwenden
            filter_settings = class_function.filter_funcs.get(
                func_name,
                [None, None, None, None, False]
            )

            x_from, x_to, y_from, y_to, hide = filter_settings

            mask = np.ones_like(x, dtype=bool)

            if x_from is not None:
                mask &= (x >= float(x_from))

            if x_to is not None:
                mask &= (x <= float(x_to))

            if y_from is not None:
                mask &= (y >= float(y_from))

            if y_to is not None:
                mask &= (y <= float(y_to))

            x, y = x[mask], y[mask]

            if not hide and len(x) > 0:
                ax.plot(
                    x,
                    y,
                    color=color,
                    label=f"{func_name}(x) = {func.interpreted_expr}"
                )
                plotted_something = True 

        except Exception as e:
            continue

    ax.set_xlim(initial_x_range)

    if class_function.show_positive_only:
        ax.set_ylim(bottom=0)

    elif getattr(class_function, "show_negative_only", False):
        ax.set_ylim(top=0)

    else:
        ax.set_ylim(initial_y_range)

    ax.grid(True)

    # Nur Legende anzeigen, wenn etwas geplottet wurde
    if plotted_something:
        ax.legend(fontsize=12)

    canvas.draw()

    return True
