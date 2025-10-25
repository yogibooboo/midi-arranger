# Guida allo sviluppo - MIDI Arranger

Questa guida ti aiutera' a iniziare lo sviluppo sul progetto MIDI Arranger.

## Setup iniziale

### 1. Attivare l'ambiente virtuale

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/macOS:**
```bash
source venv/bin/activate
```

### 2. Verificare l'installazione

```bash
python example.py
```

Dovresti vedere le porte MIDI disponibili nel tuo sistema.

## Struttura del progetto

```
midi-arranger/
├── src/                       # Codice sorgente
│   ├── __init__.py           # Package marker
│   └── midi_keyboard.py      # Modulo principale
├── tests/                    # Test unitari
│   ├── __init__.py
│   └── test_midi_keyboard.py
├── example.py                # Script di esempio
├── requirements.txt          # Dipendenze Python
├── pyproject.toml           # Configurazione progetto
└── README.md                # Documentazione principale
```

## Classi principali

### MidiKeyboard

Gestisce l'interfaccia con le porte MIDI fisiche.

```python
from src.midi_keyboard import MidiKeyboard

# Crea istanza
keyboard = MidiKeyboard()

# Apri porte MIDI
keyboard.open()

# Ascolta messaggi
def on_message(msg):
    print(f"Ricevuto: {msg}")

keyboard.listen(on_message)

# Chiudi porte
keyboard.close()
```

### MidiArranger

Aggiunge funzionalita' di registrazione e riproduzione.

```python
from src.midi_keyboard import MidiKeyboard, MidiArranger

keyboard = MidiKeyboard()
keyboard.open()

arranger = MidiArranger(keyboard)

# Registra
arranger.start_recording()
keyboard.listen(arranger.handle_message)
arranger.stop_recording()

# Riproduci
arranger.playback()

keyboard.close()
```

## Testing

### Eseguire i test

```bash
pytest tests/
```

### Con coverage

```bash
pytest tests/ --cov=src --cov-report=html
```

Il report HTML sara' disponibile in `htmlcov/index.html`.

### Eseguire test specifici

```bash
# Test singolo file
pytest tests/test_midi_keyboard.py

# Test singola funzione
pytest tests/test_midi_keyboard.py::test_midi_keyboard_creation
```

## Dipendenze

### Produzione

- **mido**: Libreria Python per lavorare con MIDI
- **python-rtmidi**: Backend real-time per I/O MIDI
- **packaging**: Utilities per gestione versioni

### Sviluppo

- **pytest**: Framework di testing
- **pytest-cov**: Plugin per coverage dei test

## Best practices

### 1. Encoding dei file

Tutti i file Python devono iniziare con:

```python
# -*- coding: utf-8 -*-
```

### 2. Docstrings

Usa docstrings in stile Google:

```python
def funzione(parametro):
    """
    Breve descrizione.

    Args:
        parametro: Descrizione del parametro.

    Returns:
        Descrizione del valore di ritorno.

    Raises:
        ErrorType: Quando si verifica l'errore.
    """
    pass
```

### 3. Type hints

Usa type hints quando possibile:

```python
from typing import List, Optional

def funzione(nome: str, eta: Optional[int] = None) -> List[str]:
    return [nome, str(eta)]
```

### 4. Testing

- Scrivi test per ogni nuova funzionalita'
- Mantieni la coverage sopra l'80%
- Testa casi limite e gestione errori

## Comandi utili

```bash
# Aggiornare le dipendenze
pip install --upgrade -r requirements.txt

# Aggiungere una nuova dipendenza
pip install nuova-libreria
pip freeze > requirements.txt

# Controllare la sintassi
python -m py_compile src/midi_keyboard.py

# Vedere le porte MIDI disponibili
python -c "import mido; print(mido.get_input_names())"
```

## Debug

### Logging dei messaggi MIDI

```python
import mido

# Stampa tutti i messaggi
with mido.open_input() as port:
    for msg in port:
        print(msg)
```

### Test manuale delle porte

```python
# Lista porte
print("Input:", mido.get_input_names())
print("Output:", mido.get_output_names())

# Apri porta specifica
with mido.open_input('nome-porta') as port:
    for msg in port:
        print(msg)
```

## Prossimi passi

1. Implementare salvataggio/caricamento pattern MIDI
2. Aggiungere supporto per MIDI clock/sync
3. Creare interfaccia grafica (GUI)
4. Supporto per effetti MIDI (transpose, velocity curve, ecc.)
5. Gestione multi-traccia

## Risorse

- [Documentazione Mido](https://mido.readthedocs.io/)
- [MIDI Specification](https://www.midi.org/specifications)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [pytest Documentation](https://docs.pytest.org/)
