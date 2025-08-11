#!/usr/bin/env python3
"""
Test script to verify TOC formatting functionality
"""

import sys
import os
sys.path.append('/Users/ducleminh/practice-dcdual/dc-pdf2markdown')

from service import MarkerPDFConverter

def test_toc_formatting():
    # Sample horizontal TOC text (similar to what marker produces)
    horizontal_toc = """# Contents

[Learning English Through Short Stories](#page-7-0) [Using this Book Effectively](#page-7-1)

[1. The Key](#page-9-0) [2. What is Culture?](#page-0-0) [3. Food Poisoning](#page-0-0) [4. The Neighbor](#page-10-0) [5. Headache](#page-0-0) [6. A New Driver's License](#page-0-0) [7. New Year's Eve in Europe](#page-0-0) [8. Invoices and Contracts](#page-0-0) [9. World Traveler](#page-0-0) [10. Hobby Chef](#page-0-0)

[11. The Break In](#page-0-1) [12. A Broken Phone](#page-0-0) [13. The Painters](#page-0-0) [14. Quitting](#page-0-0) [15. Swimming](#page-0-0)

# Next Section
Some other content here.
"""
    
    # Create converter instance to test the formatting function
    converter = MarkerPDFConverter()
    formatted_text = converter._format_table_of_contents(horizontal_toc, "test")
    
    print("=== ORIGINAL ===")
    print(horizontal_toc)
    print("\n=== FORMATTED ===")
    print(formatted_text)
    
    # Check if the formatting worked
    lines = formatted_text.split('\n')
    toc_section_started = False
    vertical_count = 0
    
    for line in lines:
        if '# Contents' in line:
            toc_section_started = True
            continue
        if toc_section_started and line.startswith('#') and 'Contents' not in line:
            break
        if toc_section_started and line.strip().startswith('[') and '](' in line:
            # Count individual TOC entries
            if line.count('[') == 1:  # Single entry per line
                vertical_count += 1
    
    print(f"\nFound {vertical_count} vertical TOC entries")
    print("Test", "PASSED" if vertical_count > 5 else "FAILED")

if __name__ == "__main__":
    test_toc_formatting()
