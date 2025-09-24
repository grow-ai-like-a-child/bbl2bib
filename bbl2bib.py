#!/usr/bin/env python3
"""
BBL to BIB Converter
Main script for converting BBL files back to BIB format
"""

import argparse
import sys
import os
from pathlib import Path
from typing import Optional

from parser.bbl_parser import BBLParser
from writer.bib_writer import BIBWriter
from utils.logger import setup_logger


def main():
    """Main entry point for the BBL to BIB converter."""
    parser = argparse.ArgumentParser(
        description='Convert BBL files back to BIB format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.bbl                  # Convert to input.bib
  %(prog)s input.bbl -o output.bib    # Specify output file
  %(prog)s *.bbl                      # Convert multiple files
  %(prog)s input.bbl --verbose        # Enable verbose logging
        """
    )
    
    parser.add_argument(
        'input_files',
        nargs='+',
        help='BBL file(s) to convert'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output BIB file (default: same name as input with .bib extension)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='Overwrite existing output files without asking'
    )
    
    parser.add_argument(
        '--format',
        choices=['standard', 'minimal', 'full'],
        default='standard',
        help='Output format style (default: standard)'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logger(verbose=args.verbose)
    
    # Process each input file
    for input_file in args.input_files:
        input_path = Path(input_file)
        
        if not input_path.exists():
            logger.error(f"Input file does not exist: {input_file}")
            continue
            
        if not input_path.suffix.lower() == '.bbl':
            logger.warning(f"Input file does not have .bbl extension: {input_file}")
        
        # Determine output file
        if args.output and len(args.input_files) == 1:
            output_path = Path(args.output)
        else:
            output_path = input_path.with_suffix('.bib')
        
        # Check if output exists
        if output_path.exists() and not args.overwrite:
            response = input(f"Output file {output_path} exists. Overwrite? (y/n): ")
            if response.lower() != 'y':
                logger.info(f"Skipping {input_file}")
                continue
        
        try:
            logger.info(f"Processing: {input_file} -> {output_path}")
            
            # Parse BBL file
            bbl_parser = BBLParser()
            entries = bbl_parser.parse_file(input_path)
            
            if not entries:
                logger.warning(f"No bibliography entries found in {input_file}")
                continue
            
            logger.info(f"Found {len(entries)} bibliography entries")
            
            # Write BIB file
            bib_writer = BIBWriter(format_style=args.format)
            bib_writer.write_file(output_path, entries)
            
            logger.info(f"Successfully converted: {output_path}")
            
        except Exception as e:
            logger.error(f"Error processing {input_file}: {str(e)}")
            if args.verbose:
                import traceback
                traceback.print_exc()
            sys.exit(1)


if __name__ == '__main__':
    main()
