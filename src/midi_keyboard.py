import tkinter as tk
from tkinter import ttk
import mido
import threading

class VirtualKeyboard:
    def __init__(self, root):
        self.root = root
        self.root.title("MIDI Virtual Keyboard")
        self.root.geometry("1200x400")
        
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
        
        # Frame per la tastiera
        keyboard_frame = ttk.Frame(self.root, padding="10")
        keyboard_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas per la tastiera
        self.canvas = tk.Canvas(keyboard_frame, bg="white", highlightthickness=1, highlightbackground="gray")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
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
        """Disegna la tastiera virtuale (3 ottave, da C3 a B5)"""
        self.canvas.delete("all")
        
        # Dimensioni
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        if width <= 1:
            width = 1180
        if height <= 1:
            height = 300
        
        # Configurazione tastiera: 3 ottave (36 tasti)
        self.start_note = 48  # C3
        self.num_octaves = 3
        self.white_keys_per_octave = 7
        total_white_keys = self.white_keys_per_octave * self.num_octaves
        
        self.white_key_width = width / total_white_keys
        self.white_key_height = height - 20
        self.black_key_width = self.white_key_width * 0.6
        self.black_key_height = self.white_key_height * 0.6
        
        # Mappa note (0=C, 1=C#, 2=D, etc.)
        self.key_positions = {}
        
        # Pattern tasti bianchi e neri per ottava
        white_notes = [0, 2, 4, 5, 7, 9, 11]  # C, D, E, F, G, A, B
        black_notes = [1, 3, 6, 8, 10]  # C#, D#, F#, G#, A#
        black_positions = [0.7, 1.7, 3.7, 4.7, 5.7]  # Posizioni relative dei tasti neri
        
        # Disegna tasti bianchi
        white_key_index = 0
        for octave in range(self.num_octaves):
            for white_note in white_notes:
                note_number = self.start_note + octave * 12 + white_note
                x = white_key_index * self.white_key_width
                
                rect = self.canvas.create_rectangle(
                    x, 10, x + self.white_key_width, 10 + self.white_key_height,
                    fill="white", outline="black", width=2, tags=f"note_{note_number}"
                )
                
                # Etichetta nota
                note_name = self.get_note_name(note_number)
                self.canvas.create_text(
                    x + self.white_key_width / 2, 10 + self.white_key_height - 20,
                    text=note_name, font=("Arial", 9), tags=f"note_{note_number}_text"
                )
                
                self.key_positions[note_number] = rect
                white_key_index += 1
        
        # Disegna tasti neri
        for octave in range(self.num_octaves):
            for i, black_note in enumerate(black_notes):
                note_number = self.start_note + octave * 12 + black_note
                x = (octave * self.white_keys_per_octave + black_positions[i]) * self.white_key_width
                
                rect = self.canvas.create_rectangle(
                    x, 10, x + self.black_key_width, 10 + self.black_key_height,
                    fill="black", outline="black", width=2, tags=f"note_{note_number}"
                )
                
                self.key_positions[note_number] = rect
    
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
    def on_resize(event):
        app.draw_keyboard()
    
    root.bind('<Configure>', on_resize)
    root.mainloop()


if __name__ == "__main__":
    main()