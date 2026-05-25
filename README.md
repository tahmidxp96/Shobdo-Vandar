# Shobdo vandar (শব্দ ভান্ডার) 📚🇧🇩

A developer-centric reference project and high-performance compilation pipeline showing how to build custom, search-compliant Kindle bilingual and monolingual dictionaries from raw lexicographical datasets.

[![GitHub Release](https://img.shields.io/github/v/release/tahmidxp96/Shobdo-Vandar?logo=github&style=for-the-badge&color=3383FF)](https://github.com/tahmidxp96/Shobdo-Vandar/releases)
[![Total Downloads](https://img.shields.io/github/downloads/tahmidxp96/Shobdo-Vandar/total?logo=github&style=for-the-badge&color=2EA043)](https://github.com/tahmidxp96/Shobdo-Vandar/releases)
[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg?logo=python&style=for-the-badge&color=FFD43B)](https://www.python.org/)
[![Kindle Compatible](https://img.shields.io/badge/format-Kindle%20MOBI-orange.svg?style=for-the-badge)](https://www.amazon.com/gp/feature.html?ie=UTF8&docId=1000765211)

---

## 📖 The Kindle Dictionary Blueprint

Official documentation on building custom Kindle dictionaries is notoriously sparse, fragmented, and outdated. This repository serves as a modern, open-source boilerplate to demystify Kindle's proprietary formatting standards. 

By analyzing this codebase, you can easily adapt the pipeline to compile high-fidelity dictionaries for any language pair. The project highlights four essential implementation areas:

1. **XHTML Schema Compliance (`idx` Namespace)**: Demonstrates how to structure dictionary entries using standard Kindle markup elements—such as `<idx:entry>`, `<idx:orth>`, and `<idx:infl>`—to allow Kindle's indexing system to parse and index inflections successfully.
2. **OPF Package Metadata Configuration**: Shows how to properly structure target and source languages (`DictionaryInLanguage`, `DictionaryOutLanguage`) and declare lookup indexes inside the mandatory `<x-metadata>` block of the `.opf` manifest.
3. **Database Integration & Normalization**: Standardizes, deduplicates, and merges unstructured source data (from SQLite or JSON formats) into a unified relational database before sharding the output into size-compliant XHTML files to prevent compiler crashes.
4. **Embedded KindleGen Toolchain Invocation**: Automatically resolves and calls Amazon's Kindle compiler from a Python environment, ensuring compatibility on both local setups and headless CI/CD runner pipelines.

---

## 📐 System Architecture & Data Flow

This diagram illustrates how raw source lexicons are ingested, consolidated, formatted into Kindle-compliant markups, and compiled into optimized dictionary files:

```text
 ┌────────────────────────────────────────────────────────────────────────┐
 │                        DATA PIPELINE ARCHITECTURE                      │
 └────────────────────────────────────────────────────────────────────────┘

  [ Raw Lexicons ]        [ Normalization & DB ]         [ Document Generation ]
  ┌──────────────┐        ┌────────────────────┐         ┌─────────────────────┐
  │ MinhasKamal  │───┐    │                    │         │  XHTML Sharding     │
  └──────────────┘   │    │                    │         │  (Max 1000 entries) │
  ┌──────────────┐   │    │                    │         │  ┌────────────────┐ │
  │  Aparajeyo   │───┼───>│ kindle_dictionary_ │────────>│  │ content_N.html │ │
  └──────────────┘   │    │     builder.py     │         │  └────────────────┘ │
  ┌──────────────┐   │    │                    │         │  - xmlns:idx markup │
  │    Ridmik    │───┤    │                    │         │  - <idx:entry> tags │
  └──────────────┘   │    │  - SQLite Staging  │         └──────────┬──────────┘
  ┌──────────────┐   │    │    (lexicon.db)    │                    │
  │    Ankur     │───┤    │  - Deduplication   │                    ▼
  └──────────────┘   │    │  - Normalization   │         ┌─────────────────────┐
  ┌──────────────┐   │    └────────────────────┘         │ OPF Meta / Nav XML  │
  │  Wiktionary  │───┤                                   │ - dict.opf          │
  └──────────────┘   │                                   │ - nav.html          │
  ┌──────────────┐   │                                   └──────────┬──────────┘
  │   Hunspell   │───┤                                              │
  └──────────────┘   │                                              ▼
  ┌──────────────┐   │                                   ┌─────────────────────┐
  │   BoiBhai    │───┤                                   │  Tri-Directional    │
  └──────────────┘   │                                   │  Kindle MOBI Books  │
  ┌──────────────┐   │                                   └──────────┬──────────┘
  │MuntashirAkon │───┘                                              │
  └──────────────┘                                                  │
                                                                    ▼
  [ Compiler Invocation ]                                [ Distribution ]
  ┌────────────────────────────────────────────────┐     ┌─────────────────────┐
  │           Kindle Previewer 3 Toolchain         │     │  Direct Sideload    │
  │  ┌──────────────────────────────────────────┐  │     │  (USB to device)    │
  │  │      Embedded kindlegen Compiler         │  │     └──────────▲──────────┘
  │  └────────────────────┬─────────────────────┘  │                │
  │                       │                        ├────────────────┘
  │                       ▼                        │
  │  ┌──────────────────────────────────────────┐  │     ┌─────────────────────┐
  │  │        High-Fidelity .MOBI Outputs       │──┼────>│   GitHub Releases   │
  │  │  - Shobdo_Vandar_en-bn_v1.5.1.mobi       │  │     │   (Automated CI)    │
  │  │  - Shobdo_Vandar_bn-en_v1.5.1.mobi       │  │     └─────────────────────┘
  │  │  - Shobdo_Vandar_bn-bn_v1.5.1.mobi       │  │
  │  └──────────────────────────────────────────┘  │
  └────────────────────────────────────────────────┘
```

---

## 🧠 Project Origins & AI Collaboration

This repository began as a personal hobby project. The goal was twofold: to gain a practical understanding of writing robust Python scripts and managing GitHub CI/CD workflows, and to create an accurate, highly responsive dictionary for reading Bangla literature on a Kindle.

The codebase was developed in close collaboration with an AI pair-programmer:
* **Assistant:** **Antigravity** (an agentic AI developer)
* **Cognitive Model:** **Gemini 3.5 Flash** (responsible for parsing optimizations, SQL querying structures, and automated tests)

This project demonstrates how pairing standard developer workflows with AI capabilities can produce reliable, production-ready output from fragmented, legacy documentations.

---

## 📥 Downloading Compiled Dictionaries

You do not need to build these files manually. The compilation pipeline runs automatically on every release, compiling and attaching ready-to-use `.mobi` files to the release page.

1. Navigate to the **[Releases](https://github.com/tahmidxp96/Shobdo-Vandar/releases)** page.
2. Download the dictionary binary you need from the assets section:
   * **`Shobdo_Vandar_en-bn_v1.5.1.mobi`** (English-to-Bangla: **94,348 entries**, ~10.4 MB)
   * **`Shobdo_Vandar_bn-en_v1.5.1.mobi`** (Bangla-to-English: **50,928 entries**, ~6.4 MB)
   * **`Shobdo_Vandar_bn-bn_v1.5.1.mobi`** (Bangla-to-Bangla: **46,552 entries**, ~9.2 MB)

---

## 📲 Installation on Kindle Devices

To load the compiled dictionaries onto any physical Kindle (including Kindle Paperwhite, Oasis, Scribe, and Basic models):

1. **Connect your Kindle** to your computer via a USB cable.
2. Open your system file manager and navigate to the mounted **Kindle** directory.
3. Copy the downloaded `.mobi` files into the Kindle's **`documents/dictionaries/`** folder:
   ```text
   Kindle/
   └── documents/
       └── dictionaries/
            ├── Shobdo_Vandar_en-bn_v1.5.1.mobi
            ├── Shobdo_Vandar_bn-en_v1.5.1.mobi
            └── Shobdo_Vandar_bn-bn_v1.5.1.mobi
   ```
4. **Safely eject** the Kindle from your computer.
5. **Activate the Dictionaries:**
   * On your device, go to **Settings ➔ Language & Dictionaries ➔ Dictionaries**.
   * Under the **English** language category, select **Shobdo Vandar English-to-Bangla Dictionary**.
   * Under the **Bangla** language category, select **Shobdo Vandar Bangla-to-English Dictionary** and **Shobdo Vandar Bangla-to-Bangla Dictionary**.
6. Highlight any English or Bangla word inside an e-book to view instant, context-rich definitions.

---

## 🛠️ Local Development & Manual Compilation

If you want to modify source definitions, add custom glossaries, or run the compilation suite locally, follow these steps:

### Prerequisites
* **Python 3.8+**
* **Kindle Previewer 3** (must be installed on the host machine).
  * [Download Kindle Previewer 3 macOS / Windows Installer](https://d2bzeorukaqrvt.cloudfront.net/KindlePreviewerInstaller.pkg)
  * The Python builder script automatically resolves the installation and detects the embedded `kindlegen` binary.

### Execution Guide

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/tahmidxp96/Shobdo-Vandar.git
   cd Shobdo-Vandar
   ```

2. **Run the Complete Build Suite** (performs database staging, consolidation, and full MOBI generation for all 3 directions):
   ```bash
   python3 kindle_dictionary_builder.py
   ```

3. **Recompile MOBI Binaries Only** (skips raw ingestion stages for rapid pipeline prototyping):
   ```bash
   python3 kindle_dictionary_builder.py -c
   ```

4. **Preview Dictionary Layouts Directly in Terminal**:
   You can verify how an entry is displayed on Kindle popups and full-page layouts using the terminal lookup previewer:
   ```bash
   python3 kindle_dictionary_builder.py -p "benevolent"
   # Or monolingual lookup
   python3 kindle_dictionary_builder.py -p "হিতৈষী"
   ```

---

## 📊 Lexicon Architecture & Coverage

The builder compiles custom dictionaries by normalising data across multiple staging references:

| Source | Records Processed | Translation Pathway | Primary Lexical Characteristics | Link | License |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Aparajeyo** | 186,776 | English ➔ Bangla | Comprehensive synonym groups and parts of speech | [Aparajeyo Community](https://facebook.com/groups/aparajeyobangla) | Open Source |
| **MinhasKamal** | 93,421 | English ➔ Bangla | Standard colloquial vocabulary mapping | [MinhasKamal/BengaliDictionary](https://github.com/MinhasKamal/BengaliDictionary) | MIT License |
| **Ridmik** | 13,474 | Bangla ➔ English | Standardized lexical mappings | [Ridmik Keyboard](https://github.com/ridmik) | MIT License |
| **Ankur** | 1,984 | English ➔ Bangla | Traditional terminology vocabulary | [Ankur Project](http://www.ankur.org.bd/) | GPL License |
| **Wiktionary** | 24 | English ➔ Bangla | Collaborative contextual examples & POS tags | [Wiktionary](https://www.wiktionary.org/) | CC-BY-SA 3.0 |
| **Hunspell** | 30 | Bangla ➔ English | Orthographical verified spelling lemmas | [Hunspell BN](https://github.com/tushar-rishav/hunspell-bn) | LGPL / GPL |
| **BoiBhai** | 11 | Bangla ➔ Bangla | Crowdsourced native monolingual glossary | [BoiBhai bn-dict](https://github.com/BoiBhai/bn-dict-database) | Open Source |
| **MuntashirAkon** | 46,551 | Bangla ➔ Bangla | Comprehensive HTML definitions, POS, and Sanskrit etymology | [MuntashirAkon/BanglaDictionary](https://github.com/MuntashirAkon/BanglaDictionary) | GPL License |

### Consolidated Output Statistics:
* **English-to-Bangla (`en-bn`)**: `94,348` unique entries
* **Bangla-to-English (`bn-en`)**: `50,928` unique entries
* **Bangla-to-Bangla (`bn-bn`)**: `46,552` unique entries
* **Total Combined Database**: **`191,828`** deduplicated, high-fidelity words

---

## 🤖 CI/CD Automation

This repository utilizes GitHub Actions (`.github/workflows/release.yml`) for continuous deployment. 

Whenever a release version tag (e.g., `v1.5.1`) is pushed to the repository:
1. A fresh macOS environment is provisioned on GitHub runners.
2. The latest **Kindle Previewer 3** package is dynamically fetched and installed.
3. The `kindle_dictionary_builder.py` script initializes the ingestion pipeline, performs standardizations, and runs the MOBI compilation for all three targets.
4. The workflow bundles the completed `.mobi` binaries and publishes them directly to your repository's Releases page.

---

## 📄 License & Attribution

The builder and compilation pipeline scripts are distributed under the **MIT License**. All raw lexicographical resources remain the intellectual property of their respective authors and projects:

* **MinhasKamal (Bangla Dictionary):** Large-scale English-to-Bangla translation mappings hosted at the [MinhasKamal/BengaliDictionary](https://github.com/MinhasKamal/BengaliDictionary) repository (licensed under the permissive MIT License).
* **Aparajeyo Dictionary:** Compiled English-to-Bangla and Bangla-to-English database compiled by Nazmul Hossain Nihal and the open-source [Aparajeyo Bangla Express Community](https://facebook.com/groups/aparajeyobangla).
* **Ridmik Dictionary:** Open-source Bangla-to-English dictionary assets by Ridmik Labs, creators of the open-source [Ridmik Keyboard](https://github.com/ridmik).
* **Ankur Dictionary:** English-to-Bangla translation terminology database compiled by the open-source [Ankur Bangla Project](http://www.ankur.org.bd/) (distributed under the GPL License).
* **Wiktionary Bilingual Dataset:** Collaborative community-driven definitions and bilingual translations from [Wiktionary](https://www.wiktionary.org/) (distributed under the CC-BY-SA 3.0 License).
* **Hunspell Spelling Dictionary:** Standardized Bengali spell-checker lemmas and orthographical reference definitions from [Hunspell](https://hunspell.github.io/) / [hunspell-bn](https://github.com/tushar-rishav/hunspell-bn) (distributed under the LGPL/GPL License).
* **BoiBhai Monolingual Dictionary:** Crowdsourced and collaborative Bengali-to-Bengali monolingual dictionary containing pronunciation, etymology, ontology, and native definition data from [BoiBhai bn-dict-database](https://github.com/BoiBhai/bn-dict-database).
* **MuntashirAkon Monolingual Dictionary:** Extensive Bangla-to-Bangla monolingual definitions and grammatical etymologies from [MuntashirAkon/BanglaDictionary](https://github.com/MuntashirAkon/BanglaDictionary) (distributed under the GNU GPL License).
