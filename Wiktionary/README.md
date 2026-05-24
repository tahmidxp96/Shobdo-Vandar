# Wiktionary Bilingual Dataset Staging 📚🇧🇩

This folder holds the staged structured bilingual glossary file extracted from **Wiktionary** (the open-source collaborative dictionary).

---

## ⚖️ License & Attribution

* **Original Project:** [Wiktionary](https://www.wiktionary.org/) (Wikimedia Foundation).
* **Reference Links:**
  * [Wikimedia Downloads](https://dumps.wikimedia.org/)
  * Curated parsing formats supported by [Kaikki.org](https://kaikki.org/).
* **License:** Creative Commons Attribution-ShareAlike 3.0 Unported (**CC-BY-SA 3.0**) / GNU Free Documentation License (GFDL).
* **Credits:** Special thanks to thousands of collaborative Wiktionary editors for maintaining detailed multilingual entries.

---

## 🛠️ Pipeline Integration

The compilation script `kindle_dictionary_builder.py` automatically parses `wiktionary_dictionary.json` during the ingestion phase:
1. Parses each JSON object.
2. Extracts word headwords (`word`), parts of speech (`pos`), meanings list, synonym lists, and detailed contextual examples in English/Bangla.
3. Consolidates these details to enrich entries with premium example sentences and parts of speech in the master SQLite database.
