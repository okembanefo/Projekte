import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import logic_gui as lg
import bildbearbeitung as bb

# Globale Variablen für die GUI
fenster = None
bild_frame = None
button_liste = []
bild_label = None
slider_liste = []
fenster_buttons = []
fenster_frame = None

def main():
    global fenster, bild_frame, slider_liste

    fenster = tk.Tk()
    fenster.title("Tkpaint")
    fenster.state('zoomed')
    fenster.configure(bg="white")

    bild_frame = tk.Frame(fenster, width=550, height=700, bg="white")
    bild_frame.place(x=670, y=170)

    separator_buttons = ttk.Separator(fenster, orient='horizontal')
    separator_buttons.place(x=0, y=150, width=2000, height=2)

    separator_slider = ttk.Separator(fenster, orient='vertical')
    separator_slider.place(x=390, y=150, height=750)

    btn_set = {
        'bg': 'white',
        'fg': 'black',
        'width': 15,
        'height': 2,
        'bd': 1,
        'highlightbackground': 'black',
        'highlightthickness': 1
    }

    butt_y_pos = 935
    butt_x_pos = 360
    butt_x_of = 210

    tk.Button(fenster, text="Bilder hinzufügen", command=lg.bild_hinzufügen, **btn_set).place(x=butt_x_pos, y=butt_y_pos)
    butt_x_pos += butt_x_of
    tk.Button(fenster, text="Bilder löschen", command=lg.bilder_löschen, **btn_set).place(x=butt_x_pos, y=butt_y_pos)
    butt_x_pos += butt_x_of
    tk.Button(fenster, text="Speichern", command=lg.speichern, **btn_set).place(x=butt_x_pos, y=butt_y_pos)
    butt_x_pos += butt_x_of
    tk.Button(fenster, text="Maximieren", command=lg.maximieren, **btn_set).place(x=butt_x_pos, y=butt_y_pos)
    butt_x_pos += butt_x_of
    tk.Button(fenster, text="Zurücksetzen", command=lg.reset, **btn_set).place(x=butt_x_pos, y=butt_y_pos)
    butt_x_pos += butt_x_of
    tk.Button(fenster, text="Schließen", command=lambda: lg.schliessen(fenster), **btn_set).place(x=butt_x_pos, y=butt_y_pos)

    separator_buttons = ttk.Separator(fenster, orient='horizontal')
    separator_buttons.place(x=0, y=900, width=2000, height=2)

    slid_x_pos = 1550

    helligkeit_slider = tk.Scale(
        fenster, from_=-50, to=50, orient="horizontal", label="Helligkeit",
        command=lambda val: bb.anwenden_filter(), bg="white", fg="black", troughcolor="lightgrey", bd=1,
        highlightbackground='black', highlightthickness=1
    )
    helligkeit_slider.place(x=slid_x_pos, y=200, width=300)
    slider_liste.append(helligkeit_slider)

    kontrast_slider = tk.Scale(
        fenster, from_=-50, to=50, orient="horizontal", label="Kontrast",
        command=lambda val: bb.anwenden_filter(), bg="white", fg="black", troughcolor="lightgrey", bd=1,
        highlightbackground='black', highlightthickness=1
    )
    kontrast_slider.place(x=slid_x_pos, y=320, width=300)
    slider_liste.append(kontrast_slider)

    sättigung_slider = tk.Scale(
        fenster, from_=-50, to=50, orient="horizontal", label="Sättigung",
        command=lambda val: bb.anwenden_filter(), bg="white", fg="black", troughcolor="lightgrey", bd=1,
        highlightbackground='black', highlightthickness=1
    )
    sättigung_slider.place(x=slid_x_pos, y=440, width=300)
    slider_liste.append(sättigung_slider)

    schärfe_slider = tk.Scale(
        fenster, from_=-50, to=50, orient="horizontal", label="Schärfe",
        command=lambda val: bb.anwenden_filter(), bg="white", fg="black", troughcolor="lightgrey", bd=1,
        highlightbackground='black', highlightthickness=1
    )
    schärfe_slider.place(x=slid_x_pos, y=560, width=300)
    slider_liste.append(schärfe_slider)

    gamma_slider = tk.Scale(
        fenster, from_=-50, to=50, orient="horizontal", label="Gamma-Korrektur",
        command=lambda val: bb.anwenden_filter(), bg="white", fg="black", troughcolor="lightgrey", bd=1,
        highlightbackground='black', highlightthickness=1
    )
    gamma_slider.place(x=slid_x_pos, y=680, width=300)
    slider_liste.append(gamma_slider)

    separator_slider = ttk.Separator(fenster, orient='vertical')
    separator_slider.place(x=1500, y=150, height=750)

    lg.akt_bild_buttons()
    fenster.mainloop()

if __name__ == "__main__":
    main()
