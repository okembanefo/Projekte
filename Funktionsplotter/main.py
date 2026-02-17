import tkinter as tk
import numpy as np
from tkinter import ttk, BooleanVar, Checkbutton, Toplevel, Frame, Canvas, messagebox, simpledialog, font
import logic_gui
import comp_input
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from add_ons import ableitung, integration
from comp_input import interpreted, parser
from plot_logic import conv_to_func
from logic_gui import plot_functions, lighter_color, darker_color


# Einheitliche Schriftart und Farbe
schriftart = "Calibri"
farbe = "darkslategrey"
text = (schriftart, 12)
sm_text = (schriftart, 10)
aktion = (schriftart, 18)
entry = (schriftart, 12)
plt.rcParams['font.family'] = schriftart
plt.rcParams['font.size'] = 10

# Styles für Textbutton und Aktionsbutton
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


# Hauptfenster
root = tk.Tk()
root.title("Funktionsplotter")

# Fenstergröße und Layout
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry(f"{int(screen_width*0.8)}x{int(screen_height*0.8)}+{int(screen_width*0.1)}+{int(screen_height*0.1)}")

# Globale Variablen für die GUI
func_entries = []
interpreted_labels = []
delete_buttons = []
color_circles = []
plus_button = None
ableitungs_popup = None


# Hauptframe für Eingabefelder und Koordinatensystem
main_frame = ttk.Frame(root)
main_frame.pack(fill='both', expand=True)

# Frame für Eingabefelder (links)
input_frame = ttk.Frame(main_frame, width=int(screen_width*0.8*1/3))
input_frame.pack(side='left', fill='y', padx=5, pady=10)
input_frame.pack_propagate(False)

# Frame für Koordinatensystem (mittig)
plot_frame = ttk.Frame(main_frame, height=400) 
plot_frame.pack(side='left', fill='both', expand=True, padx=5, pady=5)
plot_frame.pack_propagate(False)

# Frame für Buttons (rechts)
button_frame = ttk.Frame(main_frame, width=int(screen_width*0.8*1/5))
button_frame.pack(side='right', fill='y', padx=5, pady=10)
button_frame.pack_propagate(False)

# Koordinatensystem
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

ax.spines["bottom"].set_color(farbe)   # x-Achse
ax.spines["left"].set_color(farbe)    # y-Achse

ax.set_xlabel("")
ax.set_ylabel("")

ax.tick_params(axis='both', labelsize=10, labelcolor=farbe)

# Fehlerlabel
error_label = ttk.Label(root, text="", foreground="red", font=text)
error_label.pack(pady=5)


def open_settings():
    """Öffnet das Einstellungsfenster."""
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

    if len(func_entries) >= logic_gui.max_funcs:
        return

    row = len(func_entries)
    entry_frame = ttk.Frame(input_frame)
    entry_frame.grid(row=row, column=0, columnspan=2, padx=5, pady=20, sticky='ew')

    # Farbiger Kreis
    circle = Canvas(entry_frame, width=20, height=20, bg=logic_gui.colors[row], bd=0, highlightthickness=0)
    circle.grid(row=0, column=0, padx=(0, 5))

    # Eingabefeld
    entry = ttk.Entry(entry_frame, width=20, font=text)
    entry.grid(row=0, column=1, sticky='ew', ipady=5)            

    # Interpretationsfeld
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
        text="X",
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

    if len(func_entries) < logic_gui.max_funcs:
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

    # --- Widgets zerstören ---
    try:
        func_entries[index].master.destroy()
        interpreted_labels[index].destroy()
        delete_buttons[index].destroy()
        color_circles[index].destroy()
    except Exception as e:
        print(f"Fehler beim Löschen der Widgets: {e}")

    # --- Entferne aus Listen ---
    del func_entries[index]
    del interpreted_labels[index]
    del delete_buttons[index]
    del color_circles[index]

    # --- Funktion aus func_dict löschen ---
    func_keys = list(logic_gui.func_dict.keys())
    if index < len(func_keys):
        key_to_delete = func_keys[index]
        del logic_gui.func_dict[key_to_delete]

    # --- Alle verbleibenden Funktionen nach oben verschieben ---
    new_func_dict = {}
    remaining_keys = list(logic_gui.func_dict.keys())
    for new_key_index, old_key in enumerate(remaining_keys):
        new_key = logic_gui.func_names[new_key_index]
        new_func_dict[new_key] = logic_gui.func_dict[old_key]
    logic_gui.func_dict = new_func_dict

    # --- Alle Eingabefelder neu anordnen, Farben und Index anpassen ---
    for row, entry in enumerate(func_entries):
        frame = entry.master
        frame.grid(row=row, column=0, columnspan=2, padx=5, pady=15, sticky='ew')

        # Farbkreis aktualisieren
        color_circles[row].config(bg=logic_gui.colors[row])

        # Bindings mit neuem Index setzen
        entry.bind("<FocusIn>", lambda e, idx=row: on_focus_in(idx))
        entry.bind("<FocusOut>", lambda e, idx=row: on_focus_out(idx))
        entry.bind("<KeyRelease>", lambda e, idx=row: on_entry_change(e, idx))
        delete_buttons[row].config(command=lambda idx=row: delete_input_field(idx))

    # --- Plus-Button löschen, falls vorhanden ---
    if plus_button:
        plus_button.destroy()
        plus_button = None

    # --- Plus-Button unter dem letzten Feld platzieren ---
    if len(func_entries) < logic_gui.max_funcs:
        plus_button = ttk.Button(
            input_frame,
            text="+",
            width=3,
            command=add_input_field,
            style="AktionButton.TButton"
        )
        plus_button.grid(row=len(func_entries), column=0, columnspan=2, pady=10)

    # --- Alle Funktionen aus dem Koordinatensystem löschen und neu plotten ---
    try:
        logic_gui.plot_functions(canvas, ax)
    except Exception as e:
        print(f"Fehler beim Neuzeichnen der Funktionen: {e}")



def on_focus_in(index):
    """Zeigt das Interpretationsfeld beim Fokus."""
    interpreted_labels[index].grid()
    update_interpretation(index)

def on_focus_out(index):
    """Ersetzt Entry-Text durch interpretierte Darstellung beim Verlassen."""

    # Interpretationslabel ausblenden
    interpreted_labels[index].grid_remove()

    # Aktuellen Text holen
    text = func_entries[index].get().strip()

    if not text:
        return

    try:
        interpreted_text = interpreted(text)

        func_entries[index].delete(0, tk.END)
        func_entries[index].insert(0, interpreted_text)

    except Exception as e:
        interpreted_labels[index].config(
            text=f"Fehler: {e}",
            foreground="red"
        )

def update_interpretation(index):
    """Aktualisiert das Interpretationsfeld."""
    text = func_entries[index].get().strip()
    if text:
        interpreted_expr = comp_input.interpreted(text)
        interpreted_labels[index].config(text=f"Interpretiert als: {interpreted_expr}")
    else:
        interpreted_labels[index].config(text="Interpretiert als: ")

def on_entry_change(event, index):
    """Aktualisiert die Interpretation bei jeder Eingabe."""
    if index >= len(func_entries):
        print(index)
        return

    text = func_entries[index].get().strip()
    func_name = logic_gui.func_names[index]   

    if text:
        try:
            logic_gui.func_dict[func_name] = [text]
            update_interpretation(index)
            error = logic_gui.plot_functions(canvas, ax)
            if error != True:
                error_label.config(text=error, foreground="red")
            else:
                error_label.config(text="")
        except Exception as e:  
            interpreted_labels[index].config(
                text=f"Fehler: {e}",
                foreground="red"
            )
    else:
        interpreted_labels[index].config(text="Interpretiert als: ", foreground="gray")

def open_ableitung_popup():
    global ableitungs_popup

    if ableitungs_popup is not None and ableitungs_popup.winfo_exists():
        ableitungs_popup.destroy()
        ableitungs_popup = None

    ableitungs_popup = Toplevel(root)
    ableitungs_popup.title("Ableitung berechnen")
    ableitungs_popup.geometry("300x400")

    frame = Frame(ableitungs_popup)
    frame.pack(padx=10, pady=10, fill='both')

    func_list = []
    for i, func_name in enumerate(logic_gui.func_names):
        if func_name in logic_gui.func_dict:
            func_str = logic_gui.func_dict[func_name][0]
            func_list.append((func_name, func_str))

    if not func_list:
        tk.Label(frame, text="Keine Funktionen definiert.", font=text).pack(pady=10)
        return

    for func_name, func_str in func_list:
        idx = logic_gui.func_names.index(func_name)
        base_color = logic_gui.colors[idx]

        container = Frame(frame)
        container.pack(pady=5, fill='x')

        circle = Canvas(container, width=20, height=20, bg=base_color, bd=0, highlightthickness=0)
        circle.pack(side='left', padx=(0, 5))

        btn = ttk.Button(
            container,
            text=f"{func_name} = {interpreted(func_str)}",
            command=lambda name=func_name, s=func_str: plot_ableitung(name, s),
            style="TextButton.TButton",
            padding=(5, 12)
        )
        btn.pack(side='left', fill='x', expand=True)


def select_integration_range(func_name, func_str):
    """Öffnet ein Dialogfenster zur Eingabe des Integrationsbereichs als Text (z.B. '0', 'pi', '2*pi')."""
    range_popup = Toplevel(integration_popup)
    range_popup.title(f"Integrationsbereich für {func_name}")
    range_popup.geometry("250x200")

    tk.Label(range_popup, text="Untergrenze (a):").pack(pady=5)
    entry_a = tk.Entry(range_popup)
    entry_a.pack(pady=5)
    tk.Label(range_popup, text="Obergrenze (b):").pack(pady=5)
    entry_b = tk.Entry(range_popup)
    entry_b.pack(pady=5)

    spec_cons = {
        "pi": np.pi,
        "e": np.e,
        "euler": np.e,
        "tau": 2*np.pi
    }

    def submit():
        a_str = entry_a.get()
        b_str = entry_b.get()
        try:
            a = eval(a_str, {"np": np}, spec_cons)
            b = eval(b_str, {"np": np}, spec_cons)
        except Exception as e:
            messagebox.showerror("Fehler", f"Ungültiger Wert: {e}")
            return
        range_popup.destroy()
        plot_integration(func_name, func_str, a, b)

    tk.Button(range_popup, text="OK", command=submit).pack(pady=10)

def open_integration_popup():
    global integration_popup

    if 'integration_popup' in globals() and integration_popup is not None and integration_popup.winfo_exists():
        integration_popup.destroy()
        integration_popup = None

    integration_popup = Toplevel(root)
    integration_popup.title("Integration berechnen")
    integration_popup.geometry("300x400")

    frame = Frame(integration_popup)
    frame.pack(padx=10, pady=10, fill='both')

    func_list = []
    for i, func_name in enumerate(logic_gui.func_names):
        if func_name in logic_gui.func_dict:
            func_str = logic_gui.func_dict[func_name][0]
            func_list.append((func_name, func_str))

    if not func_list:
        ttk.Label(frame, text="Keine Funktionen definiert.", font=text).pack(pady=10)
        return

    for func_name, func_str in func_list:
        idx = logic_gui.func_names.index(func_name)
        base_color = logic_gui.colors[idx]

        container = Frame(frame)
        container.pack(pady=5, fill='x')

        circle = Canvas(container, width=20, height=20, bg=base_color, bd=0, highlightthickness=0)
        circle.pack(side='left', padx=(0, 5))

        btn = ttk.Button(
            container,
            text=f"{func_name} = {interpreted(func_str)}",
            command=lambda name=func_name, s=func_str: select_integration_range(name, s),
            style="TextButton.TButton",
            padding=(5, 12)
        )
        btn.pack(side='left', fill='x', expand=True)
        
def plot_ableitung(func_name, func_str):
    try:
        deriv_str = ableitung(func_str)

        if deriv_str.startswith("d/dx("):
            messagebox.showerror(
                "Fehler",
                f"Ableitung von {func_str} nicht bekannt."
            )
            return

        if func_name not in logic_gui.func_dict:
            logic_gui.func_dict[func_name] = [func_str]

        func_list = logic_gui.func_dict[func_name]

        if len(func_list) >= 2:
            func_list[1] = deriv_str    
        else:
            func_list.insert(1, deriv_str)

        logic_gui.plot_functions(canvas, ax)

    except Exception as e:
        messagebox.showerror(
            "Fehler",
            f"Ableitung konnte nicht berechnet werden: {e}"
        )

def plot_integration(func_name, func_str, a, b):

    try:
        func = logic_gui.func_dict[func_name][0]
        func = conv_to_func(func)

        x = np.linspace(a - 1, b + 1, 400)
        y = func(x)

        fig, ax = plt.subplots()
        ax.plot(x, y, label=f'{func_name} = {interpreted(func_str)}')
        ax.axvline(x=a, color='gray', linestyle='--')
        ax.axvline(x=b, color='gray', linestyle='--')


        x_fill = np.linspace(a, b, 100)
        y_fill = func(x_fill)
        ax.fill_between(x_fill, y_fill, color='gray', alpha=0.3)

        ax.set_title(f'Integral von {func_name} von {a:.2f} bis {b:.2f}')
        ax.legend()
        
        area = integration(func, a, b)

        # GUI für die Anzeige des Plots
        plot_window = Toplevel(root)
        plot_window.title("Integral Plot")

        canvas = FigureCanvasTkAgg(fig, master=plot_window)
        canvas.draw()
        canvas.get_tk_widget().pack()

        # Fläche anzeigen
        ttk.Label(plot_window, text=f"Fläche: {area:.2f}").pack(pady=10)

    except Exception as e:
        messagebox.showerror("Fehler", f"Fehler beim Plotten: {e}")


def open_legend():
    legend_popup = Toplevel(root)
    legend_popup.title("Legende")
    legend_popup.geometry("350x900")

    frame = Frame(legend_popup)
    frame.pack(padx=10, pady=10, fill='both', expand=True)

    ttk.Label(frame, text="Standardoperationen:", font=(schriftart, 11, 'bold')).pack(anchor='w')

    ttk.Label(frame, text="x^2      →   x²", font=text).pack(anchor='w')
    ttk.Label(frame, text="x^(10)   →   x¹⁰", font=text).pack(anchor='w')
    ttk.Label(frame, text="x^(-5)   →   x⁻⁵", font=text).pack(anchor='w')
    ttk.Label(frame, text="x^(2x)   →   x²ˣ", font=text).pack(anchor='w')

    row_frame = Frame(frame)
    row_frame.pack(anchor='w', padx=0)

    ttk.Label(row_frame, text="x^(1/x)  →", font=text).pack(side="left")

    frac_frame = Frame(row_frame)
    frac_frame.pack(side="left")

    small_font = (schriftart, 9)

    ttk.Label(frac_frame, text="  1", font=small_font).pack()
    ttk.Label(frac_frame, text="  ─", font=small_font).pack()
    ttk.Label(frac_frame, text="  x", font=small_font).pack()

    tk.Label(frame, text="", font=text).pack()

    ttk.Label(frame, text="Spezielle Funktionen:", font=(schriftart, 11, 'bold')).pack(anchor='w')
    for name, expr in comp_input.spec_funcs.items():
        tk.Label(frame, text=f"{name} → {expr}", font=text).pack(anchor='w')

    tk.Label(frame, text="", font=text).pack()

    tk.Label(frame, text="Verfügbare Konstanten:", font=(schriftart, 11, 'bold')).pack(anchor='w')
    for name, expr in comp_input.spec_cons.items():
        tk.Label(frame, text=f"{name} → {expr}", font=text).pack(anchor='w')

    tk.Button(frame, text="Schließen", command=legend_popup.destroy).pack(pady=10)


# Buttons für Filter, Ableitung, Integration 
button_frame = ttk.Frame(root)
button_frame.place(relx=0.915, rely=0.3, anchor='center', height=500, relwidth=0.15)   

filter_button = ttk.Button(
    button_frame,
    text="Filter",
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

# Event-Bindings für Zoomen/Panning
canvas.mpl_connect("button_press_event", lambda event: logic_gui.on_press(event, ax, canvas))
canvas.mpl_connect("motion_notify_event", lambda event: logic_gui.on_motion(event, ax, canvas))
canvas.mpl_connect("button_release_event", lambda event: logic_gui.on_release(event))
canvas.mpl_connect("scroll_event", lambda event: logic_gui.on_scroll(event, ax, canvas))

# Erstes Eingabefeld hinzufügen
add_input_field()

root.mainloop()