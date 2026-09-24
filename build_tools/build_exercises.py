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
import ex_tail
import ex_spec

for module in (ex_p01a, ex_p01b, ex_p02):
    module.build()
# The bundle order is the order Practice lists them in, so p04's warm-ups go
# in ahead of its own exercises.
ex_tail.build_warmups()
for module in (ex_p04, ex_p05, ex_mid, ex_late, ex_tail, ex_spec):
    module.build()

OUT = Path(__file__).resolve().parent.parent / "src" / "operators_console" / "data" / "exercises.json"
ex_lib.dump(OUT)
print("wrote", OUT)
