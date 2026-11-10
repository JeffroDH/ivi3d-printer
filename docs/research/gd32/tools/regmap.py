import os
import re,json
raw=json.load(open(os.path.join(os.path.dirname(__file__) or '.', 'regs_raw.json')))
# base lines -> instances. GD32_MANUAL is the datasheet text; without it only
# the Cortex-M23 system registers below are named.
bases=[]
manual=os.environ.get('GD32_MANUAL')
L=open(manual).read().split('\n') if manual else []
for i,l in enumerate(L):
    m=re.search(r'([A-Z0-9/]+) base address\s*[:：]\s*0x([0-9A-F ]+)',l)
    if m: bases.append((i,m.group(1),int(m.group(2).replace(' ',''),16)))
REG={}
def add(a,n):
    REG.setdefault(a,n)
for name,off,line in raw:
    # instances: bases whose line is the latest base group before this register line
    prior=[b for b in bases if b[0]<line]
    if not prior: continue
    last=prior[-1][0]
    group=[b for b in prior if last-b[0]<=3]
    for _,inst,base in group:
        inst=inst.split('/')[0]
        if inst=='CMP': base=0x40010000; 
        m=re.fullmatch(r'0x([0-9A-Fa-f]+)',off)
        pfx=name.split('_')[0]
        rn=re.sub(r'^(GPIOx|TIMERx|USARTx|I2Cx|SPIx|CMPx)', inst, name) if name.split('_')[0].endswith('x') else name
        if pfx in('USART','I2C','SPI') and inst!=pfx: rn=inst+name[len(pfx):]
        if m: add(base+int(m.group(1),16),rn)
        elif 'DMA_CHx' in name:
            o=int(off[:4],16)
            for x in range(5): add(base+o+0x14*x,name.replace('CHx','CH%d'%x))
        elif 'BKP' in name:
            for k,a in enumerate(range(0x50,0x64,4)): add(base+a,'RTC_BKP%d'%k)
# Cortex-M23 system registers (ARMv8-M architecture, not in GD32 manual)
SCS={0xE000E010:'SysTick_CTRL',0xE000E014:'SysTick_LOAD',0xE000E018:'SysTick_VAL',0xE000E01C:'SysTick_CALIB',
0xE000E100:'NVIC_ISER0',0xE000E180:'NVIC_ICER0',0xE000E200:'NVIC_ISPR0',0xE000E280:'NVIC_ICPR0',
0xE000ED00:'SCB_CPUID',0xE000ED04:'SCB_ICSR',0xE000ED08:'SCB_VTOR',0xE000ED0C:'SCB_AIRCR',0xE000ED10:'SCB_SCR',0xE000ED14:'SCB_CCR',
0xE000ED1C:'SCB_SHPR2',0xE000ED20:'SCB_SHPR3',0xE000ED24:'SCB_SHCSR'}
for k in range(8): SCS[0xE000E400+4*k]='NVIC_IPR%d'%k
REG.update(SCS)
PERIPH=[(b,i) for _,i,b in bases]+[(0x40010000,'SYSCFG'),(0xE000E000,'SCS'),(0x1FFFF800,'OptionBytes'),(0x1FFFF7E0,'FlashSize/UID')]
def name(a):
    if a in REG: return REG[a]
    for b,i in sorted(PERIPH,reverse=True):
        if b<=a<b+0x400: return '%s+0x%X'%(i.split('/')[0],a-b)
    return None
if __name__=='__main__':
    for a in sorted(REG): print(hex(a),REG[a])
