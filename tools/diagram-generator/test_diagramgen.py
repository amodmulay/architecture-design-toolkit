import sys
import unittest
from pathlib import Path
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parent))
from diagramgen import build_drawio, calculate_layout, validate_model


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

    def test_invalid_boundary_reference_rejected(self):
        self.model["components"][0]["boundary"] = "not_defined"
        with self.assertRaisesRegex(ValueError, "unknown boundary"):
            validate_model(self.model)

    def test_generates_parseable_drawio_with_edges(self):
        xml = build_drawio(self.model)
        root = ET.fromstring(xml)
        self.assertEqual(root.tag, "mxfile")
        self.assertEqual(len(root.findall(".//mxCell[@edge='1']")), 1)
        self.assertEqual(len(root.findall(".//mxCell[@vertex='1']")), 3)

    def test_dag_places_downstream_component_to_the_right(self):
        positions, _, warnings = calculate_layout(self.model)
        self.assertGreater(positions["service"][0], positions["api"][0])
        self.assertEqual(warnings, [])

    def test_parallel_components_stack_without_overlap(self):
        self.model["components"].append({
            "id": "audit", "title": "Audit Service", "responsibility": "Record audit events", "boundary": "cloud"
        })
        self.model["connections"].append({
            "id": "api_audit", "source": "api", "target": "audit", "label": "Audit", "mode": "async"
        })
        positions, _, _ = calculate_layout(self.model)
        service = positions["service"]
        audit = positions["audit"]
        self.assertEqual(service[0], audit[0])
        self.assertTrue(service[1] + service[3] <= audit[1] or audit[1] + audit[3] <= service[1])

    def test_cycles_are_reported_not_crashed(self):
        self.model["connections"].append({
            "id": "service_api", "source": "service", "target": "api", "label": "Callback", "mode": "sync"
        })
        _, _, warnings = calculate_layout(self.model)
        self.assertTrue(any("cycles" in warning for warning in warnings))


if __name__ == "__main__":
    unittest.main()
