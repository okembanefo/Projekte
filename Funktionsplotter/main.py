import tkinter as tk
import numpy as np
from tkinter import ttk, BooleanVar, Checkbutton, Toplevel, Frame, Canvas, messagebox, simpledialog, font, BOTH
import logic_gui
import comp_input
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from add_ons import ableitung, integration, process_filters
from comp_input import interpreted, parser
from plot_logic import conv_to_func
from logic_gui import plot_functions, lighter_color, darker_color
import class_function
from class_function import Funktion, functions, func_names, colors, max_funcs
from comp_input import handle_error


root = tk.Tk()
root.title("Funktionsplotter")

schriftart = "Helvetica"
b_schrift = "Tahoma"
farbe = "darkslategrey"
text = (schriftart, 12)
sm_text = (schriftart, 10)
aktion = (b_schrift, 12)
entry = (schriftart, 12)
plt.rcParams['font.family'] = schriftart
plt.rcParams['font.size'] = 10

style = ttk.Style()
style.configure('TextButton.TButton', font=text)
style.configure('AktionButton.TButton', font=aktion)
style.configure(
    "TEntry",
    font=text,
    fieldbackground="white",
    bordercolor="gray",
    lightcolor="gray",
    darkcolor="gray"
)
style.map(
    "TEntry",
    bordercolor=[("focus", farbe)],
    lightcolor=[("focus", farbe)],
    darkcolor=[("focus", farbe)]
)

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry(f"{int(screen_width*0.8)}x{int(screen_height*0.8)}+{int(screen_width*0.1)}+{int(screen_height*0.1)}")

func_entries = []
interpreted_labels = []
delete_buttons = []
color_circles = []
plus_button = None
ableitungs_popup = None

main_frame = ttk.Frame(root)
main_frame.pack(fill='both', expand=True)

input_frame = ttk.Frame(main_frame, width=int(screen_width*0.8*1/3))
input_frame.pack(side='left', fill='y', padx=5, pady=10)
input_frame.pack_propagate(False)

plot_frame = ttk.Frame(main_frame, height=400)
plot_frame.pack(side='left', fill='both', expand=True, padx=5, pady=5)
plot_frame.pack_propagate(False)

button_frame = ttk.Frame(main_frame, width=int(screen_width*0.8*1/5))
button_frame.pack(side='right', fill='y', padx=5, pady=10)
button_frame.pack_propagate(False)

fig = Figure(figsize=(6, 4.5))
ax = fig.add_subplot(111)
canvas = FigureCanvasTkAgg(fig, master=plot_frame)
canvas.get_tk_widget().pack(fill='both', expand=True)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["bottom"].set_linewidth(1)
ax.spines["left"].set_linewidth(1)
ax.spines["left"].set_linestyle("-")
ax.spines["left"].set_linestyle("-")
ax.spines["bottom"].set_color(farbe)
ax.spines["left"].set_color(farbe)
ax.set_xlabel("")
ax.set_ylabel("")
ax.tick_params(axis='both', labelsize=10, labelcolor=farbe)

error_label = ttk.Label(root, text="", foreground="red", font=text)
error_label.pack(pady=5)

def open_settings():
    settings_window = Toplevel(root)
    settings_window.title("Einstellungen")
    settings_window.geometry("300x200")
    frame = Frame(settings_window)
    frame.pack(padx=10, pady=10, fill='both')
    rad_var = BooleanVar(value=logic_gui.axis_in_radians)
    rad_check = Checkbutton(frame, text="Achsen in Bogenmaß", variable=rad_var, font=text)
    rad_check.pack(anchor='w', pady=5)
    pos_var = BooleanVar(value=logic_gui.show_positive_only)
    pos_check = Checkbutton(frame, text="Nur positive Y-Werte anzeigen", variable=pos_var, font=text)
    pos_check.pack(anchor='w', pady=5)
    def apply_settings():
        logic_gui.axis_in_radians = rad_var.get()
        logic_gui.show_positive_only = pos_var.get()
        logic_gui.plot_functions(canvas, ax)
        settings_window.destroy()
    def reset_settings():
        logic_gui.axis_in_radians = False
        logic_gui.show_positive_only = False
        rad_var.set(False)
        pos_var.set(False)
        logic_gui.plot_functions(canvas, ax)
        settings_window.destroy()
    ttk.Button(frame, text="Übernehmen", command=apply_settings).pack(pady=10)
    ttk.Button(frame, text="Zurücksetzen", command=reset_settings).pack()

def add_input_field():
    global plus_button
    if len(func_entries) >= max_funcs:
        return
    row = len(func_entries)
    entry_frame = ttk.Frame(input_frame)
    entry_frame.grid(row=row, column=0, columnspan=2, padx=5, pady=20, sticky='ew')
    circle = Canvas(entry_frame, width=20, height=20, bg=colors[row], bd=0, highlightthickness=0)
    circle.grid(row=0, column=0, padx=(0, 5))
    entry = ttk.Entry(entry_frame, width=20, font=text)
    entry.grid(row=0, column=1, sticky='ew', ipady=5)
    interpreted_label = ttk.Label(
        entry_frame,
        text="Interpretiert als: ",
        foreground="gray",
        font=sm_text
    )
    interpreted_label.grid(row=1, column=0, columnspan=2, sticky='w')
    interpreted_label.grid_remove()
    delete_button = ttk.Button(
        entry_frame,
        text="-",
        width=2,
        command=lambda idx=row: delete_input_field(idx),
        style="AktionButton.TButton"
    )
    delete_button.grid(row=0, column=2, padx=2)
    entry.bind("<FocusIn>", lambda e, idx=row: on_focus_in(idx))
    entry.bind("<FocusOut>", lambda e, idx=row: on_focus_out(idx))
    entry.bind("<KeyRelease>", lambda e, idx=row: on_entry_change(e, idx))
    func_entries.append(entry)
    interpreted_labels.append(interpreted_label)
    delete_buttons.append(delete_button)
    color_circles.append(circle)
    if plus_button:
        plus_button.destroy()
    if len(func_entries) < max_funcs:
        plus_button = ttk.Button(
            input_frame,
            text="+",
            width=3,
            command=add_input_field,
            style="AktionButton.TButton"
        )
        plus_button.grid(row=row+1, column=0, columnspan=2, pady=10)

def delete_input_field(index):
    global plus_button
    if index >= len(func_entries):
        return
    try:
        func_entries[index].master.destroy()
        interpreted_labels[index].destroy()
        delete_buttons[index].destroy()
        color_circles[index].destroy()
    except Exception as e:
        print(f"Fehler beim Löschen der Widgets: {e}")
    del func_entries[index]
    del interpreted_labels[index]
    del delete_buttons[index]
    del color_circles[index]
    func_name = func_names[index]
    if func_name in functions:
        del functions[func_name]
    for row, entry in enumerate(func_entries):
        frame = entry.master
        frame.grid(row=row, column=0, columnspan=2, padx=5, pady=15, sticky='ew')
        color_circles[row].config(bg=colors[row])
        entry.bind("<FocusIn>", lambda e, idx=row: on_focus_in(idx))
        entry.bind("<FocusOut>", lambda e, idx=row: on_focus_out(idx))
        entry.bind("<KeyRelease>", lambda e, idx=row: on_entry_change(e, idx))
        delete_buttons[row].config(command=lambda idx=row: delete_input_field(idx))
    if plus_button:
        plus_button.destroy()
        plus_button = None
    if len(func_entries) < max_funcs:
        plus_button = ttk.Button(
            input_frame,
            text="+",
            width=3,
            command=add_input_field,
            style="AktionButton.TButton"
        )
        plus_button.grid(row=len(func_entries), column=0, columnspan=2, pady=10)
    try:
        logic_gui.plot_functions(canvas, ax)
    except Exception as e:
        print(f"Fehler beim Neuzeichnen der Funktionen: {e}")

def on_focus_in(index):
    interpreted_labels[index].grid()
    func_name = func_names[index]
    if func_name in functions:
        func_entries[index].delete(0, tk.END)
        func_entries[index].insert(0, functions[func_name].raw_expr)
    update_interpretation(index)

def on_focus_out(index):
    interpreted_labels[index].grid_remove()
    raw_text = func_entries[index].get().strip()
    if not raw_text:
        return
    func_name = func_names[index]
    try:
        if func_name not in functions:
            functions[func_name] = class_function.Funktion(func_name, raw_text)
        else:
            functions[func_name].update(raw_text)
        interpreted_text = interpreted(raw_text)
        func_entries[index].delete(0, tk.END)
        func_entries[index].insert(0, interpreted_text)
    except Exception as e:
        interpreted_labels[index].config(
            text=f"Fehler: {e}",
            foreground="red"
        )

def update_interpretation(index):
    text = func_entries[index].get().strip()
    if text:
        interpreted_expr = comp_input.interpreted(text)
        interpreted_labels[index].config(text=f"Interpretiert als: {interpreted_expr}")
    else:
        interpreted_labels[index].config(text="Interpretiert als: ")

def is_valid_expression(expr):
    try:
        parser(expr)
        return True
    except Exception as e:
        return False

def on_entry_change(event, index):
    if index >= len(func_entries):
        return
    text = func_entries[index].get().strip()
    func_name = func_names[index]
    if text:
        try:
            if is_valid_expression(text):
                if func_name in functions and text == functions[func_name].raw_expr:
                    return
                if func_name not in functions:
                    functions[func_name] = Funktion(func_name, text)
                else:
                    functions[func_name].update(text)
                update_interpretation(index)
                error = plot_functions(canvas, ax, error_label)
                if error != True:
                    error_label.config(text=error, foreground="red")
                else:
                    error_label.config(text="")
            else:
                interpreted_labels[index].config(
                    text="Fehler: Ungültiger Ausdruck",
                    foreground="red"
                )
        except Exception as e:
            interpreted_labels[index].config(
                text=f"Fehler: {e}",
                foreground="red"
            )
            error_label.config(text=f"Fehler: {e}", foreground="red")
    else:
        interpreted_labels[index].config(
            text="Interpretiert als: ",
            foreground="gray"
        )

def open_ableitung_popup():
    global ableitungs_popup

    if 'ableitungs_popup' in globals() and ableitungs_popup is not None and ableitungs_popup.winfo_exists():
        ableitungs_popup.destroy()
        ableitungs_popup = None

    ableitungs_popup = Toplevel(root)
    ableitungs_popup.title("Ableitung")
    ableitungs_popup.geometry("300x400")

    frame = Frame(ableitungs_popup)
    frame.pack(padx=15, pady=15, fill='both', expand=True)

    func_list = []

    for func_name in func_names:
        if func_name in functions:
            func_str = functions[func_name].raw_expr
            func_list.append((func_name, func_str))

    if not func_list:
        ttk.Label(frame, text="Keine Funktionen definiert.", font=text).pack(pady=10)
        return

    for func_name, func_str in func_list:
        idx = func_names.index(func_name)
        base_color = colors[idx]

        container = Frame(frame)
        container.pack(pady=5, fill='x')

        circle = Canvas(container, width=20, height=20,
                        bg=base_color, bd=0, highlightthickness=0)
        circle.pack(side='left', padx=(0, 5))

        btn = ttk.Button(
            container,
            text=f"{func_name} = {interpreted(func_str)}",
            command=lambda n=func_name, s=func_str:
                open_derivative_window(n, s),
            style="TextButton.TButton",
            padding=(5, 12)
        )
        btn.pack(side='left', fill='x', expand=True)


    def open_derivative_window(func_name, func_str):

        ableitungs_popup.destroy()

        deriv_popup = Toplevel(root)
        deriv_popup.title(f"Ableitung von {func_name}")
        deriv_popup.geometry("500x450")

        main_frame = Frame(deriv_popup, padx=15, pady=10)
        main_frame.pack(fill='both', expand=True)

        ttk.Label(
            main_frame,
            text=f"Ableitung von f(x) = {interpreted(func_str)}",
            font=text
        ).pack(pady=(0, 10))

        input_frame = Frame(main_frame)
        input_frame.pack(fill='x', pady=5)

        ttk.Label(input_frame, text="x-Wert:", font=text).grid(row=0, column=0, padx=5)

        entry_x = ttk.Entry(input_frame, font=text, width=10)
        entry_x.grid(row=0, column=1, padx=5)
        entry_x.insert(0, "0")

        plot_frame = Frame(main_frame, width=450, height=300)
        plot_frame.pack(pady=5)
        plot_frame.pack_propagate(False)

        fig = Figure(figsize=(4.5, 3), dpi=90)
        plot_ax = fig.add_subplot(111)

        canvas_local = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas_local.get_tk_widget().pack(fill='both', expand=False)

        # ---------- ACHSENSTYLING ---------- #

        plot_ax.spines["top"].set_visible(False)
        plot_ax.spines["right"].set_visible(False)

        plot_ax.spines["bottom"].set_color(farbe)
        plot_ax.spines["left"].set_color(farbe)

        plot_ax.spines["bottom"].set_linewidth(1)
        plot_ax.spines["left"].set_linewidth(1)

        plot_ax.tick_params(axis='both', labelsize=10, labelcolor=farbe)

        # ---------- FARBEN ---------- #

        idx = func_names.index(func_name)
        base_color = colors[idx]
        light_color = lighter_color(base_color)

        result_label = ttk.Label(main_frame, text="", font=text)
        result_label.pack(pady=5)

        func = conv_to_func(functions[func_name].parsed_expr)

        deriv_str = ableitung(func_str)
        deriv_func = conv_to_func(parser(deriv_str))

        def parse_x_value(val):
            val = val.replace("pi", str(np.pi))
            val = val.replace("tau", str(2 * np.pi))
            return float(eval(val))

        def update_plot(event=None):
            try:
                x_val = parse_x_value(entry_x.get())
            except:
                result_label.config(text="Ungültiger x-Wert", foreground="red")
                return

            x = np.linspace(x_val - 5, x_val + 5, 400)

            y = func(x)
            y_deriv = deriv_func(x)

            plot_ax.clear()

            # ---------- ACHSEN NACH CLEAR ---------- #

            plot_ax.spines["top"].set_visible(False)
            plot_ax.spines["right"].set_visible(False)

            plot_ax.spines["bottom"].set_color(farbe)
            plot_ax.spines["left"].set_color(farbe)

            plot_ax.spines["bottom"].set_linewidth(1)
            plot_ax.spines["left"].set_linewidth(1)

            plot_ax.tick_params(axis='both', labelsize=10, labelcolor=farbe)

            # ---------- PLOTS (GEÄNDERT) ---------- #

            # f(x) originale Farbe
            plot_ax.plot(
                x, y,
                color=base_color,
                label=f"f(x) = {interpreted(func_str)}"
            )

            # f'(x) heller + gestrichelt
            plot_ax.plot(
                x, y_deriv,
                color=light_color,
                linestyle="--",
                label=f"f'(x) = {interpreted(deriv_str)}"
            )

            y_val = deriv_func(x_val)

            # Hilfslinien beide grau
            plot_ax.axvline(x=x_val, color='gray', linestyle='--')
            plot_ax.axhline(y=y_val, color='gray', linestyle='--')

            plot_ax.legend(fontsize=9)

            canvas_local.draw()

            result_label.config(
                text=f"f'({x_val}) = {y_val:.4f}",
                foreground="black"
            )

        entry_x.bind("<KeyRelease>", update_plot)

        update_plot()



def open_integration_popup():
    global integration_popup

    if 'integration_popup' in globals() and integration_popup is not None and integration_popup.winfo_exists():
        integration_popup.destroy()
        integration_popup = None

    integrations_poup = Toplevel(root)
    integrations_poup.title("Integration")
    integrations_poup.geometry("300x400")

    frame = Frame(integrations_poup)
    frame.pack(padx=15, pady=15, fill='both', expand=True)

    func_list = []

    for i, func_name in enumerate(func_names):
        if func_name in functions:
            func_str = functions[func_name].raw_expr
            func_list.append((func_name, func_str))
    if not func_list:
        ttk.Label(frame, text="Keine Funktionen definiert.", font=text).pack(pady=10)
        return
    for func_name, func_str in func_list:
        idx = func_names.index(func_name)
        base_color = colors[idx]
        container = Frame(frame)
        container.pack(pady=5, fill='x')
        circle = Canvas(container, width=20, height=20, bg=base_color, bd=0, highlightthickness=0)
        circle.pack(side='left', padx=(0, 5))
        btn = ttk.Button(
            container,
            text=f"{func_name} = {interpreted(func_str)}",
            command=lambda name=func_name, s=func_str: open_integration_window(name, s),
            style="TextButton.TButton",
            padding=(5, 12)
        )
        btn.pack(side='left', fill='x', expand=True)

    def open_integration_window(func_name, func_str):
        integrations_poup.destroy()

        integration_popup = Toplevel(root)
        integration_popup.title(f"Integration von {func_name}")
        integration_popup.geometry("500x430")

        main_frame = Frame(integration_popup, padx=15, pady=10)
        main_frame.pack(fill='both', expand=True)

        # Funktionsanzeige
        ttk.Label(main_frame, text=f"Integration von f(x) = {interpreted(func_str)}", font=text).pack(pady=(0, 10))

        input_frame = Frame(main_frame)
        input_frame.pack(fill='x', pady=5)

        empty_column = Frame(input_frame, width=100)
        empty_column.grid(row=0, column=2)

        # Label und Eingabefeld für a
        ttk.Label(input_frame, text="a:", font=text).grid(row=0, column=0, padx=5, pady=2)
        entry_a = ttk.Entry(input_frame, font=text, width=8)
        entry_a.grid(row=0, column=1, padx=5, pady=2, sticky='ew')

        empty_column = Frame(input_frame, width=130)
        empty_column.grid(row=0, column=2)

        # Label und Eingabefeld für b
        ttk.Label(input_frame, text="b:", font=text).grid(row=0, column=3, padx=5, pady=2)
        entry_b = ttk.Entry(input_frame, font=text, width=8)
        entry_b.grid(row=0, column=4, padx=5, pady=2, sticky='ew')

        # Plot-Frame mit fester Größe
        plot_frame = Frame(main_frame, width=450, height=250)  
        plot_frame.pack(pady=5)
        plot_frame.pack_propagate(False)  

        fig = Figure(figsize=(4.5, 2.3), dpi=90)  # Y-Richtung um 1/4 verkleinert
        plot_ax = fig.add_subplot(111)
        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas.get_tk_widget().pack(fill='both', expand=False)  

        # Achsen formatieren
        plot_ax.spines["top"].set_visible(False)
        plot_ax.spines["right"].set_visible(False)
        plot_ax.spines["bottom"].set_color(farbe)
        plot_ax.spines["left"].set_color(farbe)
        plot_ax.spines["bottom"].set_linewidth(1)
        plot_ax.spines["left"].set_linewidth(1)
        plot_ax.tick_params(axis='both', labelsize=10, labelcolor=farbe)

        # Farbeinstellungen
        idx = func_names.index(func_name)
        line_color = colors[idx]

        # Ergebnisanzeige direkt unter dem Plot
        result_frame = Frame(main_frame)
        result_frame.pack(fill='x', pady=5)

        result_label = ttk.Label(result_frame, text="", font=text)
        result_label.pack()

        spec_cons = {
            "pi": np.pi,
            "e": np.e,
            "euler": np.e,
            "tau": 2 * np.pi
        }

        def calculate_area(event=None):
            a_str = entry_a.get()
            b_str = entry_b.get()
            try:
                a = eval(a_str, {"__builtins__": None}, {"np": np, **spec_cons})
                b = eval(b_str, {"__builtins__": None}, {"np": np, **spec_cons})
            except Exception as e:
                result_label.config(text=f"Fehler: Ungültiger Wert: {e}", foreground="red")
                return

            try:
                func = conv_to_func(functions[func_name].parsed_expr)
                x = np.linspace(a - 0.5, b + 0.5, 400)
                y = func(x)

                plot_ax.clear()
                plot_ax.plot(x, y, color=line_color)
                plot_ax.axvline(x=a, color='gray', linestyle='--')
                plot_ax.axvline(x=b, color='gray', linestyle='--')

                x_fill = np.linspace(a, b, 100)
                y_fill = func(x_fill)
                fill_color = darker_color(line_color)
                plot_ax.fill_between(x_fill, y_fill, color=fill_color, alpha=0.5)

                # Y-Achsenbereich anpassen
                plot_ax.set_ylim(min(0, min(y_fill)*1.1), max(y_fill)*1.1)

                canvas.draw()

                area = integration(func, a, b)
                result_label.config(text=f"Fläche: {area:.4f}", foreground="black")
            except Exception as e:
                result_label.config(text=f"Fehler: {e}", foreground="red")

        entry_a.bind("<KeyRelease>", calculate_area)
        entry_b.bind("<KeyRelease>", calculate_area)

        entry_a.insert(0, "0")
        entry_b.insert(0, "0")

        calculate_area()


def open_filter_popup():
    global filter_popup
    if 'filter_popup' in globals() and filter_popup is not None and filter_popup.winfo_exists():
        filter_popup.destroy()
    filter_popup = Toplevel(root)
    filter_popup.title("Filter")
    filter_popup.geometry("720x400")
    frame = Frame(filter_popup)
    frame.pack(padx=15, pady=15, fill='both', expand=True)
    func_list = []
    for func_name in func_names:
        if func_name in functions:
            func_str = functions[func_name].raw_expr
            func_list.append((func_name, func_str))
    if not func_list:
        ttk.Label(frame, text="Keine Funktionen definiert.", font=text).pack(pady=10)
        return
    table = Frame(frame)
    table.pack(fill='x')
    table.grid_columnconfigure(0, minsize=25)
    table.grid_columnconfigure(1, minsize=180)
    table.grid_columnconfigure(2, minsize=55)
    table.grid_columnconfigure(3, minsize=55)
    table.grid_columnconfigure(4, minsize=55)
    table.grid_columnconfigure(5, minsize=55)
    table.grid_columnconfigure(6, minsize=85)
    table.grid_columnconfigure(7, minsize=25)
    ttk.Label(table, text="Funktion:", font=text).grid(row=0, column=0, columnspan=2, pady=(0, 8), sticky="w")
    ttk.Label(table, text="X-Bereich:", font=text).grid(row=0, column=2, columnspan=2, sticky="w")
    ttk.Label(table, text="Y-Bereich:", font=text).grid(row=0, column=4, columnspan=2, sticky="w")
    ttk.Label(table, text="von", font=sm_text).grid(row=1, column=2, sticky="w")
    ttk.Label(table, text="bis", font=sm_text).grid(row=1, column=3, sticky="w")
    ttk.Label(table, text="von", font=sm_text).grid(row=1, column=4, sticky="w")
    ttk.Label(table, text="bis", font=sm_text).grid(row=1, column=5, sticky="w")
    entry_widgets = {}
    for row, (func_name, func_str) in enumerate(func_list, start=2):
        idx = func_names.index(func_name)
        base_color = colors[idx]
        circle = Canvas(table, width=18, height=18, bg=base_color, bd=0, highlightthickness=0)
        circle.grid(row=row, column=0, padx=(0, 5), pady=4)
        func_label = ttk.Label(
            table,
            text=f"{func_name} = {interpreted(func_str)}",
            font=text,
            anchor="w"
        )
        func_label.grid(row=row, column=1, sticky='w', padx=(0, 10))
        x_from_entry = ttk.Entry(table, width=8, font=sm_text)
        x_from_entry.grid(row=row, column=2, padx=1)
        x_to_entry = ttk.Entry(table, width=8, font=sm_text)
        x_to_entry.grid(row=row, column=3, padx=1)
        y_from_entry = ttk.Entry(table, width=8, font=sm_text)
        y_from_entry.grid(row=row, column=4, padx=1)
        y_to_entry = ttk.Entry(table, width=8, font=sm_text)
        y_to_entry.grid(row=row, column=5, padx=1)
        hide_var = BooleanVar()
        hide_check = Checkbutton(
            table,
            text="Ausblenden",
            variable=hide_var,
            font=sm_text
        )
        hide_check.grid(row=row, column=6, padx=3, sticky="w")
        reset_button = ttk.Button(
            table,
            text="↻",
            style="AktionButton.TButton",
            width=2,
            command=lambda xf=x_from_entry, xt=x_to_entry,
                           yf=y_from_entry, yt=y_to_entry, hv=hide_var:
                reset_filter_row(xf, xt, yf, yt, hv)
        )
        reset_button.grid(row=row, column=7, padx=2)
        entry_widgets[func_name] = {
            "x_from": x_from_entry,
            "x_to": x_to_entry,
            "y_from": y_from_entry,
            "y_to": y_to_entry,
            "hide": hide_var
        }
    button_frame = Frame(frame)
    button_frame.pack(pady=15)
    apply_button = ttk.Button(
        button_frame,
        text="Anwenden",
        command=lambda: process_filters(entry_widgets, canvas, ax),
        style="TextButton.TButton",
        width=12
    )
    apply_button.pack(side="left", padx=5, ipady=3)
    reset_all_button = ttk.Button(
        button_frame,
        text="Alles zurücksetzen",
        command=reset_all_filters,
        style="TextButton.TButton",
        width=20
    )
    reset_all_button.pack(side="left", padx=5, ipady=3)

def reset_filter_row(x_from_entry, x_to_entry, y_from_entry, y_to_entry, hide_var):
    x_from_entry.delete(0, tk.END)
    x_to_entry.delete(0, tk.END)
    y_from_entry.delete(0, tk.END)
    y_to_entry.delete(0, tk.END)
    hide_var.set(False)

def reset_all_filters():
    for func_name in functions:
        functions[func_name].set_filter([None, None, None, None])
    logic_gui.plot_functions(canvas, ax)

def open_legend():
    legend_popup = Toplevel(root)
    legend_popup.title("Legende")
    legend_popup.geometry("350x800")
    frame = Frame(legend_popup)
    frame.pack(padx=10, pady=10, fill='both', expand=True)
    ttk.Label(frame, text="Standardoperationen:", font=(schriftart, 11, 'bold')).pack(anchor='w')
    ttk.Label(frame, text="x²    → x^2", font=text).pack(anchor='w')
    ttk.Label(frame, text="x¹⁰   → x^(10)", font=text).pack(anchor='w')
    ttk.Label(frame, text="x⁻⁵   → x^(-5)", font=text).pack(anchor='w')
    ttk.Label(frame, text="x²ˣ   → x^(2x)", font=text).pack(anchor='w')
    ttk.Label(frame, text="|2x|  → abs(2x)", font=text).pack(anchor='w', pady=(2, 5))
    tk.Label(frame, text="", font=text).pack()
    ttk.Label(frame, text="Spezielle Funktionen:", font=(schriftart, 11, 'bold')).pack(anchor='w')
    for func in comp_input.spec_funcs.keys():
        tk.Label(frame, text=f"- {func}(x)", font=text).pack(anchor='w')
    tk.Label(frame, text="- eˣ    → exp(x)", font=text).pack(anchor='w', pady=(5, 0))
    tk.Label(frame, text="- e²ˣ   → exp(2x)", font=text).pack(anchor='w', pady=(5, 0))
    tk.Label(frame, text="- √x    → sqrt(x)", font=text).pack(anchor='w')
    tk.Label(frame, text="- √(2x) → sqrt(2x)", font=text).pack(anchor='w')
    tk.Label(frame, text="", font=text).pack()
    ttk.Label(frame, text="Verfügbare Konstanten:", font=(schriftart, 11, 'bold')).pack(anchor='w')
    tk.Label(frame, text="π       → pi", font=text).pack(anchor='w')
    tk.Label(frame, text="euler   → e", font=text).pack(anchor='w')
    tk.Label(frame, text="τ       → tau", font=text).pack(anchor='w')

button_frame = ttk.Frame(root)
button_frame.place(relx=0.915, rely=0.3, anchor='center', height=500, relwidth=0.15)
filter_button = ttk.Button(
    button_frame,
    text="Filter",
    command=open_filter_popup,
    style="TextButton.TButton"
)
ableitung_button = ttk.Button(
    button_frame,
    text="Ableitung",
    command=open_ableitung_popup,
    style="TextButton.TButton"
)
integration_button = ttk.Button(
    button_frame,
    text="Integration",
    command=open_integration_popup,
    style="TextButton.TButton"
)
ft_button = ttk.Button(
    button_frame,
    text="Fouriertransformierte",
    style="TextButton.TButton"
)
rft_button = ttk.Button(
    button_frame,
    text="Rücktransformierte",
    style="TextButton.TButton"
)
filter_button.pack(fill='x', pady=10, ipady=9)
ableitung_button.pack(fill='x', pady=10, ipady=9)
integration_button.pack(fill='x', pady=10, ipady=9)
ft_button.pack(fill='x', pady=10, ipady=9)
rft_button.pack(fill='x', pady=10, ipady=9)
settings_button = ttk.Button(
    button_frame,
    text="Einstellungen",
    command=open_settings,
    style="TextButton.TButton"
)
legend_button = ttk.Button(
    button_frame,
    text="Legende",
    command=open_legend,
    style="TextButton.TButton"
)
settings_button.pack(fill='x', pady=10, ipady=9)
legend_button.pack(fill='x', pady=10, ipady=9)

canvas.mpl_connect("button_press_event", lambda event: logic_gui.on_press(event, ax, canvas))
canvas.mpl_connect("motion_notify_event", lambda event: logic_gui.on_motion(event, ax, canvas))
canvas.mpl_connect("button_release_event", lambda event: logic_gui.on_release(event))
canvas.mpl_connect("scroll_event", lambda event: logic_gui.on_scroll(event, ax, canvas))

add_input_field()
root.mainloop()
