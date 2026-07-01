import sys
import os
import unittest
import json
import xml.etree.ElementTree as ET

# Add project root to path to import kindle_dictionary_builder
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from kindle_dictionary_builder import (
    BanglaNormalizer,
    EnglishMorphologyEngine,
    BanglaMorphologyEngine,
    xml_escape_attr,
    KindleDictionaryCompiler,
    get_project_version
)


class TestBanglaNormalizer(unittest.TestCase):
    def test_nfc_standardization(self):
        # 1. Test standard NFC decomposition merging (Nuqta + Ra -> Rra)
        decomposed = "\u09b0\u09bc" # র + ়
        normalized = BanglaNormalizer.normalize(decomposed)
        self.assertEqual(normalized, "\u09dc") # ড়

    def test_custom_vowel_merges(self):
        # 2. Test composite vowel conversion (E-kar + Aa-kar -> O-kar)
        decomposed_o = "\u09c7\u09be"
        normalized_o = BanglaNormalizer.normalize(decomposed_o)
        self.assertEqual(normalized_o, "\u09cb") # ো (O-kar)
        
        decomposed_ou = "\u09c7\u09d7"
        normalized_ou = BanglaNormalizer.normalize(decomposed_ou)
        self.assertEqual(normalized_ou, "\u09cc") # ৌ (Ou-kar)

    def test_punc_and_whitespace_strip(self):
        # 3. Test removal of brackets, quotes, and punctuation
        raw = " (হিতৈষী) ।"
        self.assertEqual(BanglaNormalizer.normalize(raw), "হিতৈষী")


class TestEnglishMorphologyEngine(unittest.TestCase):
    def test_regular_inflections(self):
        # Test regular verb forms
        forms = EnglishMorphologyEngine.generate_inflections("walk", "verb")
        self.assertIn("walks", forms)
        self.assertIn("walking", forms)
        self.assertIn("walked", forms)
        
        # Test regular noun forms
        forms = EnglishMorphologyEngine.generate_inflections("cat", "noun")
        self.assertIn("cats", forms)

    def test_irregular_overrides(self):
        # Test irregular verb override mapping
        forms = EnglishMorphologyEngine.generate_inflections("see", "verb")
        self.assertIn("saw", forms)
        self.assertIn("seen", forms)
        self.assertIn("sees", forms)
        self.assertNotIn("seeed", forms) # Ensure default regular suffix isn't generated
        
        # Test irregular noun override mapping
        forms = EnglishMorphologyEngine.generate_inflections("child", "noun")
        self.assertEqual(forms, ["children"])

    def test_adjective_length_limit(self):
        # Short adjectives should take suffixes
        short_forms = EnglishMorphologyEngine.generate_inflections("tall", "adjective")
        self.assertIn("taller", short_forms)
        self.assertIn("tallest", short_forms)
        
        # Long adjectives should NOT take suffixes
        long_forms = EnglishMorphologyEngine.generate_inflections("benevolent", "adjective")
        self.assertEqual(long_forms, [])


class TestBanglaMorphologyEngine(unittest.TestCase):
    def test_nominal_suffixes(self):
        # Generate noun/adjective inflections
        forms = BanglaMorphologyEngine.generate_inflections("মানুষ", "noun")
        self.assertIn("মানুষটি", forms)
        self.assertIn("মানুষগুলো", forms)
        self.assertIn("মানুষকে", forms)

    def test_verb_conjugations(self):
        # Generate regular verb inflections (e.g. করা -> করি, করেছে, করব, করলেন)
        forms = BanglaMorphologyEngine.generate_inflections("করা", "verb")
        self.assertIn("করি", forms)
        self.assertIn("করছি", forms)
        self.assertIn("করবে", forms)
        self.assertIn("করলেন", forms)
        self.assertNotIn("করাটি", forms) # Noun suffixes should be blocked for verbs

    def test_verb_conjugations_wa_ending(self):
        # Generate Wa-ending verb conjugations (e.g. খাওয়া -> খাই, খায়, খাব, খেলাম, খেতে)
        forms = BanglaMorphologyEngine.generate_inflections("খাওয়া", "ক্রিয়া")
        self.assertIn("খাই", forms)
        self.assertIn("খায়", forms)
        self.assertIn("খাব", forms)
        self.assertIn("খেলাম", forms)
        self.assertIn("খেতে", forms)
        self.assertNotIn("খাওয়াটি", forms)


class TestXmlFormatting(unittest.TestCase):
    def test_xml_attribute_quote_escaping(self):
        # Ensure quotes inside attributes are escaped properly
        raw = 'inch"'
        escaped = xml_escape_attr(raw)
        self.assertEqual(escaped, "inch&quot;")

    def test_render_entry_xhtml_nesting(self):
        # Set up a compiler instance
        compiler = KindleDictionaryCompiler(output_dir="./build/test-build", direction="en-bn")
        
        # Render a mockup entry
        senses = [{'sense_id': 1, 'pos': 'noun', 'meanings': ['বিড়াল']}]
        inflections = ['cats']
        entry_xhtml = compiler.render_entry_xhtml("cat", "noun", senses, inflections)
        
        # Parse output and verify well-formed XML structure
        # Since it is a fragment, wrap it in a root tag
        wrapped_fragment = f"<root xmlns:idx='http://www.amazon.com/xmlns/idx'>{entry_xhtml}</root>"
        root = ET.fromstring(wrapped_fragment)
        
        # Find idx:entry -> idx:short -> idx:orth
        namespaces = {'idx': 'http://www.amazon.com/xmlns/idx'}
        entry = root.find('.//idx:entry', namespaces)
        self.assertIsNotNone(entry)
        
        short = entry.find('.//idx:short', namespaces)
        self.assertIsNotNone(short)
        
        orth = short.find('.//idx:orth', namespaces)
        self.assertIsNotNone(orth)
        
        # Ensure idx:infl is a child of idx:short (sibling to idx:orth), NOT nested in idx:orth
        infl_inside_orth = orth.find('.//idx:infl', namespaces)
        self.assertIsNone(infl_inside_orth) # MUST NOT be inside idx:orth
        
        infl_inside_short = short.find('./idx:infl', namespaces)
        self.assertIsNotNone(infl_inside_short) # MUST be a direct child of idx:short


if __name__ == '__main__':
    unittest.main()
