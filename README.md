# MIDI Arranger

Applicazione Python per arranger MIDI con supporto tastiera.

## Requisiti

- Python 3.8 o superiore
- Windows/Linux/macOS

## Installazione

1. Clona o scarica il repository
2. Crea un ambiente virtuale (già presente in `venv/`)
3. Attiva l'ambiente virtuale:
   - Windows: `venv\Scripts\activate`
   - Linux/macOS: `source venv/bin/activate`
4. Installa le dipendenze: `pip install -r requirements.txt`

## Sviluppo

### Struttura del progetto

```
midi-arranger/
├── src/                    # Codice sorgente
│   ├── __init__.py
│   └── midi_keyboard.py   # Visualizzatore tastiera MIDI GUI
├── tests/                 # Test unitari
│   ├── __init__.py
│   └── test_midi_keyboard.py
├── venv/                  # Ambiente virtuale
├── example.py             # Script di test base
├── requirements.txt       # Dipendenze
├── pyproject.toml        # Configurazione progetto
├── README.md             # Questo file
└── DEVELOPMENT.md        # Guida sviluppatori
```

### Dipendenze

- **mido**: Libreria per gestione MIDI in Python
- **python-rtmidi**: Backend real-time per MIDI I/O
- **packaging**: Utilities per packaging

### Eseguire i test

```bash
pytest tests/
```

## Uso

### Avvio dell'applicazione

```bash
python src/midi_keyboard.py
```

### Caratteristiche

Il visualizzatore offre:
- **Interfaccia grafica** con tastiera virtuale (tkinter)
- **88 tasti completi** come un pianoforte reale (da A0 a C8)
- **Proporzioni realistiche** - rapporto 6.5:1 come un pianoforte vero
- **Adattamento automatico** alle dimensioni dello schermo (90% larghezza)
- **Scrollbar orizzontale** per navigare facilmente tra i tasti
- **Finestra centrata** automaticamente sullo schermo
- **Selezione porta MIDI** tramite menu dropdown
- **Visualizzazione in tempo reale** delle note suonate
- **Tasti colorati** in base alla velocity della nota
- **Connessione/disconnessione** dinamica della porta MIDI
- **Ridimensionamento dinamico** - la tastiera si adatta quando ridimensioni la finestra
- **Etichette note** su tasti C e F per orientamento rapido

### Uso da codice Python

```python
from src.midi_keyboard import VirtualKeyboard
import tkinter as tk

# Crea finestra
root = tk.Tk()

# Crea applicazione
app = VirtualKeyboard(root)

# Avvia interfaccia
root.mainloop()
```

## Licenza

Da definire
