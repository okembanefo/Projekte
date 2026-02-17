from PIL import Image, ImageTk, ImageFilter
import threading
import queue
import main
import logic_gui as lg

aktuelles_bild = None
original_bild = None
lock = threading.Lock()
bilder_schlange = queue.Queue()
prev_slider = [0, 0, 0, 0, 0]

def anwenden_filter():
    if original_bild is None:
        return

    def filter_thread():
        global aktuelles_bild
        with lock:
            bild = aktuelles_bild.copy().convert("RGB")
        pixels = bild.load()
        breite, höhe = bild.size

        hell = main.slider_liste[0].get()
        kontr = main.slider_liste[1].get()
        sätt = main.slider_liste[2].get()
        schärfe = main.slider_liste[3].get()
        gamma = main.slider_liste[4].get()

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
    main.fenster.after(100, akt_bilder_schlange)

def akt_bild(bild):
    with lock:
        global aktuelles_bild
        aktuelles_bild = bild
    main.fenster.after(0, lambda: akt_anzeige(bild))

def akt_bilder_schlange():
    try:
        while True:
            bild = bilder_schlange.get_nowait()
            akt_bild(bild)
    except queue.Empty:
        pass
    main.fenster.after(100, akt_bilder_schlange)

def akt_anzeige(bild):
    frame_breite = main.bild_frame.winfo_width()
    frame_höhe = main.bild_frame.winfo_height()

    if frame_breite == 1 or frame_höhe == 1:
        main.bild_frame.after(100, lambda: akt_anzeige(bild))
        return

    bild_breite, bild_höhe = bild.size
    faktor = min(frame_breite / bild_breite, frame_höhe / bild_höhe)
    neue_breite = int(bild_breite * faktor)
    neue_höhe = int(bild_höhe * faktor)
    bild_resized = bild.resize((neue_breite, neue_höhe), Image.LANCZOS)

    tk_bild = ImageTk.PhotoImage(bild_resized)

    if main.bild_label is not None:
        main.bild_label.destroy()

    main.bild_label = tk.Label(
        main.bild_frame, image=tk_bild, borderwidth=0, highlightthickness=0, bg="white"
    )
    main.bild_label.image = tk_bild
    main.bild_label.place(relx=0.5, rely=0.5, anchor="center")

def lade_bild(pfad, frame):
    global aktuelles_bild, original_bild, prev_slider
    try:
        bild = Image.open(pfad).convert("RGB")
        with lock:
            aktuelles_bild = bild.copy()
            original_bild = bild.copy()

        for slider in main.slider_liste:
            slider.set(0)

        akt_anzeige(aktuelles_bild)
        prev_slider = [0, 0, 0, 0, 0]
    except Exception as e:
        messagebox.showerror("Fehler", f"Fehler beim Laden des Bildes:\n{e}")

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

def maximieren():
    global aktuelles_bild
    if aktuelles_bild is None:
        messagebox.showwarning("Maximieren", "Kein Bild zum Maximieren geladen!")
        return

    max_fenster = tk.Toplevel(main.fenster)
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

def reset():
    global aktuelles_bild, prev_slider
    for slider in main.slider_liste:
        slider.set(0)
    if original_bild is not None:
        aktuelles_bild = original_bild.copy()
        akt_anzeige(aktuelles_bild)
    prev_slider = [0, 0, 0, 0, 0]
