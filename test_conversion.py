#!/usr/bin/env python3
"""
Test script for bbl2bib conversion
"""

import sys
import os
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent))

from parser.bbl_parser import BBLParser
from writer.bib_writer import BIBWriter


def test_conversion():
    """Test the BBL to BIB conversion with the sample file."""
    
    print("Testing BBL to BIB conversion...")
    print("-" * 50)
    
    # Parse sample BBL file
    sample_bbl = Path(__file__).parent / "examples" / "sample.bbl"
    
    if not sample_bbl.exists():
        print(f"Error: Sample file not found: {sample_bbl}")
        return False
    
    print(f"Reading: {sample_bbl}")
    
    parser = BBLParser()
    entries = parser.parse_file(sample_bbl)
    
    print(f"Found {len(entries)} entries:")
    for entry in entries:
        print(f"  - {entry.cite_key} ({entry.entry_type}): {entry.fields.get('title', 'No title')[:50]}...")
    
    print("\nWriting output...")
    
    # Write to string for display
    writer = BIBWriter(format_style='standard')
    output = writer.write_entries_to_string(entries)
    
    print("\nGenerated BIB content (first 1000 chars):")
    print("-" * 50)
    print(output[:1000])
    if len(output) > 1000:
        print("... (truncated)")
    
    print("-" * 50)
    print("Test completed successfully!")
    
    # Also write to file
    output_file = Path(__file__).parent / "examples" / "sample_converted.bib"
    writer.write_file(output_file, entries)
    print(f"\nOutput written to: {output_file}")
    
    return True


if __name__ == "__main__":
    success = test_conversion()
    sys.exit(0 if success else 1)
