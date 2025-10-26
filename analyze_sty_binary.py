#!/usr/bin/env python3
"""Analizza la struttura binaria di un file .STY Yamaha"""

import struct

sty_file = r'sty\stili_miei\Swing1.S733.sty'

print(f"Analisi file: {sty_file}")
print("=" * 80)

with open(sty_file, 'rb') as f:
    # Leggi i primi 512 bytes per vedere l'header
    data = f.read(512)

    print(f"\nDimensione file: {len(data)} bytes (primi 512)")
    print("\nPrimi 80 bytes (hex):")
    print(" ".join(f"{b:02X}" for b in data[:80]))

    print("\n\nPrimi 80 bytes (ASCII, punti per non-stampabili):")
    ascii_str = "".join(chr(b) if 32 <= b < 127 else '.' for b in data[:80])
    print(ascii_str)

    # Cerca RIFF header
    if data[:4] == b'RIFF':
        print("\n✅ File format: RIFF")
        file_size = struct.unpack('<I', data[4:8])[0]
        file_type = data[8:12]
        print(f"   File size (header): {file_size} bytes")
        print(f"   File type: {file_type}")

        # Cerca chunks
        pos = 12
        print("\n📦 CHUNKS trovati:")
        while pos < len(data) - 8:
            chunk_id = data[pos:pos+4]
            if len(chunk_id) < 4:
                break
            chunk_size = struct.unpack('<I', data[pos+4:pos+8])[0]
            print(f"   • {chunk_id.decode('latin1', errors='ignore'):4s} - size: {chunk_size:8d} bytes @ offset {pos}")
            pos += 8 + chunk_size
            if pos >= len(data):
                print(f"     (continua oltre i primi 512 bytes...)")
                break
    else:
        print(f"\n❓ Unknown format: {data[:4]}")

print("\n" + "=" * 80)

# Leggi tutto il file e cerca pattern
with open(sty_file, 'rb') as f:
    full_data = f.read()

print(f"\nDimensione totale file: {len(full_data)} bytes")

# Cerca stringhe interessanti
search_strings = [b'Main A', b'Main B', b'Intro', b'Ending', b'Fill', b'CASM', b'Sdec']
print("\n🔍 Stringhe trovate:")
for s in search_strings:
    positions = []
    pos = 0
    while True:
        pos = full_data.find(s, pos)
        if pos == -1:
            break
        positions.append(pos)
        pos += 1
    if positions:
        print(f"   • '{s.decode('latin1')}' trovato {len(positions)} volte a offset: {positions[:5]}{'...' if len(positions) > 5 else ''}")
