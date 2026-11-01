#!/usr/bin/env python3
"""Assemble ivi3d_laser.cps / ivi3d_cnc.cps from *.src.js + _common.js (Fusion needs single files)."""
import os
d = os.path.dirname(os.path.abspath(__file__))
common = open(os.path.join(d, "_common.js")).read()
for src, dst in (("laser.src.js", "ivi3d_laser.cps"), ("cnc.src.js", "ivi3d_cnc.cps")):
    s = open(os.path.join(d, src)).read().replace("//@@COMMON@@", common)
    open(os.path.join(d, dst), "w").write(s)
    print("wrote", dst)
