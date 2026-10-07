OUTPUT_FORMAT(elf32-littlearm)
OUTPUT_ARCH(arm)
ENTRY(plugin_start)
PHDRS {
    text PT_LOAD FLAGS(5);
    rodata PT_LOAD FLAGS(4);
    data PT_LOAD FLAGS(6);
    dynamic PT_DYNAMIC;
}
SECTIONS {
    . = 0;
    .text : { KEEP(*(.text.crt0)) *(.text .text.*) } :text
    .plt : { *(.plt .plt.*) } :text
    . = ALIGN(0x1000);
    .rodata : { *(.rodata .rodata.*) } :rodata
    .hash : { *(.hash) } :rodata
    .gnu.hash : { *(.gnu.hash) } :rodata
    .dynsym : { *(.dynsym) } :rodata
    .dynstr : { *(.dynstr) } :rodata
    .rel.dyn : { *(.rel.dyn) } :rodata
    .rel.plt : { *(.rel.plt) } :rodata
    .note.gnu.build-id : { *(.note.gnu.build-id) } :rodata
    . = ALIGN(0x1000);
    .data : { *(.data .data.*) *(.data.rel.ro*) } :data
    .got : { *(.got.plt) *(.got) } :data
    .dynamic : { HIDDEN(__dynamic_start__ = .); *(.dynamic) } :data :dynamic
    . = ALIGN(0x1000);
    .bss (NOLOAD) : {
        HIDDEN(__bss_start__ = .);
        *(.bss .bss.*) *(COMMON)
        HIDDEN(__bss_end__ = .);
        . = ALIGN(0x1000);
    } :data
    /DISCARD/ : { *(.interp) *(.ARM.exidx*) *(.ARM.extab*) *(.eh_frame*) *(.init) *(.fini) }
}
