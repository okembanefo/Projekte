import glob
import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk, ImageFilter
import threading
import queue

# Globale Variablen
aktueller_pfad = None
bild_frame = None
button_liste = []
aktuelles_bild = None
original_bild = None
bild_label = None
slider_liste = []
aktueller_index = 0
fenster_buttons = []
fenster_frame = None
bilder_schlange = queue.Queue()
lock = threading.Lock()
pfade = []
prev_slider = [0, 0, 0, 0, 0]

# Funktion soll Filter auf das ausgewählte Bild anwenden
def anwenden_filter():
    if original_bild is None:
        return
    
    # Funktion soll ermöglichen mehrere Filter gleichzeitig zu starten (um freezing zu verhindern)
    def filter_thread():
        global aktuelles_bild
        with lock:
            bild = aktuelles_bild.copy().convert("RGB")
        pixels = bild.load()
        breite, höhe = bild.size

        hell = slider_liste[0].get()
        kontr = slider_liste[1].get()
        sätt = slider_liste[2].get()
        schärfe = slider_liste[3].get()
        gamma = slider_liste[4].get()

        if hell != prev_slider[0]:
            for x in range(breite):
                for y in range(höhe):
                    r, g, b = pixels[x, y]
                    hell_faktor = 0.5
                    r = min(max(r + int(hell * hell_faktor), 0), 255)
                    g = min(max(g + int(hell * hell_faktor), 0), 255)
                    b = min(max(b + int(hell * hell_faktor), 0), 255)
                    pixels[x, y] = (r, g, b)

        if kontr != prev_slider[1]:
            kontr_faktor = 1 + ((kontr / 2) / 100.0)
            for x in range(breite):
                for y in range(höhe):
                    r, g, b = pixels[x, y]
                    r = int((r - 128) * kontr_faktor + 128)
                    g = int((g - 128) * kontr_faktor + 128)
                    b = int((b - 128) * kontr_faktor + 128)
                    pixels[x, y] = (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))

        if sätt != prev_slider[2]:
            sätt_faktor = 1 + ((sätt / 2) / 100.0)
            for x in range(breite):
                for y in range(höhe):
                    r, g, b = pixels[x, y]
                    grau = 0.299 * r + 0.587 * g + 0.114 * b
                    r = int(grau + (r - grau) * sätt_faktor)
                    g = int(grau + (g - grau) * sätt_faktor)
                    b = int(grau + (b - grau) * sätt_faktor)
                    pixels[x, y] = (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))

        if gamma != prev_slider[3]:
            gamma_korr = max((gamma / 2 + 100) / 100.0, 0.01)
            for x in range(breite):
                for y in range(höhe):
                    r, g, b = pixels[x, y]
                    if r == 0: r = 1
                    if g == 0: g = 1
                    if b == 0: b = 1
                    r = int(255 * ((r / 255) ** (1 / gamma_korr)))
                    g = int(255 * ((g / 255) ** (1 / gamma_korr)))
                    b = int(255 * ((b / 255) ** (1 / gamma_korr)))
                    pixels[x, y] = (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))

        if schärfe != prev_slider[4]:
            if schärfe != 0:
                alpha = (schärfe / 2) / 100.0
                geblurtes = bild.filter(ImageFilter.GaussianBlur(radius=2.5)).convert("RGB")
                original_pixels = bild.load()
                blur_pixels = geblurtes.load()
                for x in range(breite):
                    for y in range(höhe):
                        r, g, b = original_pixels[x, y]
                        r_blur, g_blur, b_blur = blur_pixels[x, y]
                        r = int(r + alpha * (r - r_blur))
                        g = int(g + alpha * (g - g_blur))
                        b = int(b + alpha * (b - b_blur))
                        original_pixels[x, y] = (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))

        with lock:
            aktuelles_bild = bild
            prev_slider[0] = hell
            prev_slider[1] = kontr
            prev_slider[2] = sätt
            prev_slider[3] = gamma
            prev_slider[4] = schärfe

        bilder_schlange.put(aktuelles_bild)

    threading.Thread(target=filter_thread).start()
    fenster.after(100, akt_bilder_schlange)

# Funktion speichert akt. Bild als globales Bild
def akt_bild(bild):
    with lock:
        global aktuelles_bild
        aktuelles_bild = bild
    fenster.after(0, lambda: akt_anzeige(bild))

# Funktion pulled das die von filter thread erstellten Bilder der Reihe nach
def akt_bilder_schlange():
    try:
        while True:
            bild = bilder_schlange.get_nowait()
            akt_bild(bild)
    except queue.Empty:
        pass
    fenster.after(100, akt_bilder_schlange)

# Funktion erstellt Fenster welche die nächsten 10 Bilder oben skaliert anzeigen soll
def zeige_fenster():
    global fenster_buttons, fenster_frame, aktueller_index

    if fenster_frame is None:
        fenster_frame = tk.Frame(fenster, bg="white", height=120)
        fenster_frame.place(x=450, y=30, width=1000, height=120)

    try:
        for b in fenster_buttons:
            if b.winfo_exists():
                b.destroy()
        fenster_buttons.clear()
    except:
        pass

    fenster_anzahl = 10
    ziel_höhe = 100

    for i in range(fenster_anzahl):
        idx = aktueller_index + i
        if idx >= len(pfade):
            break
        pfad = pfade[idx]
        try:
            img = Image.open(pfad)
            img_ratio = img.width / img.height
            ziel_breite = int(ziel_höhe * img_ratio)
            img = img.resize((ziel_breite, ziel_höhe), Image.LANCZOS)
            tk_img = ImageTk.PhotoImage(img)

            def lade_bild_call(p=pfad):
                lade_bild(p, bild_frame)

            btn = tk.Button(fenster_frame, image=tk_img, command=lade_bild_call, bg="white", bd=1)
            btn.image = tk_img
            btn.grid(row=0, column=i, padx=0, pady=0)
            fenster_buttons.append(btn)

        except Exception as e:
            print(f"Fehler beim Laden des Fensters von {pfad}: {e}")

# Funktion sucht nach Bilder im Pfad in dem das Programm gestartet wird
def bilder_finden():
    pfad = os.getcwd()
    endungen = ["*.png", "*.PNG", "*.pgm", "*.PGM"]
    pfade = []
    for endung in endungen:
        pfade.extend(glob.glob(os.path.join(pfad, "**", endung), recursive=True))
    return list(set(pfade))[:30]

# Funjktion begrenzt den Namen der Bildbuttons auf 17 Zeichen
def begrenze_name(name):
    max_len = 17
    if len(name) > max_len:
        return name[:max_len] + "..."
    return name

# Funktion erstellt die Bildbuttons im Fenster
def akt_bild_buttons():
    global button_liste

    try:
        for b in button_liste:
            if b.winfo_exists():
                b.destroy()
        button_liste.clear()
    except:
        pass

    start_x = 50
    start_y = 175
    spalten_anzahl = 2
    buttons_pro_spalte = 20
    x_abstand = 150
    y_abstand = 35

    for idx, pfad in enumerate(pfade[:40]):
        spalte = idx // buttons_pro_spalte
        zeile = idx % buttons_pro_spalte

        x = start_x + spalte * x_abstand
        y = start_y + zeile * y_abstand

        dateiname = begrenze_name(os.path.basename(pfad))

        def button_klicken(index=idx, pfad_=pfad):
            global aktueller_index
            aktueller_index = index
            lade_bild(pfad_, bild_frame)
            zeige_fenster()

        b = tk.Button(
            fenster,
            text=dateiname,
            command=button_klicken,
            bg="white",
            fg="black",
            bd=1,
            highlightbackground='black',
            highlightthickness=1
        )
        b.place(x=x, y=y)
        button_liste.append(b)

    if pfade:
        zeige_fenster()

# Fuunktion gibt das aktuelle Bild im Fenster aus
def akt_anzeige(bild):
    global bild_label, bild_frame

    frame_breite = bild_frame.winfo_width()
    frame_höhe = bild_frame.winfo_height()

    if frame_breite == 1 or frame_höhe == 1:
        bild_frame.after(100, lambda: akt_anzeige(bild))
        return

    bild_breite, bild_höhe = bild.size
    faktor = min(frame_breite / bild_breite, frame_höhe / bild_höhe)
    neue_breite = int(bild_breite * faktor)
    neue_höhe = int(bild_höhe * faktor)
    bild_resized = bild.resize((neue_breite, neue_höhe), Image.LANCZOS)

    tk_bild = ImageTk.PhotoImage(bild_resized)

    if bild_label is not None:
        bild_label.destroy()

    bild_label = tk.Label(
        bild_frame,
        image=tk_bild,
        borderwidth=0,
        highlightthickness=0,
        bg="white"
    )
    bild_label.image = tk_bild
    bild_label.place(relx=0.5, rely=0.5, anchor="center")

# Funktion lädt ein Bild mithilfe des übergebenen Pfad
def lade_bild(pfad, frame):
    global aktuelles_bild, original_bild, slider_liste, aktueller_index, prev_slider
    try:
        bild = Image.open(pfad).convert("RGB")
        with lock:
            aktuelles_bild = bild.copy()
            original_bild = bild.copy()

        for slider in slider_liste:
            slider.set(0)

        akt_anzeige(aktuelles_bild)
        aktueller_index = pfade.index(pfad)
        prev_slider = [0, 0, 0, 0, 0]

    except Exception as e:
        messagebox.showerror("Fehler", f"Fehler beim Laden des Bildes:\n{e}")

# Funktion soll Bilder die aus dem Exploer hinzugeügt werden auf den Typ überprüfen und dann laden
def bild_hinzufügen():
    global pfade

    dateipfade = filedialog.askopenfilenames(
        title="Bilder auswählen",
        filetypes=[("Bilddateien", "*.png;*.PNG;*.pgm;*.PGM"), ("Alle Dateien", "*.*")]
    )

    if not dateipfade:
        return

    if len(pfade) + len(dateipfade) > 40:
        messagebox.showerror("Fehler", "Es können nicht mehr als 40 Bilder hinzugefügt werden. Löschen Sie, wenn möglich vorher andere Bilder.")
        bilder_löschen()

        if len(pfade) + len(dateipfade) > 40:
            unique_dateipfade = [pfad for pfad in dateipfade if pfad not in pfade]
            pfade.extend(unique_dateipfade)
            akt_bild_buttons()
        return

    unique_dateipfade = [pfad for pfad in dateipfade if pfad not in pfade]
    pfade.extend(unique_dateipfade)
    akt_bild_buttons()

# Funktion soll angegebene Bilder bzw. Bildbutton im Programm löschen
def bilder_löschen():
    global pfade, aktueller_index

    if not pfade:
        messagebox.showwarning("Bilder löschen", "Keine Bilder zum Löschen vorhanden!")
        return

    bild_count = 0
    popup = tk.Toplevel(fenster)
    popup.title("Bilder zum Löschen auswählen")
    popup.geometry("500x600")

    ausgewählte_bilder = []

    canvas = tk.Canvas(popup)
    scroll_frame = tk.Frame(canvas)

    scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.place(x=0, y=0, width=300, height=600)

    def scroll(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    canvas.bind_all("<MouseWheel>", scroll)

    for pfad in pfade:
        filename = os.path.basename(pfad)
        button = tk.Button(scroll_frame, text=filename, width=30, anchor='w')

        def wechseln(p=pfad, b=button):
            if p in ausgewählte_bilder:
                ausgewählte_bilder.remove(p)
                b.config(bg="SystemButtonFace")
            else:
                ausgewählte_bilder.append(p)
                b.config(bg="dark grey")

        button.config(command=wechseln)
        button.pack(padx=5, pady=2, fill=tk.X)

    separator = ttk.Separator(popup, orient='vertical')
    separator.place(x=280, y=0, height=600)


    def löschen_bestätigen():
        bild_count = len(ausgewählte_bilder)
        if not ausgewählte_bilder:
            messagebox.showwarning("Keine Auswahl", "Keine Bilder ausgewählt!")
            return
        if messagebox.askyesno("Löschen bestätigen", f"Sind Sie sicher, dass Sie {bild_count} ausgewählte(s) Bilder löschen möchten?"):
            pfade[:] = [pfad for pfad in pfade if pfad not in ausgewählte_bilder]
            akt_bild_buttons()
            popup.destroy()

    def alle_löschen():
        bild_count = len(pfade)
        if messagebox.askyesno("Alle löschen", f"Sind Sie sicher, dass Sie alle {bild_count} Bilder löschen möchten?"):
            popup.destroy()
            pfade.clear()
            akt_bild_buttons()
            zeige_fenster()

    button_area = tk.Frame(popup, width=200, height=600)
    button_area.place(x=300, y=0)

    tk.Button(button_area, text="Alle löschen", width=15, command=alle_löschen).place(x=10, y=150)
    tk.Button(button_area, text="Löschen", width=15, command=löschen_bestätigen).place(x=10, y=200)
    tk.Button(button_area, text="Abbrechen", width=15, command=popup.destroy).place(x=10, y=250)

# Funktion soll bearbeitete Bild im Explorer speichern
def speichern():
    global aktuelles_bild
    if aktuelles_bild is None:
        messagebox.showwarning("Speichern", "Kein Bild zum Speichern geladen!")
        return

    dateipfad = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG-Bild", "*.png"), ("PGM-Bild", "*.pgm"), ("Alle Dateien", "*.*")]
    )

    if dateipfad:
        try:
            aktuelles_bild.save(dateipfad)
            messagebox.showinfo("Speichern", f"Bild erfolgreich gespeichert unter:\n{dateipfad}")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Speichern: {e}")

# Funktion soll Bild in einerm sparratem Popup Fenster laden
def maximieren():
    global aktuelles_bild

    if aktuelles_bild is None:
        messagebox.showwarning("Maximieren", "Kein Bild zum Maximieren geladen!")
        return

    max_fenster = tk.Toplevel(fenster)
    max_fenster.title("Maximiertes Bild")

    bild_breite, bild_höhe = aktuelles_bild.size
    max_breite = max_fenster.winfo_screenwidth() - 100
    max_höhe = max_fenster.winfo_screenheight() - 100

    faktor = min(max_breite / bild_breite, max_höhe / bild_höhe) / 1.25
    neue_breite = int(bild_breite * faktor)
    neue_höhe = int(bild_höhe * faktor)

    bild_resized = aktuelles_bild.resize((neue_breite, neue_höhe), Image.LANCZOS)
    tk_bild = ImageTk.PhotoImage(bild_resized)

    bild_label = tk.Label(max_fenster, image=tk_bild, borderwidth=0, highlightthickness=0, bg="white")
    bild_label.image = tk_bild
    bild_label.pack()

    max_fenster.geometry(f"{neue_breite}x{neue_höhe}")

# Funktion soll alle Änderungen resetten, indem das gespeicherte original_bild wieder geöaden wird
def reset():
    global aktuelles_bild, prev_slider

    for slider in slider_liste:
        slider.set(0)

    if original_bild is not None:
        aktuelles_bild = original_bild.copy()
        akt_anzeige(aktuelles_bild)
    prev_slider = [0, 0, 0, 0, 0]

# Funktion soll das Hauptfenster schließen
def schliessen(fenster):
    fenster.destroy()

# Funktion soll das Hauptfenster mit allen Buttons, Slidern und Separatoren
def main():
    global bild_frame, button_liste, slider_liste, fenster, pfade

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

    tk.Button(fenster, text="Bilder hinzufügen", command=bild_hinzufügen, **btn_set).place(x=butt_x_pos, y=butt_y_pos)
    butt_x_pos += butt_x_of
    tk.Button(fenster, text="Bilder löschen", command=bilder_löschen, **btn_set).place(x=butt_x_pos, y=butt_y_pos)
    butt_x_pos += butt_x_of
    tk.Button(fenster, text="Speichern", command=speichern, **btn_set).place(x=butt_x_pos, y=butt_y_pos)
    butt_x_pos += butt_x_of
    tk.Button(fenster, text="Maximieren", command=maximieren, **btn_set).place(x=butt_x_pos, y=butt_y_pos)
    butt_x_pos += butt_x_of
    tk.Button(fenster, text="Zurücksetzen", command=reset, **btn_set).place(x=butt_x_pos, y=butt_y_pos)
    butt_x_pos += butt_x_of
    tk.Button(fenster, text="Schließen", command=lambda: schliessen(fenster), **btn_set).place(x=butt_x_pos, y=butt_y_pos)

    separator_buttons = ttk.Separator(fenster, orient='horizontal')
    separator_buttons.place(x=0, y=900, width=2000, height=2)

    slid_x_pos = 1550

    helligkeit_slider = tk.Scale(
        fenster,
        from_=-50,
        to=50,
        orient="horizontal",
        label="Helligkeit",
        command=lambda val: anwenden_filter(),
        bg="white",
        fg="black",
        troughcolor="lightgrey",
        bd=1,
        highlightbackground='black',
        highlightthickness=1
    )
    helligkeit_slider.place(x=slid_x_pos, y=200, width=300)
    slider_liste.append(helligkeit_slider)

    kontrast_slider = tk.Scale(
        fenster,
        from_=-50,
        to=50,
        orient="horizontal",
        label="Kontrast",
        command=lambda val: anwenden_filter(),
        bg="white",
        fg="black",
        troughcolor="lightgrey",
        bd=1,
        highlightbackground='black',
        highlightthickness=1
    )
    kontrast_slider.place(x=slid_x_pos, y=320, width=300)
    slider_liste.append(kontrast_slider)

    sättigung_slider = tk.Scale(
        fenster,
        from_=-50,
        to=50,
        orient="horizontal",
        label="Sättigung",
        command=lambda val: anwenden_filter(),
        bg="white",
        fg="black",
        troughcolor="lightgrey",
        bd=1,
        highlightbackground='black',
        highlightthickness=1
    )
    sättigung_slider.place(x=slid_x_pos, y=440, width=300)
    slider_liste.append(sättigung_slider)

    schärfe_slider = tk.Scale(
        fenster,
        from_=-50,
        to=50,
        orient="horizontal",
        label="Schärfe",
        command=lambda val: anwenden_filter(),
        bg="white",
        fg="black",
        troughcolor="lightgrey",
        bd=1,
        highlightbackground='black',
        highlightthickness=1
    )
    schärfe_slider.place(x=slid_x_pos, y=560, width=300)
    slider_liste.append(schärfe_slider)

    gamma_slider = tk.Scale(
        fenster,
        from_=-50,
        to=50,
        orient="horizontal",
        label="Gamma-Korrektur",
        command=lambda val: anwenden_filter(),
        bg="white",
        fg="black",
        troughcolor="lightgrey",
        bd=1,
        highlightbackground='black',
        highlightthickness=1
    )
    gamma_slider.place(x=slid_x_pos, y=680, width=300)
    slider_liste.append(gamma_slider)

    separator_slider = ttk.Separator(fenster, orient='vertical')
    separator_slider.place(x=1500, y=150, height=750)

    pfade = bilder_finden()
    akt_bild_buttons()
    fenster.mainloop()

if __name__ == "__main__":
    main()
