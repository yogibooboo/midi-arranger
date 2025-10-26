#!/usr/bin/env python3
"""Test script per analizzare file .STY Yamaha"""

import sys
sys.path.insert(0, 'sff2-tools-repo')

from style_codec import Style
from pprint import pprint

# Test con uno dei tuoi file .STY
sty_file = r'sty\stili_miei\Swing1.S733.sty'

print(f"Caricamento file: {sty_file}")
print("-" * 80)

try:
    # Carica lo style file
    style = Style.fromSty(sty_file)

    print("\n📋 SEZIONI DISPONIBILI:")
    print("-" * 80)
    for section_name in style.trackSections.keys():
        section = style.trackSections[section_name]
        if section_name not in ['Prologue', 'SInt', 'Epilogue']:
            length_beats = section['length'] / 1920  # beatResolution = 1920
            channels = [ch for ch in section['channels'].keys() if ch != 'common']
            print(f"  • {section_name:15s} - {length_beats:5.1f} battute - {len(channels)} canali")

    print("\n🎵 DETTAGLI CASM (Chord Assign Memory):")
    print("-" * 80)

    # Mostra info CASM per Main A come esempio
    if 'Main A' in style.casm:
        print("\nMain A - Configurazione canali:")
        for channel, config in style.casm['Main A'].items():
            if config['type'] == 'ctb2':
                ntt_rule = config['middle']['ntt']['rule']
                is_bass = config['middle']['ntt']['bass']
                print(f"  Canale {channel:2d}: {config['name']:20s} - NTT: {ntt_rule:15s} Bass: {is_bass}")

    print("\n✅ File caricato con successo!")
    print(f"   Totale sezioni: {len([s for s in style.trackSections.keys() if s not in ['Prologue', 'SInt', 'Epilogue']])}")

except Exception as e:
    print(f"\n❌ Errore durante il caricamento: {e}")
    import traceback
    traceback.print_exc()
