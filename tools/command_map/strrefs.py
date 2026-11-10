#!/usr/bin/env python3
"""Resolve PC-relative string references in app.elf (ARM, PIC: ldr rY,[pc,#L]; add rX,pc,rY) and map them to functions.
Offline, read-only. Output TSV: func_addr func_name ref_addr string"""
import os, re, struct, bisect, sys, capstone
ELF=os.environ.get('IVI_APP_ELF','firmware/Firmware/firmware')
FNSTR=os.environ.get('IVI_FNSTR','')
if not FNSTR:
    sys.exit('set IVI_FNSTR to a Ghidra function list (not published in this repo)')
d=open(ELF,'rb').read(); BASE=0x8000; TEXT_END=0xa6208+BASE
md=capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_ARM)
funcs=[]
for l in open(FNSTR):
    m=re.match(r'== ([0-9a-f]+) (.*)',l)
    if m: funcs.append((int(m.group(1),16),m.group(2).strip()))
funcs.sort(); fa=[f[0] for f in funcs]
def fn(a):
    i=bisect.bisect_right(fa,a)-1; return funcs[i] if i>=0 else (0,'?')
def cstr(a):
    o=a-BASE
    if not (0<=o<len(d)): return None
    e=d.find(b'\0',o)
    if e<0 or e-o>300: return None
    s=d[o:e]
    try: s=s.decode('utf-8')
    except: return None
    return s if s and all(c.isprintable() or c in '\n\r\t' for c in s) else None
ins={}
for off in range(0x5000, TEXT_END-BASE, 4):
    for i in md.disasm(d[off:off+4], off+BASE): ins[i.address]=i
lit={}  # (addr,reg)->literal value
out=[]
addrs=sorted(ins)
for a in addrs:
    i=ins[a]
    m=re.match(r'(r\d+|sb|sl|fp|ip|lr), \[pc, #(-?0x[0-9a-f]+|\d+)\]$', i.op_str) if i.mnemonic=='ldr' else None
    if m:
        la=a+8+int(m.group(2),0)
        if BASE<=la<BASE+len(d)-3: lit[m.group(1)]=(a,struct.unpack_from('<I',d,la-BASE)[0])
        continue
    m=re.match(r'(r\d+|sb|sl|fp|ip|lr), pc, (r\d+|sb|sl|fp|ip|lr)$', i.op_str) if i.mnemonic=='add' else None
    if m and m.group(2) in lit and a-lit[m.group(2)][0] < 400:
        t=(a+8+lit[m.group(2)][1])&0xffffffff
        s=cstr(t)
        if s is not None:
            f=fn(a); out.append((f[0],f[1],a,s))
for f0,f1,a,s in out:
    print("%08x\t%s\t%08x\t%s"%(f0,f1,a,s.replace('\n','\\n').replace('\t','\\t')))
