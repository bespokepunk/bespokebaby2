#!/usr/bin/env python3
"""
Comprehensive caption review for:
- Spacing issues
- Common typos
- Formatting problems
- Grammar issues
"""

import os
import re
from collections import defaultdict

TRAINING_DIR = "sd15_training_512"

# Track issues found
issues = defaultdict(list)

def check_caption(txt_file, caption):
    """Check for various issues in a caption"""
    problems = []

    # Check for double spaces
    if '  ' in caption:
        problems.append("double spaces")

    # Check for missing spaces after commas
    if re.search(r',[^\s]', caption):
        problems.append("missing space after comma")

    # Check for spaces before commas
    if re.search(r'\s,', caption):
        problems.append("space before comma")

    # Check for double commas
    if ',,' in caption:
        problems.append("double commas")

    # Check for missing commas between hex codes and text
    if re.search(r'\(#[0-9a-fA-F]{6}\)[a-z]', caption):
        problems.append("missing comma after hex code")

    # Common typos to check
    typos = {
        r'\beand\b': 'and',
        r'\bmeidum\b': 'medium',
        r'\bnekclace\b': 'necklace',
        r'\bckip\b': 'clip',
        r'\bshari\b': 'shiny',
        r'\bblackgrey\b': 'black-grey',
        r'\ban\s+reflection\b': 'and reflection',
        r'\ban\s+reflective\b': 'and reflective',
    }

    for pattern, replacement in typos.items():
        if re.search(pattern, caption, flags=re.IGNORECASE):
            problems.append(f"typo: {pattern} -> {replacement}")

    # Check for inconsistent capitalization
    if re.search(r',\s+[A-Z]', caption) and 'Red Hooded Cape' not in caption:
        problems.append("unexpected capitalization mid-sentence")

    # Check for malformed words (letters stuck together)
    common_malformed = [
        'innerswearing', 'reflectionlips', 'centerdark', 'centermedium',
        'eyelight', 'eyedark', 'eyemedium'
    ]
    for malformed in common_malformed:
        if malformed in caption.lower():
            problems.append(f"malformed: {malformed}")

    return problems

def main():
    print("="*100)
    print("COMPREHENSIVE CAPTION REVIEW")
    print("="*100)
    print()

    total_files = 0
    files_with_issues = 0

    for txt_file in sorted(os.listdir(TRAINING_DIR)):
        if not txt_file.endswith('.txt'):
            continue

        total_files += 1
        txt_path = os.path.join(TRAINING_DIR, txt_file)

        with open(txt_path, 'r') as f:
            caption = f.read().strip()

        problems = check_caption(txt_file, caption)

        if problems:
            files_with_issues += 1
            issues[txt_file] = problems

            if files_with_issues <= 20:
                print(f"[{files_with_issues}] {txt_file}")
                for problem in problems:
                    print(f"    ⚠️  {problem}")
                print()

    print()
    print("="*100)
    print("REVIEW SUMMARY")
    print("="*100)
    print()
    print(f"📁 Total files: {total_files}")
    print(f"⚠️  Files with issues: {files_with_issues}")
    print(f"✅ Clean files: {total_files - files_with_issues}")
    print()

    if files_with_issues > 20:
        print(f"Note: Only showing first 20 files with issues. Total: {files_with_issues}")
        print()

    # Summary by issue type
    issue_types = defaultdict(int)
    for file_issues in issues.values():
        for issue in file_issues:
            issue_type = issue.split(':')[0]
            issue_types[issue_type] += 1

    if issue_types:
        print("Issue breakdown:")
        for issue_type, count in sorted(issue_types.items(), key=lambda x: -x[1]):
            print(f"  • {issue_type}: {count} files")
        print()

if __name__ == "__main__":
    main()
