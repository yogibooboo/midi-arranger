#!/usr/bin/env python3
"""Test del ChordRecognizer"""

import sys
sys.path.insert(0, 'src')

from chord_recognizer import ChordRecognizer

print("=" * 80)
print("TEST CHORD RECOGNIZER")
print("=" * 80)

recognizer = ChordRecognizer()

# Test vari accordi
test_chords = [
    ("C Maggiore", [60, 64, 67]),          # C E G
    ("Dm (Re minore)", [62, 65, 69]),      # D F A
    ("G7 (Sol dominante)", [67, 71, 74, 77]),  # G B D F
    ("Am7 (La min 7)", [69, 72, 76, 79]),  # A C E G
    ("F Maggiore", [65, 69, 72]),          # F A C
    ("E minore", [64, 67, 71]),            # E G B
]

for name, notes in test_chords:
    print(f"\n[TEST] {name}")
    print(f"  Note MIDI: {notes}")

    # Simula note_on
    for note in notes:
        recognizer.note_on(note)

    # Leggi accordo riconosciuto
    chord = recognizer.get_current_chord()
    chord_name = recognizer.get_chord_name()

    if chord:
        print(f"  Riconosciuto: {chord_name}")
        print(f"  Root: {chord['root_name']}")
        print(f"  Tipo: {chord['type']}")
        print(f"  Confidenza: {chord['confidence']:.2f}")
        print(f"  Note filtro: {sorted(recognizer.get_notes_for_transposition())}")
    else:
        print("  Nessun accordo riconosciuto")

    # Clear per prossimo test
    recognizer.clear()

print("\n" + "=" * 80)
print("Test completato!")
print("=" * 80)
