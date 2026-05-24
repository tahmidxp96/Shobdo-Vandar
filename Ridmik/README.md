# Ridmik Bangla-to-English Dictionary Staging 📚🇧🇩

This folder holds the raw word list mapping database for the **Ridmik Keyboard Dictionary** project.

---

## ⚖️ License & Attribution

* **Original Creator/Author:** Ridmik Labs (Shamim Hasnath and team)
* **Original Project Reference:** Part of the open-source dictionary data used in Ridmik Keyboard and Android repositories ([Ridmik Labs GitHub](https://github.com/ridmik)).
* **License:** MIT License / Open Source.
* **Details:** This raw `dictionary` file contains clean, structured Bangla headwords mapped to their direct English translations.

---

## 🛠️ Pipeline Integration

The compilation script `kindle_dictionary_builder.py` automatically processes the `dictionary` file:
1. Scans the file line-by-line using a fast parsing regex helper.
2. Identifies Bangla lemma keys and their English translated equivalents.
3. Cleans, normalizes, and maps Bangla character variations.
4. Ingests all `13,474` direct translations into the master builder staging database.
