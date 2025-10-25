# -*- coding: utf-8 -*-
"""
Test per il modulo midi_keyboard.
"""

import pytest
from src.midi_keyboard import VirtualKeyboard


def test_example():
    """Test di esempio."""
    assert True


def test_mido_import():
    """Verifica che mido sia importabile."""
    import mido
    assert mido is not None


def test_rtmidi_backend():
    """Verifica che il backend rtmidi sia disponibile."""
    import mido
    import mido.backends.rtmidi
    assert mido.backends.rtmidi is not None


def test_virtual_keyboard_creation():
    """Verifica che si possa creare un'istanza di VirtualKeyboard."""
    import tkinter as tk
    root = tk.Tk()
    keyboard = VirtualKeyboard(root)

    assert keyboard is not None
    assert len(keyboard.active_notes) == 0

    root.destroy()


def test_virtual_keyboard_get_note_name():
    """Verifica il metodo get_note_name della VirtualKeyboard."""
    import tkinter as tk
    root = tk.Tk()
    keyboard = VirtualKeyboard(root)

    # Test note specifiche del pianoforte a 88 tasti
    assert keyboard.get_note_name(21) == "A0"   # Prima nota del pianoforte
    assert keyboard.get_note_name(60) == "C4"   # Middle C
    assert keyboard.get_note_name(69) == "A4"   # 440 Hz
    assert keyboard.get_note_name(108) == "C8"  # Ultima nota del pianoforte

    root.destroy()
