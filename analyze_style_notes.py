#!/usr/bin/env python3
"""Analizza le note effettive suonate in uno style"""

import sys
sys.path.insert(0, 'src')

from style_player import StylePlayer

# Carica uno style
sty_file = r'sty\stili_miei\Swing1.S733.sty'
player = StylePlayer()

print("=" * 80)
print(f"ANALISI NOTE STYLE: {sty_file}")
print("=" * 80)

if player.load_style(sty_file):
    info = player.get_style_info()
    print(f"\nStyle: {info['name']}")
    print(f"Tempo: {info['tempo']:.0f} BPM")

    # Analizza Main A
    section_name = 'Main A'
    section = player.sections[section_name]
    events = section['events']

    # Raccogli tutte le note suonate
    notes_played = {}  # note_number -> count
    channels_used = set()

    print(f"\n[SEZIONE: {section_name}]")
    print("-" * 80)

    for event in events:
        if event.type == 'note_on' and event.velocity > 0:
            note = event.note
            channel = event.channel if hasattr(event, 'channel') else 0

            if note not in notes_played:
                notes_played[note] = 0
            notes_played[note] += 1
            channels_used.add(channel)

    # Mappa note MIDI a nomi
    NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

    def note_to_name(midi_note):
        octave = (midi_note // 12) - 1
        note_name = NOTE_NAMES[midi_note % 12]
        return f"{note_name}{octave}"

    # Ordina per frequenza
    sorted_notes = sorted(notes_played.items(), key=lambda x: x[1], reverse=True)

    print(f"\nNote suonate (ordinate per frequenza):")
    print(f"Totale note uniche: {len(sorted_notes)}")
    print(f"Canali MIDI usati: {sorted(channels_used)}\n")

    # Mostra prime 20 note più comuni
    print("Top 20 note più suonate:")
    for i, (note, count) in enumerate(sorted_notes[:20]):
        note_name = note_to_name(note)
        print(f"  {i+1:2d}. {note_name:4s} (MIDI {note:3d}) - suonata {count:3d} volte")

    # Analizza la scala/tonalità
    print("\n" + "-" * 80)
    print("ANALISI TONALITA':")
    print("-" * 80)

    # Conta note per classe (ignorando ottava)
    note_classes = {}
    for note, count in notes_played.items():
        note_class = note % 12
        if note_class not in note_classes:
            note_classes[note_class] = 0
        note_classes[note_class] += count

    # Ordina per frequenza
    sorted_classes = sorted(note_classes.items(), key=lambda x: x[1], reverse=True)

    print("\nDistribuzione per classe di nota (senza ottava):")
    for note_class, count in sorted_classes:
        note_name = NOTE_NAMES[note_class]
        percentage = (count / sum(note_classes.values())) * 100
        bar = "█" * int(percentage / 2)
        print(f"  {note_name:3s}: {bar:30s} {percentage:5.1f}% ({count} note)")

    # Identifica possibile accordo
    print("\n" + "-" * 80)
    print("IDENTIFICAZIONE ACCORDO:")
    print("-" * 80)

    # Prendi le note più comuni (top 40%)
    total_notes = sum(note_classes.values())
    cumulative = 0
    main_notes = []

    for note_class, count in sorted_classes:
        cumulative += count
        main_notes.append(note_class)
        if cumulative / total_notes > 0.4:
            break

    print(f"\nNote principali (top 40%): {[NOTE_NAMES[n] for n in main_notes]}")

    # Prova a identificare accordo
    # Gli style Yamaha sono di solito registrati in CM7 (C Maj7)
    # Cerca pattern di accordi comuni

    def check_chord_pattern(notes, root, pattern, name):
        """Controlla se le note corrispondono a un pattern di accordo"""
        expected = [(root + interval) % 12 for interval in pattern]
        matches = sum(1 for n in expected if n in notes)
        return matches, expected

    # Pattern comuni
    patterns = {
        'Maj': [0, 4, 7],           # C E G
        'Maj7': [0, 4, 7, 11],      # C E G B
        'min': [0, 3, 7],           # C Eb G
        'min7': [0, 3, 7, 10],      # C Eb G Bb
        '7': [0, 4, 7, 10],         # C E G Bb
    }

    print("\nProbabilità per accordo (root = C):")
    for chord_type, pattern in patterns.items():
        matches, expected = check_chord_pattern(main_notes, 0, pattern, chord_type)
        probability = (matches / len(pattern)) * 100
        expected_names = [NOTE_NAMES[n] for n in expected]
        print(f"  C{chord_type:6s}: {probability:5.1f}% - Note attese: {expected_names}")

    print("\n" + "=" * 80)

else:
    print("[ERRORE] Impossibile caricare il file")
