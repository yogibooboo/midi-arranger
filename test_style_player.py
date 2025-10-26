#!/usr/bin/env python3
"""Test della classe StylePlayer"""

import sys
sys.path.insert(0, 'src')

from style_player import StylePlayer
import mido

# Test del caricamento
print("=" * 80)
print("TEST STYLE PLAYER")
print("=" * 80)

player = StylePlayer()

# Carica uno style
sty_file = r'sty\stili_miei\Swing1.S733.sty'
print(f"\n[1] Caricamento file: {sty_file}")

if player.load_style(sty_file):
    print("    [OK] File caricato!")

    # Mostra info style
    info = player.get_style_info()
    print(f"\n[2] Info Style:")
    print(f"    Nome: {info['name']}")
    print(f"    Tempo: {info['tempo']:.1f} BPM")
    print(f"    Sezioni trovate: {info['sections']}")

    # Lista sezioni
    print(f"\n[3] Sezioni disponibili:")
    for section in info['section_list']:
        section_info = player.get_section_info(section)
        print(f"    - {section:15s}: {section_info['beats']:5.1f} battute, "
              f"{section_info['num_events']:4d} eventi")

    # Test lista porte MIDI
    print(f"\n[4] Porte MIDI disponibili:")
    output_ports = mido.get_output_names()
    for idx, port in enumerate(output_ports):
        print(f"    [{idx}] {port}")

    # Chiedi all'utente se vuole testare il playback
    print(f"\n[5] Test Playback:")
    print("    Per testare il playback, decommentare il codice seguente")
    print("    e impostare la porta MIDI corretta.\n")

    # DECOMMENTARE PER TESTARE IL PLAYBACK:
    # if output_ports:
    #     # Apri la prima porta disponibile
    #     midi_out = mido.open_output(output_ports[0])
    #     player.set_midi_output(midi_out)
    #
    #     print(f"    Suono 'Main A' per 10 secondi...")
    #     player.play_section('Main A', loop=True)
    #
    #     import time
    #     time.sleep(10)
    #
    #     player.stop()
    #     print("    [OK] Playback fermato")
    #
    #     midi_out.close()

else:
    print("    [ERRORE] Impossibile caricare il file")

print("\n" + "=" * 80)
print("Test completato!")
print("=" * 80)
