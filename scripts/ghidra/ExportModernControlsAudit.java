// Read-only controls review. Original instructions remain the byte authority.
// @category MHGU
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.DecompInterface;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import com.google.gson.GsonBuilder;
import java.nio.file.*;
import java.util.*;

public class ExportModernControlsAudit extends GhidraScript {
    @Override public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 3) throw new IllegalArgumentException("Expected output, original image, comma-separated main offsets");
        Path out = Path.of(args[0]); Files.createDirectories(out);
        byte[] original = Files.readAllBytes(Path.of(args[1]));
        long base = currentProgram.getImageBase().getOffset();
        if (base != 0x9c9000L) throw new IllegalStateException("Unexpected database image base");
        List<Map<String,Object>> results = new ArrayList<>();
        DecompInterface decompiler = new DecompInterface();
        decompiler.openProgram(currentProgram);
        try {
            for (String text : args[2].split(",")) {
                monitor.checkCancelled();
                long offset = Long.decode(text);
                Address address = currentProgram.getImageBase().add(offset);
                Function function = getFunctionAt(address);
                Map<String,Object> row = new LinkedHashMap<>();
                row.put("offset", offset); row.put("database_address", address.toString());
                row.put("function", function == null ? null : function.getName(true));
                List<Map<String,Object>> refs = new ArrayList<>();
                for (var ref : currentProgram.getReferenceManager().getReferencesTo(address)) {
                    Map<String,Object> r = new LinkedHashMap<>();
                    r.put("from_offset", ref.getFromAddress().getOffset()-base);
                    r.put("type", ref.getReferenceType().toString()); refs.add(r);
                }
                row.put("references", refs);
                List<Map<String,Object>> instructions = new ArrayList<>();
                var iterator = function == null ?
                    currentProgram.getListing().getInstructions(address, true) :
                    currentProgram.getListing().getInstructions(function.getBody(), true);
                int mismatch = 0;
                while (iterator.hasNext()) {
                    var ins = iterator.next();
                    long rel = ins.getAddress().getOffset()-base;
                    if (function == null && rel >= offset+32) break;
                    byte[] bytes = ins.getBytes();
                    if (rel < 0 || rel+bytes.length > original.length) throw new IllegalStateException("Instruction outside original image");
                    for (int i=0;i<bytes.length;i++) if (bytes[i]!=original[(int)rel+i]) mismatch++;
                    Map<String,Object> r = new LinkedHashMap<>();
                    r.put("offset", rel); r.put("text", ins.toString());
                    r.put("bytes", HexFormat.of().formatHex(bytes)); instructions.add(r);
                }
                row.put("instructions", instructions); row.put("instruction_byte_mismatches", mismatch);
                if (function != null) {
                    var d = decompiler.decompileFunction(function, 30, monitor);
                    row.put("decompiled", d.decompileCompleted());
                    if (d.decompileCompleted()) Files.writeString(out.resolve(String.format("function_%08x.c",offset)), d.getDecompiledFunction().getC());
                }
                results.add(row);
            }
        } finally { decompiler.dispose(); }
        Map<String,Object> report = new LinkedHashMap<>();
        report.put("image_base", base); report.put("executable_sha256",currentProgram.getExecutableSHA256());
        report.put("functions",results); report.put("scope","Read-only imported annotations and decompilation; no reanalysis or runtime dumper");
        Files.writeString(out.resolve("ghidra-audit.json"),new GsonBuilder().setPrettyPrinting().create().toJson(report)+"\n");
        println("MODERN_CONTROLS_AUDIT_COMPLETE " + out);
    }
}
