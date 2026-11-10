import pickle,struct,sys,json,os
sys.path.insert(0,'.')
from regmap import name as rname
import io,contextlib
with contextlib.redirect_stdout(io.StringIO()):
    from rda import VEC,NV,w,d,BASE,END
P=pickle.load(open('rda.pkl','rb'))
code,lits,funcs,gaps=P['code'],P['lits'],P['funcs'],P['gaps']
NAMES=json.load(open('names.json')) if os.path.exists('names.json') else {}
NAMES={int(k,16):v for k,v in NAMES.items()}
COMMENTS=json.load(open('comments.json')) if os.path.exists('comments.json') else {}
COMMENTS={int(k,16):v for k,v in COMMENTS.items()}
def fn(a): return NAMES.get(a,{}).get('name','sub_%08x'%a) if isinstance(NAMES.get(a),dict) else NAMES.get(a,'sub_%08x'%a)
EXTRA={0x08001118:'scatter-load region table start',0x08001138:'scatter-load region table end',0x40012438:'ADC+0x38 (ADC_ISQ in GD32 SPL headers; not documented in this manual rev; dead branch)',0x40012424:'ADC_WDHT'}
def annot_val(v):
    n=EXTRA.get(v) or rname(v)
    if n: return n
    SV={0x20000000:'g_SystemCoreClock (.data, init 72000000)',0x20000004:'g_btn_last (.data, init 1)',0x20000008:'g_delay_ms (.bss)',0x2000000c:'g_press_tick (.bss)',0x20000010:'g_blink_count (.bss)',0x20000014:'g_mode (.bss, write-only)',0x20000018:'g_tick_ms (.bss)',0x20000420:'initial SP / top of 0x400 stack'}
    if v in SV: return 'SRAM '+SV[v]
    if 0x20000000<=v<0x20001000: return 'SRAM var'
    if BASE<=v<BASE+END: 
        if v&1 and (v&~1) in funcs: return 'code ptr -> '+fn(v&~1)
        return 'flash addr'
    return None
out=[]
out.append('; GD32E230F4 flash image, base 0x08000000, SHA256 540f4967976e390a5a1822347a148b332ee3da78329d03e1880c851ab17f0167')
out.append('; Recursive-descent disassembly (Capstone 5, Thumb, M-class, ARMv8-M Baseline). Register names from GD32E23x User Manual;')
out.append('; Cortex-M23 SCS names (SysTick/NVIC/SCB) from ARMv8-M architecture.')
out.append('')
out.append('; ===== SECTION: VECTOR TABLE 0x08000000-0x080000CB (%d entries) ====='%NV)
for i in range(NV):
    v=w(BASE+4*i)
    t='' if i==0 else ('(unused/0)' if v==0 else '-> '+fn(v&~1))
    out.append('%08x: .word 0x%08x   ; [%2d] %-24s %s'%(BASE+4*i,v,i,VEC[i],t))
out.append('')
out.append('; ===== SECTION: CODE / LITERAL POOLS 0x080000CC-0x08001117 =====')
a=BASE+4*NV
regtab=0x08001118
while a<regtab:
    if a in funcs:
        out.append('')
        out.append('; ---------------------------------------------------------------')
        out.append('; FUNCTION %s @ 0x%08x   refs: %s'%(fn(a),a,', '.join(funcs[a][:6])+(' ...' if len(funcs[a])>6 else '')))
        if a in NAMES and isinstance(NAMES[a],dict) and NAMES[a].get('role'): out.append(';   role: '+NAMES[a]['role'])
        out.append('; ---------------------------------------------------------------')
    if a in code and a not in lits:
        sz,m,op,b=code[a]
        c=''
        if m.startswith('ldr') and '[pc' in op:
            la=((a+4)&~3)+int(op.split('#')[1].rstrip(']'),16) if '#' in op else ((a+4)&~3)
            v=w(la); n=annot_val(v)
            c='=0x%08x'%v+(' '+n if n else '')
        if m in('bl',) or (m.startswith('b') and op.startswith('#') and m not in('bics','bic')):
            t=int(op[1:],16)
            if t in funcs: c=fn(t)
        if a in COMMENTS: c=(c+' | ' if c else '')+COMMENTS[a]
        out.append('%08x: %-9s %-8s %-28s%s'%(a,b.hex(),m,op,('; '+c) if c else ''))
        a+=sz
    elif a in lits:
        sz,ref=lits[a]
        if sz==4:
            v=w(a); n=annot_val(v)
            refs=sorted(x for x,(sz2,m2,op2,b2) in code.items() if m2.startswith('ldr') and '[pc' in op2 and (((x+4)&~3)+(int(op2.split('#')[1].rstrip(']'),16) if '#' in op2 else 0))==a)
            out.append('%08x: .word 0x%08x            ; LITERAL (ref by %s)%s'%(a,v,','.join('%08x'%r for r in refs),' '+n if n else ''))
        else:
            out.append('%08x: .%s literal'%(a,sz))
        a+=sz
    else:
        b=d[a-BASE:a-BASE+2]
        lab={b'\xc0\x46':'nop (mov r8,r8) alignment padding',b'\x00\x00':'zero padding',b'\xfe\xe7':'b . (unreferenced default-handler stub)',b'\x70\x47':'bx lr (unreferenced)'}.get(b,'data')
        out.append('%08x: %-9s .hword               ; %s'%(a,b.hex(),lab))
        a+=2
out.append('')
out.append('; ===== SECTION: ARM scatter-load region table 0x08001118-0x08001137 =====')
for r in range(2):
    e=[w(regtab+16*r+4*k) for k in range(4)]
    out.append('%08x: .word 0x%08x,0x%08x,0x%08x,0x%08x ; src=%08x dst=%08x len=0x%x handler=%s'%(regtab+16*r,*e,e[0],e[1],e[2],fn(e[3]&~1)))
out.append('')
out.append('; ===== SECTION: .data initial values 0x08001138-0x0800113F (copied to 0x20000000) =====')
out.append('08001138: .word 0x%08x   ; -> 0x20000000 = %d (72 MHz; matches GD32 SystemCoreClock)'%(w(0x08001138),w(0x08001138)))
out.append('0800113c: .word 0x%08x   ; -> 0x20000004'%w(0x0800113c))
out.append('')
out.append('; ===== 0x08001140-0x08003FFF: all 0xFF (erased), 11968 bytes =====')
open('../gd32e230_annotated.s','w').write('\n'.join(out)+'\n')
