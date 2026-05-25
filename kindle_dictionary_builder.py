#!/usr/bin/env python3
# Copyright (c) 2026 Tahmid
# This software is released under the MIT License.
# See the LICENSE file in the project root for full license details.
"""
Interactive & Standalone Bilingual Kindle Dictionary Builder 📚🇧🇩
A high-performance pipeline to compile en->bn and bn->en Kindle-compatible custom dictionaries.
"""

import os
import sys
import re
import csv
import json
import time
import sqlite3
import argparse
from xml.sax.saxutils import escape as xml_escape

DB_NAME = 'lexicon.db'
BUILD_DIR = './build'

# ANSI Color Codes for Premium Terminal Aesthetics
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def log_info(msg):
    print(f"{Colors.BLUE}[INFO]{Colors.END} {msg}")

def log_success(msg):
    print(f"{Colors.GREEN}[SUCCESS]{Colors.END} {msg}")

def log_warning(msg):
    print(f"{Colors.YELLOW}[WARNING]{Colors.END} {msg}")

def log_error(msg):
    print(f"{Colors.RED}[ERROR]{Colors.END} {msg}", file=sys.stderr)

def log_step(step_num, title):
    print(f"\n{Colors.BOLD}{Colors.HEADER}--- Step {step_num}: {title} ---{Colors.END}")

class BanglaNormalizer:
    @staticmethod
    def normalize(text):
        """Normalizes raw Bangla text by standardizing Unicode characters, stripping punctuation and cleaning variants."""
        if not text:
            return ""
        
        # 1. Strip whitespace
        text = text.strip()
        
        # 2. Remove Kindle/dictionary artifacts like pipe symbols (common tail marker in some formats)
        text = text.replace('|', '')
        
        # 3. Standardize Bangla vowel signs (specifically O-KAR 'ো' and OU-KAR 'ৌ' NFC conversion)
        # Replacing composite forms (e.g., E-KAR + AA-KAR = O-KAR) with single Unicode points
        text = re.sub(r'\u09c7\u09be', '\u09cb', text) # E-kar + Aa-kar -> O-kar
        text = re.sub(r'\u09c7\u09d7', '\u09cc', text) # E-kar + Gullah -> Ou-kar
        
        # 4. Remove Zero-Width Joiner (ZWJ) and Zero-Width Non-Joiner (ZWNJ) if not visually significant
        text = text.replace('\u200d', '') # ZWJ
        text = text.replace('\u200c', '') # ZWNJ
        
        # 5. Remove common trailing punctuation and danda (।), double danda, brackets, quotes
        punctuation_list = ['।', ',', '.', '?', '!', ':', ';', '(', ')', '-', '[', ']', '"', "'"]
        for punc in punctuation_list:
            text = text.replace(punc, '')
        
        return text.strip()

    @staticmethod
    def english_to_bangla_digits(text):
        """Converts English digits to Bangla numerals."""
        digits_map = {'0': '০', '1': '১', '2': '২', '3': '৩', '4': '৪', '5': '৫', '6': '৬', '7': '৭', '8': '৮', '9': '৯'}
        return "".join(digits_map.get(char, char) for char in text)


class EnglishMorphologyEngine:
    # Irregular dictionaries for direct mapping override
    IRREGULAR_VERBS = {
        'teach': ['teaches', 'taught', 'teaching'],
        'write': ['writes', 'wrote', 'written', 'writing'],
        'go': ['goes', 'went', 'gone', 'going'],
        'run': ['runs', 'ran', 'running']
    }
    
    IRREGULAR_NOUNS = {
        'child': ['children'],
        'mouse': ['mice'],
        'foot': ['feet']
    }

    @classmethod
    def generate_inflections(cls, lemma, pos):
        """Generates inflected forms for a base lemma based on its Part of Speech (POS)."""
        lemma = lemma.strip().lower()
        forms = set()
        
        # POS-specific rules
        if pos in ['verb', 'v']:
            if lemma in cls.IRREGULAR_VERBS:
                return cls.IRREGULAR_VERBS[lemma]
            
            # Regular verbs
            # 3rd Person Present Singular (-s / -es)
            if lemma.endswith(('sh', 'ch', 's', 'x', 'z', 'o')):
                forms.add(lemma + 'es')
            elif lemma.endswith('y') and not lemma[-2] in 'aeiou':
                forms.add(lemma[:-1] + 'ies')
            else:
                forms.add(lemma + 's')
                
            # Gerund / Present Participle (-ing)
            if lemma.endswith('e') and not lemma.endswith('ee'):
                forms.add(lemma[:-1] + 'ing')
            elif lemma.endswith('p') and lemma[-2] in 'aeiou' and not lemma[-3] in 'aeiou':
                forms.add(lemma + 'ping') # e.g. stop -> stopping
            else:
                forms.add(lemma + 'ing')
                
            # Past / Past Participle (-ed)
            if lemma.endswith('e'):
                forms.add(lemma + 'd')
            elif lemma.endswith('y') and not lemma[-2] in 'aeiou':
                forms.add(lemma[:-1] + 'ied')
            else:
                forms.add(lemma + 'ed')
                
        elif pos in ['noun', 'n']:
            if lemma in cls.IRREGULAR_NOUNS:
                return cls.IRREGULAR_NOUNS[lemma]
                
            # Regular plural rules
            if lemma.endswith(('sh', 'ch', 's', 'x', 'z')):
                forms.add(lemma + 'es')
            elif lemma.endswith('y') and not lemma[-2] in 'aeiou':
                forms.add(lemma[:-1] + 'ies')
            elif lemma.endswith('fe'):
                forms.add(lemma[:-2] + 'ves')
            elif lemma.endswith('f') and not lemma.endswith('ff'):
                forms.add(lemma[:-1] + 'ves')
            else:
                forms.add(lemma + 's')
                
        elif pos in ['adjective', 'adj']:
            # Comparative/Superlative suffixes
            if lemma.endswith('y') and not lemma[-2] in 'aeiou':
                forms.add(lemma[:-1] + 'ier')
                forms.add(lemma[:-1] + 'iest')
            elif lemma.endswith('e'):
                forms.add(lemma + 'r')
                forms.add(lemma + 'st')
            else:
                forms.add(lemma + 'er')
                forms.add(lemma + 'est')
        
        return list(forms)


class BanglaMorphologyEngine:
    NOUN_SUFFIXES = ['টি', 'টা', 'গুলো', 'গুলি', 'দের', 'র', 'এর', 'কে', 'তে', 'এ', 'য়ে']
    
    @classmethod
    def generate_inflections(cls, lemma):
        """Generates common Bangla inflections/case endings for a base lemma."""
        lemma = lemma.strip()
        forms = set()
        if len(lemma) < 2:
            return []
        for suffix in cls.NOUN_SUFFIXES:
            if not lemma.endswith(suffix):
                forms.add(lemma + suffix)
        return list(forms)


def init_database(db_name=DB_NAME):
    """Initializes the SQLite database with staging and master tables."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # 1. Source Ingestion Table (Provenance & Audit Trail)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS source_ingestion (
        ingestion_id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_name TEXT NOT NULL,
        source_license TEXT NOT NULL,
        headword_raw TEXT NOT NULL,
        lookup_direction TEXT NOT NULL,   -- 'en-bn' or 'bn-en'
        pos_raw TEXT,
        sense_text_raw TEXT NOT NULL,
        example_raw TEXT,
        import_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    # 2. Master Lexicon Table (Deduplicated, Sense-Clustered & Cleaned)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS master_lexicon (
        lemma_id INTEGER PRIMARY KEY AUTOINCREMENT,
        lemma TEXT NOT NULL,
        normalized_lemma TEXT NOT NULL,
        lookup_direction TEXT NOT NULL,   -- 'en-bn' or 'bn-en'
        pos TEXT,
        senses_json TEXT NOT NULL,        -- JSON array of structured Senses
        inflections_json TEXT,            -- JSON array of hidden inflection aliases
        source_attributions TEXT          -- comma-separated source credits
    );
    """)
    
    # Add Index for high performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_source_ingestion_hw ON source_ingestion (headword_raw, lookup_direction);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_master_lexicon_hw ON master_lexicon (lemma, lookup_direction);")
    
    conn.commit()
    conn.close()
    log_success("Database schemas and indices verified successfully!")


def populate_staging(db_name=DB_NAME):
    """Reads actual dictionary files from MinhasKamal, Ridmik, and Aparajeyo, and ingests them into staging."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # Clear previous run
    cursor.execute("DELETE FROM source_ingestion")
    conn.commit()
    
    # 1. Ingest MinhasKamal CSV
    minhas_path = 'MinhasKamal/BengaliDictionary_93.csv'
    minhas_records = []
    if os.path.exists(minhas_path):
        log_info("Reading MinhasKamal CSV...")
        with open(minhas_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2 and row[0].strip() and row[1].strip():
                    minhas_records.append((
                        'MinhasKamal',
                        'GPLv3',
                        row[0].strip(),
                        'en-bn',
                        None,
                        row[1].strip(),
                        None
                    ))
        log_info(f"Parsed {len(minhas_records):,} records from MinhasKamal CSV.")
    else:
        log_warning("MinhasKamal CSV not found at 'MinhasKamal/BengaliDictionary_93.csv'!")

    # 2. Ingest Ridmik SQLite
    ridmik_path = 'Ridmik/dictionary'
    ridmik_records = []
    if os.path.exists(ridmik_path):
        log_info("Reading Ridmik SQLite DB...")
        try:
            r_conn = sqlite3.connect(ridmik_path)
            r_cursor = r_conn.cursor()
            r_cursor.execute("SELECT en_word, bn_word FROM words")
            for en, bn in r_cursor.fetchall():
                if en and bn and en.strip() and bn.strip():
                    ridmik_records.append((
                        'Ridmik',
                        'Open Source',
                        en.strip(),
                        'en-bn',
                        None,
                        bn.strip(),
                        None
                    ))
            r_conn.close()
            log_info(f"Parsed {len(ridmik_records):,} records from Ridmik SQLite DB.")
        except Exception as e:
            log_error(f"Failed to read Ridmik SQLite: {e}")
    else:
        log_warning("Ridmik SQLite DB not found at 'Ridmik/dictionary'!")

    # 3. Ingest Aparajeyo Source
    aparajeyo_en_path = 'Aparajeyo/entobn.abedb'
    aparajeyo_bn_path = 'Aparajeyo/bntoen.abedb'
    aparajeyo_records = []
    
    # EN-to-BN
    if os.path.exists(aparajeyo_en_path):
        log_info("Reading Aparajeyo EN-BN (UTF-16)...")
        with open(aparajeyo_en_path, 'r', encoding='utf-16') as f:
            for line in f:
                if '=' in line and not line.startswith('['):
                    parts = line.strip().split('=', 1)
                    if len(parts) == 2 and parts[0].strip() and parts[1].strip():
                        aparajeyo_records.append((
                            'Aparajeyo',
                            'Open Source',
                            parts[0].strip(),
                            'en-bn',
                            None,
                            parts[1].strip(),
                            None
                        ))
        log_info(f"Parsed EN-BN records from Aparajeyo.")
    else:
        log_warning("Aparajeyo EN-BN abedb file not found!")
        
    # BN-to-EN
    aparajeyo_bn_count = 0
    if os.path.exists(aparajeyo_bn_path):
        log_info("Reading Aparajeyo BN-EN (UTF-16)...")
        with open(aparajeyo_bn_path, 'r', encoding='utf-16') as f:
            for line in f:
                if '=' in line and not line.startswith('['):
                    parts = line.strip().split('=', 1)
                    if len(parts) == 2 and parts[0].strip() and parts[1].strip():
                        aparajeyo_records.append((
                            'Aparajeyo',
                            'Open Source',
                            parts[0].strip(),
                            'bn-en',
                            None,
                            parts[1].strip(),
                            None
                        ))
                        aparajeyo_bn_count += 1
        log_info(f"Parsed {aparajeyo_bn_count:,} BN-EN records from Aparajeyo.")
    else:
        log_warning("Aparajeyo BN-EN abedb file not found!")

    # 4. Ingest Ankur CSV
    ankur_path = 'Ankur/ankur_dictionary.csv'
    ankur_records = []
    if os.path.exists(ankur_path):
        log_info("Reading Ankur CSV...")
        with open(ankur_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None) # skip header
            for row in reader:
                if len(row) >= 2 and row[0].strip() and row[1].strip():
                    ankur_records.append((
                        'Ankur',
                        'GPL',
                        row[0].strip(),
                        'en-bn',
                        None,
                        row[1].strip(),
                        None
                    ))
        log_info(f"Parsed {len(ankur_records):,} records from Ankur CSV.")
    else:
        log_warning("Ankur CSV not found at 'Ankur/ankur_dictionary.csv'!")

    # 5. Ingest Wiktionary JSON
    wiktionary_path = 'Wiktionary/wiktionary_dictionary.json'
    wiktionary_records = []
    if os.path.exists(wiktionary_path):
        log_info("Reading Wiktionary JSON...")
        with open(wiktionary_path, 'r', encoding='utf-8') as f:
            try:
                w_data = json.load(f)
                for item in w_data:
                    word = item.get('word', '').strip()
                    pos = item.get('pos', '').strip()
                    pron = item.get('pronunciation', '').strip()
                    meanings = ", ".join(item.get('meanings', []))
                    syns = ", ".join(item.get('synonyms', []))
                    ex_en = item.get('example_en', '').strip()
                    ex_bn = item.get('example_bn', '').strip()
                    
                    # format example string with bilingual and synonym info if available
                    ex_str = ""
                    if pron:
                        ex_str += f"pron: {pron} | "
                    if ex_en:
                        ex_str += f"en: {ex_en}"
                        if ex_bn:
                            ex_str += f" | bn: {ex_bn}"
                    if syns:
                        if ex_str and ex_str != f"pron: {pron} | ":
                             ex_str += f" [syns: {syns}]"
                        else:
                             ex_str += f"[syns: {syns}]"
                             
                    if word and meanings:
                        wiktionary_records.append((
                            'Wiktionary',
                            'CC-BY-SA 3.0',
                            word,
                            'en-bn',
                            pos if pos else None,
                            meanings,
                            ex_str if ex_str else None
                        ))
            except Exception as e:
                log_error(f"Failed to parse Wiktionary JSON: {e}")
        log_info(f"Parsed {len(wiktionary_records):,} records from Wiktionary JSON.")
    else:
        log_warning("Wiktionary JSON not found at 'Wiktionary/wiktionary_dictionary.json'!")

    # 6. Ingest Hunspell DIC
    hunspell_path = 'Hunspell/bangla_spelling.dic'
    hunspell_records = []
    if os.path.exists(hunspell_path):
        log_info("Reading Hunspell DIC...")
        with open(hunspell_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines[1:]:
                word = line.strip().split('/')[0].strip() # strip flags
                if word:
                    # Ingest Hunspell as verified spelling reference
                    hunspell_records.append((
                        'Hunspell',
                        'LGPL',
                        word,
                        'bn-en',
                        None,
                        'Verified Spelling Lemma',
                        None
                    ))
        log_info(f"Parsed {len(hunspell_records):,} records from Hunspell DIC.")
    else:
        log_warning("Hunspell DIC not found at 'Hunspell/bangla_spelling.dic'!")

    # 7. Ingest BoiBhai JSON
    boibhai_path = 'BoiBhai/boibhai_dictionary.json'
    boibhai_records = []
    if os.path.exists(boibhai_path):
        log_info("Reading BoiBhai JSON...")
        with open(boibhai_path, 'r', encoding='utf-8') as f:
            try:
                b_data = json.load(f)
                for item in b_data:
                    word = item.get('word', '').strip()
                    pos = item.get('pos', '').strip()
                    pron = item.get('pronunciation', '').strip()
                    etym = item.get('etymology', '').strip()
                    meanings = ", ".join(item.get('meanings', []))
                    syns = ", ".join(item.get('synonyms', []))
                    ex = item.get('example', '').strip()
                    
                    ex_str = ""
                    if pron:
                        ex_str += f"pron: {pron} | "
                    if ex:
                        ex_str += f"ex: {ex}"
                    if etym:
                        if ex_str and ex_str != f"pron: {pron} | ":
                            ex_str += f" | etym: {etym}"
                        else:
                            ex_str += f"etym: {etym}"
                    if syns:
                        if ex_str and ex_str != f"pron: {pron} | ":
                            ex_str += f" [syns: {syns}]"
                        else:
                            ex_str += f"[syns: {syns}]"
                            
                    if word and meanings:
                        boibhai_records.append((
                            'BoiBhai',
                            'Open Source',
                            word,
                            'bn-bn',
                            pos if pos else None,
                            meanings,
                            ex_str if ex_str else None
                        ))
            except Exception as e:
                log_error(f"Failed to parse BoiBhai JSON: {e}")
        log_info(f"Parsed {len(boibhai_records):,} records from BoiBhai JSON.")
    else:
        log_warning("BoiBhai JSON not found at 'BoiBhai/boibhai_dictionary.json'!")

    # Perform bulk inserts in transaction for high performance
    all_records = minhas_records + ridmik_records + aparajeyo_records + ankur_records + wiktionary_records + hunspell_records + boibhai_records
    if all_records:
        log_info(f"Inserting {len(all_records):,} raw records into source_ingestion table...")
        cursor.executemany("""
            INSERT INTO source_ingestion (source_name, source_license, headword_raw, lookup_direction, pos_raw, sense_text_raw, example_raw)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, all_records)
        conn.commit()
        log_success(f"Successfully ingested {len(all_records):,} total raw records!")
    else:
        log_warning("No source files were found, and no records were ingested.")
        
    conn.close()


def normalize_meaning(text, direction):
    """Normalizes definition meanings: Bangla normalization for en-bn/bn-bn, lowercase/punctuation strip for bn-en."""
    if not text:
        return ""
    text = text.strip()
    if direction in ['en-bn', 'bn-bn']:
        return BanglaNormalizer.normalize(text)
    else:
        text = text.lower()
        punctuation_list = [',', '.', '?', '!', ':', ';', '(', ')', '-', '[', ']', '"', "'", '_', '/', '\\']
        for punc in punctuation_list:
            text = text.replace(punc, '')
        return text.strip()


def build_master_lexicon(db_name=DB_NAME):
    """Merges raw staging entries, normalizes them, clusters senses, generates inflections, and inserts into master_lexicon."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # Reset master
    cursor.execute("DELETE FROM master_lexicon")
    conn.commit()
    
    # Process Senses Grouped by Direction and Headword
    log_info("Grouping staging entries by headword and direction...")
    cursor.execute("""
        SELECT headword_raw, lookup_direction, GROUP_CONCAT(ingestion_id) 
        FROM source_ingestion
        GROUP BY LOWER(headword_raw), lookup_direction
    """)
    groups = cursor.fetchall()
    log_info(f"Found {len(groups):,} unique headwords to consolidate.")
    
    normalizer = BanglaNormalizer()
    morph_engine = EnglishMorphologyEngine()
    
    # Load curated contextual enrichments if file exists
    enrichments = {}
    enrichment_path = 'contextual_enrichments.json'
    if os.path.exists(enrichment_path):
        log_info("Discovered 'contextual_enrichments.json'. Loading premium contextual enrichments...")
        try:
            with open(enrichment_path, 'r', encoding='utf-8') as f:
                enrichments = json.load(f)
            log_success(f"Loaded curated enrichments for {len(enrichments)} words.")
        except Exception as e:
            log_error(f"Failed to load 'contextual_enrichments.json': {e}")
            
    batch = []
    count = 0
    start_time = time.time()
    
    # Query optimizer: Rather than 145k queries inside a loop, we fetch raw fields into memory
    # mapping ingestion_id -> details
    log_info("Caching ingestion audit trails in memory for O(N) merge...")
    cursor.execute("SELECT ingestion_id, source_name, pos_raw, sense_text_raw, example_raw FROM source_ingestion")
    ingestion_map = {row[0]: row[1:] for row in cursor.fetchall()}
    
    # Source Priority Map (Lower value = higher priority)
    SOURCE_PRIORITY = {
        'CuratedContexts': 1,
        'Wiktionary': 2,
        'BoiBhai': 3,
        'Ridmik': 4,
        'MinhasKamal': 5,
        'Aparajeyo': 6,
        'Ankur': 7,
        'Hunspell': 8
    }
    
    for raw_hw, direction, ingestion_ids_str in groups:
        ids = [int(x) for x in ingestion_ids_str.split(',')]
        
        # Sort ids by source priority
        ids = sorted(ids, key=lambda idx: SOURCE_PRIORITY.get(ingestion_map[idx][0], 99))
        
        lemma = raw_hw.replace('|', '').strip()
        normalized_lemma = normalizer.normalize(lemma) if direction in ['bn-en', 'bn-bn'] else lemma.strip().lower()
        
        senses = []
        pos_list = set()
        sources = set()
        
        # Check if we have hand-curated enrichments for this word
        hw_lookup = lemma.lower() if direction == 'en-bn' else lemma
        has_enrichment = direction == 'en-bn' and hw_lookup in enrichments
        
        if has_enrichment:
            curated_senses = enrichments[hw_lookup]
            sources.add("CuratedContexts")
            for idx, c_sense in enumerate(curated_senses):
                pos_label = c_sense.get('pos', 'unk')
                pos_list.add(pos_label)
                senses.append({
                    'sense_id': idx + 1,
                    'pos': pos_label,
                    'context': c_sense.get('context', ''),
                    'meanings': c_sense.get('meanings', []),
                    'example_en': c_sense.get('example_en', ''),
                    'example_bn': c_sense.get('example_bn', ''),
                    'source': 'CuratedContexts'
                })
                
        # Now process standard raw records
        active_source = None
        if senses:
            # CuratedContexts already loaded
            active_source = "CuratedContexts"
            
        for ing_id in ids:
            source, pos_raw, sense_raw, ex_raw = ingestion_map[ing_id]
            
            # Skip lower priority sources if we already have senses from a higher priority source
            if active_source is not None and source != active_source:
                continue
                
            sources.add(source)
            pos_label = pos_raw if pos_raw else "unk"
            pos_list.add(pos_label)
            
            # Extract pronunciation if embedded in example
            pron_val = ""
            ex_clean = ex_raw if ex_raw else ""
            if ex_clean.startswith("pron: "):
                parts = ex_clean.split(" | ", 1)
                if len(parts) == 2:
                    pron_val = parts[0].replace("pron: ", "").strip()
                    ex_clean = parts[1].strip()
                else:
                    pron_val = ex_clean.replace("pron: ", "").strip()
                    ex_clean = ""
            
            # If lookup direction is en-bn, strip out Latin characters and punctuation artifacts
            if direction == 'en-bn':
                sense_raw_clean = re.sub(r'[a-zA-Z\(\)\[\]\{\}\-\_\/\\]+', ' ', sense_raw)
                sense_raw_clean = re.sub(r'\s+', ' ', sense_raw_clean).strip()
            else:
                sense_raw_clean = sense_raw
            
            # Clean senses and split by comma or semi-colon
            cleaned_meanings = [m.strip() for m in re.split(r'[,;।]', sense_raw_clean) if m.strip()]
            
            # Gather all meanings accumulated in senses so far (curated + other raw sources)
            flat_accumulated_meanings = []
            for cs in senses:
                flat_accumulated_meanings.extend(cs['meanings'])
            
            # Normalize accumulated meanings for robust comparison
            flat_accumulated_norm = [normalize_meaning(m, direction) for m in flat_accumulated_meanings]
            
            deduped = []
            for m in cleaned_meanings:
                m_norm = normalize_meaning(m, direction)
                if not m_norm:
                    continue
                # Robust match: exact normalized match OR substring/containment check
                is_dup = False
                for cur_norm in flat_accumulated_norm:
                    if not cur_norm:
                        continue
                    if m_norm == cur_norm or m_norm in cur_norm or cur_norm in m_norm:
                        is_dup = True
                        break
                if not is_dup:
                    deduped.append(m)
            cleaned_meanings = deduped
            
            if not cleaned_meanings:
                continue
            
            senses.append({
                'sense_id': len(senses) + 1,
                'pos': pos_label,
                'meanings': cleaned_meanings,
                'example': ex_clean,
                'pronunciation': pron_val,
                'source': source
            })
            active_source = source
            
        # Determine dominant POS
        dominant_pos = ", ".join(list(pos_list))
        
        # Generate Inflections
        inflections = []
        if direction == 'en-bn':
            for p in pos_list:
                inflections.extend(morph_engine.generate_inflections(lemma, p))
            inflections = list(set(inflections))  # Deduplicate
        elif direction in ['bn-en', 'bn-bn']:
            inflections = BanglaMorphologyEngine.generate_inflections(lemma)
            
        batch.append((
            lemma,
            normalized_lemma,
            direction,
            dominant_pos,
            json.dumps(senses, ensure_ascii=False),
            json.dumps(inflections, ensure_ascii=False) if inflections else None,
            ", ".join(list(sources))
        ))
        
        count += 1
        if count % 20000 == 0:
            log_info(f"Processed {count:,} / {len(groups):,} master entries...")
            
    log_info("Bulk inserting master records into master_lexicon...")
    cursor.executemany("""
        INSERT INTO master_lexicon (lemma, normalized_lemma, lookup_direction, pos, senses_json, inflections_json, source_attributions)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, batch)
    conn.commit()
    conn.close()
    
    elapsed = time.time() - start_time
    log_success(f"Master Lexicon successfully populated in {elapsed:.2f}s! ({len(batch):,} records)")


class KindleDictionaryCompiler:
    def __init__(self, output_dir, direction='en-bn', db_name=DB_NAME, entries_per_shard=1000):
        self.output_dir = output_dir
        self.direction = direction
        self.db_name = db_name
        self.entries_per_shard = entries_per_shard
        
        # Load version from version.json
        version = "1.2.0"
        try:
            version_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'version.json')
            if os.path.exists(version_path):
                with open(version_path, 'r', encoding='utf-8') as f:
                    version = json.load(f).get('version', '1.2.0')
        except Exception:
            pass
        self.version = version

        # Direction specific metadata
        if direction == 'en-bn':
            self.input_lang = 'en'
            self.output_lang = 'bn'
            self.index_name = 'english'
            self.title = f"Shobdo Vandar English-to-Bangla Dictionary v{self.version}"
        elif direction == 'bn-en':
            self.input_lang = 'bn'
            self.output_lang = 'en'
            self.index_name = 'bangla'
            self.title = f"Shobdo Vandar Bangla-to-English Dictionary v{self.version}"
        elif direction == 'bn-bn':
            self.input_lang = 'bn'
            self.output_lang = 'bn'
            self.index_name = 'bangla'
            self.title = f"Shobdo Vandar Bangla-to-Bangla Dictionary v{self.version}"
            
        os.makedirs(self.output_dir, exist_ok=True)

    def write_stylesheet(self):
        """Writes clean, minimalist stylesheet.css for Kindle."""
        css_path = os.path.join(self.output_dir, 'stylesheet.css')
        with open(css_path, 'w', encoding='utf-8') as f:
            f.write("""
            /* Georgia-serif e-ink popover styling */
            body { font-family: Georgia, serif; margin: 0; padding: 2px 4px; line-height: 1.25; }
            h2 { font-size: 1.15em; margin: 0 0 2px 0; font-weight: bold; }
            p { margin: 2px 0; }
            ol { margin: 3px 0 3px 15px; padding: 0; }
            li { margin-bottom: 3px; padding-left: 2px; }
            .pron { color: #666; font-size: 0.85em; font-family: sans-serif; margin-left: 5px; }
            .pos { font-style: italic; color: #555; font-size: 0.85em; }
            .context { font-style: italic; color: #555; font-weight: bold; font-size: 0.85em; }
            .example { font-style: italic; color: #444; margin-left: 10px; }
            .example-en { font-style: italic; color: #444; display: block; margin-left: 10px; margin-top: 2px; }
            .example-bn { color: #005580; display: block; margin-left: 25px; font-size: 0.95em; }
            .attributions { font-size: 0.75em; color: #777; margin-top: 10px; }
            hr { border: 0; border-top: 1px solid #ddd; margin: 6px 0; }
            """)
        log_info(f"Written: {css_path}")

    def render_entry_xhtml(self, lemma, pos, senses, inflections):
        """Compiles structured entry content into Kindle-compatible XHTML markup."""
        escaped_lemma = xml_escape(lemma)
        
        # Build inflections block if any
        inflections_xml = ""
        if inflections:
            inflections_xml = f'    <idx:infl inflgrp="{xml_escape(pos)}">\n'
            for infl in inflections:
                inflections_xml += f'      <idx:iform value="{xml_escape(infl)}"/>\n'
            inflections_xml += '    </idx:infl>\n'
            
        # Check if we have a pronunciation in any sense
        pron_xml = ""
        for s in senses:
            if s.get('pronunciation'):
                pron_xml = f' <span class="pron">{xml_escape(s["pronunciation"])}</span>'
                break
            
        # Build senses body HTML
        senses_html = ""
        if len(senses) == 1:
            s = senses[0]
            meanings = ", ".join(s['meanings'])
            context_html = f' <span class="context">[{xml_escape(s["context"])}]</span>' if s.get('context') else ""
            pos_label = s.get('pos', '')
            pos_html = ""
            if pos_label and pos_label.lower() not in ["unk", "unknown", "none", "null"]:
                pos_html = f'<span class="pos">({xml_escape(pos_label)})</span> '
            senses_html = f'<p>{pos_html}{context_html}<b>{xml_escape(meanings)}</b></p>'
            if s.get('example_en'):
                senses_html += f'<p class="example-en">💬 {xml_escape(s["example_en"])}</p>'
                if s.get('example_bn'):
                    senses_html += f'<p class="example-bn">➔ {xml_escape(s["example_bn"])}</p>'
            elif s.get('example'):
                senses_html += f'<p class="example">💬 {xml_escape(s["example"])}</p>'
        else:
            senses_html = '<ol>'
            for s in senses:
                meanings = ", ".join(s['meanings'])
                context_html = f' <span class="context">[{xml_escape(s["context"])}]</span>' if s.get('context') else ""
                pos_label = s.get('pos', '')
                pos_html = ""
                if pos_label and pos_label.lower() not in ["unk", "unknown", "none", "null"]:
                    pos_html = f'<span class="pos">({xml_escape(pos_label)})</span> '
                senses_html += f'<li>{pos_html}{context_html}{xml_escape(meanings)}'
                if s.get('example_en'):
                    senses_html += f'<br/><span class="example-en">💬 {xml_escape(s["example_en"])}</span>'
                    if s.get('example_bn'):
                        senses_html += f'<span class="example-bn">➔ {xml_escape(s["example_bn"])}</span>'
                elif s.get('example'):
                    senses_html += f'<br/><span class="example">💬 {xml_escape(s["example"])}</span>'
                senses_html += '</li>'
            senses_html += '</ol>'
            
        entry_xml = f"""
        <idx:entry name="{self.index_name}" scriptable="yes" spell="yes">
          <idx:short>
            <idx:orth value="{escaped_lemma}">
              <b>{escaped_lemma}</b>{pron_xml}
{inflections_xml}            </idx:orth>
            {senses_html}
          </idx:short>
        </idx:entry>
        <hr/>
        """
        return entry_xml

    def compile_xhtml_shards(self):
        """Fetches master data and writes sharded XHTML files in build directory."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT lemma, pos, senses_json, inflections_json 
            FROM master_lexicon 
            WHERE lookup_direction = ?
            ORDER BY LOWER(lemma) ASC
        """, (self.direction,))
        rows = cursor.fetchall()
        conn.close()
        
        shard_files = []
        shard_idx = 0
        total_entries = len(rows)
        
        if total_entries == 0:
            return []
            
        for i in range(0, total_entries, self.entries_per_shard):
            chunk = rows[i:i+self.entries_per_shard]
            filename = f"content_{shard_idx}.html"
            filepath = os.path.join(self.output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                # XHTML Header with exact Kindle dictionary schemas
                f.write("""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:idx="http://www.amazon.com/xmlns/idx"
      xmlns:mbp="http://www.amazon.com/xmlns/mbp"
      xmlns:mm="http://www.amazon.com/xmlns/mobi">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <link rel="stylesheet" type="text/css" href="stylesheet.css" />
    <title>Dictionary Content</title>
</head>
<body>
<mbp:frameset>
""")
                
                # Write Entries
                for lemma, pos, senses_json, inflections_json in chunk:
                    senses = json.loads(senses_json)
                    inflections = json.loads(inflections_json) if inflections_json else []
                    entry_xhtml = self.render_entry_xhtml(lemma, pos, senses, inflections)
                    f.write(entry_xhtml)
                    
                # XHTML Footer
                f.write("""
</mbp:frameset>
</body>
</html>
""")
            shard_files.append(filename)
            shard_idx += 1
            
        log_info(f"Compiled {shard_idx} XHTML shards containing {total_entries:,} entries.")
        return shard_files

    def compile_opf(self, shard_filenames):
        """Generates the OPF metadata package file binding languages and sharded contents."""
        opf_path = os.path.join(self.output_dir, 'dict.opf')
        
        manifest_items = ""
        spine_items = ""
        
        for idx, fname in enumerate(shard_filenames):
            manifest_items += f'    <item id="content_{idx}" href="{fname}" media-type="application/xhtml+xml"/>\n'
            spine_items += f'    <itemref idref="content_{idx}"/>\n'
            
        opf_content = f"""<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="2.0" unique-identifier="uid">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
    <dc:title>{self.title}</dc:title>
    <dc:language>{self.input_lang}</dc:language>
    <dc:creator>Tahmid</dc:creator>
    <dc:publisher>Shobdo Vandar v{self.version}</dc:publisher>
    
    <!-- Kindle Dictionary Metadata Declarations -->
    <meta name="BookType" content="dictionary"/>
    <x-metadata>
      <DictionaryInLanguage>{self.input_lang}</DictionaryInLanguage>
      <DictionaryOutLanguage>{self.output_lang}</DictionaryOutLanguage>
      <DefaultLookupIndex>{self.index_name}</DefaultLookupIndex>
      <meta name="dictionary_version" content="{self.version}"/>
    </x-metadata>
  </metadata>
  
  <manifest>
    <item id="stylesheet" href="stylesheet.css" media-type="text/css"/>
{manifest_items}  </manifest>
  
  <spine>
{spine_items}  </spine>
  
  <guide>
    <reference type="search" title="Search" href="{shard_filenames[0]}"/>
  </guide>
</package>
"""
        with open(opf_path, 'w', encoding='utf-8') as f:
            f.write(opf_content)

    def compile_all(self):
        """Runs the entire package compiler."""
        log_info(f"Starting Kindle compiler output for: {self.direction}...")
        self.write_stylesheet()
        shards = self.compile_xhtml_shards()
        if shards:
            self.compile_opf(shards)
            log_success(f"Compilation for direction '{self.direction}' completed successfully!")
        else:
            log_warning(f"No entries found for direction: {self.direction}")


def print_statistics(db_name=DB_NAME):
    """Queries db_name and prints formatted final dictionary statistics (User Request 4)."""
    if not os.path.exists(db_name):
        log_warning("Database not found! Run the pipeline first to collect statistics.")
        return
        
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # Get stats for each raw source
    cursor.execute("SELECT source_name, count(*) FROM source_ingestion GROUP BY source_name")
    source_counts = cursor.fetchall()
    
    # Get total unique master entries per direction
    cursor.execute("SELECT lookup_direction, count(*) FROM master_lexicon GROUP BY lookup_direction")
    direction_counts = cursor.fetchall()
    
    cursor.execute("SELECT count(*) FROM master_lexicon")
    total_master = cursor.fetchone()[0]
    conn.close()
    
    print("\n" + f"{Colors.BOLD}{Colors.CYAN}┌──────────────────────────────────────────────────────────────────────┐")
    print(f"│               📊 FINAL DICTIONARY STATS & SUMMARY                    │")
    print(f"└──────────────────────────────────────────────────────────────────────┘{Colors.END}")
    
    print(f"{Colors.BOLD}📥 Raw Source Ingestion Counts (from staging):{Colors.END}")
    if source_counts:
        for src, count in source_counts:
            print(f"   • {Colors.CYAN}{src:<15}{Colors.END} : {count:>8,} raw records")
    else:
        print("   • No raw records ingested yet.")
        
    print(f"\n{Colors.BOLD}📚 Combined Master Lexicon (Deduplicated & Cleaned):{Colors.END}")
    if direction_counts:
        for direction, count in direction_counts:
            labels = {
                'en-bn': "English-to-Bangla (en-bn)",
                'bn-en': "Bangla-to-English (bn-en)",
                'bn-bn': "Bangla-to-Bangla (bn-bn)"
            }
            dir_label = labels.get(direction, f"Unknown ({direction})")
            print(f"   • {dir_label:<28} : {Colors.GREEN}{count:>8,}{Colors.END} unique entries")
        print(f"   ----------------------------------------------------------------")
        print(f"   • {Colors.BOLD}{'Total Combined Master Entries':<28} : {Colors.GREEN}{total_master:>8,}{Colors.END} unique words")
    else:
        print("   • No master entries created yet.")
        
    print(f"{Colors.CYAN}└──────────────────────────────────────────────────────────────────────┘{Colors.END}\n")


def preview_entry(lemma, db_name=DB_NAME):
    """Provides a gorgeous terminal preview mockup of how a word will look in Kindle."""
    if not os.path.exists(db_name):
        log_error("Database lexicon.db not found. Please run the compiler pipeline first.")
        return
        
    # Check if Bangla or English to determine direction
    # Simple regex check for English characters
    is_english = bool(re.match(r'^[a-zA-Z]', lemma))
    directions = ['en-bn'] if is_english else ['bn-en', 'bn-bn']
    
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    found_any = False
    for direction in directions:
        cursor.execute("""
            SELECT lemma, pos, senses_json, inflections_json, source_attributions 
            FROM master_lexicon 
            WHERE LOWER(lemma) = ? AND lookup_direction = ?
        """, (lemma.lower(), direction))
        row = cursor.fetchone()
        if not row:
            continue
            
        found_any = True
        lemma_val, pos, senses_json, inflections_json, sources = row
        senses = json.loads(senses_json)
        inflections = json.loads(inflections_json) if inflections_json else []
        
        # Extract pronunciation if present in any sense
        pron_val = ""
        for s in senses:
            if s.get('pronunciation'):
                pron_val = f" {Colors.BLUE}{s['pronunciation']}{Colors.END}"
                break
                
        primary_sense = senses[0] if senses else {}
        primary_meaning = primary_sense.get('meanings', [""])[0] if primary_sense.get('meanings') else ""
        secondary_meanings = ", ".join(primary_sense.get('meanings', [])[1:4]) if len(primary_sense.get('meanings', [])) > 1 else ""
        context_tag = f" ({Colors.YELLOW}{primary_sense.get('context')}{Colors.END})" if primary_sense.get('context') else ""
        
        dir_title = "Bangla-to-Bangla (bn-bn)" if direction == 'bn-bn' else ("Bangla-to-English (bn-en)" if direction == 'bn-en' else "English-to-Bangla (en-bn)")
        
        # 1. RENDER POPUP BUBBLE
        print(f"\n{Colors.BOLD}{Colors.HEADER}┌──[ 📱 Kindle Lookup Popup Preview ({dir_title}) ]──────────────────────────────────┐{Colors.END}")
        print(f"│  {Colors.BOLD}{lemma_val:<25}{Colors.END}{pron_val} {Colors.CYAN}({pos}){Colors.END}{context_tag}")
        print(f"│  {Colors.BOLD}{Colors.GREEN}{primary_meaning}{Colors.END}" + (f" ({secondary_meanings})" if secondary_meanings else ""))
        if inflections:
            print(f"│  {Colors.YELLOW}🔗 Inflections:{Colors.END} {', '.join(inflections)}")
        print(f"│  {Colors.BLUE}Source credits:{Colors.END} {sources}")
        print(f"{Colors.HEADER}└──────────────────────────────────────────────────────────────────────┘{Colors.END}")
        
        # 2. RENDER FULL PAGE VIEW
        print(f"\n{Colors.BOLD}{Colors.HEADER}┌──[ 📖 Kindle Full Page View Mockup ({dir_title}) ]─────────────────────────────────┐{Colors.END}")
        print(f"│  {Colors.BOLD}{Colors.UNDERLINE}{lemma_val.upper()}{Colors.END}{pron_val} {Colors.CYAN}({pos}){Colors.END}")
        print(f"│  Attributed Sources: {sources}")
        print("│")
        print(f"│  {Colors.BOLD}Senses & Contexts:{Colors.END}")
        for idx, sense in enumerate(senses):
            meanings = ", ".join(sense['meanings'])
            context_str = f" ({Colors.YELLOW}{sense['context']}{Colors.END})" if sense.get('context') else ""
            print(f"│    {idx+1}. [{Colors.CYAN}{sense['pos']}{Colors.END}]{context_str} {Colors.BOLD}{meanings}{Colors.END}")
            if sense.get('example_en'):
                print(f"│       {Colors.GREEN}💬 En: {sense['example_en']}{Colors.END}")
                if sense.get('example_bn'):
                    print(f"│       {Colors.GREEN}   Bn: {sense['example_bn']}{Colors.END}")
            elif sense.get('example'):
                print(f"│       {Colors.GREEN}💬 Example: {sense['example']}{Colors.END}")
                
        if inflections:
            print("│")
            print(f"│  {Colors.BOLD}Hidden Inflection Index Aliases:{Colors.END}")
            print(f"│    {Colors.YELLOW}{', '.join(inflections)}{Colors.END}")
        print(f"{Colors.HEADER}└──────────────────────────────────────────────────────────────────────┘{Colors.END}\n")
        
    conn.close()
    if not found_any:
        log_error(f"Entry '{lemma}' not found in the master database.")
    
def print_banner():
    version = "1.2.0"
    try:
        version_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'version.json')
        if os.path.exists(version_path):
            with open(version_path, 'r', encoding='utf-8') as f:
                version = json.load(f).get('version', '1.2.0')
    except Exception:
        pass

    banner = f"""
{Colors.CYAN}██████╗ ██╗██╗     ██╗███╗   ██╗ ██████╗ ██╗   ██╗ █████╗ ██╗     
██╔══██╗██║██║     ██║████╗  ██║██╔════╝ ██║   ██║██╔══██╗██║     
██████╔╝██║██║     ██║██╔██╗ ██║██║  ███╗██║   ██║███████║██║     
██╔═══╝ ██║██║     ██║██║╚██╗██║██║   ██║██║   ██║██╔══██║██║     
██║     ██║███████╗██║██║ ╚████║╚██████╔╝╚██████╔╝██║  ██║███████╗
╚═╝     ╚═╝╚══════╝╚═╝╚═╝  ╚═══╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚══════╝
      ██████╗  ██████╗████████╗██╗ ██████╗ ███╗   ██╗ █████╗ ██████╗ ╚██╗  
     ██╔════╝ ██╔════╝╚══██╔══╝██║██╔═══██╗████╗  ██║██╔══██╗██╔══██╗ ╚██╗ 
     ██║  ███╗██║        ██║   ██║██║   ██║██╔██╗ ██║███████║██████╔╝  ██║ 
     ██║   ██║██║        ██║   ██║██║   ██║██║╚██╗██║██╔══██║██╔══██╗  ██║ 
     ╚██████╔╝╚██████╗   ██║   ██║╚██████╔╝██║ ╚████║██║  ██║██║  ██║ ╔██╝ 
      ╚═════╝  ╚═════╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝  ╚═╝ ╔═╝  
                  - Standalone CLI Dictionary Builder v{version} -{Colors.END}
"""
    print(banner)


def compile_mobi(opf_path, output_mobi_path):
    """Attempts to compile an OPF package file into a MOBI file using Amazon's official kindlegen compiler."""
    import shutil
    import subprocess
    
    # 1. Search for kindlegen in PATH
    kindlegen_path = shutil.which('kindlegen')
    
    # 2. Search for kindlegen in local workspace folder
    if not kindlegen_path:
        local_path = os.path.abspath('./kindlegen')
        if os.path.exists(local_path) and os.access(local_path, os.X_OK):
            kindlegen_path = local_path
            
    # 3. Check standard macOS Kindle Previewer application paths for kindlegen
    if not kindlegen_path:
        common_paths = [
            "/Applications/Kindle Previewer 3.app/Contents/lib/fc/bin/kindlegen",
            "/Applications/Kindle Previewer 3.app/Contents/MacOS/lib/fc/bin/kindlegen",
            "/Applications/Kindle Previewer 3.app/Contents/lib/fc/bin/kindlegen.exe",
            "/Applications/Kindle Previewer.app/Contents/lib/fc/bin/kindlegen"
        ]
        for p in common_paths:
            if os.path.exists(p):
                # Ensure the binary has execute permissions
                try:
                    if not os.access(p, os.X_OK):
                        os.chmod(p, 0o755)
                except Exception as e:
                    log_warning(f"Could not set execute permission on {p}: {e}")
                kindlegen_path = p
                break
                
    if kindlegen_path:
        log_info(f"Auto-compiling MOBI using Amazon's official kindlegen: '{kindlegen_path}'...")
        output_dir = os.path.dirname(output_mobi_path)
        mobi_filename = os.path.basename(output_mobi_path)
        try:
            cmd = [kindlegen_path, opf_path, "-o", mobi_filename]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if res.returncode in [0, 1]:  # kindlegen return code 1 is a warning, which is fine
                log_success(f"Successfully generated MOBI file at: {output_mobi_path}")
                return True
            else:
                log_warning(f"kindlegen failed with code {res.returncode}. Output:\n{res.stdout}\n{res.stderr}")
        except Exception as e:
            log_error(f"Error running kindlegen: {e}")
            
    log_warning(f"{Colors.RED}Kindle's official compiler 'kindlegen' was NOT found on your system.{Colors.END}")
    print(f"   {Colors.YELLOW}Please perform the following steps to build your e-books:{Colors.END}")
    print(f"   1. Download Kindle Previewer 3 for Mac from Amazon's official CDN:")
    print(f"      {Colors.CYAN}https://d2bzeorukaqrvt.cloudfront.net/KindlePreviewerInstaller.pkg{Colors.END}")
    print(f"   2. Install Kindle Previewer 3 on your Mac by running the downloaded installer.")
    print(f"   3. Run this Python script again. It will automatically detect the installation and build the .mobi files!")
    return False


def main():
    print_banner()
    
    parser = argparse.ArgumentParser(description="Standalone Bilingual Kindle Dictionary Compiler Pipeline.")
    parser.add_argument('-r', '--rebuild', action='store_true', help="Force clear database and run full raw ingestion from scratch.")
    parser.add_argument('-c', '--compile-only', action='store_true', help="Skip database ingestion and only compile XHTML/OPF files from existing database.")
    parser.add_argument('-p', '--preview', type=str, metavar="WORD", help="Query a word and display a beautiful terminal preview of its Kindle layout.")
    args = parser.parse_args()
    
    # 1. Preview Mode: Immediately run preview and exit
    if args.preview:
        preview_entry(args.preview)
        sys.exit(0)
        
    # Check if database exists or needs creation
    db_exists = os.path.exists(DB_NAME)
    
    # Determine pipeline actions
    needs_ingestion = args.rebuild or not db_exists
    needs_compilation = not args.preview
    
    if args.compile_only:
        needs_ingestion = False
        if not db_exists:
            log_error(f"Cannot run --compile-only because database '{DB_NAME}' does not exist. Run without flags first.")
            sys.exit(1)
            
    # 2. execute Ingestion Pipeline if needed
    if needs_ingestion:
        log_step(1, "Database Initialization")
        init_database()
        
        log_step(2, "Staging Ingestion from Raw Sources")
        start = time.time()
        populate_staging()
        log_info(f"Staging Ingestion completed in {time.time() - start:.2f} seconds.")
        
        log_step(3, "Master Lexicon Merging & Consolidation")
        build_master_lexicon()
        
    # 3. execute Compilation Pipeline if needed
    if needs_compilation:
        log_step(4, "Compiling Kindle XHTML Shards & OPF Configs")
        start = time.time()
        
        # 1. Compile English to Bangla Dictionary
        en_bn_compiler = KindleDictionaryCompiler(
            output_dir=os.path.join(BUILD_DIR, 'en-bn'),
            direction='en-bn',
            db_name=DB_NAME,
            entries_per_shard=1000
        )
        en_bn_compiler.compile_all()
        
        print("\n" + "="*80 + "\n")
        
        # 2. Compile Bangla to English Dictionary
        bn_en_compiler = KindleDictionaryCompiler(
            output_dir=os.path.join(BUILD_DIR, 'bn-en'),
            direction='bn-en',
            db_name=DB_NAME,
            entries_per_shard=1000
        )
        bn_en_compiler.compile_all()
        
        print("\n" + "="*80 + "\n")
        
        # 3. Compile Bangla to Bangla Dictionary
        bn_bn_compiler = KindleDictionaryCompiler(
            output_dir=os.path.join(BUILD_DIR, 'bn-bn'),
            direction='bn-bn',
            db_name=DB_NAME,
            entries_per_shard=1000
        )
        bn_bn_compiler.compile_all()
        
        # 4. Auto-compile MOBI files if tools are available
        log_step(5, "Auto-Compiling MOBI E-Books")
        
        # Load version from version.json
        version = "1.2.0"
        try:
            version_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'version.json')
            if os.path.exists(version_path):
                with open(version_path, 'r', encoding='utf-8') as f:
                    version = json.load(f).get('version', '1.2.0')
        except Exception:
            pass
            
        en_bn_filename = f"Shobdo_Vandar_en-bn_v{version}.mobi"
        bn_en_filename = f"Shobdo_Vandar_bn-en_v{version}.mobi"
        bn_bn_filename = f"Shobdo_Vandar_bn-bn_v{version}.mobi"
        
        en_bn_mobi = os.path.join(BUILD_DIR, 'en-bn', en_bn_filename)
        bn_en_mobi = os.path.join(BUILD_DIR, 'bn-en', bn_en_filename)
        bn_bn_mobi = os.path.join(BUILD_DIR, 'bn-bn', bn_bn_filename)
        
        # Explicitly delete old MOBI files if they exist to prevent false-positive success reports
        for path in [en_bn_mobi, bn_en_mobi, bn_bn_mobi]:
            if os.path.exists(path):
                try:
                    os.remove(path)
                    log_info(f"Cleaned up preexisting MOBI file: {path}")
                except Exception as e:
                    log_warning(f"Could not remove preexisting MOBI file at {path}: {e}")
        
        en_bn_success = compile_mobi(os.path.join(BUILD_DIR, 'en-bn', 'dict.opf'), en_bn_mobi)
        print("\n" + "-"*40 + "\n")
        bn_en_success = compile_mobi(os.path.join(BUILD_DIR, 'bn-en', 'dict.opf'), bn_en_mobi)
        print("\n" + "-"*40 + "\n")
        bn_bn_success = compile_mobi(os.path.join(BUILD_DIR, 'bn-bn', 'dict.opf'), bn_bn_mobi)
        
        log_success(f"Entire compilation completed in {time.time() - start:.2f} seconds!")
        
        # 5. Print detailed counts
        log_step(6, "Final Data Reports & Validation")
        print_statistics()
        
        log_success("All pipeline stages completed successfully!")
        if en_bn_success or bn_en_success or bn_bn_success:
            print(f"\n{Colors.BOLD}{Colors.GREEN}🎉 SUCCESS! Your MOBI e-books have been compiled directly in:{Colors.END}")
            if en_bn_success and os.path.exists(en_bn_mobi):
                print(f"   • English-to-Bangla : {Colors.CYAN}{en_bn_mobi}{Colors.END}")
            if bn_en_success and os.path.exists(bn_en_mobi):
                print(f"   • Bangla-to-English : {Colors.CYAN}{bn_en_mobi}{Colors.END}")
            if bn_bn_success and os.path.exists(bn_bn_mobi):
                print(f"   • Bangla-to-Bangla  : {Colors.CYAN}{bn_bn_mobi}{Colors.END}")
            print()
        else:
            print(f"\n{Colors.BOLD}{Colors.GREEN}👉 To build MOBI e-books, compile using Kindle Previewer or run:{Colors.END}")
            print(f"   kindlegen ./build/en-bn/dict.opf -o {en_bn_filename}")
            print(f"   kindlegen ./build/bn-en/dict.opf -o {bn_en_filename}")
            print(f"   kindlegen ./build/bn-bn/dict.opf -o {bn_bn_filename}\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.RED}Process interrupted by user. Exiting safely.{Colors.END}")
        sys.exit(0)
