import importlib.util
import unittest
from pathlib import Path

MODULE = Path(__file__).with_name("iconctl.py")
SPEC = importlib.util.spec_from_file_location("iconctl", MODULE)
iconctl = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(iconctl)


class SvgNormalizationTests(unittest.TestCase):
    def test_adds_dimensions_and_viewbox_from_numeric_dimensions(self):
        result = iconctl.normalize_svg(b'<svg xmlns="http://www.w3.org/2000/svg" width="24" height="12"><path d="M0 0"/></svg>')
        text = result.decode()
        self.assertIn('viewBox="0 0 24 12"', text)
        self.assertIn('width="24"', text)
        self.assertIn('height="12"', text)

    def test_does_not_overwrite_existing_viewbox(self):
        result = iconctl.normalize_svg(b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><path d="M0 0"/></svg>')
        self.assertIn(b'viewBox="0 0 10 10"', result)

    def test_rejects_non_svg_xml(self):
        with self.assertRaises(ValueError):
            iconctl.normalize_svg(b'<html/>')

    def test_rejects_invalid_xml(self):
        with self.assertRaises(ValueError):
            iconctl.normalize_svg(b'<svg>')


if __name__ == "__main__":
    unittest.main()
