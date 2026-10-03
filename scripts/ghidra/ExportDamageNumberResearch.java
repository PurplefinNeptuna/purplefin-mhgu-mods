// Read-only damage/camera research. Original executable bytes are authoritative.
// @category MHGU
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.DecompInterface;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import com.google.gson.GsonBuilder;
import java.nio.file.*;
import java.util.*;

public class ExportDamageNumberResearch extends GhidraScript {
    @Override public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 3) throw new IllegalArgumentException("Expected output, original image, comma-separated main offsets");
        Path out = Path.of(args[0]); Files.createDirectories(out);
        byte[] original = Files.readAllBytes(Path.of(args[1]));
        long base = currentProgram.getImageBase().getOffset();
        if (base != 0x9c9000L) throw new IllegalStateException("Unexpected database image base");
        if (args[2].startsWith("scan:")) {
            Set<Long> values = new HashSet<>();
            for (String text : args[2].substring(5).split(",")) values.add(Long.decode(text));
            List<Map<String,Object>> matches = new ArrayList<>();
            for (var ins : currentProgram.getListing().getInstructions(true)) {
                monitor.checkCancelled();
                Set<Long> found = new HashSet<>();
                for (int i=0;i<ins.getNumOperands();i++) for (Object object : ins.getOpObjects(i))
                    if (object instanceof ghidra.program.model.scalar.Scalar scalar && values.contains(scalar.getUnsignedValue()))
                        found.add(scalar.getUnsignedValue());
                if (found.isEmpty()) continue;
                long relative = ins.getAddress().getOffset()-base;
                byte[] bytes = ins.getBytes();
                if (relative < 0 || relative+bytes.length > original.length) continue;
                Function owner = getFunctionContaining(ins.getAddress());
                Map<String,Object> row = new LinkedHashMap<>();
                row.put("offset",relative); row.put("text",ins.toString()); row.put("values",found);
                row.put("function_offset",owner == null ? null : owner.getEntryPoint().getOffset()-base);
                row.put("function",owner == null ? null : owner.getName(true));
                row.put("original_bytes",HexFormat.of().formatHex(Arrays.copyOfRange(original,(int)relative,(int)relative+bytes.length)));
                row.put("database_bytes",HexFormat.of().formatHex(bytes)); matches.add(row);
            }
            Files.writeString(out.resolve("scalar-refs.json"),new GsonBuilder().setPrettyPrinting().create().toJson(matches)+"\n");
            println("DAMAGE_NUMBER_RESEARCH_COMPLETE " + out);
            return;
        }
        List<Map<String,Object>> results = new ArrayList<>();
        DecompInterface decompiler = new DecompInterface();
        if (!decompiler.openProgram(currentProgram)) throw new IllegalStateException("Decompiler failed to open program");
        try {
            for (String text : args[2].split(",")) {
                monitor.checkCancelled();
                long offset = Long.decode(text);
                Address address = currentProgram.getImageBase().add(offset);
                Function function = getFunctionContaining(address);
                Map<String,Object> row = new LinkedHashMap<>();
                row.put("requested_offset", offset);
                row.put("offset", function == null ? offset : function.getEntryPoint().getOffset()-base);
                row.put("function", function == null ? null : function.getName(true));
                List<Map<String,Object>> refs = new ArrayList<>();
                Address entry = function == null ? address : function.getEntryPoint();
                for (var ref : currentProgram.getReferenceManager().getReferencesTo(entry)) {
                    Map<String,Object> r = new LinkedHashMap<>();
                    Function caller = getFunctionContaining(ref.getFromAddress());
                    r.put("from_offset", ref.getFromAddress().getOffset()-base);
                    r.put("type", ref.getReferenceType().toString());
                    r.put("caller", caller == null ? null : caller.getName(true));
                    r.put("caller_offset", caller == null ? null : caller.getEntryPoint().getOffset()-base);
                    refs.add(r);
                }
                row.put("references", refs);
                List<Map<String,Object>> instructions = new ArrayList<>();
                List<Map<String,Object>> calls = new ArrayList<>();
                var iterator = function == null ? currentProgram.getListing().getInstructions(address, true) :
                    currentProgram.getListing().getInstructions(function.getBody(), true);
                int mismatch = 0;
                while (iterator.hasNext()) {
                    var ins = iterator.next();
                    long rel = ins.getAddress().getOffset()-base;
                    if (function == null && rel >= offset+32) break;
                    byte[] bytes = ins.getBytes();
                    if (rel < 0 || rel+bytes.length > original.length) throw new IllegalStateException("Instruction outside original image");
                    byte[] source = Arrays.copyOfRange(original,(int)rel,(int)rel+bytes.length);
                    for (int i=0;i<bytes.length;i++) if (bytes[i]!=source[i]) mismatch++;
                    Map<String,Object> r = new LinkedHashMap<>();
                    r.put("offset", rel); r.put("text", ins.toString());
                    r.put("database_bytes", HexFormat.of().formatHex(bytes));
                    r.put("original_bytes", HexFormat.of().formatHex(source)); instructions.add(r);
                    for (var ref : ins.getReferencesFrom()) if (ref.getReferenceType().isCall()) {
                        Map<String,Object> c = new LinkedHashMap<>();
                        c.put("from_offset",rel); c.put("target_offset",ref.getToAddress().getOffset()-base);
                        Function target = getFunctionAt(ref.getToAddress());
                        c.put("target",target == null ? null : target.getName(true)); calls.add(c);
                    }
                }
                row.put("instructions", instructions); row.put("calls",calls);
                row.put("instruction_byte_mismatches", mismatch);
                if (function != null) {
                    var d = decompiler.decompileFunction(function, 60, monitor);
                    row.put("decompiled", d.decompileCompleted()); row.put("decompiler_error",d.getErrorMessage());
                    if (d.decompileCompleted()) Files.writeString(out.resolve(String.format("function_%08x.c",function.getEntryPoint().getOffset()-base)), d.getDecompiledFunction().getC());
                }
                results.add(row);
            }
        } finally { decompiler.dispose(); }
        Map<String,Object> report = new LinkedHashMap<>();
        report.put("image_base", base); report.put("executable_sha256",currentProgram.getExecutableSHA256());
        report.put("functions",results);
        report.put("scope","Read-only imported annotations and decompilation; no reanalysis, installed changes or runtime dumper");
        Files.writeString(out.resolve("research.json"),new GsonBuilder().setPrettyPrinting().create().toJson(report)+"\n");
        println("DAMAGE_NUMBER_RESEARCH_COMPLETE " + out);
    }
}
