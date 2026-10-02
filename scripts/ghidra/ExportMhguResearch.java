// Export existing analysis and compare initialized bytes without reanalysis.
// @category MHGU
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.DecompInterface;
import ghidra.program.model.address.Address;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.Symbol;
import ghidra.program.model.data.DataType;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import java.nio.file.*;
import java.io.*;
import java.security.MessageDigest;
import java.util.*;

public class ExportMhguResearch extends GhidraScript {
    private final Gson gson = new GsonBuilder().disableHtmlEscaping().create();
    private Map<String, Object> record(Object... pairs) {
        Map<String, Object> result = new LinkedHashMap<>();
        for (int i = 0; i < pairs.length; i += 2) result.put((String)pairs[i], pairs[i+1]);
        return result;
    }
    private String hex(byte[] value) { return HexFormat.of().formatHex(value); }
    @Override public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 2) throw new IllegalArgumentException("Expected output directory and verified main memory image");
        Path out = Path.of(args[0]); Files.createDirectories(out);
        byte[] expected = Files.readAllBytes(Path.of(args[1]));
        long base = currentProgram.getImageBase().getOffset();
        List<Object> blocks = new ArrayList<>();
        for (MemoryBlock block : currentProgram.getMemory().getBlocks()) {
            monitor.checkCancelled();
            long relative = block.getStart().getOffset() - base;
            Map<String, Object> row = record("name", block.getName(), "address", block.getStart().toString(),
                "relative_address", relative, "size", block.getSize(), "initialized", block.isInitialized(),
                "execute", block.isExecute());
            if (block.isInitialized() && relative >= 0 && relative + block.getSize() <= expected.length) {
                byte[] actual = new byte[(int)block.getSize()];
                currentProgram.getMemory().getBytes(block.getStart(), actual);
                int mismatches = 0; List<Object> samples = new ArrayList<>();
                for (int i = 0; i < actual.length; i++) if (actual[i] != expected[(int)relative+i]) {
                    mismatches++;
                    if (samples.size() < 8) samples.add(record("relative_address", relative+i,
                        "database_byte", actual[i]&255, "original_byte", expected[(int)relative+i]&255));
                }
                row.put("sha256", hex(MessageDigest.getInstance("SHA-256").digest(actual)));
                row.put("mismatched_bytes", mismatches); row.put("mismatch_samples", samples);
            }
            blocks.add(row);
        }
        long symbolCount = 0, functionCount = 0, typeCount = 0;
        Map<String, Long> sources = new TreeMap<>();
        try (BufferedWriter writer = Files.newBufferedWriter(out.resolve("symbols.jsonl"))) {
            for (Symbol symbol : currentProgram.getSymbolTable().getAllSymbols(true)) {
                monitor.checkCancelled(); symbolCount++;
                sources.merge(symbol.getSource().toString(), 1L, Long::sum);
                writer.write(gson.toJson(record("name", symbol.getName(true), "address", symbol.getAddress().toString(),
                    "relative_address", symbol.getAddress().getOffset()-base, "type", symbol.getSymbolType().toString(),
                    "source", symbol.getSource().toString()))); writer.newLine();
            }
        }
        try (BufferedWriter writer = Files.newBufferedWriter(out.resolve("functions.jsonl"))) {
            for (Function function : currentProgram.getFunctionManager().getFunctions(true)) {
                monitor.checkCancelled(); functionCount++;
                writer.write(gson.toJson(record("name", function.getName(true), "address", function.getEntryPoint().toString(),
                    "relative_address", function.getEntryPoint().getOffset()-base,
                    "signature", function.getSignature().toString(), "size", function.getBody().getNumAddresses())));
                writer.newLine();
            }
        }
        try (BufferedWriter writer = Files.newBufferedWriter(out.resolve("types.jsonl"))) {
            Iterator<DataType> types = currentProgram.getDataTypeManager().getAllDataTypes();
            while (types.hasNext()) {
                monitor.checkCancelled(); DataType type = types.next(); typeCount++;
                Map<String,Object> row = record("name", type.getPathName(), "size", type.getLength(),
                    "kind", type.getClass().getSimpleName(), "description", type.getDescription());
                if (type instanceof ghidra.program.model.data.Composite composite) {
                    List<Object> fields = new ArrayList<>();
                    for (var field : composite.getDefinedComponents()) fields.add(record("name", field.getFieldName(),
                        "offset", field.getOffset(), "size", field.getLength(), "type", field.getDataType().getPathName()));
                    row.put("fields", fields);
                }
                writer.write(gson.toJson(row)); writer.newLine();
            }
        }
        List<Object> targets = new ArrayList<>();
        DecompInterface decompiler = new DecompInterface(); decompiler.openProgram(currentProgram);
        try {
            for (long offset : new long[]{0x2b489cL, 0x2a79ccL, 0x7aef68L, 0x1177f68L, 0x18a5d7cL, 0x177e9a0L, 0x283710L}) {
                Address address = currentProgram.getImageBase().add(offset);
                Function function = getFunctionAt(address);
                List<String> names = new ArrayList<>();
                for (Symbol symbol : currentProgram.getSymbolTable().getSymbols(address)) names.add(symbol.getName(true));
                Map<String,Object> row = record("relative_address", offset, "symbols", names);
                List<Object> references = new ArrayList<>();
                for (var ref : currentProgram.getReferenceManager().getReferencesTo(address)) references.add(record(
                    "from_relative_address", ref.getFromAddress().getOffset()-base, "type", ref.getReferenceType().toString()));
                row.put("references", references);
                Function containing = getFunctionContaining(address);
                if (containing != null) row.put("containing_function", containing.getName(true));
                if (function != null) {
                    row.put("function", function.getName(true));
                    var result = decompiler.decompileFunction(function, 30, monitor);
                    row.put("decompiled", result.decompileCompleted());
                    if (result.decompileCompleted()) Files.writeString(out.resolve(String.format("function_%08x.c",offset)), result.getDecompiledFunction().getC());
                }
                targets.add(row);
            }
        } finally { decompiler.dispose(); }
        Map<String,Object> summary = record("program", currentProgram.getName(), "executable_sha256", currentProgram.getExecutableSHA256(),
            "format", currentProgram.getExecutableFormat(), "language", currentProgram.getLanguageID().toString(),
            "image_base", currentProgram.getImageBase().toString(), "symbol_count", symbolCount,
            "function_count", functionCount, "type_count", typeCount, "symbol_sources", sources,
            "memory_blocks", blocks, "research_targets", targets,
            "reanalysis", false, "runtime_validation", "not performed");
        Files.writeString(out.resolve("summary.json"), new GsonBuilder().setPrettyPrinting().create().toJson(summary)+"\n");
        println("MHGU_RESEARCH_EXPORT_COMPLETE " + out);
    }
}
