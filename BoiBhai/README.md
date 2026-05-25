# BoiBhai Bengali Monolingual Dictionary Staging 📚🇧🇩

This folder holds the staged monolingual dictionary JSON database compiled under the specifications of the **BoiBhai Bengali Dictionary** project.

---

## ⚖️ License & Attribution

* **Original Project Reference:** [BoiBhai bn-dict-database](https://github.com/BoiBhai/bn-dict-database)
* **Project Nature:** A crowdsourced, collaborative Bengali lexical database containing ontological properties, etymology, synonyms, parts of speech, and native definitions.
* **License:** Open Source / Creative Commons / Community Contributed.
* **Credits:** Special thanks to the BoiBhai open-source contributors for maintaining a structured, modern lexical database for the Bengali language.

---

## 🛠️ Pipeline Integration

The builder script `kindle_dictionary_builder.py` automatically detects and parses `boibhai_dictionary.json` during execution:
1. **Direction Mapping**: Categorizes records under the `bn-bn` direction.
2. **Ingestion Schema**: Extracts Bengali headwords, pronunciations, parts of speech, synonyms, definitions, and native usage examples.
3. **Consolidation**: deduplicates entries and stores them into the master lexicon.
4. **Morphological Aliasing**: Maps common inflection suffixes (using `BanglaMorphologyEngine`) to enable native, inflected lookups on e-readers.
