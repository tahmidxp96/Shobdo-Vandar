# Shobdo Vandar (শব্দ ভাণ্ডার) 📚🇧🇩
> High-Performance Standalone Kindle Bilingual Dictionaries (English ⇄ Bangla)

[![GitHub Release](https://img.shields.io/github/v/release/tahmidxp96/Shobdo_Vandar?color=vibrant&style=for-the-badge)](https://github.com/tahmidxp96/Shobdo_Vandar/releases)
[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg?style=for-the-badge)](https://www.python.org/)
[![Kindle Compatible](https://img.shields.io/badge/format-Kindle%20MOBI-orange.svg?style=for-the-badge)](https://www.amazon.com/gp/feature.html?ie=UTF8&docId=1000765211)

An advanced, high-performance compilation pipeline that constructs comprehensive, rich, and highly accurate English-to-Bangla (`en-bn`) and Bangla-to-English (`bn-en`) dictionaries optimized specifically for **Amazon Kindle** e-readers.

Consolidated and deduplicated from master sources (**Aparajeyo, MinhasKamal, Ridmik, and Bangla Academy**), this project packages **over 145,000+ words** with precise contextual definitions, inflection index matching, and phonetic normalizations.

---

## 📥 How to Download the Dictionaries

You do not need to build the dictionaries yourself! The latest compiled, ready-to-use `.mobi` files are automatically built and published with every release.

1. Go to the **[Releases](https://github.com/tahmidxp96/Shobdo_Vandar/releases)** page (the "Download" section of the repository).
2. Under the latest release assets, download the dictionary you want:
   * **`en-bn.mobi`** (English-to-Bangla Dictionary: **94,347 entries**, ~10.4 MB)
   * **`bn-en.mobi`** (Bangla-to-English Dictionary: **50,919 entries**, ~6.4 MB)

---

## 📲 How to Load Dictionaries onto your Kindle

To install these dictionaries on any physical Kindle device (Paperwhite, Oasis, Scribe, Basic, or Voyage):

1. **Connect your Kindle** to your computer using a USB cable.
2. Open your file manager (Finder on Mac or File Explorer on Windows) and locate the **Kindle** drive.
3. Copy the downloaded `.mobi` file(s) into the Kindle's **`documents/dictionaries/`** folder:
   ```text
   Kindle/
   └── documents/
       └── dictionaries/
           ├── en-bn.mobi
           └── bn-en.mobi
   ```
4. **Eject and disconnect** your Kindle safely.
5. **Set as Default:**
   * On your Kindle: Go to **Settings ➔ Language & Dictionaries ➔ Dictionaries**.
   * Choose **English** and select **High-Quality English-to-Bangla Kindle Dictionary**.
   * Choose **Bangla** and select **Advanced Bangla-to-English Learner's Dictionary**.
6. Enjoy instant context-aware lookups while reading!

---

## 🛠️ Local Development & Manual Compilation

If you want to modify the source definitions, add custom vocabularies, or rebuild the dictionaries locally:

### Prerequisites
* **Python 3.8+**
* **Kindle Previewer 3** installed on your machine.
  * [Download Kindle Previewer 3 for Mac/Windows](https://d2bzeorukaqrvt.cloudfront.net/KindlePreviewerInstaller.pkg)
  * The compiler pipeline will automatically auto-detect the installation and locate `kindlegen` embedded inside.

### Execution Guide

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/tahmidxp96/Shobdo_Vandar.git
   cd Shobdo_Vandar
   ```

2. **Run the Full Build Pipeline (Ingestion + Compilation):**
   ```bash
   python3 kindle_dictionary_builder.py
   ```
   *This initializes the database (`lexicon.db`), parses all raw resources under staging folders, deduplicates master definitions, and builds the MOBI files.*

3. **Recompile MOBI files only (Skips staging database rebuilds for speed):**
   ```bash
   python3 kindle_dictionary_builder.py -c
   ```

4. **Query & Preview Layouts in your Terminal:**
   You can preview how any word will look inside your Kindle e-reader using a beautifully formatted terminal output:
   ```bash
   python3 kindle_dictionary_builder.py -p "benevolent"
   ```

---

## 📊 Lexicon Architecture & Master Statistics

The pipeline automatically processes and builds the dictionary from multiple staged sources:

| Source | Raw Records Ingested | Target Direction | Key Features |
| :--- | :--- | :--- | :--- |
| **Aparajeyo** | 186,776 | English ➔ Bangla | Rich synonym arrays and definitions |
| **MinhasKamal** | 93,421 | English ➔ Bangla | High coverage vocabulary index |
| **Ridmik** | 13,474 | Bangla ➔ English | Standard colloquial and formal mappings |
| **Bangla Academy** | Reference | Both | Official lexical structure validations |

### Consolidated Outputs:
* **Bangla-to-English (`bn-en`):** `50,919` unique entries
* **English-to-Bangla (`en-bn`):** `94,347` unique entries
* **Total Combined Lexicon:** **`145,266`** deduplicated, high-fidelity words.

---

## 🤖 Continuous Integration & Automatic Publishing

We use a fully automated **GitHub Actions** pipeline configured in `.github/workflows/release.yml`. 

Whenever you push a tag starting with `v` (e.g., `git tag v1.0.0` && `git push origin v1.0.0`), the workflow:
1. Provisions a secure `macos-latest` container.
2. Installs Amazon's official **Kindle Previewer 3** compiler.
3. Automatically executes `kindle_dictionary_builder.py` to ingest the raw staging sources and build fresh, optimized `.mobi` files.
4. Generates a new **GitHub Release** and uploads the `.mobi` dictionaries as downloadable assets.

---

## 📄 License & Attribution

All raw resources are proprietary properties of their respective authors and projects (Aparajeyo, MinhasKamal, Ridmik, and Bangla Academy). The builder pipeline script is distributed under the **MIT License**.
