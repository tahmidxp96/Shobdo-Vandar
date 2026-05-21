# Aparajeyo Bangla Express Database Staging 📚🇧🇩

This folder holds the raw database assets for the **Aparajeyo Dictionary** compiled by Nazmul Hossain Nihal.

---

## ⚖️ License & Attribution

* **Original Creator/Author:** Nazmul Hossain Nihal / Aparajeyo Bangla Express team
* **Source Files Included:**
  * `entobn.abedb` (English to Bangla SQLite)
  * `bntoen.abedb` (Bangla to English SQLite)
* **License Scheme:** Open Database License / Creative Commons equivalent for open-source datasets.
* **Original Project Reference:** [Aparajeyo Bangla Express Dictionary](https://facebook.com/groups/aparajeyobangla) / Nazmul Hossain Nihal's compilation work.

---

## 🛠️ Pipeline Integration

The compilation script `kindle_dictionary_builder.py` automatically parses these `.abedb` SQLite files during the data-ingestion phase:
1. Reads raw English-to-Bangla mappings from `entobn.abedb`.
2. Reads raw Bangla-to-English mappings from `bntoen.abedb`.
3. Ingests their synonym arrays, parts of speech, and translated meanings, standardizing them into a single consolidated staging format.
