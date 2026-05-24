# Hunspell Bangla Spelling Dictionary Staging 📚🇧🇩

This folder holds the staged spelling dictionary (`.dic`) file for **Hunspell** (the standard spell-checker library used by Firefox, Chrome, and LibreOffice).

---

## ⚖️ License & Attribution

* **Original Project:** [Hunspell Spell Checker](https://hunspell.github.io/) / [LibreOffice Dictionaries](https://github.com/LibreOffice/dictionaries).
* **Reference Links:**
  * [hunspell-bn](https://github.com/tushar-rishav/hunspell-bn) (Community-maintained Bengali spelling dictionaries).
* **License:** GNU Lesser General Public License (**LGPL**) / GPL / MPL tri-licensed.
* **Credits:** Special thanks to open-source contributors who compiled and standardized the Bengali spell-checker dictionaries.

---

## 🛠️ Pipeline Integration

The compilation script `kindle_dictionary_builder.py` automatically parses `bangla_spelling.dic` during the ingestion phase:
1. Reads all valid Bangla lemmas line-by-line.
2. Builds a memory set of orthographically verified Bengali words.
3. Uses this set during the master consolidation phase to validate, filter, and prune misspelled or junk Bangla definitions staged from raw unstructured text.
