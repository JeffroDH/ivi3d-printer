import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.address.*;
import ghidra.program.model.mem.*;
import ghidra.app.cmd.disassemble.*;
import ghidra.app.cmd.function.*;
import java.io.*;
public class DecompAll extends GhidraScript {
  public void run() throws Exception {
    String out = getScriptArgs()[0];
    Memory m = currentProgram.getMemory();
    AddressSpace sp = currentProgram.getAddressFactory().getDefaultAddressSpace();
    for (int i=1;i<98;i++){
      long v = m.getInt(sp.getAddress(0x08000000L+4*i)) & 0xffffffffL;
      if (v>=0x08000000L && v<0x08008000L){
        Address a = sp.getAddress(v & ~1L);
        currentProgram.getProgramContext(); 
        try { setThumb(a); } catch (Exception e) {}
        disassemble(a);
        if (getFunctionAt(a)==null) createFunction(a, null);
      }
    }
    analyzeAll(currentProgram);
    DecompInterface d = new DecompInterface(); d.openProgram(currentProgram);
    PrintWriter pw = new PrintWriter(new FileWriter(out));
    for (Function f : currentProgram.getFunctionManager().getFunctions(true)) {
      DecompileResults r = d.decompileFunction(f, 60, monitor);
      pw.println("// ===== " + f.getName() + " @ " + f.getEntryPoint());
      if (r.decompileCompleted()) pw.println(r.getDecompiledFunction().getC());
      else pw.println("// failed");
    }
    pw.close();
  }
  void setThumb(Address a) throws Exception {
    ghidra.program.model.lang.Register tm = currentProgram.getRegister("TMode");
    currentProgram.getProgramContext().setValue(tm, a, a, java.math.BigInteger.ONE);
  }
}
