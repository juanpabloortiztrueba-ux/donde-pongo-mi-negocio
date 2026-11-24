"""Pone la raiz del repo en sys.path para poder importar `app`."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# las pruebas no ensucian el registro local de preguntas del tablero (data/historial/preguntas.jsonl)
import os  # noqa: E402

os.environ["DONDE_SIN_HISTORIAL"] = "1"
