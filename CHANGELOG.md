# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2026-05-24

### Added
- Added three new staging sources: Ankur, Wiktionary, and Hunspell
- Added rule-based BanglaMorphologyEngine for automatic suffix inflections
- Added priority-based fallback merge strategy in build_master_lexicon
- Added Georgia serif premium Oxford e-ink typography and phonetic IPA formatting
- Added custom branding and Tahmid creator metadata

### Changed
- Changed root README and LICENSE files to update licensing attributions and statistics.

### Removed
- Removed obsolete BanglaAcademy reference folder

---

## [1.2.0] - 2026-05-21

### Added
- Added an ASCII architecture diagram to the README illustrating data flow from raw lexicons through SQLite normalization to sharded XHTML files and KindleGen MOBI generation.
- Added badges for release version, total downloads, Python compatibility, and Kindle format to README.

### Changed
- Revamped the README documentation completely to be more professional, modern, and detailed.
- Polished the GitHub Actions release workflow (`.github/workflows/release.yml`) for robust and silent automated installation and verification of the Kindle Previewer compiler on macOS.

---

## [1.1.0] - 2026-05-21

### Added
- **Native Dictionary Lookup support**: Added the official `<x-metadata>` wrapper inside the `dict.opf` package file containing `DictionaryInLanguage`, `DictionaryOutLanguage`, and `DefaultLookupIndex` tags.
- **AI Collaboration Recognition**: Added origin story and details of the AI pair-programming collaboration with Antigravity (powered by Gemini 3.5 Flash).

### Fixed
- **XML Namespace prefix binding**: Corrected namespace prefix from `xmlns:dx` to `xmlns:idx` inside all sharded XHTML files, allowing KindleGen to compile entry elements (`idx:entry`, `idx:orth`, `idx:infl`) without warnings or catalog failures.
- **Lowercased BookType**: Standardized the `BookType` metadata to lowercase `dictionary` for flawless indexing and cataloging on Kindle systems.
- **README badges links**: Corrected GitHub repository names from `Shobdo_Vandar` to `Shobdo-Vandar` in shields.io badges to resolve load errors.

### Removed
- **Heavy Installers**: Deleted large third-party setup files (`Aparajeyo Bangla Express - Dictionary.msi` and `aparajeyo_lite.zip`) from tracking and the workspace, successfully removing repository bloat.

---

## [1.0.0] - 2026-05-21

### Added
- **Kindle Dictionary Builder Pipeline**: Created the unified python pipeline `kindle_dictionary_builder.py` providing SQLite data ingestion, consolidation, normalisation, and sharding.
- **Staging Database Schema**: Relational SQLite database `lexicon.db` featuring ingestion tracking, duplicate reduction, morphological inflections, and source attribution metrics.
- **CI/CD Automation**: Automated release workflow triggering on tag push, downloading Amazon's compiler silently, and packaging compiled `.mobi` assets.
- **Git Ignore Config**: Set up workspace file ignores for compiler temporary products and platform binaries.
