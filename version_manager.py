#!/usr/bin/env python3
# Copyright (c) 2026 Tahmid
# This software is released under the MIT License.
# See the LICENSE file in the project root for full license details.
"""
Bilingual Dictionary Project Version Manager 🏷️
Automates semantic versioning, git tagging, and Keep a Changelog formatting.
"""

import os
import sys
import re
import json
import argparse
from datetime import datetime
import subprocess

VERSION_FILE = 'version.json'
CHANGELOG_FILE = 'CHANGELOG.md'

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

def get_current_version():
    """Reads the current version from version.json."""
    if not os.path.exists(VERSION_FILE):
        return None
    try:
        with open(VERSION_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("version")
    except Exception as e:
        log_error(f"Failed to read version.json: {e}")
        return None

def write_version(version_str):
    """Writes the version to version.json."""
    try:
        with open(VERSION_FILE, 'w', encoding='utf-8') as f:
            json.dump({"version": version_str}, f, indent=2)
            f.write("\n")
        return True
    except Exception as e:
        log_error(f"Failed to write version.json: {e}")
        return False

def parse_semver(version_str):
    """Parses a SemVer 2.0.0 string into a tuple of (major, minor, patch)."""
    match = re.match(r'^v?(\d+)\.(\d+)\.(\d+)$', version_str)
    if not match:
        raise ValueError(f"Invalid semantic version: '{version_str}'")
    return int(match.group(1)), int(match.group(2)), int(match.group(3))

def bump_version(current_version, bump_type):
    """Bumps the version based on bump_type (major, minor, patch)."""
    major, minor, patch = parse_semver(current_version)
    if bump_type == 'major':
        major += 1
        minor = 0
        patch = 0
    elif bump_type == 'minor':
        minor += 1
        patch = 0
    elif bump_type == 'patch':
        patch += 1
    else:
        raise ValueError(f"Invalid bump type: '{bump_type}'")
    return f"{major}.{minor}.{patch}"

def categorize_changelog_messages(messages):
    """Categorizes raw user messages into standard changelog sections."""
    categories = {
        'Added': [],
        'Changed': [],
        'Fixed': [],
        'Removed': [],
        'Deprecated': [],
        'Security': []
    }
    
    for msg in messages:
        msg_strip = msg.strip()
        if not msg_strip:
            continue
        
        lower = msg_strip.lower()
        if lower.startswith(('add', 'feat', 'new', 'introduc')):
            categories['Added'].append(msg_strip)
        elif lower.startswith(('fix', 'bug', 'patch', 'resolv')):
            categories['Fixed'].append(msg_strip)
        elif lower.startswith(('remov', 'delet', 'clean')):
            categories['Removed'].append(msg_strip)
        elif lower.startswith(('deprecat')):
            categories['Deprecated'].append(msg_strip)
        elif lower.startswith(('secur', 'crypt', 'auth')):
            categories['Security'].append(msg_strip)
        else:
            categories['Changed'].append(msg_strip)
            
    # Clean empty categories
    return {k: v for k, v in categories.items() if v}

def build_changelog_block(version_str, date_str, categorized_messages):
    """Builds a formatted markdown changelog block."""
    block = f"## [{version_str}] - {date_str}\n\n"
    for cat, msgs in categorized_messages.items():
        block += f"### {cat}\n"
        for m in msgs:
            # Ensure the bullet point starts nicely
            bullet = m
            # Capitalize first letter if it isn't
            if len(bullet) > 0 and bullet[0].islower():
                bullet = bullet[0].upper() + bullet[1:]
            block += f"- {bullet}\n"
        block += "\n"
    block += "---\n\n"
    return block

def insert_changelog_block(block_str):
    """Inserts a new changelog block into CHANGELOG.md before the first release header."""
    if not os.path.exists(CHANGELOG_FILE):
        # Create a new one
        header = "# Changelog\n\nAll notable changes are documented here.\n\n---\n\n"
        with open(CHANGELOG_FILE, 'w', encoding='utf-8') as f:
            f.write(header + block_str)
        return True
        
    try:
        with open(CHANGELOG_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Find the first occurrence of a release header
        match = re.search(r'^(## \[.*\] - \d{4}-\d{2}-\d{2})', content, re.MULTILINE)
        if match:
            pos = match.start()
            new_content = content[:pos] + block_str + content[pos:]
        else:
            # Append if no header found
            new_content = content + "\n\n" + block_str
            
        with open(CHANGELOG_FILE, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    except Exception as e:
        log_error(f"Failed to update CHANGELOG.md: {e}")
        return False

def show_cmd():
    """Prints the current version in a premium panel."""
    version = get_current_version()
    if not version:
        log_error("No version file found or failed to parse. Run validate to check.")
        sys.exit(1)
        
    print("\n" + f"{Colors.BOLD}{Colors.CYAN}┌────────────────────────────────────────┐")
    print(f"│      🔖 CURRENT PROJECT VERSION        │")
    print(f"├────────────────────────────────────────┤")
    print(f"│  Version : {Colors.GREEN}{Colors.BOLD}v{version:<26}{Colors.END}{Colors.CYAN}│")
    print(f"└────────────────────────────────────────┘{Colors.END}\n")

def validate_cmd():
    """Validates the project version files and consistency."""
    success = True
    print(f"\n{Colors.BOLD}{Colors.HEADER}--- Version Management Validation Suite ---{Colors.END}\n")
    
    # 1. Check version.json exists and parses
    version = get_current_version()
    if version:
        log_success(f"File '{VERSION_FILE}' verified. Active version: v{version}")
        try:
            parse_semver(version)
            log_success(f"Semantic version formatting 'v{version}' is standard-compliant (SemVer 2.0.0).")
        except ValueError as e:
            log_error(str(e))
            success = False
    else:
        log_error(f"File '{VERSION_FILE}' does not exist or is corrupted!")
        success = False
        
    # 2. Check CHANGELOG.md exists and contains the version
    if os.path.exists(CHANGELOG_FILE):
        log_success(f"File '{CHANGELOG_FILE}' verified.")
        if version:
            try:
                with open(CHANGELOG_FILE, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for header format like ## [1.2.0]
                pattern = rf'## \[{re.escape(version)}\]'
                if re.search(pattern, content):
                    log_success(f"CHANGELOG.md correctly contains release header matching v{version}.")
                else:
                    log_error(f"CHANGELOG.md is missing a release block header for '## [{version}]'!")
                    success = False
            except Exception as e:
                log_error(f"Failed to read CHANGELOG.md: {e}")
                success = False
    else:
        log_error(f"File '{CHANGELOG_FILE}' is missing!")
        success = False
        
    # Check if Git state has tag matching
    if version:
        try:
            res = subprocess.run(['git', 'tag', '-l', f'v{version}'], capture_output=True, text=True)
            if f'v{version}' in res.stdout:
                log_success(f"Git environment has tag 'v{version}' registered.")
            else:
                log_warning(f"Git environment does NOT contain tag 'v{version}' yet.")
        except Exception:
            pass

    print()
    if success:
        log_success("Validation complete: Everything is 100% compliant!")
        sys.exit(0)
    else:
        log_error("Validation failed: Please resolve the errors highlighted above.")
        sys.exit(1)

def bump_cmd(args):
    """Executes a version bump and updates files."""
    current = get_current_version()
    if not current:
        log_error("Cannot read current version. Ensure version.json is initialized.")
        sys.exit(1)
        
    try:
        new_version = bump_version(current, args.type)
    except ValueError as e:
        log_error(str(e))
        sys.exit(1)
        
    # Gather changelog messages
    messages = []
    if args.message:
        # User supplied a message. We can split by semicolon to support multiple bullet points
        messages = [m.strip() for m in args.message.split(';') if m.strip()]
    else:
        # Prompt user interactively
        print(f"\n{Colors.BOLD}{Colors.YELLOW}Bumping version from v{current} to v{new_version}...{Colors.END}")
        print("Please enter the changes for this release (use semicolon ';' or enter multiple times, empty line to finish):")
        while True:
            try:
                line = input(f"{Colors.CYAN}> {Colors.END}").strip()
                if not line:
                    break
                messages.extend([m.strip() for m in line.split(';') if m.strip()])
            except (KeyboardInterrupt, EOFError):
                print()
                log_warning("Input cancelled. Exiting.")
                sys.exit(0)
                
    if not messages:
        log_error("Changelog message is mandatory to preserve historical release integrity!")
        sys.exit(1)
        
    categorized = categorize_changelog_messages(messages)
    date_str = datetime.now().strftime('%Y-%m-%d')
    changelog_block = build_changelog_block(new_version, date_str, categorized)
    
    # Dry Run output
    if args.dry_run:
        print(f"\n{Colors.BOLD}{Colors.YELLOW}=== DRY RUN: VERSION BUMP PREVIEW ==={Colors.END}")
        print(f"Current Version  : v{current}")
        print(f"Bumped Version   : v{new_version}")
        print(f"Proposed Release Date: {date_str}")
        print(f"\nProposed CHANGELOG.md Insertion:")
        print("-" * 50)
        print(changelog_block.strip())
        print("-" * 50)
        print(f"{Colors.GREEN}Dry-run completed. No files were modified.{Colors.END}\n")
        return
        
    # Real Write
    log_info(f"Bumping version from v{current} to v{new_version}...")
    if not write_version(new_version):
        log_error("Aborting version bump.")
        sys.exit(1)
        
    if not insert_changelog_block(changelog_block):
        # Rollback version.json
        write_version(current)
        log_error("Aborting version bump.")
        sys.exit(1)
        
    log_success(f"Updated '{VERSION_FILE}' to version {new_version}")
    log_success(f"Prepended new release block to '{CHANGELOG_FILE}'")
    
    # Git Integration
    if args.git:
        log_info("Executing Git integration actions...")
        try:
            # Stage files
            subprocess.run(['git', 'add', VERSION_FILE, CHANGELOG_FILE], check=True)
            # Commit
            commit_msg = f"chore: Bump version to v{new_version}"
            subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
            log_success(f"Committed changes with message: '{commit_msg}'")
            # Tag
            tag_name = f"v{new_version}"
            tag_msg = f"Release {tag_name}\n\nChangelog:\n"
            for cat, msgs in categorized.items():
                tag_msg += f"\n{cat}:\n"
                for m in msgs:
                    tag_msg += f"- {m}\n"
            subprocess.run(['git', 'tag', '-a', tag_name, '-m', tag_msg], check=True)
            log_success(f"Created annotated Git tag '{tag_name}'")
        except subprocess.CalledProcessError as e:
            log_error(f"Git commands failed: {e}")
            log_warning("Files were updated, but git commit/tag was not completed successfully.")
            sys.exit(1)

    print()
    log_success(f"Version bump to v{new_version} successfully completed! 🎉")

def main():
    parser = argparse.ArgumentParser(description="Standalone versioning & release suite.")
    subparsers = parser.add_subparsers(dest="command", required=True, help="Sub-commands")
    
    # Show subcommand
    subparsers.add_parser("show", help="Show current project version")
    
    # Validate subcommand
    subparsers.add_parser("validate", help="Validate semver file consistency")
    
    # Bump subcommand
    bump_parser = subparsers.add_parser("bump", help="Bump version, update changelog, and tag git")
    bump_parser.add_argument("--type", "-t", choices=['major', 'minor', 'patch'], required=True, help="Semantic increment type")
    bump_parser.add_argument("--message", "-m", type=str, help="Changelog bullet point contents (semicolon separated)")
    bump_parser.add_argument("--git", "-g", action="store_true", help="Automatically git commit and tag")
    bump_parser.add_argument("--dry-run", "-d", action="store_true", help="Preview version changes without writing to disk")
    
    args = parser.parse_args()
    
    if args.command == "show":
        show_cmd()
    elif args.command == "validate":
        validate_cmd()
    elif args.command == "bump":
        bump_cmd(args)

if __name__ == '__main__':
    main()
