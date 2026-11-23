"""Pone la raiz del repo en sys.path para poder importar `app`."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
