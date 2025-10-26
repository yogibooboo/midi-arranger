#!/usr/bin/env python3
"""Verifica quale accordo base è registrato nello style"""

import sys
sys.path.insert(0, 'src')

from style_player import StylePlayer

sty_file = r'sty\stili_miei\Swing1.S733.sty'
player = StylePlayer()

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

if player.load_style(sty_file):
    section = player.sections['Main A']
    events = section['events']

    # Raccogli solo le classi di note (senza ottava)
    note_classes = set()

    for event in events:
        if event.type == 'note_on' and event.velocity > 0:
            note_class = event.note % 12
            note_classes.add(note_class)

    # Converti in nomi
    notes = sorted([NOTE_NAMES[n] for n in sorted(note_classes)])

    print("=" * 60)
    print(f"ACCORDO BASE REGISTRATO NELLO STYLE")
    print("=" * 60)
    print(f"\nNote suonate (senza ottava): {notes}")

    # Identifica pattern
    nc = sorted(note_classes)

    print(f"\nNote MIDI (classi): {nc}")
    print(f"\nInterpretazione:")

    # C Maj7 = C(0), E(4), G(7), B(11)
    if 0 in nc and 4 in nc and 7 in nc:
        if 11 in nc:
            print("  -> Accordo BASE: C Major 7 (CM7)")
            print("     Note: C - E - G - B")
        else:
            print("  -> Accordo BASE: C Major (C)")
            print("     Note: C - E - G")

    print("\n" + "=" * 60)
    print("CONCLUSIONE:")
    print("=" * 60)
    print("\nLo style sta suonando l'accordo di RIFERIMENTO")
    print("registrato nel file (probabilmente CM7 o C).")
    print("\nSenza chord recognition, suona sempre lo stesso accordo.")
    print("Per cambiare accordo serve implementare:")
    print("  1. Riconoscimento accordi dal MIDI input")
    print("  2. Trasposizione delle note in base all'accordo")
    print("=" * 60)
