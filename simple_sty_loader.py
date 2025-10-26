#!/usr/bin/env python3
"""Parser semplificato per file .STY Yamaha usando mido"""

import mido
from pprint import pprint

sty_file = r'sty\stili_miei\Swing1.S733.sty'

print(f"Caricamento file: {sty_file}")
print("=" * 80)

try:
    # Leggi il file come MIDI standard
    mid = mido.MidiFile(sty_file)

    print(f"\n[OK] File MIDI caricato!")
    print(f"   Tipo: {mid.type}")
    print(f"   Ticks per beat: {mid.ticks_per_beat}")
    print(f"   Numero di tracce: {len(mid.tracks)}")

    # Analizza la prima traccia per trovare info sullo style
    print("\n[TRACCIA 0] - Header/Metadata:")
    print("-" * 80)

    sections_found = []
    style_name = None
    sff_version = None

    for i, msg in enumerate(mid.tracks[0][:30]):  # Prime 30 messaggi
        if msg.type == 'track_name':
            style_name = msg.name
            print(f"   Nome style: {msg.name}")
        elif msg.type == 'marker':
            print(f"   Marker: {msg.text}")
            if msg.text in ['Main A', 'Main B', 'Main C', 'Main D', 'Intro A', 'Intro B', 'Intro C',
                            'Ending A', 'Ending B', 'Ending C', 'Fill In AA', 'Fill In BB', 'Fill In CC', 'Fill In DD']:
                sections_found.append(msg.text)
        elif msg.type == 'text':
            if 'SFF' in msg.text:
                sff_version = msg.text
                print(f"   SFF Version: {msg.text}")
        elif msg.type == 'copyright':
            print(f"   Copyright: {msg.text}")
        elif msg.type == 'set_tempo':
            bpm = mido.tempo2bpm(msg.tempo)
            print(f"   Tempo: {bpm:.1f} BPM")
        elif msg.type == 'time_signature':
            print(f"   Time signature: {msg.numerator}/{msg.denominator}")

    # Cerca markers di sezione in tutte le tracce
    print("\n[SEZIONI STYLE] trovate:")
    print("-" * 80)

    all_sections = {}
    for track_idx, track in enumerate(mid.tracks):
        current_section = None
        section_start_time = 0
        absolute_time = 0

        for msg in track:
            absolute_time += msg.time

            if msg.type == 'marker':
                # Fine sezione precedente
                if current_section and current_section in ['Main A', 'Main B', 'Main C', 'Main D',
                                                            'Intro A', 'Intro B', 'Intro C',
                                                            'Ending A', 'Ending B', 'Ending C',
                                                            'Fill In AA', 'Fill In BB', 'Fill In CC', 'Fill In DD']:
                    if current_section not in all_sections:
                        all_sections[current_section] = {
                            'start': section_start_time,
                            'end': absolute_time,
                            'length_ticks': absolute_time - section_start_time,
                            'tracks': []
                        }
                    if track_idx not in all_sections[current_section]['tracks']:
                        all_sections[current_section]['tracks'].append(track_idx)

                # Nuova sezione
                if msg.text in ['Main A', 'Main B', 'Main C', 'Main D',
                                'Intro A', 'Intro B', 'Intro C',
                                'Ending A', 'Ending B', 'Ending C',
                                'Fill In AA', 'Fill In BB', 'Fill In CC', 'Fill In DD']:
                    current_section = msg.text
                    section_start_time = absolute_time

    for section_name, info in sorted(all_sections.items()):
        beats = info['length_ticks'] / mid.ticks_per_beat
        print(f"   • {section_name:15s} - {beats:5.1f} battute ({info['length_ticks']:6d} ticks) - {len(info['tracks'])} tracce")

    print("\n[OK] Analisi completata!")

except Exception as e:
    print(f"\n[ERRORE] {e}")
    import traceback
    traceback.print_exc()
