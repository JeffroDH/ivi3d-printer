import os
import capstone,struct,sys,json
from capstone import arm
sys.path.insert(0,'.')
from regmap import name as rname
BIN=os.environ.get('GD32_BIN','')
if not BIN:
    sys.exit('set GD32_BIN to the 16 KiB flash image (not published in this repo)')
d=open(BIN,'rb').read(); BASE=0x08000000; END=0x1140
md=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_THUMB|capstone.CS_MODE_MCLASS|capstone.CS_MODE_V8)
md.detail=True
def w(a): return struct.unpack_from('<I',d,a-BASE)[0]
VEC=['Initial_SP','Reset','NMI','HardFault']+['Reserved']*7+['SVCall','Reserved','Reserved','PendSV','SysTick']
irq=['WWDGT','LVD','RTC','FMC','RCU','EXTI0_1','EXTI2_3','EXTI4_15','Reserved','DMA_CH0','DMA_CH1_2','DMA_CH3_4','ADC_CMP','TIMER0_BRK_UP_TRG_COM','TIMER0_Channel','Reserved','TIMER2','TIMER5','Reserved','TIMER13','TIMER14','TIMER15','TIMER16','I2C0_EV','I2C1_EV','SPI0','SPI1','USART0','USART1','Reserved','Reserved','Reserved','I2C0_ER','Reserved','I2C1_ER']
VEC+= [x+'_IRQ' if x!='Reserved' else x for x in irq]
NV=len(VEC); VEND=BASE+4*NV
code={}   # addr->insn
lits={}   # addr->(size,referer)
funcs={}  # addr->set of sources
todo=[]
def addf(a,src):
    a&=~1
    funcs.setdefault(a,set()).add(src); todo.append(a)
for extra in (0x080010f8,0x08001108): addf(extra,'scatter-load region table @0x08001118/0x08001128')
for i in range(1,NV):
    v=w(BASE+4*i)
    if v: addf(v,'vector:'+VEC[i])
xrefs={}
NORET={0x080000d4,0x080000fc}  # __rt_entry/__scatterload tail: never return (bx to main)
while todo:
    a=todo.pop()
    while a not in code and BASE<=a<BASE+END:
        ins=next(md.disasm(d[a-BASE:a-BASE+4],a),None)
        if ins is None: print('BAD',hex(a)); break
        code[a]=ins
        m=ins.mnemonic; ops=ins.operands
        nxt=a+ins.size
        # literal loads
        if m.startswith('ldr') and len(ops)==2 and ops[1].type==arm.ARM_OP_MEM and ops[1].mem.base==arm.ARM_REG_PC:
            la=((a+4)&~3)+ops[1].mem.disp
            sz={'ldr':4,'ldrh':2,'ldrb':1}.get(m.split('.')[0],4)
            lits[la]=(sz,a)
            if sz==4:
                v=w(la)
                if BASE<v<BASE+END and v&1 and m=='ldr':
                    # possible code pointer
                    xrefs.setdefault(v&~1,[]).append(a)
        if m=='adr' or (m=='add' and len(ops)==3 and ops[1].reg==arm.ARM_REG_PC):
            pass
        if m in ('bl','b') or m.startswith('b') and ops and ops[0].type==arm.ARM_OP_IMM and m not in('bic','bics','bkpt'):
            t=ops[0].imm
            if m=='bl': addf(t,'bl@%x'%a)
            else: todo.append(t)
            xrefs.setdefault(t,[]).append(a)
            if m=='b' or (m=='bl' and t in NORET): break
        elif m in('cbz','cbnz'):
            todo.append(ops[1].imm)
        if m=='bx' or (m=='pop' and any(o.reg==arm.ARM_REG_PC for o in ops)) or (m=='mov' and ops[0].reg==arm.ARM_REG_PC):
            break
        if m=='blx' : pass
        a=nxt
# code pointers in literals: follow them as functions
changed=True
while changed:
    changed=False
    for la,(sz,ref) in list(lits.items()):
        if sz==4:
            v=w(la)
            if BASE+VEND-BASE<=v<BASE+END and v&1 and (v&~1) not in code:
                addf(v,'literal@%x'%la); changed=True
    while todo:
        a=todo.pop()
        # reuse loop: crude re-run
        stack=[a]
        while stack:
            a=stack.pop()
            while a not in code and BASE<=a<BASE+END:
                ins=next(md.disasm(d[a-BASE:a-BASE+4],a),None)
                if ins is None: break
                code[a]=ins; m=ins.mnemonic; ops=ins.operands
                if m.startswith('ldr') and len(ops)==2 and ops[1].type==arm.ARM_OP_MEM and ops[1].mem.base==arm.ARM_REG_PC:
                    la=((a+4)&~3)+ops[1].mem.disp; lits[la]=({'ldr':4,'ldrh':2,'ldrb':1}.get(m,4),a)
                if ops and ops[0].type==arm.ARM_OP_IMM and m.startswith('b') and m not in('bic','bics','bkpt'):
                    t=ops[0].imm
                    if m=='bl': addf(t,'bl@%x'%a); stack.append(t)
                    else: stack.append(t)
                    if m=='b' or (m=='bl' and t in NORET): break
                if m in('cbz','cbnz'): stack.append(ops[1].imm)
                if m=='bx' or (m=='pop' and any(o.reg==arm.ARM_REG_PC for o in ops)): break
                a+=ins.size
import pickle
cov=set()
for a,i in code.items(): cov.update(range(a,a+i.size))
for la,(sz,_) in lits.items(): cov.update(range(la,la+sz))
gaps=[];g=None
for a in range(VEND,BASE+END):
    if a not in cov:
        if g is None: g=a
    elif g is not None: gaps.append((g,a)); g=None
if g: gaps.append((g,BASE+END))
import sys as _s
if __name__!='__main__': pass
print('insns',len(code),'lits',len(lits),'funcs',len(funcs))
for g in gaps: print('gap',hex(g[0]),hex(g[1]),d[g[0]-BASE:g[1]-BASE].hex())
print(sorted(hex(f) for f in funcs))
pickle.dump({'code':{a:(i.size,i.mnemonic,i.op_str,bytes(i.bytes)) for a,i in code.items()},'lits':lits,'funcs':{k:sorted(v) for k,v in funcs.items()},'gaps':gaps},open('rda.pkl','wb'))
