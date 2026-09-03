"""Assemble every authored exercise into the shipped bank."""
from pathlib import Path

import ex_lib
import ex_p01a
import ex_p01b
import ex_p02
import ex_p04
import ex_p05
import ex_mid
import ex_late

for module in (ex_p01a, ex_p01b, ex_p02, ex_p04, ex_p05, ex_mid, ex_late):
    module.build()

OUT = Path(__file__).resolve().parent.parent / "src" / "operators_console" / "data" / "exercises.json"
ex_lib.dump(OUT)
print("wrote", OUT)
