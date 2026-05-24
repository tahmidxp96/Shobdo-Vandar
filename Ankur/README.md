# Ankur English-Bangla Dictionary Staging 📚🇧🇩

This folder holds the staged vocabulary mapping file for the **Ankur Bangla-English Dictionary** database.

---

## ⚖️ License & Attribution

* **Original Project:** [Ankur Bangla Project](http://www.ankur.org.bd/) (and related Indic computing terminal terminology datasets).
* **Reference Link:** Supported by contributors at [Ankur India](https://github.com/ankur-india).
* **License:** GNU General Public License (GPL) / Open Source.
* **Credits:** Special thanks to Ankur contributors for pioneering open-source Bengali language computing and fonts.

---

## 🛠️ Pipeline Integration

The compilation script `kindle_dictionary_builder.py` automatically parses `ankur_dictionary.csv` during the ingestion phase:
1. Extracts English headwords and their Bangla translation equivalents.
2. Deduplicates senses and merges them into the master staging SQL table.
