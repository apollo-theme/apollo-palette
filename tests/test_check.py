import copy, sys, unittest; from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from check import check_readme, check_schema, check_slots, check_contrast, REQUIRED_SECTIONS, load_palettes
WORDS = " ".join(["word"] * 80)
HEAD = "| Role | Hex | Background | Ratio | Reason |\n| --- | --- | --- | --- | --- |\n"
def table(v, rows): return f"<!-- example:{v} -->\n{HEAD}{rows}<!-- /example:{v} -->\n"
def doc(dark="| Text | #cfbc97 | #141617 | 9.76 | primary |\n", light="| Text | #3c3836 | #f9f5d7 | 10.53 | primary |\n"):
    return "".join(f"## {s}\n\n{WORDS}\n\n" for s in REQUIRED_SECTIONS) + table("dark", dark) + table("light", light)
class ReadmeTests(unittest.TestCase):
    def errs(self, text): return check_readme(text, load_palettes())
    def test_valid_is_error_free(self): self.assertEqual([], self.errs(doc()))
    def test_wrong_ratio_fails(self): self.assertTrue(any("ratio 1.00" in e for e in self.errs(doc().replace("9.76", "1.00"))))
    def test_unknown_hex_fails(self): self.assertTrue(any("not in dark" in e for e in self.errs(doc().replace("#cfbc97", "#123456"))))
    def test_empty_example_fails(self): self.assertIn("light: worked example has no rows", self.errs(doc(light="")))
    def test_short_section_fails(self): self.assertTrue(any("80 words" in e for e in self.errs(doc().replace(WORDS, "short", 1))))
    def test_missing_section_fails(self): self.assertTrue(any("missing section" in e for e in self.errs(doc().replace("## Lineage", "## Other"))))
class PaletteTests(unittest.TestCase):
    def setUp(self): self.p = copy.deepcopy(load_palettes())
    def test_real_palettes_pass(self): self.assertEqual([], check_schema(self.p) + check_slots(self.p) + check_contrast(self.p))
    def test_schema(self): del self.p["dark"]["roles"]; self.assertIn("dark: missing key roles", check_schema(self.p))
    def test_schema_rejects_null_color(self): self.p["dark"]["colors"]["surfaceHover"] = None; self.assertIn("dark: colors.surfaceHover is not a hex color", check_schema(self.p))
    def test_schema_rejects_non_hex_color(self): self.p["dark"]["colors"]["surfaceHover"] = "not-a-color"; self.assertIn("dark: colors.surfaceHover is not a hex color", check_schema(self.p))
    def test_schema_rejects_non_hex_slot(self): self.p["light"]["terminal"]["ansi"][1] = "red"; self.assertIn("light: terminal.ansi[1] is not a hex color", check_schema(self.p))
    def test_slot_order(self):
        a = self.p["light"]["terminal"]["ansi"]; a[1], a[2] = a[2], a[1]; self.assertIn("light: terminal.ansi slot order differs", check_slots(self.p))
    def test_contrast(self): self.p["light"]["colors"]["foreground"] = "#e0e0e0"; self.assertTrue(any(e.startswith("light foreground") for e in check_contrast(self.p)))
