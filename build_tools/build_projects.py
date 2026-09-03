from pathlib import Path

import proj_lib
import proj_a
import proj_b
import proj_c

for module in (proj_a, proj_b, proj_c):
    module.build()

OUT = (Path(__file__).resolve().parent.parent / "src" / "operators_console" /
       "data" / "projects.json")
proj_lib.dump(OUT)
print("wrote", OUT)
