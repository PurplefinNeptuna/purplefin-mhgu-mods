// Exact-address references also cover unseparated functions in the imported database.
// @category MHGU
import ghidra.app.script.GhidraScript;
import com.google.gson.GsonBuilder;
import java.nio.file.*;
import java.util.*;
public class ExportQuestBadgeRefs extends GhidraScript {
 public void run() throws Exception {
  String[] args=getScriptArgs();long base=currentProgram.getImageBase().getOffset();
  if(args.length!=2 || base!=0x9c9000L)throw new IllegalArgumentException("output and offsets required");
  var rows=new ArrayList<Map<String,Object>>();
  for(String text:args[1].split(",")) {
   long offset=Long.decode(text);var addr=currentProgram.getImageBase().add(offset);
   for(var ref:currentProgram.getReferenceManager().getReferencesTo(addr)) {
    var row=new LinkedHashMap<String,Object>();var from=ref.getFromAddress();var fn=getFunctionContaining(from);
    row.put("target",offset);row.put("from",from.getOffset()-base);row.put("kind",ref.getReferenceType().toString());
    row.put("function",fn==null?null:fn.getEntryPoint().getOffset()-base);
    var ins=currentProgram.getListing().getInstructionAt(from);row.put("instruction",ins==null?null:ins.toString());rows.add(row);
   }
  }
  Files.writeString(Path.of(args[0]),new GsonBuilder().setPrettyPrinting().create().toJson(rows)+"\n");
  println("QUEST_BADGE_REFS_COMPLETE");
 }
}
