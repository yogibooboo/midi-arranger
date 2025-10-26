"""
ChordRecognizer - Riconosce accordi dal MIDI input
"""


class ChordRecognizer:
    """Riconosce accordi dalle note MIDI suonate"""

    # Nomi delle note
    NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

    # Pattern di accordi comuni (intervalli dalla root)
    CHORD_PATTERNS = {
        'Maj': [0, 4, 7],           # Maggiore: C E G
        'min': [0, 3, 7],           # Minore: C Eb G
        'Maj7': [0, 4, 7, 11],      # Maggiore 7: C E G B
        'min7': [0, 3, 7, 10],      # Minore 7: C Eb G Bb
        '7': [0, 4, 7, 10],         # Dominante 7: C E G Bb
        'dim': [0, 3, 6],           # Diminuito: C Eb Gb
        'aug': [0, 4, 8],           # Aumentato: C E G#
        'sus4': [0, 5, 7],          # Sospeso 4: C F G
        'sus2': [0, 2, 7],          # Sospeso 2: C D G
        '6': [0, 4, 7, 9],          # Maggiore 6: C E G A
        'min6': [0, 3, 7, 9],       # Minore 6: C Eb G A
        'dim7': [0, 3, 6, 9],       # Diminuito 7: C Eb Gb Bbb
        'm7b5': [0, 3, 6, 10],      # Semi-diminuito: C Eb Gb Bb
    }

    def __init__(self):
        self.active_notes = set()  # Note attualmente premute (MIDI note numbers)
        self.current_chord = None  # Accordo corrente riconosciuto
        self.bass_note = None      # Nota più bassa (per rivolti)

    def note_on(self, note):
        """Registra una nota premuta"""
        self.active_notes.add(note)
        self._analyze_chord()

    def note_off(self, note):
        """Registra una nota rilasciata"""
        self.active_notes.discard(note)
        self._analyze_chord()

    def clear(self):
        """Cancella tutte le note attive"""
        self.active_notes.clear()
        self.current_chord = None
        self.bass_note = None

    def _analyze_chord(self):
        """Analizza le note attive e identifica l'accordo"""
        if len(self.active_notes) == 0:
            self.current_chord = None
            self.bass_note = None
            return

        # Converti note in classi (0-11, ignorando ottave)
        note_classes = set(note % 12 for note in self.active_notes)

        # Trova la nota più bassa (bass)
        self.bass_note = min(self.active_notes) % 12

        # Se c'è solo una nota, non è un accordo
        if len(note_classes) == 1:
            root = list(note_classes)[0]
            self.current_chord = {
                'root': root,
                'root_name': self.NOTE_NAMES[root],
                'type': 'single',
                'type_name': '',
                'notes': note_classes,
                'bass': self.bass_note
            }
            return

        # Prova a identificare l'accordo provando ogni nota come root
        best_match = None
        best_score = 0

        for potential_root in note_classes:
            for chord_type, pattern in self.CHORD_PATTERNS.items():
                # Calcola le note attese per questo accordo
                expected_notes = set((potential_root + interval) % 12 for interval in pattern)

                # Calcola quante note corrispondono
                matches = len(note_classes & expected_notes)
                total = len(note_classes | expected_notes)

                # Score: percentuale di match
                score = matches / total if total > 0 else 0

                # Bonus se tutte le note dell'accordo ci sono
                if note_classes >= expected_notes:
                    score += 0.5

                if score > best_score:
                    best_score = score
                    best_match = {
                        'root': potential_root,
                        'root_name': self.NOTE_NAMES[potential_root],
                        'type': chord_type,
                        'type_name': chord_type,
                        'notes': note_classes,
                        'bass': self.bass_note,
                        'confidence': score
                    }

        # Accetta solo se lo score è abbastanza alto
        if best_match and best_score > 0.6:
            self.current_chord = best_match
        else:
            # Accordo non riconosciuto - usa almeno la root e le note
            root = min(note_classes)  # Usa la nota più bassa come root
            self.current_chord = {
                'root': root,
                'root_name': self.NOTE_NAMES[root],
                'type': 'unknown',
                'type_name': '?',
                'notes': note_classes,
                'bass': self.bass_note,
                'confidence': best_score
            }

    def get_current_chord(self):
        """
        Ritorna l'accordo corrente riconosciuto.

        Returns:
            dict o None:
                {
                    'root': 0-11,           # Nota root (0=C, 1=C#, etc.)
                    'root_name': 'C',       # Nome della root
                    'type': 'Maj',          # Tipo accordo
                    'type_name': 'Maj',     # Nome tipo
                    'notes': {0, 4, 7},     # Note dell'accordo
                    'bass': 0,              # Nota basso
                    'confidence': 0.95      # Confidenza (0-1)
                }
        """
        return self.current_chord

    def get_chord_name(self):
        """
        Ritorna il nome dell'accordo corrente (es. "Cmaj7", "Dm", etc.)

        Returns:
            str o None: Nome dell'accordo o None se nessun accordo
        """
        if not self.current_chord:
            return None

        root_name = self.current_chord['root_name']
        type_name = self.current_chord['type_name']

        # Se il basso è diverso dalla root, aggiungi il rivolto
        if self.current_chord['bass'] != self.current_chord['root']:
            bass_name = self.NOTE_NAMES[self.current_chord['bass']]
            return f"{root_name}{type_name}/{bass_name}"
        else:
            return f"{root_name}{type_name}"

    def get_notes_for_transposition(self):
        """
        Ritorna le note da usare per la trasposizione dello style.

        Returns:
            set o None: Set di note (0-11) da suonare, o None se nessun accordo
        """
        if not self.current_chord:
            return None

        # Se abbiamo un pattern riconosciuto, usa quello
        if self.current_chord['type'] in self.CHORD_PATTERNS:
            root = self.current_chord['root']
            pattern = self.CHORD_PATTERNS[self.current_chord['type']]
            return set((root + interval) % 12 for interval in pattern)

        # Altrimenti usa le note effettivamente suonate
        return self.current_chord['notes']

    def get_transposition_semitones(self, from_root=0):
        """
        Calcola di quanti semitoni trasporre dalla root originale.

        Args:
            from_root: nota root originale (default 0 = C)

        Returns:
            int: numero di semitoni (+/- 11)
        """
        if not self.current_chord:
            return 0

        root = self.current_chord['root']
        # Calcola distanza più breve (max 6 semitoni in su o giù)
        diff = root - from_root
        if diff > 6:
            diff -= 12
        elif diff < -6:
            diff += 12

        return diff
