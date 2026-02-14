import tkinter as tk
import numpy as np
from tkinter import ttk, BooleanVar, Checkbutton, Toplevel, Frame, Canvas, messagebox, simpledialog
import logic_gui
import comp_input
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from add_ons import ableitung, integration
from comp_input import interpreted, parser
from plot_logic import conv_to_func
from logic_gui import plot_functions
from logic_gui import lighter_color, darker_color


# Einheitliche Schriftart
font_style = ('Segoe UI', 10)

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

def open_settings():
    """Öffnet das Einstellungsfenster."""
    settings_window = Toplevel(root)
    settings_window.title("Einstellungen")
    settings_window.geometry("300x200")

    frame = Frame(settings_window)
    frame.pack(padx=10, pady=10, fill='both')

    rad_var = BooleanVar(value=logic_gui.axis_in_radians)
    rad_check = Checkbutton(frame, text="Achsen in Bogenmaß", variable=rad_var, font=font_style)
    rad_check.pack(anchor='w', pady=5)

    pos_var = BooleanVar(value=logic_gui.show_positive_only)
    pos_check = Checkbutton(frame, text="Nur positive Y-Werte anzeigen", variable=pos_var, font=font_style)
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
    """Fügt ein neues Eingabefeld hinzu (max. 5)."""
    global plus_button


    if len(func_entries) >= 5:
        return

    row = len(func_entries)
    entry_frame = ttk.Frame(input_frame)
    entry_frame.grid(row=row, column=0, columnspan=2, padx=5, pady=15, sticky='ew')

    # Farbiger Kreis
    circle = Canvas(entry_frame, width=20, height=20, bg=logic_gui.colors[row], bd=0, highlightthickness=0)
    circle.grid(row=0, column=0, padx=(0, 5))

    # Eingabefeld
    entry = tk.Entry(
        entry_frame,
        width=20,
        font=('Segoe UI', 12),
        bd=1,
        relief='solid',
        highlightthickness=1,
        highlightcolor='lightgray',
        highlightbackground='lightgray'
    )
    entry.grid(row=0, column=1, sticky='ew')

    # Interpretationsfeld
    interpreted_label = ttk.Label(
        entry_frame,
        text="Interpretiert als: ",
        foreground="gray",
        font=('Segoe UI', 9)
    )
    interpreted_label.grid(row=1, column=0, columnspan=2, sticky='w')
    interpreted_label.grid_remove()  # Verwende row statt index

    delete_button = ttk.Button(
        entry_frame,
        text="X",
        width=2,
        command=lambda idx=row: delete_input_field(idx)
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

    if len(func_entries) < 5:
        plus_button = ttk.Button(
            input_frame,
            text="+",
            width=3,
            command=add_input_field
        )
        plus_button.grid(row=row+1, column=0, columnspan=2, pady=10)


def delete_input_field(index):
    """Löscht das Eingabefeld an der gegebenen Position."""
    global plus_button

    if index >= len(func_entries):
        return

    func_name = ['f(x)', 'g(x)', 'h(x)', 'i(x)', 'j(x)'][index]
    if func_name in logic_gui.func_dict:
        del logic_gui.func_dict[func_name]

    func_entries[index].master.destroy()
    interpreted_labels[index].destroy()
    delete_buttons[index].destroy()

    del func_entries[index]
    del interpreted_labels[index]
    del delete_buttons[index]
    del color_circles[index]

    if plus_button:
        plus_button.destroy()

    if len(func_entries) < 5:
        plus_button = ttk.Button(
            input_frame,
            text="+",
            width=3,
            command=add_input_field
        )
        plus_button.grid(row=len(func_entries), column=0, columnspan=2, pady=10)

    logic_gui.plot_functions(canvas, ax)

def on_focus_in(index):
    """Zeigt das Interpretationsfeld beim Fokus."""
    interpreted_labels[index].grid()
    update_interpretation(index)

def on_focus_out(index):
    """Versteckt das Interpretationsfeld beim Verlassen."""
    interpreted_labels[index].grid_remove()

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
    func_name = ['f(x)', 'g(x)', 'h(x)', 'i(x)', 'j(x)'][index]   

    if text:
        try:
            logic_gui.func_dict[func_name] = [text]
            update_interpretation(index)
            error = logic_gui.plot_functions(canvas, ax)
            if error:
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

# --- UI-Setup ---
style = ttk.Style()
style.configure('TButton', font=font_style)
style.configure('TEntry', fieldbackground='white')

# Hauptframe für Eingabefelder und Koordinatensystem
main_frame = ttk.Frame(root)
main_frame.pack(fill='both', expand=True)

# Frame für Eingabefelder (links)
input_frame = ttk.Frame(main_frame, width=int(screen_width*0.8*1/3))
input_frame.pack(side='left', fill='y', padx=5, pady=10)
input_frame.pack_propagate(False)

# Frame für Koordinatensystem (mittig)
plot_frame = ttk.Frame(main_frame)
plot_frame.pack(side='left', fill='both', expand=True, padx=5, pady=5)

# Frame für Buttons (rechts)
button_frame = ttk.Frame(main_frame, width=int(screen_width*0.8*1/5))
button_frame.pack(side='right', fill='y', padx=5, pady=10)
button_frame.pack_propagate(False)

# Koordinatensystem
fig = Figure(figsize=(6, 4.5))
ax = fig.add_subplot(111)
canvas = FigureCanvasTkAgg(fig, master=plot_frame)
canvas.get_tk_widget().pack(fill='both', expand=True)

# Fehlerlabel
error_label = ttk.Label(root, text="", foreground="red", font=font_style)
error_label.pack(pady=5)

# Toolbar mit Einstellungen-Button (nach oben verschoben)
toolbar_frame = ttk.Frame(root)
toolbar_frame.pack(side="top", fill="x", pady=(5, 0))

settings_button = ttk.Button(
    root,
    text="Einstellungen",
    command=open_settings,
    style='TButton'
)
settings_button.place(relx=0.99, rely=0.95, anchor='se') 

def open_ableitung_popup():
    """Öffnet ein Popup-Fenster zur Auswahl der abzuleitenden Funktion."""
    global ableitungs_popup

    # Wenn bereits ein Popup existiert, zuerst schließen
    if ableitungs_popup is not None and ableitungs_popup.winfo_exists():
        ableitungs_popup.destroy()
        ableitungs_popup = None

    # Neues Popup erstellen
    ableitungs_popup = Toplevel(root)
    ableitungs_popup.title("Ableitung berechnen")
    ableitungs_popup.geometry("300x400")

    frame = Frame(ableitungs_popup)
    frame.pack(padx=10, pady=10, fill='both')

    # Durchlaufe die in logic_gui.func_dict gespeicherten Funktionen
    func_list = []
    for i, func_name in enumerate(['f(x)', 'g(x)', 'h(x)', 'i(x)', 'j(x)']):
        if func_name in logic_gui.func_dict:
            func_str = logic_gui.func_dict[func_name][0]  # Erste Funktion in der Liste
            func_list.append((func_name, func_str))

    if not func_list:
        tk.Label(frame, text="Keine Funktionen definiert.", font=font_style).pack(pady=10)
        return

    # Buttons für jede Funktion erstellen
    for func_name, func_str in func_list:
        idx = ['f(x)', 'g(x)', 'h(x)', 'i(x)', 'j(x)'].index(func_name)
        base_color = logic_gui.colors[idx]
        lighter_color_value = lighter_color(base_color)  # Hellere Farbe berechnen

        btn = tk.Button(
            frame,
            text=f"{func_name} = {interpreted(func_str)}",
            command=lambda name=func_name, s=func_str: plot_ableitung(name, s),
            bg=lighter_color_value,  # Hellere Farbe verwenden
            fg="black",  # Textfarbe auf Schwarz setzen für bessere Lesbarkeit
            width=30,
            height=2
        )
        btn.pack(pady=5)

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
    """Öffnet ein Popup-Fenster zur Auswahl der zu integrierenden Funktion."""
    global integration_popup

    # Wenn bereits ein Popup existiert, zuerst schließen
    if 'integration_popup' in globals() and integration_popup is not None and integration_popup.winfo_exists():
        integration_popup.destroy()
        integration_popup = None

    # Neues Popup erstellen
    integration_popup = Toplevel(root)
    integration_popup.title("Integration berechnen")
    integration_popup.geometry("300x400")

    frame = Frame(integration_popup)
    frame.pack(padx=10, pady=10, fill='both')

    # Durchlaufe die in logic_gui.func_dict gespeicherten Funktionen
    func_list = []
    for i, func_name in enumerate(['f(x)', 'g(x)', 'h(x)', 'i(x)', 'j(x)']):
        if func_name in logic_gui.func_dict:
            func_str = logic_gui.func_dict[func_name][0]  
            func_list.append((func_name, func_str))

    if not func_list:
        tk.Label(frame, text="Keine Funktionen definiert.", font=font_style).pack(pady=10)
        return

    # Buttons für jede Funktion erstellen
    for func_name, func_str in func_list:
        idx = ['f(x)', 'g(x)', 'h(x)', 'i(x)', 'j(x)'].index(func_name)
        base_color = logic_gui.colors[idx]
        darker_color_value = darker_color(base_color)  # Dunklere Farbe berechnen

        btn = tk.Button(
            frame,
            text=f"{func_name} = {interpreted(func_str)}",
            command=lambda name=func_name, s=func_str: select_integration_range(name, s),
            bg=darker_color_value,
            fg="white",
            width=30,
            height=2
        )
        btn.pack(pady=5)

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
        tk.Label(plot_window, text=f"Fläche: {area:.2f}").pack(pady=10)

    except Exception as e:
        messagebox.showerror("Fehler", f"Fehler beim Plotten: {e}")


# Buttons für Filter, Ableitung, Integration (untereinander)
filter_button = ttk.Button(
    button_frame,
    text="Filter",
    style='TButton'
)
filter_button.pack(fill='x', pady=10)

ableitung_button = ttk.Button(
    button_frame,
    text="Ableitung",
    command=open_ableitung_popup,
    style='TButton'
)
ableitung_button.pack(fill='x', pady=10)

integration_button = ttk.Button(
    button_frame,
    text="Integration",
    command=open_integration_popup,
    style='TButton'
)
integration_button.pack(fill='x', pady=10)

ft_button = ttk.Button(
    button_frame,
    text="Fouriertransformierte",
    style='TButton'
)
ft_button.pack(fill='x', pady=10)

rft_button = ttk.Button(
    button_frame,
    text="Rücktransformierte",
    style='TButton'
)
rft_button.pack(fill='x', pady=10)

def open_legend():
    """Öffnet ein Popup, das alle verfügbaren Funktionen und Konstanten zeigt."""
    legend_popup = Toplevel(root)
    legend_popup.title("Legende")
    legend_popup.geometry("350x600")

    frame = Frame(legend_popup)
    frame.pack(padx=10, pady=10, fill='both', expand=True)

    tk.Label(frame, text="Verfügbare Funktionen:", font=('Segoe UI', 11, 'bold')).pack(anchor='w')
    for name, expr in comp_input.spec_funcs.items():
        tk.Label(frame, text=f"{name} → {expr}", font=font_style).pack(anchor='w')

    tk.Label(frame, text="", font=font_style).pack()  # Leerzeile

    tk.Label(frame, text="Verfügbare Konstanten:", font=('Segoe UI', 11, 'bold')).pack(anchor='w')
    for name, expr in comp_input.spec_cons.items():
        tk.Label(frame, text=f"{name} → {expr}", font=font_style).pack(anchor='w')

    tk.Button(frame, text="Schließen", command=legend_popup.destroy).pack(pady=10)

# --- Legende-Button unten links --- 
legend_button = ttk.Button(
    root,
    text="Legende",
    command=open_legend,
    style='TButton'
)
legend_button.place(relx=0.01, rely=0.95, anchor='sw')


# Event-Bindings für Zoomen/Panning
canvas.mpl_connect("button_press_event", lambda event: logic_gui.on_press(event, ax, canvas))
canvas.mpl_connect("motion_notify_event", lambda event: logic_gui.on_motion(event, ax, canvas))
canvas.mpl_connect("button_release_event", lambda event: logic_gui.on_release(event))
canvas.mpl_connect("scroll_event", lambda event: logic_gui.on_scroll(event, ax, canvas))

# Erstes Eingabefeld hinzufügen
add_input_field()

root.mainloop()