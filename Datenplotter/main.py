import tkinter as tk
import numpy as np
from tkinter import ttk, Radiobutton, BooleanVar, Checkbutton, Toplevel, Frame, Canvas, messagebox, simpledialog, font, BOTH
import logic_gui
import comp_input
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from add_ons import ableitung, integration, fourier, rfourier, process_filters
from comp_input import interpreted, parser
from plot_logic import conv_to_func
from logic_gui import plot_functions, lighter_color, darker_color
import class_function
from class_function import Funktion, functions, func_names, max_funcs, filter_funcs, entry_widgets, color_palettes, color_palette_names
from comp_input import handle_error

root = tk.Tk()
root.title("Datenplotter")

schriftart = "Segoe UI"
b_schrift = "Tahoma"
farbe = "darkslategrey"
text = (schriftart, 10)
sm_text = (schriftart, 10)
aktion = (b_schrift, 12)
entry = (schriftart, 11)
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
plus_button = None
ableitungs_popup = None
integration_popup = None
fourier_popup = None
rfourier_popup = None
filter_popup = None

input_frame_visible = True
button_frame_visible = True

def main():
    global main_frame
    main_frame = ttk.Frame(root)
    main_frame.pack(fill='both', expand=True)

    input_frame_setup()
    plot_frame_setup()
    button_frame_setup()
    setup_toggle_buttons()
    setup_legend_and_settings_buttons()

    add_input_field()
    root.mainloop()

def input_frame_setup():
    global input_frame, toggle_left_frame
    # Erstelle input_frame
    input_frame = ttk.Frame(main_frame, width=int(screen_width * 0.8 * 0.2))
    input_frame.pack(side='left', fill='y', padx=5, pady=10)
    input_frame.pack_propagate(False)

    # Erstelle toggle_left_frame
    toggle_left_frame = ttk.Frame(main_frame, width=30)
    toggle_left_frame.pack(side='left', fill='y', padx=0, pady=0)
    toggle_left_frame.pack_propagate(False)

def plot_frame_setup():
    global fig, ax, canvas, canvas_widget, plot_frame, toggle_right_frame
    # Erstelle plot_frame
    plot_frame = ttk.Frame(main_frame)
    plot_frame.pack(side='left', fill='both', expand=True, padx=10, pady=20)
    plot_frame.pack_propagate(False)

    # Erstelle toggle_right_frame
    toggle_right_frame = ttk.Frame(main_frame, width=30)
    toggle_right_frame.pack(side='right', fill='y')
    toggle_right_frame.pack_propagate(False)

    # Matplotlib-Figur und Achsen
    fig = Figure(figsize=(5, 7), dpi=100)
    ax = fig.add_subplot(111)

    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(fill='both', expand=True)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_linewidth(1)
    ax.spines["left"].set_linewidth(1)
    ax.spines["bottom"].set_color(farbe)
    ax.spines["left"].set_color(farbe)
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.tick_params(axis='both', labelsize=10, labelcolor=farbe)

    error_label = ttk.Label(root, text="", foreground="red", font=text)
    error_label.pack(pady=5)

    canvas.mpl_connect("button_press_event", lambda event: logic_gui.on_press(event, ax, canvas))
    canvas.mpl_connect("motion_notify_event", lambda event: logic_gui.on_motion(event, ax, canvas))
    canvas.mpl_connect("button_release_event", lambda event: logic_gui.on_release(event))
    canvas.mpl_connect("scroll_event", lambda event: logic_gui.on_scroll(event, ax, canvas))

def button_frame_setup():
    global button_frame, filter_button, ableitung_button, integration_button, ft_button, rft_button
    # Erstelle button_frame
    button_frame = ttk.Frame(main_frame, width=int(screen_width * 0.8 * 0.15))
    button_frame.pack(
        side='right',
        fill='y',
        padx=(5, 40),
        before=toggle_right_frame
    )
    button_frame.pack_propagate(False)

    # Erstelle Buttons
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
        command=open_fourier_popup,
        style="TextButton.TButton"
    )
    rft_button = ttk.Button(
        button_frame,
        text="Rücktransformierte",
        command=open_rfourier_popup,
        style="TextButton.TButton"
    )

    # Packe Buttons
    spacer_top = ttk.Frame(button_frame, height=130)
    spacer_top.pack(fill='x')
    filter_button.pack(fill='x', pady=10, ipady=9, padx=5, anchor='e')
    ableitung_button.pack(fill='x', pady=10, ipady=9, padx=5, anchor='e')
    integration_button.pack(fill='x', pady=10, ipady=9, padx=5, anchor='e')
    ft_button.pack(fill='x', pady=10, ipady=9, padx=5, anchor='e')
    rft_button.pack(fill='x', pady=10, ipady=9, padx=5, anchor='e')

def setup_toggle_buttons():
    global toggle_input_button, toggle_addons_button
    # Erstelle Toggle-Buttons
    toggle_input_button = ttk.Button(
        toggle_left_frame,
        text="↩",
        style="AktionButton.TButton",
        command=lambda: toggle_input_fields()
    )
    toggle_input_button.pack(pady=(screen_height//2, 0))

    toggle_addons_button = ttk.Button(
        toggle_right_frame,
        text="↪",
        style="AktionButton.TButton",
        command=lambda: toggle_addons()
    )
    toggle_addons_button.pack(pady=(screen_height//2, 0))

def setup_legend_and_settings_buttons():
    global legend_button, settings_button
    legend_button = ttk.Button(
        main_frame,
        text="Legende",
        style="TextButton.TButton",
        command=open_legend
    )
    legend_button.place(
        relx=0.03,
        rely=0.96,
        anchor='sw',
        width=90,
        height=40
    )

    settings_button = ttk.Button(
        main_frame,
        text="Einstellungen",
        style="TextButton.TButton",
        command=open_settings
    )
    settings_button.place(
        relx=0.97,
        rely=0.96,
        anchor='se',
        width=115,
        height=40
    )


def toggle_input_fields():
    global input_frame_visible

    if input_frame_visible:
        input_frame.pack_forget()
        toggle_input_button.config(text="↪")
    else:
        input_frame.pack(
            side='left',
            fill='y',
            padx=5,
            pady=10,
            before=toggle_left_frame
        )
        toggle_input_button.config(text="↩")

    input_frame_visible = not input_frame_visible
    logic_gui.plot_functions(canvas, ax)

def toggle_addons():
    global button_frame_visible

    if button_frame_visible:
        button_frame.pack_forget()
        toggle_addons_button.config(text="↩")
    else:
        button_frame.pack(
            side='right',
            fill='y',
            padx=5,
            pady=10,
            before=toggle_right_frame
        )
        toggle_addons_button.config(text="↪")

    button_frame_visible = not button_frame_visible
    logic_gui.plot_functions(canvas, ax)

def open_settings():
    settings_window = Toplevel(root)
    settings_window.title("Einstellungen")
    settings_window.geometry("350x400")

    frame = Frame(settings_window)
    frame.pack(padx=15, pady=15, fill="both", expand=True)

    def open_coordinate_popup():
        from class_function import x_range_kord, y_range_kord

        popup = Toplevel(settings_window)
        popup.title("Koordinatensystem")
        popup.geometry("350x250")

        # Speichere den aktuellen Zoom-Bereich (X- und Y-Achse)
        original_x_range = list(x_range_kord)
        original_y_range = list(y_range_kord)

        # Variable für die Auswahl
        selection = tk.StringVar()
        if getattr(class_function, 'show_negative_only', False):
            selection.set("negative")
        elif class_function.show_positive_only:
            selection.set("positive")
        else:
            selection.set("all")

        def apply():
            # Wende die Auswahl an
            if selection.get() == "positive":
                class_function.show_positive_only = True
                class_function.show_negative_only = False
            elif selection.get() == "negative":
                class_function.show_positive_only = False
                class_function.show_negative_only = True
            else:  # "all"
                class_function.show_positive_only = False
                class_function.show_negative_only = False

            # Zeichne die Funktionen mit den neuen Filtereinstellungen
            logic_gui.plot_functions(canvas, ax)


            # Stelle den ursprünglichen Zoom-Bereich wieder her
            x_range_kord[:] = original_x_range
            y_range_kord[:] = original_y_range

            # Setze den Achsenbereich zurück
            ax.set_xlim(original_x_range)
            if class_function.show_positive_only:
                ax.set_ylim(bottom=0)  # Nur positive Y-Werte
            elif getattr(class_function, 'show_negative_only', False):
                ax.set_ylim(top=0)  # Nur negative Y-Werte
            else:
                ax.set_ylim(original_y_range)  # Standard-Y-Bereich

            canvas.draw()
            popup.destroy()

        # Radiobuttons für die Auswahl
        tk.Radiobutton(
            popup,
            text="Positive & Negative Y-Werte",
            variable=selection,
            value="all"
        ).pack(anchor="w", pady=5)

        tk.Radiobutton(
            popup,
            text="Nur positive Y-Werte",
            variable=selection,
            value="positive"
        ).pack(anchor="w", pady=5)

        tk.Radiobutton(
            popup,
            text="Nur negative Y-Werte",
            variable=selection,
            value="negative"
        ).pack(anchor="w", pady=5)

        # Button zum Übernehmen
        ttk.Button(popup, text="Übernehmen", command=apply).pack(pady=15)


    def open_axis_popup():
        popup = Toplevel(settings_window)
        popup.title("Achsen")
        popup.geometry("300x200")

        x_var = BooleanVar(value=logic_gui.axis_in_radians)
        y_var = BooleanVar(value=False)

        def apply():
            logic_gui.axis_in_radians = x_var.get()
            logic_gui.plot_functions(canvas, ax)
            popup.destroy()

        Checkbutton(popup, text="X-Achse in Bogenmaß", variable=x_var).pack(anchor="w", pady=5)
        Checkbutton(popup, text="Y-Achse in Bogenmaß", variable=y_var).pack(anchor="w", pady=5)

        ttk.Button(popup, text="Übernehmen", command=apply).pack(pady=15)

    def open_palette_popup():
        popup = Toplevel(settings_window)
        popup.title("Farbpalette")
        popup.geometry("400x450")

        selected_palette = tk.IntVar(value=class_function.palette_index)

        def apply():
            class_function.palette_index = selected_palette.get()
            class_function.colors = color_palettes[class_function.palette_index]

            ax.clear()
            logic_gui.plot_functions(canvas, ax)

            for i, circle in enumerate(class_function.color_circles):
                if i < len(class_function.colors):
                    circle.config(bg=class_function.colors[i])

            if 'ableitungs_popup' in globals() and ableitungs_popup is not None and ableitungs_popup.winfo_exists():
                for widget in ableitungs_popup.winfo_children():
                    if isinstance(widget, Canvas) and widget.cget("width") == "20" and widget.cget("height") == "20":
                        idx = class_function.func_names.index(widget.master.winfo_children()[1].cget("text").split("(")[0])
                        widget.config(bg=class_function.colors[idx])

            if 'integration_popup' in globals() and integration_popup is not None and integration_popup.winfo_exists():
                for widget in integration_popup.winfo_children():
                    if isinstance(widget, Canvas) and widget.cget("width") == "20" and widget.cget("height") == "20":
                        idx = class_function.func_names.index(widget.master.winfo_children()[1].cget("text").split("(")[0])
                        widget.config(bg=class_function.colors[idx])

            if 'ableitungs_popup' in globals() and ableitungs_popup is not None and ableitungs_popup.winfo_exists():
                ableitungs_popup.destroy()
                open_ableitung_popup()

            if 'integration_popup' in globals() and integration_popup is not None and integration_popup.winfo_exists():
                integration_popup.destroy()
                open_integration_popup()

            canvas.draw()
            popup.destroy()

        ttk.Label(popup, text="Palette auswählen:", font=text).pack(pady=10)

        for idx, palette in enumerate(color_palettes):
            row = Frame(popup)
            row.pack(fill="x", pady=5)

            rb = Radiobutton(
                row,
                text=f"{color_palette_names[idx]}",
                variable=selected_palette,
                value=idx
            )
            rb.pack(side="left", padx=5)

            preview = Frame(row, width=180, height=20)
            preview.pack(side="left", padx=10)
            preview.pack_propagate(False)

            for col, color in enumerate(palette[:max_funcs]):
                c = Canvas(
                    preview,
                    width=18,
                    height=18,
                    bg=color,
                    highlightthickness=0
                )
                c.place(x=2 + col * 22, y=1)

        ttk.Button(popup, text="Übernehmen", command=apply).pack(pady=20)


    
    def open_max_funcs_popup():
        popup = Toplevel(settings_window)
        popup.title("Maximale Funktionen")
        popup.geometry("300x180")

        tk.Label(popup, text="Zahl (1-10):").pack(pady=10)

        entry = ttk.Entry(popup)
        entry.pack(pady=5)

        def apply():
            try:
                value = int(entry.get())

                if value < 1 or value > 10:
                    messagebox.showerror("Fehler", "Nur Zahlen zwischen 1 und 10 erlaubt.")
                    return

                global max_funcs
                global plus_button

                max_funcs = value

                while len(func_entries) > max_funcs:
                    delete_input_field(len(func_entries) - 1)

                if len(func_entries) < max_funcs:
                    if plus_button:
                        plus_button.destroy()

                    plus_button = ttk.Button(
                        input_frame,
                        text="+",
                        width=3,
                        command=add_input_field,
                        style="AktionButton.TButton"
                    )

                    plus_button.grid(
                        row=len(func_entries),
                        column=0,
                        columnspan=2,
                        pady=10
                    )

                logic_gui.plot_functions(canvas, ax)
                popup.destroy()

            except ValueError:
                messagebox.showerror("Fehler", "Bitte eine gültige Zahl eingeben.")

        ttk.Button(popup, text="Anwenden", command=apply).pack(pady=15)

    ttk.Button(frame, text="Max. Funktionen", command=open_max_funcs_popup, width=25).pack(ipady=10, pady=10)
    ttk.Button(frame, text="Koordinatensystem", command=open_coordinate_popup, width=25).pack(ipady=10, pady=10)
    ttk.Button(frame, text="Achsen", command=open_axis_popup, width=25).pack(ipady=10, pady=10)
    ttk.Button(frame, text="Farbpalette", command=open_palette_popup, width=25).pack(ipady=10, pady=10)


def add_input_field():
    global plus_button

    if len(func_entries) >= max_funcs:
        return

    row = len(func_entries)

    # Erweitere func_names, falls nötig
    if len(func_names) <= row:
        alphabet = "fghijklmnopqrstuvwxyz"
        func_names.append(alphabet[row])

    entry_frame = ttk.Frame(input_frame)

    top_padding = 40 if row == 0 else 20

    entry_frame.grid(
        row=row,
        column=0,
        columnspan=2,
        padx=5,
        pady=(top_padding, 20),
        sticky='ew'
    )

    # Farbkreis
    circle = Canvas(
        entry_frame,
        width=20,
        height=20,
        bg=class_function.colors[row],
        bd=0,
        highlightthickness=0
    )
    circle.grid(row=0, column=0, padx=(0, 5))

    # Entry
    entry = ttk.Entry(entry_frame, width=20, font=text)
    entry.grid(row=0, column=1, sticky='ew', ipady=5)

    entry.func_name = func_names[row]

    # Interpretationslabel
    interpreted_label = ttk.Label(
        entry_frame,
        text="Interpretiert als: ",
        foreground="gray",
        font=sm_text
    )
    interpreted_label.grid(row=1, column=0, columnspan=2, sticky='w')
    interpreted_label.grid_remove()

    # Delete Button
    delete_button = ttk.Button(
        entry_frame,
        text="-",
        width=2,
        command=lambda idx=row: delete_input_field(idx),
        style="AktionButton.TButton"
    )
    delete_button.grid(row=0, column=2, padx=2)

    # Event Bindings
    entry.bind("<FocusIn>", lambda e, idx=row: on_focus_in(idx))
    entry.bind("<FocusOut>", lambda e, idx=row: on_focus_out(idx))
    entry.bind("<KeyRelease>", lambda e, idx=row: on_entry_change(e, idx, None))

    func_entries.append(entry)
    interpreted_labels.append(interpreted_label)
    delete_buttons.append(delete_button)
    class_function.color_circles.append(circle)

    # Plus Button neu positionieren
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
        plus_button.grid(
            row=len(func_entries),
            column=0,
            columnspan=2,
            pady=10
        )


def delete_input_field(index):
    global plus_button

    if index >= len(func_entries):
        return

    try:
        func_entries[index].master.destroy()
        interpreted_labels[index].destroy()
        delete_buttons[index].destroy()
        class_function.color_circles[index].destroy()
    except Exception as e:
        print(f"Fehler beim Löschen der Widgets: {e}")

    # Widget-Listen bereinigen
    del func_entries[index]
    del interpreted_labels[index]
    del delete_buttons[index]
    del class_function.color_circles[index]

    # Aktualisiere func_names und functions
    old_functions = list(functions.values())
    functions.clear()
    func_names.pop(index)

    alphabet = "fghijklmnopqrstuvwxyz"

    for i, func_obj in enumerate(old_functions):
        if i == index:
            continue

        new_name = alphabet[i]
        func_obj.name = new_name
        functions[new_name] = func_obj
        if i < index:
            func_names[i] = new_name

    for row, entry in enumerate(func_entries):
        func_obj = functions.get(func_names[row], None)

        frame = entry.master
        frame.grid(row=row, column=0, columnspan=2, padx=5, pady=15, sticky='ew')

        class_function.color_circles[row].config(bg=class_function.colors[row])

        entry.func_name = func_names[row]
        entry.bind("<FocusIn>", lambda e, idx=row: on_focus_in(idx))
        entry.bind("<FocusOut>", lambda e, idx=row: on_focus_out(idx))
        entry.bind("<KeyRelease>", lambda e, idx=row, fo=func_obj: on_entry_change(e, idx, fo))

        delete_buttons[row].config(command=lambda idx=row: delete_input_field(idx))

    # Plus Button neu setzen
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

    # Plot komplett neu zeichnen
    try:
        ax.clear()
        logic_gui.plot_functions(canvas, ax)
    except Exception as e:
        print(f"Fehler beim Neuzeichnen der Funktionen: {e}")



def on_focus_in(index):
    entry = func_entries[index]
    func_name = entry.func_name

    interpreted_labels[index].grid()

    if func_name in functions:
        entry.delete(0, tk.END)
        entry.insert(0, functions[func_name].raw_expr)

    update_interpretation(index)

def on_focus_out(index):
    interpreted_labels[index].grid_remove()

    entry = func_entries[index]
    func_name = entry.func_name
    raw_text = entry.get().strip()

    if not raw_text:
        return

    try:
        if func_name not in functions:
            functions[func_name] = Funktion(func_name, raw_text)
        else:
            functions[func_name].update(raw_text)

        interpreted_text = interpreted(raw_text)

        entry.delete(0, tk.END)
        entry.insert(0, interpreted_text)

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
        print(f"Fehler bei der Überprüfung des Ausdrucks: {e}")
        return False

def on_entry_change(event, index, func_obj=None):

    if index >= len(func_entries):
        return

    entry = func_entries[index]
    func_name = entry.func_name
    label = interpreted_labels[index]

    text = entry.get().strip()

    if not text:
        label.config(
            text="Interpretiert als: ",
            foreground="gray"
        )
        return

    try:
        parser(text)

        if func_name not in functions:
            functions[func_name] = Funktion(func_name, text)
        else:
            functions[func_name].update(text)

        interpreted_expr = interpreted(text)

        label.config(
            text=f"Interpretiert als: {interpreted_expr}",
            foreground="gray"
        )

        ax.clear()
        logic_gui.plot_functions(canvas, ax)
        canvas.draw()

    except Exception as e:
        handle_error(
            expr=text,
            error=e,
            func_name=func_name,
            label=label,
            max_line_length=45
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
            func_list.append(func_name)

    if not func_list:
        ttk.Label(frame, text="Keine Funktionen definiert.", font=text).pack(pady=10)
        return

    for func_name in func_list:
        idx = func_names.index(func_name)
        base_color = class_function.colors[idx]
        func_obj = functions[func_name]

        container = Frame(frame)
        container.pack(pady=5, fill='x')

        circle = Canvas(container, width=20, height=20,
                        bg=base_color, bd=0, highlightthickness=0)
        circle.pack(side='left', padx=(0, 5))

        btn = ttk.Button(
            container,
            text=f"{func_name}(x) = {interpreted(func_obj.raw_expr)}",
            command=lambda fo=func_obj: open_derivative_window(fo),
            style="TextButton.TButton",
            padding=(5, 12)
        )
        btn.pack(side='left', fill='x', expand=True)

    def open_derivative_window(func_obj):

        ableitungs_popup.destroy()

        deriv_popup = Toplevel(root)
        deriv_popup.title(f"Ableitung von {func_obj.name}")
        deriv_popup.geometry("500x450")

        main_frame = Frame(deriv_popup, padx=15, pady=10)
        main_frame.pack(fill='both', expand=True)

        ttk.Label(
            main_frame,
            text=f"Ableitung von f(x) = {interpreted(func_obj.raw_expr)}",
            font=text
        ).pack(pady=(0, 10))

        input_frame = Frame(main_frame)
        input_frame.pack(fill='x', pady=5)

        ttk.Label(input_frame, text="x:", font=text).grid(row=0, column=0, padx=(170, 0))

        entry_x = ttk.Entry(input_frame, font=text, width=10)
        entry_x.grid(row=0, column=1, padx=(5, 200))
        entry_x.insert(0, "0")

        plot_frame = Frame(main_frame, width=450, height=300)
        plot_frame.pack(pady=5)
        plot_frame.pack_propagate(False)

        fig = Figure(figsize=(4.5, 3), dpi=90)
        plot_ax = fig.add_subplot(111)

        canvas_local = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas_local.get_tk_widget().pack(fill='both', expand=False)

        plot_ax.spines["top"].set_visible(False)
        plot_ax.spines["right"].set_visible(False)
        plot_ax.spines["bottom"].set_color(farbe)
        plot_ax.spines["left"].set_color(farbe)

        idx = func_names.index(func_obj.name)
        base_color = class_function.colors[idx]
        light_color = lighter_color(base_color)

        result_label = ttk.Label(main_frame, text="", font=text)
        result_label.pack(pady=5)

        func = conv_to_func(func_obj.parsed_expr)

        deriv_str = ableitung(func_obj)
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

            x_vals = np.linspace(x_val - 5, x_val + 5, 400)

            y = func(x_vals)
            y_deriv = deriv_func(x_vals)

            plot_ax.clear()

            plot_ax.plot(x_vals, y, color=base_color,
                         label=f"f(x) = {interpreted(func_obj.raw_expr)}")

            plot_ax.plot(x_vals, y_deriv, color=light_color,
                         linestyle="--",
                         label=f"f'(x) = {interpreted(deriv_str)}")

            y_val = deriv_func(x_val)

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

    integration_popup = Toplevel(root)
    integration_popup.title("Integration")
    integration_popup.geometry("300x400")

    frame = Frame(integration_popup)
    frame.pack(padx=15, pady=15, fill='both', expand=True)

    func_list = []

    for func_name in func_names:
        if func_name in functions:
            func_list.append(func_name)

    if not func_list:
        ttk.Label(frame, text="Keine Funktionen definiert.", font=text).pack(pady=10)
        return

    for func_name in func_list:
        idx = func_names.index(func_name)
        base_color = class_function.colors[idx]
        func_obj = functions[func_name]

        container = Frame(frame)
        container.pack(pady=5, fill='x')

        circle = Canvas(container, width=20, height=20,
                        bg=base_color, bd=0, highlightthickness=0)
        circle.pack(side='left', padx=(0, 5))

        btn = ttk.Button(
            container,
            text=f"{func_name}(x) = {interpreted(func_obj.raw_expr)}",
            command=lambda fo=func_obj: open_integration_window(fo),
            style="TextButton.TButton",
            padding=(5, 12)
        )
        btn.pack(side='left', fill='x', expand=True)

    def open_integration_window(func_obj):

        integration_popup.destroy()

        popup = Toplevel(root)
        popup.title(f"Integration von {func_obj.name}")
        popup.geometry("500x450")

        main_frame = Frame(popup, padx=15, pady=10)
        main_frame.pack(fill='both', expand=True)

        ttk.Label(
            main_frame,
            text=f"Integration von f(x) = {interpreted(func_obj.raw_expr)}",
            font=text
        ).pack(pady=(0, 10))

        input_frame = Frame(main_frame)
        input_frame.pack(fill='x', pady=5)

        ttk.Label(input_frame, text="a:", font=text).grid(row=0, column=0, padx=(50, 5))
        entry_a = ttk.Entry(input_frame, font=text, width=10)
        entry_a.grid(row=0, column=1, padx=(0, 85))

        ttk.Label(input_frame, text="b:", font=text).grid(row=0, column=2, padx=(20, 5))
        entry_b = ttk.Entry(input_frame, font=text, width=10)
        entry_b.grid(row=0, column=3, padx=(0, 95))

        plot_frame = Frame(main_frame, width=450, height=300)
        plot_frame.pack(pady=5)
        plot_frame.pack_propagate(False)

        fig = Figure(figsize=(4.5, 3), dpi=90)
        plot_ax = fig.add_subplot(111)

        canvas_local = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas_local.get_tk_widget().pack(fill='both', expand=False)

        idx = func_names.index(func_obj.name)
        base_color = class_function.colors[idx]
        dark_color = darker_color(base_color)

        result_label = ttk.Label(main_frame, text="", font=text)
        result_label.pack(pady=5)

        func = conv_to_func(func_obj.parsed_expr)

        integral_str = integration(func_obj)

        plot_integral_str = integral_str.replace("+ C", "").replace("+C", "").strip()
        integral_func = conv_to_func(parser(plot_integral_str))

        def parse_val(val):
            val = val.replace("pi", str(np.pi))
            val = val.replace("tau", str(2 * np.pi))
            return float(eval(val))

        def update_plot(event=None):
            try:
                a = parse_val(entry_a.get())
                b = parse_val(entry_b.get())
            except:
                result_label.config(text="Ungültige Grenzen", foreground="red")
                return

            x_vals = np.linspace(min(a, b) - 5, max(a, b) + 5, 400)

            y = func(x_vals)
            Y = integral_func(x_vals)

            plot_ax.clear()

            plot_ax.plot(x_vals, y, color=base_color,
                         label=f"f(x) = {interpreted(func_obj.raw_expr)}")

            plot_ax.plot(x_vals, Y, color=dark_color,
                         linestyle="--",
                         label=f"F(x) = {interpreted(integral_str)}")

            Fa = integral_func(a)
            Fb = integral_func(b)
            value = Fb - Fa

            result_label.config(
                text=f"F({b:.2f}) − F({a:.2f}) = {value:.4f}",
                foreground="black"
            )

            plot_ax.legend(fontsize=9)
            canvas_local.draw()

        entry_a.bind("<KeyRelease>", update_plot)
        entry_b.bind("<KeyRelease>", update_plot)

        entry_a.insert(0, "0")
        entry_b.insert(0, "0")

        update_plot()

def open_fourier_popup():
    global fourier_popup

    if 'fourier_popup' in globals() and fourier_popup is not None and fourier_popup.winfo_exists():
        fourier_popup.destroy()
        fourier_popup = None

    fourier_popup = Toplevel(root)
    fourier_popup.title("Fourier Transformation")
    fourier_popup.geometry("300x400")

    frame = Frame(fourier_popup)
    frame.pack(padx=15, pady=15, fill='both', expand=True)

    func_list = [name for name in func_names if name in functions]

    if not func_list:
        ttk.Label(frame, text="Keine Funktionen definiert.", font=text).pack(pady=10)
        return

    for func_name in func_list:
        idx = func_names.index(func_name)
        base_color = class_function.colors[idx]
        func_obj = functions[func_name]

        container = Frame(frame)
        container.pack(pady=5, fill='x')

        Canvas(container, width=20, height=20,
               bg=base_color, bd=0, highlightthickness=0).pack(side='left', padx=(0,5))

        btn = ttk.Button(
            container,
            text=f"{func_name}(x) = {interpreted(func_obj.raw_expr)}",
            command=lambda fo=func_obj: open_fourier_window(fo),
            style="TextButton.TButton",
            padding=(5,12)
        )
        btn.pack(side='left', fill='x', expand=True)

    def open_fourier_window(func_obj):

        fourier_popup.destroy()

        popup = Toplevel(root)
        popup.title(f"Fourier von {func_obj.name}")
        popup.geometry("600x450")

        main_frame = Frame(popup, padx=15, pady=10)
        main_frame.pack(fill='both', expand=True)

        ttk.Label(
            main_frame,
            text=f"F̂(x) von f(x) = {interpreted(func_obj.raw_expr)}",
            font=text
        ).pack(pady=(0,10))

        plot_frame = Frame(main_frame, width=550, height=350)
        plot_frame.pack()
        plot_frame.pack_propagate(False)

        fig = Figure(figsize=(5,3.5), dpi=90)
        ax_local = fig.add_subplot(111)

        canvas_local = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas_local.get_tk_widget().pack(fill='both', expand=True)

        idx = func_names.index(func_obj.name)
        base_color = class_function.colors[idx]

        fourier_str = fourier(func_obj)

        fourier_plot_str = fourier_str.replace("w", "f")

        try:
            fourier_func = conv_to_func(parser(fourier_plot_str))
        except:
            fourier_func = None

        def update_plot():

            ax_local.clear()

            try:
                x_vals = np.linspace(-10,10,400)

                if fourier_func:
                    y_vals = fourier_func(x_vals)
                    ax_local.plot(x_vals, y_vals, color=base_color,
                                label=f"F̂(f) = {fourier_str}")

            except:
                pass

            ax_local.legend(fontsize=9)
            canvas_local.draw()

        update_plot()


def open_rfourier_popup():
    global rfourier_popup

    if 'rfourier_popup' in globals() and rfourier_popup is not None and rfourier_popup.winfo_exists():
        rfourier_popup.destroy()
        rfourier_popup = None

    rfourier_popup = Toplevel(root)
    rfourier_popup.title("Rück-Fourier Transformation")
    rfourier_popup.geometry("300x400")

    frame = Frame(rfourier_popup)
    frame.pack(padx=15, pady=15, fill='both', expand=True)

    func_list = [name for name in func_names if name in functions]

    if not func_list:
        ttk.Label(frame, text="Keine Funktionen definiert.", font=text).pack(pady=10)
        return

    for func_name in func_list:
        idx = func_names.index(func_name)
        base_color = class_function.colors[idx]
        func_obj = functions[func_name]

        container = Frame(frame)
        container.pack(pady=5, fill='x')

        Canvas(container, width=20, height=20,
               bg=base_color, bd=0, highlightthickness=0).pack(side='left', padx=(0,5))

        btn = ttk.Button(
            container,
            text=f"{func_name}(x) = {interpreted(func_obj.raw_expr)}",
            command=lambda fo=func_obj: open_rfourier_window(fo),
            style="TextButton.TButton",
            padding=(5,12)
        )
        btn.pack(side='left', fill='x', expand=True)
    
    def open_rfourier_window(func_obj):

        rfourier_popup.destroy()

        popup = Toplevel(root)
        popup.title(f"Rück-Fourier von {func_obj.name}")
        popup.geometry("600x450")

        main_frame = Frame(popup, padx=15, pady=10)
        main_frame.pack(fill='both', expand=True)

        ttk.Label(
            main_frame,
            text=f"F(x) = ℱ⁻¹({interpreted(func_obj.raw_expr)})",
            font=text
        ).pack(pady=(0,10))

        plot_frame = Frame(main_frame, width=550, height=350)
        plot_frame.pack()
        plot_frame.pack_propagate(False)

        fig = Figure(figsize=(5,3.5), dpi=90)
        ax_local = fig.add_subplot(111)

        canvas_local = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas_local.get_tk_widget().pack(fill='both', expand=True)

        idx = func_names.index(func_obj.name)
        base_color = class_function.colors[idx]

        rfourier_str = rfourier(func_obj)

        try:
            rfourier_func = conv_to_func(parser(rfourier_str))
        except:
            rfourier_func = None

        def update_plot():

            ax_local.clear()

            try:
                x_vals = np.linspace(-10,10,400)

                if rfourier_func:
                    y_vals = rfourier_func(x_vals)
                    ax_local.plot(x_vals, y_vals, color=base_color,
                                label=f"ℱ⁻¹ = {rfourier_str}")

            except:
                pass

            ax_local.legend(fontsize=9)
            canvas_local.draw()

        update_plot()



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


    for row, (func_name, func_str) in enumerate(func_list, start=2):
        idx = func_names.index(func_name)
        base_color = class_function.colors[idx]

        circle = Canvas(table, width=18, height=18, bg=base_color, bd=0, highlightthickness=0)
        circle.grid(row=row, column=0, padx=(0, 5), pady=4)

        func_label = ttk.Label(table, text=f"{func_name}(x) = {interpreted(func_str)}", font=text, anchor="w")
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
        hide_check = Checkbutton(table, text="Ausblenden", variable=hide_var, font=sm_text)
        hide_check.grid(row=row, column=6, padx=3, sticky="w")

        reset_button = ttk.Button(
            table,
            text="↻",
            style="AktionButton.TButton",
            width=2,
            command=lambda fn=func_name: reset_filter_row(fn)
        )
        reset_button.grid(row=row, column=7, padx=2)

        # --- Vorher gespeicherte Filterwerte übernehmen ---
        if func_name in class_function.filter_funcs:
            cf = class_function.filter_funcs[func_name]
            x_from_entry.delete(0, tk.END)
            if cf[0] is not None:
                x_from_entry.insert(0, str(cf[0]))
            x_to_entry.delete(0, tk.END)
            if cf[1] is not None:
                x_to_entry.insert(0, str(cf[1]))
            y_from_entry.delete(0, tk.END)
            if cf[2] is not None:
                y_from_entry.insert(0, str(cf[2]))
            y_to_entry.delete(0, tk.END)
            if cf[3] is not None:
                y_to_entry.insert(0, str(cf[3]))
            hide_var.set(cf[4])

        entry_widgets[func_name] = {
            "x_from": x_from_entry,
            "x_to": x_to_entry,
            "y_from": y_from_entry,
            "y_to": y_to_entry,
            "hide": hide_var
        }

    button_frame = Frame(frame)
    button_frame.pack(pady=15)

    def apply_and_store_filters():
        # Filter anwenden
        process_filters(entry_widgets, canvas, ax)
        # Alle angewendeten Filter in class_function.filter_funcs speichern
        for fname, widgets in entry_widgets.items():
            x_from_val = widgets["x_from"].get().strip() or None
            x_to_val = widgets["x_to"].get().strip() or None
            y_from_val = widgets["y_from"].get().strip() or None
            y_to_val = widgets["y_to"].get().strip() or None
            hide_val = widgets["hide"].get()
            class_function.filter_funcs[fname] = [x_from_val, x_to_val, y_from_val, y_to_val, hide_val]
        # Popup schließen
        filter_popup.destroy()

    def reset_all_filters():
        global entry_widgets
        for func_name, widgets in entry_widgets.items():
            widgets["x_from"].delete(0, 'end')
            widgets["x_to"].delete(0, 'end')
            widgets["y_from"].delete(0, 'end')
            widgets["y_to"].delete(0, 'end')
            widgets["hide"].set(False)
            class_function.filter_funcs[func_name] = [None, None, None, None, False]

            # Funktion neu plotten
            func_obj = functions[func_name]
            f = conv_to_func(func_obj.parsed_expr)
            x = np.linspace(-50, 50, 1000)
            y = f(x)
            for line in ax.lines[:]:
                if line.get_label().startswith(func_name):
                    line.remove()
            ax.plot(x, y, label=f"{func_name}(x) = {interpreted(func_obj.raw_expr)}", color=class_function.colors[func_names.index(func_name)])

        ax.legend(fontsize=12)
        canvas.draw()

    apply_button = ttk.Button(
        button_frame,
        text="Anwenden",
        command=apply_and_store_filters,
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

def reset_filter_row(func_name):
    global entry_widgets
    if func_name not in entry_widgets:
        return

    widgets = entry_widgets[func_name]
    # Eingabefelder leeren
    widgets["x_from"].delete(0, 'end')
    widgets["x_to"].delete(0, 'end')
    widgets["y_from"].delete(0, 'end')
    widgets["y_to"].delete(0, 'end')
    widgets["hide"].set(False)

    # Filter zurücksetzen
    class_function.filter_funcs[func_name] = [None, None, None, None, False]

    # Funktion neu plotten
    func_obj = functions[func_name]
    f = conv_to_func(func_obj.parsed_expr)
    x = np.linspace(-50, 50, 1000)
    y = f(x)

    # Alte Linien der Funktion entfernen
    for line in ax.lines[:]:
        if line.get_label().startswith(func_name):
            line.remove()

    # Neue Linie plotten
    ax.plot(x, y, label=f"{func_name}(x) = {interpreted(func_obj.raw_expr)}",
            color=class_function.colors[func_names.index(func_name)])
    ax.legend(fontsize=12)
    canvas.draw() 
    
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
    for func in comp_input.allowed_funcs.keys():
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

if __name__ == "__main__":
    main()