import tkinter as tk
from tkinter import ttk
import mido
import threading

class VirtualKeyboard:
    def __init__(self, root):
        self.root = root
        self.root.title("MIDI Virtual Keyboard - 88 Keys")

        # Rileva dimensioni dello schermo
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Calcola larghezza finestra (90% dello schermo, max 2400px)
        window_width = min(int(screen_width * 0.9), 2400)

        # Calcola altezza basata sulle proporzioni dei tasti del pianoforte
        # Un pianoforte ha 52 tasti bianchi, rapporto lunghezza:larghezza = 6.5:1
        # Quindi: larghezza_tasto = window_width / 52
        #         altezza_tasto = larghezza_tasto * 6.5
        # Aggiungiamo spazio per controlli (70px) e scrollbar (30px)
        white_key_width = window_width / 52
        keyboard_height = int(white_key_width * 6.5)  # Proporzione realistica
        window_height = keyboard_height + 100  # +100px per controlli e scrollbar

        # Limita altezza allo schermo disponibile (max 80% altezza schermo)
        max_height = int(screen_height * 0.8)
        window_height = min(window_height, max_height)

        # Centra la finestra sullo schermo
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2

        self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        
        # Variabili
        self.midi_input = None
        self.midi_thread = None
        self.running = False
        self.active_notes = set()
        
        # Frame principale
        self.setup_ui()
        
    def setup_ui(self):
        # Frame per la selezione MIDI
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(fill=tk.X)
        
        ttk.Label(control_frame, text="MIDI Input:").pack(side=tk.LEFT, padx=5)
        
        self.midi_combo = ttk.Combobox(control_frame, width=40, state="readonly")
        self.midi_combo.pack(side=tk.LEFT, padx=5)
        
        self.refresh_button = ttk.Button(control_frame, text="Aggiorna", command=self.refresh_midi_ports)
        self.refresh_button.pack(side=tk.LEFT, padx=5)
        
        self.connect_button = ttk.Button(control_frame, text="Connetti", command=self.connect_midi)
        self.connect_button.pack(side=tk.LEFT, padx=5)
        
        self.disconnect_button = ttk.Button(control_frame, text="Disconnetti", command=self.disconnect_midi, state=tk.DISABLED)
        self.disconnect_button.pack(side=tk.LEFT, padx=5)
        
        self.status_label = ttk.Label(control_frame, text="Non connesso", foreground="red")
        self.status_label.pack(side=tk.LEFT, padx=20)
        
        # Frame per la tastiera con scrollbar
        keyboard_frame = ttk.Frame(self.root, padding="10")
        keyboard_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollbar orizzontale
        h_scrollbar = ttk.Scrollbar(keyboard_frame, orient=tk.HORIZONTAL)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Canvas per la tastiera
        self.canvas = tk.Canvas(
            keyboard_frame,
            bg="white",
            highlightthickness=1,
            highlightbackground="gray",
            xscrollcommand=h_scrollbar.set
        )
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Configura scrollbar
        h_scrollbar.config(command=self.canvas.xview)
        
        # Disegna la tastiera
        self.draw_keyboard()
        
        # Inizializza lista porte MIDI
        self.refresh_midi_ports()
        
        # Gestione chiusura finestra
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def refresh_midi_ports(self):
        """Aggiorna la lista delle porte MIDI disponibili"""
        ports = mido.get_input_names()
        self.midi_combo['values'] = ports
        if ports:
            self.midi_combo.current(0)
    
    def draw_keyboard(self):
        """Disegna la tastiera virtuale (88 tasti, da A0 a C8)"""
        self.canvas.delete("all")

        # Dimensioni
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        if width <= 1:
            width = 2360  # Larghezza per 88 tasti
        if height <= 1:
            height = 300

        # Configurazione tastiera: 88 tasti completi del pianoforte
        # Pianoforte standard: A0 (MIDI 21) a C8 (MIDI 108)
        self.start_note = 21  # A0 (primo tasto del pianoforte)
        self.end_note = 108    # C8 (ultimo tasto del pianoforte)
        self.total_notes = self.end_note - self.start_note + 1  # 88 tasti

        # Calcola quanti tasti bianchi ci sono in totale (52 per un pianoforte da 88 tasti)
        # A0-B0 (3 tasti: A, A#, B) + 7 ottave complete (C1-B7) + C8 (1 tasto)
        # Tasti bianchi: A0, B0 (2) + 7 ottave * 7 bianchi (49) + C8 (1) = 52
        total_white_keys = 52

        self.white_key_width = width / total_white_keys
        self.white_key_height = height - 20
        self.black_key_width = self.white_key_width * 0.6
        self.black_key_height = self.white_key_height * 0.6

        # Mappa note (0=C, 1=C#, 2=D, etc.)
        self.key_positions = {}

        # Disegna tutti i tasti (sia bianchi che neri)
        # Prima disegniamo i tasti bianchi, poi i neri (così i neri vanno sopra)

        white_key_index = 0

        # Disegna tasti bianchi
        for note_number in range(self.start_note, self.end_note + 1):
            note_in_octave = note_number % 12
            # Verifica se è un tasto bianco (nota senza #)
            # Note bianche: 0=C, 2=D, 4=E, 5=F, 7=G, 9=A, 11=B
            is_white = note_in_octave in [0, 2, 4, 5, 7, 9, 11]

            if is_white:
                x = white_key_index * self.white_key_width

                rect = self.canvas.create_rectangle(
                    x, 10, x + self.white_key_width, 10 + self.white_key_height,
                    fill="white", outline="black", width=2, tags=f"note_{note_number}"
                )

                # Etichetta nota (solo per C e F per non affollare)
                note_name = self.get_note_name(note_number)
                if note_in_octave in [0, 5]:  # Solo C e F
                    self.canvas.create_text(
                        x + self.white_key_width / 2, 10 + self.white_key_height - 15,
                        text=note_name, font=("Arial", 7), tags=f"note_{note_number}_text"
                    )

                self.key_positions[note_number] = rect
                white_key_index += 1

        # Disegna tasti neri (sopra i bianchi)
        white_key_index = 0
        for note_number in range(self.start_note, self.end_note + 1):
            note_in_octave = note_number % 12
            is_white = note_in_octave in [0, 2, 4, 5, 7, 9, 11]

            if is_white:
                white_key_index += 1
            else:
                # Tasto nero - posizionalo tra i tasti bianchi
                # I tasti neri sono posizionati con un offset di 0.7 dal tasto bianco precedente
                x = (white_key_index - 0.3) * self.white_key_width

                rect = self.canvas.create_rectangle(
                    x, 10, x + self.black_key_width, 10 + self.black_key_height,
                    fill="black", outline="black", width=2, tags=f"note_{note_number}"
                )

                self.key_positions[note_number] = rect

        # Configura la scroll region per permettere lo scorrimento
        # La larghezza totale è data dal numero di tasti bianchi * larghezza del tasto
        total_width = 52 * self.white_key_width
        self.canvas.configure(scrollregion=(0, 0, total_width, self.white_key_height + 20))

    def get_note_name(self, note_number):
        """Restituisce il nome della nota con l'ottava"""
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        octave = (note_number // 12) - 1
        note_name = notes[note_number % 12]
        return f"{note_name}{octave}"
    
    def connect_midi(self):
        """Connette alla porta MIDI selezionata"""
        selected_port = self.midi_combo.get()
        if not selected_port:
            return
        
        try:
            self.midi_input = mido.open_input(selected_port)
            self.running = True
            
            # Avvia thread per leggere messaggi MIDI
            self.midi_thread = threading.Thread(target=self.read_midi, daemon=True)
            self.midi_thread.start()
            
            self.status_label.config(text=f"Connesso a {selected_port}", foreground="green")
            self.connect_button.config(state=tk.DISABLED)
            self.disconnect_button.config(state=tk.NORMAL)
            self.midi_combo.config(state=tk.DISABLED)
            
        except Exception as e:
            self.status_label.config(text=f"Errore: {str(e)}", foreground="red")
    
    def disconnect_midi(self):
        """Disconnette dalla porta MIDI"""
        self.running = False
        
        if self.midi_input:
            self.midi_input.close()
            self.midi_input = None
        
        # Resetta tutti i tasti
        for note in list(self.active_notes):
            self.note_off(note)
        
        self.status_label.config(text="Non connesso", foreground="red")
        self.connect_button.config(state=tk.NORMAL)
        self.disconnect_button.config(state=tk.DISABLED)
        self.midi_combo.config(state="readonly")
    
    def read_midi(self):
        """Legge i messaggi MIDI in un thread separato"""
        try:
            for msg in self.midi_input:
                if not self.running:
                    break
                
                if msg.type == 'note_on' and msg.velocity > 0:
                    self.root.after(0, self.note_on, msg.note, msg.velocity)
                elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                    self.root.after(0, self.note_off, msg.note)
                    
        except Exception as e:
            self.root.after(0, lambda: self.status_label.config(
                text=f"Errore lettura MIDI: {str(e)}", foreground="red"
            ))
    
    def note_on(self, note, velocity):
        """Evidenzia il tasto premuto"""
        if note in self.key_positions:
            self.active_notes.add(note)
            
            # Calcola il colore in base alla velocity
            intensity = int((velocity / 127) * 100) + 155
            color = f"#{intensity:02x}{intensity//2:02x}{intensity//2:02x}"
            
            # Colora il tasto
            is_black = (note % 12) in [1, 3, 6, 8, 10]
            if is_black:
                self.canvas.itemconfig(self.key_positions[note], fill=color)
            else:
                self.canvas.itemconfig(self.key_positions[note], fill=color)
    
    def note_off(self, note):
        """Ripristina il colore originale del tasto"""
        if note in self.key_positions and note in self.active_notes:
            self.active_notes.remove(note)
            
            # Ripristina colore originale
            is_black = (note % 12) in [1, 3, 6, 8, 10]
            original_color = "black" if is_black else "white"
            self.canvas.itemconfig(self.key_positions[note], fill=original_color)
    
    def on_closing(self):
        """Gestisce la chiusura della finestra"""
        self.disconnect_midi()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = VirtualKeyboard(root)

    # Ridisegna la tastiera quando la finestra viene ridimensionata
    # Questo permette alla tastiera di adattarsi automaticamente
    resize_timer = None

    def on_resize(event):
        nonlocal resize_timer
        # Evita di ridisegnare troppo frequentemente (debouncing)
        if resize_timer is not None:
            root.after_cancel(resize_timer)
        resize_timer = root.after(100, app.draw_keyboard)

    root.bind('<Configure>', on_resize)
    root.mainloop()


if __name__ == "__main__":
    main()