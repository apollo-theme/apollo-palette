import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from common import load_palettes
from tables import BLOCKS, check, render, replace_between, stale


def readme(roles="old roles", contrast="old contrast"):
    return (
        "# Title\n\nintro\n\n"
        f"<!-- tables:roles:start -->\n{roles}\n<!-- tables:roles:end -->\n\n"
        "between\n\n"
        f"<!-- tables:contrast:start -->\n{contrast}\n<!-- tables:contrast:end -->\n\nafter\n"
    )


class RenderTests(unittest.TestCase):
    def setUp(self):
        self.tables = render(load_palettes())

    def test_blocks(self):
        self.assertEqual(("roles", "contrast"), BLOCKS)
        self.assertEqual(set(BLOCKS), set(self.tables))

    def test_role_table_has_one_sorted_row_per_role(self):
        lines = self.tables["roles"].splitlines()
        self.assertEqual("| Role | Apollo Dark | Apollo Light |", lines[0])
        roles = [line.split("|")[1].strip().strip("`") for line in lines[2:]]
        palettes = load_palettes()
        self.assertEqual(sorted(set(palettes["dark"]["roles"]) | set(palettes["light"]["roles"])), roles)
        primary = next(line for line in lines if line.startswith("| `textPrimary` |"))
        self.assertIn("`#cfbc97`", primary)
        self.assertIn("`#3c3836`", primary)
        selection_text = next(line for line in lines if line.startswith("| `selectionText` |"))
        self.assertIn("—", selection_text.split("|")[2])

    def test_contrast_table_covers_text_roles_on_three_backgrounds(self):
        lines = self.tables["contrast"].splitlines()
        self.assertEqual("| Variant | Color | Hex | On background | On surface | On selection |", lines[0])
        self.assertEqual(14, len(lines) - 2)
        self.assertIn("| Dark | `foreground` | `#cfbc97` | 9.76 | 8.82 | 6.24 |", lines)
        self.assertIn("| Light | `foreground` | `#3c3836` | 10.53 | 10.22 | 8.45 |", lines)


class MarkerTests(unittest.TestCase):
    def test_replace_between_swaps_only_the_block(self):
        out = replace_between(readme(), "roles", "NEW")
        self.assertEqual(readme(roles="NEW"), out)

    def test_stale_detects_changed_block(self):
        tables = render(load_palettes())
        fresh = readme(tables["roles"], tables["contrast"])
        self.assertEqual([], stale(fresh))
        self.assertEqual(["roles"], stale(fresh.replace("| `canvas` |", "| `kanvas` |")))

    def test_missing_markers_raise(self):
        with self.assertRaisesRegex(ValueError, "^missing tables:roles markers$"):
            replace_between("no markers", "roles", "x")
        with self.assertRaisesRegex(ValueError, "^missing tables:roles markers$"):
            stale("no markers")

    def test_check_reads_a_file_and_reports_missing_as_stale(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "README.md"
            self.assertEqual(list(BLOCKS), check(path))
            path.write_text(readme(), encoding="utf-8")
            self.assertEqual(list(BLOCKS), check(path))


if __name__ == "__main__":
    unittest.main()
