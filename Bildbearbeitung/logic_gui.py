import tkinter as tk
from tkinter import messagebox, filedialog
import glob
import os
import bildbearbeitung as bb
import main

pfade = []
aktueller_index = 0

def bilder_finden():
    pfad = os.getcwd()
    endungen = ["*.png", "*.PNG", "*.pgm", "*.PGM"]
    pfade = []
    for endung in endungen:
        pfade.extend(glob.glob(os.path.join(pfad, "**", endung), recursive=True))
    return list(set(pfade))[:30]

def begrenze_name(name):
    max_len = 17
    if len(name) > max_len:
        return name[:max_len] + "..."
    return name

def akt_bild_buttons():
    main.button_liste.clear()
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
            bb.lade_bild(pfad_, main.bild_frame)
            zeige_fenster()

        b = tk.Button(
            main.fenster, text=dateiname, command=button_klicken, bg="white", fg="black", bd=1,
            highlightbackground='black', highlightthickness=1
        )
        b.place(x=x, y=y)
        main.button_liste.append(b)

    if pfade:
        zeige_fenster()

def zeige_fenster():
    main.fenster_buttons.clear()
    if main.fenster_frame is None:
        main.fenster_frame = tk.Frame(main.fenster, bg="white", height=120)
        main.fenster_frame.place(x=450, y=30, width=1000, height=120)

    for b in main.fenster_buttons:
        if b.winfo_exists():
            b.destroy()

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
                bb.lade_bild(p, main.bild_frame)

            btn = tk.Button(main.fenster_frame, image=tk_img, command=lade_bild_call, bg="white", bd=1)
            btn.image = tk_img
            btn.grid(row=0, column=i, padx=0, pady=0)
            main.fenster_buttons.append(btn)
        except Exception as e:
            print(f"Fehler beim Laden des Fensters von {pfad}: {e}")

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

def bilder_löschen():
    global pfade, aktueller_index
    if not pfade:
        messagebox.showwarning("Bilder löschen", "Keine Bilder zum Löschen vorhanden!")
        return

    popup = tk.Toplevel(main.fenster)
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

def speichern():
    bb.speichern()

def maximieren():
    bb.maximieren()

def reset():
    bb.reset()

def schliessen(fenster):
    fenster.destroy()
