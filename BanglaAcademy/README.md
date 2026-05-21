# Bangla Academy / Nazmul Hossain Nihal Database Integration 📚🇧🇩

This directory is designated for drop-in SQLite databases containing rich contextual meanings and usage examples (such as Nazmul Hossain Nihal's compiled Bangla Academy database).

The compilation pipeline `kindle_dictionary_builder.py` is equipped with a **resilient, schema-agnostic auto-detector** that will automatically discover and ingest databases placed here.

---

## How to use

1. Place your compiled SQLite database file (e.g., `nihal_academy.db`, `bangla_academy.sqlite`, or any other `.db`/`.sqlite` file) directly inside this `./BanglaAcademy/` folder.
2. Run the rebuild pipeline command:
   ```bash
   python3 kindle_dictionary_builder.py --rebuild
   ```
3. The script will automatically:
   - Identify the database files.
   - Connect and query the SQLite schemas.
   - Scan for tables containing candidate columns like `word`, `headword`, `lemma`, `english` (for query keys) and `meaning`, `translation`, `definition`, `bangla` (for translated senses), along with any example sentence columns.
   - Import all entries into the staging table under the source name `'BanglaAcademy'`.
   - Merge these rich, detailed senses directly into the final `master_lexicon` alongside the high-coverage datasets from MinhasKamal, Ridmik, and Aparajeyo.

---

## Resilient Auto-Discovery Specification
To ensure zero configuration, our importer automatically searches for:
*   **Word Columns**: `word`, `headword`, `lemma`, `english`, `en_word`
*   **Meaning/Definition Columns**: `meaning`, `definition`, `bangla`, `bn_word`, `translation`
*   **Context Columns (Optional)**: `context`, `situation`, `pos`
*   **Example Columns (Optional)**: `example`, `example_en`, `example_bn`

If found, it imports the fields directly to give you the ultimate bilingual Kindle dictionary with massive coverage and high-quality contextual definitions!
