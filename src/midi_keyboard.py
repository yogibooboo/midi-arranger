import tkinter as tk
from tkinter import ttk
import mido
import threading

# Lista completa degli strumenti General MIDI (128 programs)
GM_INSTRUMENTS = [
    # Piano (0-7)
    "0: Acoustic Grand Piano", "1: Bright Acoustic Piano", "2: Electric Grand Piano",
    "3: Honky-tonk Piano", "4: Electric Piano 1", "5: Electric Piano 2",
    "6: Harpsichord", "7: Clavinet",
    # Chromatic Percussion (8-15)
    "8: Celesta", "9: Glockenspiel", "10: Music Box", "11: Vibraphone",
    "12: Marimba", "13: Xylophone", "14: Tubular Bells", "15: Dulcimer",
    # Organ (16-23)
    "16: Drawbar Organ", "17: Percussive Organ", "18: Rock Organ", "19: Church Organ",
    "20: Reed Organ", "21: Accordion", "22: Harmonica", "23: Tango Accordion",
    # Guitar (24-31)
    "24: Acoustic Guitar (nylon)", "25: Acoustic Guitar (steel)", "26: Electric Guitar (jazz)",
    "27: Electric Guitar (clean)", "28: Electric Guitar (muted)", "29: Overdriven Guitar",
    "30: Distortion Guitar", "31: Guitar Harmonics",
    # Bass (32-39)
    "32: Acoustic Bass", "33: Electric Bass (finger)", "34: Electric Bass (pick)",
    "35: Fretless Bass", "36: Slap Bass 1", "37: Slap Bass 2",
    "38: Synth Bass 1", "39: Synth Bass 2",
    # Strings (40-47)
    "40: Violin", "41: Viola", "42: Cello", "43: Contrabass",
    "44: Tremolo Strings", "45: Pizzicato Strings", "46: Orchestral Harp", "47: Timpani",
    # Ensemble (48-55)
    "48: String Ensemble 1", "49: String Ensemble 2", "50: Synth Strings 1", "51: Synth Strings 2",
    "52: Choir Aahs", "53: Voice Oohs", "54: Synth Voice", "55: Orchestra Hit",
    # Brass (56-63)
    "56: Trumpet", "57: Trombone", "58: Tuba", "59: Muted Trumpet",
    "60: French Horn", "61: Brass Section", "62: Synth Brass 1", "63: Synth Brass 2",
    # Reed (64-71)
    "64: Soprano Sax", "65: Alto Sax", "66: Tenor Sax", "67: Baritone Sax",
    "68: Oboe", "69: English Horn", "70: Bassoon", "71: Clarinet",
    # Pipe (72-79)
    "72: Piccolo", "73: Flute", "74: Recorder", "75: Pan Flute",
    "76: Blown Bottle", "77: Shakuhachi", "78: Whistle", "79: Ocarina",
    # Synth Lead (80-87)
    "80: Lead 1 (square)", "81: Lead 2 (sawtooth)", "82: Lead 3 (calliope)", "83: Lead 4 (chiff)",
    "84: Lead 5 (charang)", "85: Lead 6 (voice)", "86: Lead 7 (fifths)", "87: Lead 8 (bass + lead)",
    # Synth Pad (88-95)
    "88: Pad 1 (new age)", "89: Pad 2 (warm)", "90: Pad 3 (polysynth)", "91: Pad 4 (choir)",
    "92: Pad 5 (bowed)", "93: Pad 6 (metallic)", "94: Pad 7 (halo)", "95: Pad 8 (sweep)",
    # Synth Effects (96-103)
    "96: FX 1 (rain)", "97: FX 2 (soundtrack)", "98: FX 3 (crystal)", "99: FX 4 (atmosphere)",
    "100: FX 5 (brightness)", "101: FX 6 (goblins)", "102: FX 7 (echoes)", "103: FX 8 (sci-fi)",
    # Ethnic (104-111)
    "104: Sitar", "105: Banjo", "106: Shamisen", "107: Koto",
    "108: Kalimba", "109: Bag pipe", "110: Fiddle", "111: Shanai",
    # Percussive (112-119)
    "112: Tinkle Bell", "113: Agogo", "114: Steel Drums", "115: Woodblock",
    "116: Taiko Drum", "117: Melodic Tom", "118: Synth Drum", "119: Reverse Cymbal",
    # Sound Effects (120-127)
    "120: Guitar Fret Noise", "121: Breath Noise", "122: Seashore", "123: Bird Tweet",
    "124: Telephone Ring", "125: Helicopter", "126: Applause", "127: Gunshot"
]

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
        
        # Variabili MIDI Input
        self.midi_input = None
        self.midi_thread = None
        self.running = False
        self.active_notes = set()

        # Variabili MIDI Output
        self.midi_output = None
        self.midi_channel = 0  # Canale MIDI (0-15, che corrisponde a 1-16)
        self.midi_program = 0  # Program MIDI (0-127, strumento GM)
        
        # Frame principale
        self.setup_ui()
        
    def setup_ui(self):
        # Frame per la selezione MIDI Input
        input_frame = ttk.Frame(self.root, padding="10")
        input_frame.pack(fill=tk.X)

        ttk.Label(input_frame, text="MIDI Input:").pack(side=tk.LEFT, padx=5)

        self.midi_input_combo = ttk.Combobox(input_frame, width=35, state="readonly")
        self.midi_input_combo.pack(side=tk.LEFT, padx=5)
        self.midi_input_combo.bind('<<ComboboxSelected>>', self.on_input_change)

        self.input_status_label = ttk.Label(input_frame, text="Input: Non connesso", foreground="red")
        self.input_status_label.pack(side=tk.LEFT, padx=10)

        # Frame per la selezione MIDI Output
        output_frame = ttk.Frame(self.root, padding="10")
        output_frame.pack(fill=tk.X)

        ttk.Label(output_frame, text="MIDI Output:").pack(side=tk.LEFT, padx=5)

        self.midi_output_combo = ttk.Combobox(output_frame, width=35, state="readonly")
        self.midi_output_combo.pack(side=tk.LEFT, padx=5)
        self.midi_output_combo.bind('<<ComboboxSelected>>', self.on_output_change)

        ttk.Label(output_frame, text="Canale:").pack(side=tk.LEFT, padx=(20, 5))

        self.channel_combo = ttk.Combobox(output_frame, width=5, state="readonly")
        self.channel_combo['values'] = [str(i) for i in range(1, 17)]  # Canali 1-16
        self.channel_combo.current(0)  # Default: canale 1
        self.channel_combo.pack(side=tk.LEFT, padx=5)
        self.channel_combo.bind('<<ComboboxSelected>>', self.on_channel_change)

        ttk.Label(output_frame, text="Strumento:").pack(side=tk.LEFT, padx=(20, 5))

        self.program_combo = ttk.Combobox(output_frame, width=30, state="readonly")
        self.program_combo['values'] = GM_INSTRUMENTS
        self.program_combo.current(0)  # Default: Acoustic Grand Piano
        self.program_combo.pack(side=tk.LEFT, padx=5)
        self.program_combo.bind('<<ComboboxSelected>>', self.on_program_change)

        self.output_status_label = ttk.Label(output_frame, text="Output: Non connesso", foreground="red")
        self.output_status_label.pack(side=tk.LEFT, padx=10)

        # Pulsante refresh porte
        refresh_frame = ttk.Frame(self.root, padding="5")
        refresh_frame.pack(fill=tk.X)

        self.refresh_button = ttk.Button(refresh_frame, text="Aggiorna Porte MIDI", command=self.refresh_midi_ports)
        self.refresh_button.pack(side=tk.LEFT, padx=5)
        
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
        """Aggiorna la lista delle porte MIDI disponibili e connette automaticamente"""
        # Aggiorna porte input
        input_ports = mido.get_input_names()
        self.midi_input_combo['values'] = input_ports
        if input_ports:
            self.midi_input_combo.current(0)
            # Connetti automaticamente alla prima porta
            self.connect_midi_input()

        # Aggiorna porte output
        output_ports = mido.get_output_names()
        self.midi_output_combo['values'] = output_ports
        if output_ports:
            self.midi_output_combo.current(0)
            # Connetti automaticamente alla prima porta
            self.connect_midi_output()

    def on_input_change(self, event=None):
        """Gestisce il cambio di porta MIDI input"""
        # Disconnetti la porta precedente
        if self.midi_input:
            self.disconnect_midi_input()
        # Connetti alla nuova porta
        self.connect_midi_input()

    def on_output_change(self, event=None):
        """Gestisce il cambio di porta MIDI output"""
        # Disconnetti la porta precedente
        if self.midi_output:
            self.disconnect_midi_output()
        # Connetti alla nuova porta
        self.connect_midi_output()

    def on_channel_change(self, event=None):
        """Gestisce il cambio di canale MIDI"""
        self.midi_channel = int(self.channel_combo.get()) - 1  # 1-16 -> 0-15

    def on_program_change(self, event=None):
        """Gestisce il cambio di strumento MIDI (Program Change)"""
        selected = self.program_combo.get()
        # Estrae il numero dal formato "0: Acoustic Grand Piano"
        self.midi_program = int(selected.split(':')[0])

        # Invia il messaggio Program Change se la porta output è connessa
        if self.midi_output:
            msg = mido.Message('program_change', program=self.midi_program, channel=self.midi_channel)
            self.midi_output.send(msg)

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

                # Binding clic mouse per suonare il tasto
                self.canvas.tag_bind(f"note_{note_number}", "<Button-1>", lambda _, n=note_number: self.play_note(n, 100))
                self.canvas.tag_bind(f"note_{note_number}", "<ButtonRelease-1>", lambda _, n=note_number: self.stop_note(n))

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

                # Binding clic mouse per suonare il tasto
                self.canvas.tag_bind(f"note_{note_number}", "<Button-1>", lambda _, n=note_number: self.play_note(n, 100))
                self.canvas.tag_bind(f"note_{note_number}", "<ButtonRelease-1>", lambda _, n=note_number: self.stop_note(n))

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
    
    def connect_midi_input(self):
        """Connette alla porta MIDI input selezionata"""
        selected_port = self.midi_input_combo.get()
        if not selected_port:
            return

        try:
            self.midi_input = mido.open_input(selected_port)
            self.running = True

            # Avvia thread per leggere messaggi MIDI
            self.midi_thread = threading.Thread(target=self.read_midi, daemon=True)
            self.midi_thread.start()

            # Mostra nome porta abbreviato se troppo lungo
            port_display = selected_port if len(selected_port) <= 25 else selected_port[:22] + "..."
            self.input_status_label.config(text=f"Input: {port_display}", foreground="green")

        except Exception as e:
            self.input_status_label.config(text=f"Input Errore: {str(e)[:20]}", foreground="red")

    def disconnect_midi_input(self):
        """Disconnette dalla porta MIDI input"""
        self.running = False

        if self.midi_input:
            self.midi_input.close()
            self.midi_input = None

        # Resetta tutti i tasti
        for note in list(self.active_notes):
            self.note_off(note)

        self.input_status_label.config(text="Input: Non connesso", foreground="orange")

    def connect_midi_output(self):
        """Connette alla porta MIDI output selezionata"""
        selected_port = self.midi_output_combo.get()
        if not selected_port:
            return

        try:
            self.midi_output = mido.open_output(selected_port)

            # Invia il Program Change iniziale per impostare lo strumento
            msg = mido.Message('program_change', program=self.midi_program, channel=self.midi_channel)
            self.midi_output.send(msg)

            # Mostra nome porta abbreviato se troppo lungo
            port_display = selected_port if len(selected_port) <= 25 else selected_port[:22] + "..."
            self.output_status_label.config(text=f"Output: {port_display}", foreground="green")

        except Exception as e:
            self.output_status_label.config(text=f"Output Errore: {str(e)[:20]}", foreground="red")

    def disconnect_midi_output(self):
        """Disconnette dalla porta MIDI output"""
        if self.midi_output:
            # Invia note-off per tutte le note eventualmente attive
            for note in range(128):
                try:
                    msg = mido.Message('note_off', note=note, velocity=0, channel=self.midi_channel)
                    self.midi_output.send(msg)
                except:
                    pass

            self.midi_output.close()
            self.midi_output = None

        self.output_status_label.config(text="Output: Non connesso", foreground="orange")

    def play_note(self, note, velocity):
        """Suona una nota inviandola all'output MIDI e visualizzandola"""
        if self.midi_output:
            # Invia note-on al dispositivo MIDI
            msg = mido.Message('note_on', note=note, velocity=velocity, channel=self.midi_channel)
            self.midi_output.send(msg)

        # Visualizza il tasto premuto
        self.note_on(note, velocity)

    def stop_note(self, note):
        """Ferma una nota inviando note-off"""
        if self.midi_output:
            # Invia note-off al dispositivo MIDI
            msg = mido.Message('note_off', note=note, velocity=0, channel=self.midi_channel)
            self.midi_output.send(msg)

        # Visualizza il tasto rilasciato
        self.note_off(note)

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
        self.disconnect_midi_input()
        self.disconnect_midi_output()
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