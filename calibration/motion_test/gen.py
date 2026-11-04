import math
L=["; IVI3D motion test: head circles above bed, no heat, no extrusion","G53","G90","M82","G28","G1 Z30 F3000","G1 X0 Y0 F3000"]
for r,z,f in [(20,30,1800),(40,30,3000),(60,25,4200),(70,25,4800),(40,20,6000)]:
  for lap in range(3):
    for i in range(0,73):
      a=2*math.pi*i/72; L.append(f"G1 X{r*math.cos(a):.2f} Y{r*math.sin(a):.2f} Z{z} F{f}")
  L.append(f"G1 X0 Y0 F{f}")
L+=["G1 Z60 F3000","G28","M84","; end"]
open("IVI3D_circle_test.gcode","w").write("\n".join(L)+"\n")
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as p
xs=[];ys=[]
for l in L:
  if l.startswith("G1 X"): t=l.split(); xs.append(float(t[1][1:])); ys.append(float(t[2][1:]))
fig,ax=p.subplots(figsize=(5,5)); ax.plot(xs,ys,lw=.6); ax.add_patch(p.Circle((0,0),100,fill=False,ls="--",color="gray")); ax.set_aspect(1); ax.set_title("Circle test (dashed = bed edge, r100)"); fig.savefig("preview.png",dpi=110)
print(len(L))
