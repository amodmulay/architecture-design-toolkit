import sys
import unittest
from pathlib import Path
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parent))
from diagramgen import build_drawio, validate_model


class DiagramGeneratorTests(unittest.TestCase):
    def setUp(self):
        self.model = {
            "name": "Demo Platform",
            "boundaries": [{"id": "cloud", "title": "Cloud Platform"}],
            "components": [
                {"id": "api", "title": "API Gateway", "responsibility": "Expose secured APIs", "boundary": "cloud"},
                {"id": "service", "title": "Order Service", "responsibility": "Process orders", "boundary": "cloud"}
            ],
            "connections": [
                {"id": "api_orders", "source": "api", "target": "service", "label": "REST", "mode": "sync"}
            ]
        }

    def test_valid_model(self):
        validate_model(self.model)

    def test_unknown_connection_target_rejected(self):
        self.model["connections"][0]["target"] = "missing"
        with self.assertRaisesRegex(ValueError, "unknown component"):
            validate_model(self.model)

    def test_duplicate_component_id_rejected(self):
        self.model["components"].append(dict(self.model["components"][0]))
        with self.assertRaisesRegex(ValueError, "Duplicate component"):
            validate_model(self.model)

    def test_generates_parseable_drawio_with_edges(self):
        xml = build_drawio(self.model)
        root = ET.fromstring(xml)
        self.assertEqual(root.tag, "mxfile")
        self.assertEqual(len(root.findall(".//mxCell[@edge='1']")), 1)
        self.assertEqual(len(root.findall(".//mxCell[@vertex='1']")), 3)


if __name__ == "__main__":
    unittest.main()
