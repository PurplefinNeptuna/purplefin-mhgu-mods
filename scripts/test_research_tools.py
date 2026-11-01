"""The negative answers research relies on must first find known positives."""
from pathlib import Path
import unittest
from research_tools import ROOT, branch_sites, main_bytes, word_sites


def arm_branch(site, target, opcode):
    return (opcode << 24 | ((target - site - 8) >> 2 & 0xFF_FFFF)).to_bytes(4, "little")


class BranchSites(unittest.TestCase):
    def test_finds_forward_backward_conditional_and_tail_branches(self):
        image = bytearray(0x100)
        image[0x10:0x14] = arm_branch(0x10, 0x80, 0xEB)  # bl, forward
        image[0xC0:0xC4] = arm_branch(0xC0, 0x80, 0xEB)  # bl, backward
        image[0x20:0x24] = arm_branch(0x20, 0x80, 0x1B)  # blne
        image[0x30:0x34] = arm_branch(0x30, 0x80, 0xEA)  # b
        image[0x40:0x44] = arm_branch(0x40, 0x84, 0xEB)  # another target
        self.assertEqual(branch_sites(bytes(image), 0x80),
                         [(0x10, "bl"), (0x20, "bl"), (0x30, "b"), (0xC0, "bl")])

    def test_word_sites_are_aligned(self):
        image = b"\0" * 5 + (0xABCD).to_bytes(4, "little") + b"\0" * 3 + (0xABCD).to_bytes(4, "little")
        self.assertEqual(word_sites(image, 0xABCD), [12])


@unittest.skipUnless(Path(ROOT, "work/shared/game-exefs/main").exists(), "needs the copied main NSO")
class KnownSites(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.image = main_bytes()

    def test_draw_walker_has_its_call_and_its_tail_branch(self):
        self.assertEqual(branch_sites(self.image, 0xa494a0), [(0xa39664, "bl"), (0xa56a20, "b")])

    def test_mask_enter_handler_is_found_in_its_vtable(self):
        self.assertIn(0x178fb3c, word_sites(self.image, 0xa4ba94))


if __name__ == "__main__":
    unittest.main()
