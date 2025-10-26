"""
StylePlayer - Classe per gestire il playback di file .STY Yamaha
"""

import mido
import time
import threading


class StylePlayer:
    """Gestisce il caricamento e playback di file .STY Yamaha"""

    # Sezioni standard degli style Yamaha
    SECTION_TYPES = {
        'intro': ['Intro A', 'Intro B', 'Intro C'],
        'main': ['Main A', 'Main B', 'Main C', 'Main D'],
        'fill': ['Fill In AA', 'Fill In BB', 'Fill In CC', 'Fill In DD'],
        'ending': ['Ending A', 'Ending B', 'Ending C']
    }

    def __init__(self):
        self.midi_file = None
        self.style_name = None
        self.tempo_bpm = 120
        self.ticks_per_beat = 480
        self.sections = {}
        self.current_section = None
        self.playing = False
        self.play_thread = None
        self.midi_output = None

        # Filtro accordo - se impostato, filtra le note suonate
        self.chord_filter = None  # None = no filter, oppure set di note (0-11)

        # Trasposizione - numero di semitoni da trasporre
        self.transpose_semitones = 0  # 0 = nessuna trasposizione

        # Stop a fine battuta
        self.stop_at_measure_end = False  # Se True, ferma alla fine della battuta corrente

    def load_style(self, filename):
        """Carica un file .STY"""
        try:
            self.midi_file = mido.MidiFile(filename)
            self.ticks_per_beat = self.midi_file.ticks_per_beat

            # Analizza metadata e sezioni
            self._parse_metadata()
            self._parse_sections()

            return True

        except Exception as e:
            print(f"Errore caricamento style: {e}")
            return False

    def _parse_metadata(self):
        """Estrae metadata dallo style (nome, tempo, ecc.)"""
        if not self.midi_file or len(self.midi_file.tracks) == 0:
            return

        for msg in self.midi_file.tracks[0]:
            if msg.type == 'track_name':
                self.style_name = msg.name.strip()
            elif msg.type == 'set_tempo':
                self.tempo_bpm = mido.tempo2bpm(msg.tempo)

    def _parse_sections(self):
        """Identifica le sezioni dello style (Main A, Intro, ecc.)"""
        self.sections = {}

        # Unisci tutti i nomi di sezione validi
        all_section_names = []
        for section_list in self.SECTION_TYPES.values():
            all_section_names.extend(section_list)

        # Scansiona tutte le tracce per trovare i markers di sezione
        for track in self.midi_file.tracks:
            current_section = None
            section_start_time = 0
            absolute_time = 0
            section_events = []

            for msg in track:
                absolute_time += msg.time

                # Controlla se è un marker di sezione
                if msg.type == 'marker' and msg.text in all_section_names:
                    # Salva la sezione precedente se esiste
                    if current_section and section_events:
                        if current_section not in self.sections:
                            self.sections[current_section] = {
                                'events': [],
                                'length_ticks': absolute_time - section_start_time,
                                'start_time': section_start_time
                            }
                        # Aggiungi gli eventi alla sezione
                        self.sections[current_section]['events'].extend(section_events)

                    # Inizia nuova sezione
                    current_section = msg.text
                    section_start_time = absolute_time
                    section_events = []

                # Aggiungi evento alla sezione corrente
                elif current_section:
                    # Crea una copia del messaggio con tempo relativo alla sezione
                    event_copy = msg.copy()
                    section_events.append(event_copy)

            # Salva l'ultima sezione
            if current_section and section_events:
                if current_section not in self.sections:
                    self.sections[current_section] = {
                        'events': [],
                        'length_ticks': absolute_time - section_start_time,
                        'start_time': section_start_time
                    }
                self.sections[current_section]['events'].extend(section_events)

    def get_available_sections(self):
        """Ritorna lista delle sezioni disponibili nello style"""
        return sorted(list(self.sections.keys()))

    def get_section_info(self, section_name):
        """Ottiene informazioni su una sezione specifica"""
        if section_name not in self.sections:
            return None

        info = self.sections[section_name]
        beats = info['length_ticks'] / self.ticks_per_beat

        return {
            'name': section_name,
            'beats': beats,
            'length_ticks': info['length_ticks'],
            'num_events': len(info['events'])
        }

    def set_midi_output(self, midi_output):
        """Imposta la porta MIDI output per il playback"""
        self.midi_output = midi_output

    def play_section(self, section_name, loop=True):
        """Avvia il playback di una sezione"""
        if section_name not in self.sections:
            print(f"Sezione '{section_name}' non trovata")
            return False

        if not self.midi_output:
            print("MIDI output non configurato")
            return False

        # Ferma playback precedente
        self.stop()

        self.current_section = section_name
        self.playing = True

        # Avvia thread di playback
        self.play_thread = threading.Thread(
            target=self._playback_loop,
            args=(section_name, loop),
            daemon=True
        )
        self.play_thread.start()

        return True

    def _playback_loop(self, section_name, loop):
        """Loop di playback (eseguito in thread separato)"""
        section = self.sections[section_name]
        events = section['events']

        # Tempo in secondi per tick
        seconds_per_tick = 60.0 / (self.tempo_bpm * self.ticks_per_beat)

        # Una battuta = 4 beat * ticks_per_beat
        ticks_per_measure = 4 * self.ticks_per_beat
        current_tick = 0

        while self.playing:
            # Riproduci gli eventi della sezione
            for event in events:
                if not self.playing:
                    break

                # Controlla se dobbiamo fermarci a fine battuta
                if self.stop_at_measure_end:
                    # Se abbiamo completato una battuta, ferma
                    if current_tick >= ticks_per_measure and current_tick % ticks_per_measure == 0:
                        self.playing = False
                        break

                # Attendi il tempo dell'evento
                if event.time > 0:
                    time.sleep(event.time * seconds_per_tick)
                    current_tick += event.time

                # Invia il messaggio MIDI (solo messaggi non-meta)
                if not event.is_meta:
                    # Crea una copia del messaggio per non modificare l'originale
                    msg = event.copy()

                    # Applica trasposizione alle note (ma NON al canale drums - channel 9)
                    if self.transpose_semitones != 0 and msg.type in ['note_on', 'note_off'] and msg.channel != 9:
                        msg.note = max(0, min(127, msg.note + self.transpose_semitones))

                    # Applica filtro accordo se impostato (ma NON al canale drums - channel 9)
                    should_send = True
                    if self.chord_filter is not None and msg.type in ['note_on', 'note_off'] and msg.channel != 9:
                        note_class = msg.note % 12
                        if note_class not in self.chord_filter:
                            should_send = False

                    if should_send:
                        try:
                            self.midi_output.send(msg)
                        except Exception as e:
                            print(f"Errore invio MIDI: {e}")

            # Reset tick count per il prossimo loop
            current_tick = 0

            # Se non è in loop, esci
            if not loop:
                break

            # Se dobbiamo fermarci, esci
            if self.stop_at_measure_end:
                break

        self.playing = False
        self.stop_at_measure_end = False  # Reset flag

    def stop(self):
        """Ferma il playback immediatamente"""
        self.playing = False
        self.stop_at_measure_end = False

        # Attendi che il thread termini
        if self.play_thread and self.play_thread.is_alive():
            self.play_thread.join(timeout=1.0)

        # Invia All Notes Off su tutti i canali
        if self.midi_output:
            for channel in range(16):
                try:
                    msg = mido.Message('control_change',
                                      control=123,  # All Notes Off
                                      value=0,
                                      channel=channel)
                    self.midi_output.send(msg)
                except:
                    pass

    def request_stop_at_measure_end(self):
        """Richiede di fermare il playback alla fine della battuta corrente"""
        self.stop_at_measure_end = True

    def set_tempo(self, bpm):
        """Imposta il tempo di playback"""
        self.tempo_bpm = bpm

    def set_chord_filter(self, chord_notes):
        """
        Imposta il filtro accordo per il playback.

        Args:
            chord_notes: None (no filter) oppure set/list di note 0-11
                        Es: {0, 4, 7} per C maggiore (C, E, G)
        """
        if chord_notes is None:
            self.chord_filter = None
        else:
            self.chord_filter = set(chord_notes)

    def set_c_major(self):
        """Imposta filtro per C maggiore (C, E, G)"""
        self.set_chord_filter({0, 4, 7})  # C, E, G

    def disable_filter(self):
        """Disabilita il filtro accordo"""
        self.set_chord_filter(None)

    def set_transpose(self, semitones):
        """
        Imposta la trasposizione in semitoni.

        Args:
            semitones: numero di semitoni da trasporre (-11 a +11)
                      0 = nessuna trasposizione
                      +2 = traspone 1 tono in su (es. C -> D)
                      -3 = traspone 1 tono e mezzo in giù
        """
        self.transpose_semitones = max(-11, min(11, semitones))

    def is_playing(self):
        """Verifica se è in corso un playback"""
        return self.playing

    def stop_melodic_notes(self, hold_drums=True):
        """
        Ferma immediatamente le note melodiche (non drums).

        Args:
            hold_drums: Se True, i drums continuano a suonare
        """
        if not self.midi_output:
            return

        # Invia All Notes Off su tutti i canali tranne drums (se hold_drums=True)
        for channel in range(16):
            if hold_drums and channel == 9:
                # Salta il canale drums
                continue

            try:
                msg = mido.Message('control_change',
                                  control=123,  # All Notes Off
                                  value=0,
                                  channel=channel)
                self.midi_output.send(msg)
            except:
                pass

    def change_section(self, section_name):
        """
        Cambia sezione in tempo reale senza fermare il playback.

        Args:
            section_name: Nome della nuova sezione da suonare
        """
        if section_name not in self.sections:
            print(f"Sezione '{section_name}' non trovata")
            return False

        # Ferma il playback corrente
        self.playing = False

        # Attendi che il thread termini
        if self.play_thread and self.play_thread.is_alive():
            self.play_thread.join(timeout=0.5)

        # Avvia la nuova sezione
        self.current_section = section_name
        self.playing = True

        # Avvia nuovo thread di playback
        self.play_thread = threading.Thread(
            target=self._playback_loop,
            args=(section_name, True),  # Loop sempre attivo
            daemon=True
        )
        self.play_thread.start()

        return True

    def get_style_info(self):
        """Ritorna informazioni generali sullo style"""
        if not self.midi_file:
            return None

        return {
            'name': self.style_name or 'Unknown',
            'tempo': self.tempo_bpm,
            'sections': len(self.sections),
            'section_list': self.get_available_sections()
        }
