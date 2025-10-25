"""
Esempio di utilizzo del MIDI Arranger.
"""

import mido

def list_midi_ports():
    """Elenca tutte le porte MIDI disponibili."""
    print("Porte MIDI di input disponibili:")
    for port in mido.get_input_names():
        print(f"  - {port}")

    print("\nPorte MIDI di output disponibili:")
    for port in mido.get_output_names():
        print(f"  - {port}")

def main():
    print("=== MIDI Arranger - Test ===\n")
    list_midi_ports()

    print("\n[OK] Sistema MIDI funzionante!")
    print("[OK] Librerie installate correttamente")

if __name__ == "__main__":
    main()
