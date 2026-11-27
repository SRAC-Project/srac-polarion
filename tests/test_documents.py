"""Guard the checked-in contract and presentation against format drift."""

import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET
import zipfile

from exporter.contract import SCHEMA

ROOT = Path(__file__).resolve().parents[1]
DECK = ROOT / "presentations" / "SRAC_Polarion_Integration v3.pptx"
NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main",
      "p": "http://schemas.openxmlformats.org/presentationml/2006/main"}


class DocumentConsistencyTests(unittest.TestCase):
    def test_schema_uses_only_the_runtime_validators_supported_vocabulary(self):
        allowed = {"$schema", "$id", "title", "description", "$defs", "type", "oneOf",
                   "$ref", "properties", "required", "additionalProperties", "items",
                   "const", "enum", "minLength", "pattern", "minimum", "minItems"}
        def walk(spec):
            self.assertFalse(set(spec) - allowed, "Extend runtime validation for new keywords")
            for key in ("$defs", "properties"):
                for child in spec.get(key, {}).values():
                    walk(child)
            for child in spec.get("oneOf", []):
                walk(child)
            if "items" in spec:
                walk(spec["items"])
        walk(json.loads(SCHEMA.read_bytes()))

    def test_presentation_excerpt_is_a_literal_subset_of_the_reference_export(self):
        reference = json.loads((ROOT / "examples" / "sample-export.json").read_bytes())
        with zipfile.ZipFile(DECK) as package:
            slide = ET.fromstring(package.read("ppt/slides/slide7.xml"))
        candidates = []
        for shape in slide.findall(".//p:sp", NS):
            text = "\n".join(t.text or "" for t in shape.findall(".//a:t", NS))
            if text.lstrip().startswith("{"):
                candidates.append(json.loads(text))
        self.assertEqual(len(candidates), 1)
        excerpt = candidates[0]
        self.assertIn("formatVersion", excerpt)
        self.assertEqual(excerpt, {key: reference[key] for key in excerpt})
        self.assertNotIn("sracVersion", excerpt)

    def test_reference_reports_individually_disclose_synthetic_origin(self):
        for name in ("sample-export.json", "coverage-report.json", "provenance-report.json"):
            with self.subTest(name=name):
                report = json.loads((ROOT / "examples" / name).read_bytes())
                self.assertEqual(report["dataOrigin"], "synthetic")
                self.assertFalse(report["liveExtractionPerformed"])
                self.assertIn("Illustrative synthetic example", report["notice"])
                self.assertEqual(report["formatVersion"], "0.2.0")

    def test_presentation_retains_twelve_slides_and_editable_evidence_tables(self):
        with zipfile.ZipFile(DECK) as package:
            slides = [n for n in package.namelist() if n.startswith("ppt/slides/slide") and n.endswith(".xml")]
            self.assertEqual(len(slides), 12)
            for number in (4, 5, 11):
                slide = ET.fromstring(package.read("ppt/slides/slide" + str(number) + ".xml"))
                self.assertIsNotNone(slide.find(".//a:tbl", NS))
            all_text = "\n".join(package.read(name).decode("utf-8") for name in package.namelist()
                                 if name.endswith(".xml"))
            self.assertNotIn("SRAC-compatible evidence records", all_text)
