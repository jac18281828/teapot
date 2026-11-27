"""Build a part's glaze shell: its geometry pushed out along the vertex normals by THICKNESS.

usage: python3 -I tools/glaze.py THICKNESS IN.rib OUT.rib

IN is a geo/ master, one PointsPolygons with "P", "N" and "st". OUT keeps the faces, the winding
and the normals, so the shell's outside faces the same way as the part's.
"""

import re
import sys

import numpy as np


def arrays(text):
    head, _, body = text.partition("PointsPolygons")
    fields = re.findall(r'(?:"(\w+)"\s*)?\[([^\]]*)\]', body)
    return head, fields


def main():
    thickness = float(sys.argv[1])
    with open(sys.argv[2]) as f:
        _, fields = arrays(f.read())
    nverts, indices = fields[0][1], fields[1][1]
    named = {name: np.array(values.split(), dtype=np.float64) for name, values in fields[2:]}
    p = named["P"].reshape(-1, 3)
    n = named["N"].reshape(-1, 3)
    shell = p + thickness * n / np.linalg.norm(n, axis=1, keepdims=True)
    fmt = lambda a: " ".join(f"{v:.6g}" for v in a.ravel())
    with open(sys.argv[3], "w") as f:
        f.write(f"## glaze shell, {thickness} out along N, from {sys.argv[2]}\n")
        f.write(f'PointsPolygons [{nverts}] [{indices}]\n  "P" [{fmt(shell)}]\n  "N" [{fmt(n)}]\n')


if __name__ == "__main__":
    main()
