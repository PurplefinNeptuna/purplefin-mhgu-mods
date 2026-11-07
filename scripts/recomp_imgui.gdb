# Count MHGURecomp's plugin ImGui mirror objects and name their owner.
# The release build keeps .symtab + .debug_info, so these are readable live:
#   mir[]/nmir/nmfree  the 8192-slot mirror pool (runtime/forge_imgui.c:138)
#   mtypes[]           object class names (121)
#   g_modules[]        guest address ranges of main/sdk/each plugin .nro
#   t_cpu              the plugin thread's Cpu*, whose r[14] is the caller's guest pc
#
# kernel.yama.ptrace_scope=1 blocks attaching to a running process, so start the
# game under gdb (or set that to 0 and use: gdb -q -p $(pidof mhgurecomp)):
#   cd /mnt/storage2/Programs/MHGURecomp
#   gdb -q -x /mnt/storage2/Programs/MHGU_Modding/scripts/recomp_imgui.gdb --args ./mhgurecomp
#   (gdb) r            play; for the numbers press Ctrl-C then
#   (gdb) imgui_dump   (resume with 'c'; 'imgui_watch' early turns on per-plugin tracking)

set pagination off
set debuginfod enabled off

python
import gdb, struct, collections

ROW = "<QIHBxQ"               # Mirror: host, guest, type, flags, (pad), shadow = 24 bytes
FIELDS, TYPE_AT = 5, 2        # 5 unpacked values per row, type is the 3rd

def val(n):
    return gdb.parse_and_eval(n)

def modules():
    out = []
    gms = val("g_modules")
    for i in range(128):
        base = int(gms[i]["base"])
        if base:
            nm = gms[i]["name"]
            out.append((nm.string() if nm != 0 else "?", base, int(gms[i]["size"])))
    return out

def owner(pc):
    for name, base, size in modules():
        if base <= pc < base + size:
            return "%s+0x%x" % (name, pc - base)
    return "host+0x%x" % pc

def type_names():
    mt = val("mtypes")
    return [mt[i]["name"].string() for i in range(121)]

def live_pool():
    # One read of the whole mirror array: 8192 separate gdb reads crawl.
    size = struct.calcsize(ROW)
    raw = gdb.selected_inferior().read_memory(int(val("mir").address), 8192 * size)
    return struct.unpack("<" + ROW * 8192, bytes(raw))

class Watch(gdb.Breakpoint):
    hits = collections.Counter()
    def __init__(self):
        gdb.Breakpoint.__init__(self, "mirror_new")
        self.silent = True
        self.names = type_names()
    def stop(self):
        try:
            tc = val("t_cpu")
            if tc != 0:
                self.hits[(owner(int(tc["r"][14])), self.names[int(val("type"))])] += 1
        except gdb.error:
            pass
        return False        # let the game run; just count

class Cmd(gdb.Command):
    def __init__(self, name, doc, fn):
        gdb.Command.__init__(self, name, gdb.COMMAND_USER)
        self.fn = fn
    def invoke(self, arg, _tty):
        try:
            self.fn(arg)
        except gdb.MemoryError:
            print("no live process: start the game under gdb (header of this file),")
            print("or set kernel.yama.ptrace_scope=0 and run: gdb -q -p $(pidof mhgurecomp)")

def dump(arg):
    nmir, nmfree = int(val("nmir")), int(val("nmfree"))
    names = type_names()
    words = live_pool()
    by_type = collections.Counter(names[t] if t < len(names) else "type%d" % t
                                  for t in words[:nmir * FIELDS][TYPE_AT::FIELDS])
    print("mirrors: %d made, %d free, %d live, cap 8192, %d left"
          % (nmir, nmfree, nmir - nmfree, 8192 - nmir))
    for name, n in by_type.most_common(12):
        print("  %6d  %s" % (n, name))
    if not Watch.hits:
        print("  ('imgui_watch' at startup attributes new mirrors to plugins)")

Cmd("imgui_dump", "Live mirror pool: made/free/live and a per-class histogram.", dump)
Cmd("imgui_watch", "Count every new mirror by the plugin that created it.",
    lambda a: Watch() or print("tracking new mirrors by caller from here on"))
Cmd("imgui_owners", "New mirrors grouped by plugin, biggest first.",
    lambda a: [print("  %6d  %-30s %s" % (n, who, ty))
               for (who, ty), n in Watch.hits.most_common(15)] or print("  nothing tracked yet"))
Cmd("imgui_mods", "Guest address range of every loaded module.",
    lambda a: [print("  0x%08x +0x%-8x %s" % (b, s, n)) for n, b, s in modules()])
end
