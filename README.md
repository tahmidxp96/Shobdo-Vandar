# Shondo vandar (শব্দ ভান্ডার) 📚🇧🇩

A developer-centric reference project and high-performance compilation pipeline showing how to build custom, search-compliant Kindle bilingual dictionaries from raw lexicographical datasets.

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
 │ MinhasKamal  │───────>│                    │         │  XHTML Sharding     │
 └──────────────┘        │                    │         │  (Max 1000 entries) │
 ┌──────────────┐        │                    │         │  ┌────────────────┐ │
 │  Aparajeyo   │───────>│ kindle_dictionary_ │────────>│  │ content_N.html │ │
 └──────────────┘        │     builder.py     │         │  └────────────────┘ │
 ┌──────────────┐        │                    │         │  - xmlns:idx markup │
 │    Ridmik    │───────>│                    │         │  - <idx:entry> tags │
 └──────────────┘        │                    │         └──────────┬──────────┘
 ┌──────────────┐        │                    │                    │
 │ Bangla Acad. │───────>│  - SQLite Staging  │                    ▼
 └──────────────┘        │    (lexicon.db)    │         ┌─────────────────────┐
                         │  - Deduplication   │         │ OPF Meta / Nav XML  │
                         │  - Normalization   │         │ - dict.opf          │
                         └────────────────────┘         │ - <x-metadata> tags │
                                                        │ - nav.html          │
                                                        └──────────┬──────────┘
                                                                   │
                                                                   ▼
 [ Compiler Invocation ]                                [ Distribution ]
 ┌────────────────────────────────────────────────┐     ┌─────────────────────┐
 │           Kindle Previewer 3 Toolchain         │     │  Direct Sideload    │
 │  ┌──────────────────────────────────────────┐  │     │  (USB to device)    │
 │  │      Embedded kindlegen Compiler        │  │     └──────────▲──────────┘
 │  └────────────────────┬─────────────────────┘  │                │
 │                       │                        ├────────────────┘
 │                       ▼                        │
 │  ┌──────────────────────────────────────────┐  │     ┌─────────────────────┐
 │  │        High-Fidelity .MOBI Output        │──┼────>│   GitHub Releases   │
 │  │  - en-bn.mobi (~94.4k entries, 10.4 MB)  │  │     │   (Automated CI)    │
 │  │  - bn-en.mobi (~50.9k entries,  6.4 MB)  │  │     └─────────────────────┘
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
   * **`en-bn.mobi`** (English-to-Bangla: **94,347 entries**, ~10.4 MB)
   * **`bn-en.mobi`** (Bangla-to-English: **50,919 entries**, ~6.4 MB)

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
           ├── en-bn.mobi
           └── bn-en.mobi
   ```
4. **Safely eject** the Kindle from your computer.
5. **Activate the Dictionaries:**
   * On your device, go to **Settings ➔ Language & Dictionaries ➔ Dictionaries**.
   * Under the **English** language category, select **High-Quality English-to-Bangla Kindle Dictionary**.
   * Under the **Bangla** language category, select **Advanced Bangla-to-English Learner's Dictionary**.
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

2. **Run the Complete Build Suite** (performs database staging, consolidation, and full MOBI generation):
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
   ```

---

## 📊 Lexicon Architecture & Coverage

The builder compiles custom bilingual dictionaries by normalising data across multiple staging references:

| Source | Records Processed | Translation Pathway | Primary Lexical Characteristics |
| :--- | :--- | :--- | :--- |
| **Aparajeyo** | 186,776 | English ➔ Bangla | Comprehensive synonym groups and parts of speech |
| **MinhasKamal** | 93,421 | English ➔ Bangla | Standard colloquial vocabulary mapping |
| **Ridmik** | 13,474 | Bangla ➔ English | Standardized lexical mappings |
| **Bangla Academy** | Reference | Both | Direct orthographical and spelling validations |

### Consolidated Output Statistics:
* **Bangla-to-English (`bn-en`)**: `50,919` unique entries
* **English-to-Bangla (`en-bn`)**: `94,347` unique entries
* **Total Combined Database**: **`145,266`** deduplicated, high-fidelity words

---

## 🤖 CI/CD Automation

This repository utilizes GitHub Actions (`.github/workflows/release.yml`) for continuous deployment. 

Whenever a release version tag (e.g., `v1.2.0`) is pushed to the repository:
1. A fresh macOS environment is provisioned on GitHub runners.
2. The latest **Kindle Previewer 3** package is dynamically fetched and installed.
3. The `kindle_dictionary_builder.py` script initializes the ingestion pipeline, performs standardizations, and runs the MOBI compilation.
4. The workflow bundles the completed `.mobi` binaries and publishes them directly to your repository's Releases page.

---

## 📄 License & Attribution

All raw lexicographical resources remain the intellectual property of their respective authors and projects (Aparajeyo, MinhasKamal, Ridmik, and Bangla Academy). The builder and compilation pipeline scripts are distributed under the **MIT License**.
