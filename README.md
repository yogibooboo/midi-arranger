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

### Come usare

**Connessione automatica:**
- All'avvio, l'app si connette automaticamente alla prima porta Input e Output disponibile
- Lo stato viene mostrato sotto ogni menu dropdown (verde = connesso, arancione = non connesso)

**Cambiare porta MIDI:**
- Seleziona una porta diversa dal menu dropdown **MIDI Input** o **MIDI Output**
- La connessione si aggiorna automaticamente senza bisogno di disconnettere

**Cambiare canale MIDI:**
- Scegli il canale (1-16) dal menu dropdown **Canale**
- Le nuove note verranno inviate sul canale selezionato

**Cambiare strumento (General MIDI):**
- Seleziona uno strumento dal menu dropdown **Strumento** (128 strumenti General MIDI)
- L'applicazione invierà un messaggio Program Change al dispositivo output
- Gli strumenti vanno da pianoforte, chitarra, archi, ottoni, sintetizzatori e molto altro
- Compatibile con dispositivi che supportano lo standard General MIDI (es. Microsoft GS Wavetable Synth)

**Ricevere note (visualizzazione):**
- Suona sulla tua tastiera MIDI fisica
- I tasti si illumineranno sulla tastiera virtuale in tempo reale

**Inviare note (suonare):**
- Clicca sui tasti della tastiera virtuale con il mouse
- Le note verranno inviate al dispositivo Output sul canale selezionato
- Rilascia il mouse per fermare la nota

**Modalità simultanea:**
- Input e Output funzionano contemporaneamente
- Esempio: ricevi note da una tastiera fisica E suoni con il mouse verso Cubase

### Caratteristiche

Il visualizzatore offre:

**Visualizzazione:**
- **Interfaccia grafica** con tastiera virtuale (tkinter)
- **88 tasti completi** come un pianoforte reale (da A0 a C8)
- **Proporzioni realistiche** - rapporto 6.5:1 come un pianoforte vero
- **Adattamento automatico** alle dimensioni dello schermo (90% larghezza)
- **Scrollbar orizzontale** per navigare facilmente tra i tasti
- **Finestra centrata** automaticamente sullo schermo
- **Ridimensionamento dinamico** - la tastiera si adatta quando ridimensioni la finestra
- **Etichette note** su tasti C e F per orientamento rapido

**MIDI Input (ricevere note):**
- **Selezione porta MIDI Input** tramite menu dropdown
- **Visualizzazione in tempo reale** delle note suonate
- **Tasti colorati** in base alla velocity della nota
- **Connessione/disconnessione** dinamica della porta MIDI

**MIDI Output (suonare):**
- **Selezione porta MIDI Output** tramite menu dropdown
- **Scelta canale MIDI** (1-16) per multi-timbral playback
- **Selezione strumento** (128 program General MIDI) con Program Change automatico
- **Tasti cliccabili** - suona note cliccando sui tasti con il mouse
- **Invio messaggi MIDI** a dispositivi esterni (synth, DAW, ecc.)
- **Note-on al clic** e **note-off al rilascio** del mouse

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
