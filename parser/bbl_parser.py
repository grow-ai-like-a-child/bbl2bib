"""
BBL Parser Module
Parses BBL files and extracts bibliography entries
"""

import re
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field


@dataclass
class BibEntry:
    """Represents a bibliography entry."""
    entry_type: str
    cite_key: str
    fields: Dict[str, str] = field(default_factory=dict)
    raw_text: str = ""


class BBLParser:
    """Parser for BBL files."""
    
    def __init__(self):
        """Initialize the BBL parser."""
        self.entries: List[BibEntry] = []
        
        # Common BBL patterns
        self.bibitem_pattern = re.compile(r'\\bibitem(?:\[([^\]]*)\])?\{([^}]+)\}')
        self.newblock_pattern = re.compile(r'\\newblock\s*')
        self.emph_pattern = re.compile(r'\\emph\{([^}]+)\}')
        self.textit_pattern = re.compile(r'\\textit\{([^}]+)\}')
        self.textbf_pattern = re.compile(r'\\textbf\{([^}]+)\}')
        
        # Field detection patterns
        self.author_patterns = [
            re.compile(r'^([A-Z][^,]+(?:,\s*[A-Z][^,]+)*?)(?:\.|,|\s+and\s+)'),
            re.compile(r'^([A-Z]\.\s*(?:[A-Z]\.\s*)?[A-Z][^,]+(?:(?:,|\s+and)\s+[A-Z]\.\s*(?:[A-Z]\.\s*)?[A-Z][^,]+)*)'),
        ]
        
        self.year_pattern = re.compile(r'\b(19|20)\d{2}\b')
        self.pages_pattern = re.compile(r'\b(\d+)\s*[-–—]\s*(\d+)\b')
        self.volume_pattern = re.compile(r'\bvolume\s+(\d+)\b', re.IGNORECASE)
        self.number_pattern = re.compile(r'\bnumber\s+(\d+)\b', re.IGNORECASE)
        self.doi_pattern = re.compile(r'(?:doi:\s*|https?://doi\.org/)([^\s,]+)', re.IGNORECASE)
        self.url_pattern = re.compile(r'https?://[^\s,]+')
        self.isbn_pattern = re.compile(r'ISBN[:\s]+([0-9X-]+)', re.IGNORECASE)
        
    def parse_file(self, filepath: Path) -> List[BibEntry]:
        """Parse a BBL file and extract bibliography entries."""
        self.entries = []
        
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Split by \bibitem
        items = self.bibitem_pattern.split(content)
        
        # Process each bibliography item
        for i in range(1, len(items), 3):
            if i + 1 < len(items):
                optional_label = items[i] if items[i] else None
                cite_key = items[i + 1]
                text = items[i + 2] if i + 2 < len(items) else ""
                
                entry = self._parse_bibitem(cite_key, text, optional_label)
                if entry:
                    self.entries.append(entry)
        
        return self.entries
    
    def _parse_bibitem(self, cite_key: str, text: str, label: Optional[str] = None) -> Optional[BibEntry]:
        """Parse a single bibliography item."""
        # Clean up the text
        text = self._clean_text(text)
        
        if not text.strip():
            return None
        
        # Detect entry type and extract fields
        entry_type = self._detect_entry_type(text)
        fields = self._extract_fields(text, entry_type)
        
        entry = BibEntry(
            entry_type=entry_type,
            cite_key=cite_key,
            fields=fields,
            raw_text=text
        )
        
        return entry
    
    def _clean_text(self, text: str) -> str:
        """Clean LaTeX formatting from text."""
        # Remove \newblock commands
        text = self.newblock_pattern.sub(' ', text)
        
        # Handle emphasis and formatting
        text = self.emph_pattern.sub(r'\1', text)
        text = self.textit_pattern.sub(r'\1', text)
        text = self.textbf_pattern.sub(r'\1', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove trailing punctuation from the end
        text = text.rstrip('.')
        
        return text.strip()
    
    def _detect_entry_type(self, text: str) -> str:
        """Detect the type of bibliography entry based on content."""
        text_lower = text.lower()
        
        # Check for specific indicators
        if 'phd thesis' in text_lower or 'doctoral dissertation' in text_lower:
            return 'phdthesis'
        elif 'master' in text_lower and 'thesis' in text_lower:
            return 'mastersthesis'
        elif 'technical report' in text_lower or 'tech. rep.' in text_lower:
            return 'techreport'
        elif 'in proceedings' in text_lower or 'conference' in text_lower:
            return 'inproceedings'
        elif 'in:' in text or 'In ' in text and ('editor' in text_lower or 'eds.' in text_lower):
            return 'incollection'
        elif self._has_journal_indicators(text):
            return 'article'
        elif 'http' in text_lower or 'www.' in text_lower:
            return 'misc'
        elif self._has_book_indicators(text):
            return 'book'
        else:
            # Default to article if we find volume/number/pages
            if self.volume_pattern.search(text) or self.pages_pattern.search(text):
                return 'article'
            return 'misc'
    
    def _has_journal_indicators(self, text: str) -> bool:
        """Check if text has journal article indicators."""
        indicators = ['journal', 'vol.', 'volume', 'pp.', 'pages', 'issue']
        text_lower = text.lower()
        return any(ind in text_lower for ind in indicators)
    
    def _has_book_indicators(self, text: str) -> bool:
        """Check if text has book indicators."""
        indicators = ['publisher', 'press', 'isbn', 'edition']
        text_lower = text.lower()
        return any(ind in text_lower for ind in indicators)
    
    def _extract_fields(self, text: str, entry_type: str) -> Dict[str, str]:
        """Extract fields from bibliography text."""
        fields = {}
        
        # Extract authors
        authors = self._extract_authors(text)
        if authors:
            fields['author'] = authors
        
        # Extract title
        title = self._extract_title(text, bool(authors))
        if title:
            fields['title'] = title
        
        # Extract year
        year_match = self.year_pattern.search(text)
        if year_match:
            fields['year'] = year_match.group(0)
        
        # Extract pages
        pages_match = self.pages_pattern.search(text)
        if pages_match:
            fields['pages'] = f"{pages_match.group(1)}--{pages_match.group(2)}"
        
        # Extract volume
        volume_match = self.volume_pattern.search(text)
        if volume_match:
            fields['volume'] = volume_match.group(1)
        
        # Extract number
        number_match = self.number_pattern.search(text)
        if number_match:
            fields['number'] = number_match.group(1)
        
        # Extract DOI
        doi_match = self.doi_pattern.search(text)
        if doi_match:
            fields['doi'] = doi_match.group(1)
        
        # Extract URL
        url_match = self.url_pattern.search(text)
        if url_match:
            fields['url'] = url_match.group(0)
        
        # Extract ISBN
        isbn_match = self.isbn_pattern.search(text)
        if isbn_match:
            fields['isbn'] = isbn_match.group(1)
        
        # Extract journal/booktitle/publisher based on entry type
        if entry_type == 'article':
            journal = self._extract_journal(text)
            if journal:
                fields['journal'] = journal
        elif entry_type in ['inproceedings', 'incollection']:
            booktitle = self._extract_booktitle(text)
            if booktitle:
                fields['booktitle'] = booktitle
        
        # Extract publisher
        publisher = self._extract_publisher(text)
        if publisher:
            fields['publisher'] = publisher
        
        return fields
    
    def _extract_authors(self, text: str) -> Optional[str]:
        """Extract authors from text."""
        # Clean up LaTeX tilde for non-breaking space
        clean_text = text.replace('~', ' ')
        
        # Pattern for typical author format in BBL files
        # Matches: "Initial. Lastname" or "Firstname Lastname" with "and" or comma separators
        author_patterns = [
            # D. E. Knuth or A. Einstein format
            re.compile(r'^([A-Z]\.\s*(?:[A-Z]\.\s*)?[A-Z][a-z]+(?:\s+(?:and|,)\s+[A-Z]\.\s*(?:[A-Z]\.\s*)?[A-Z][a-z]+)*)'),
            # Full first name format
            re.compile(r'^([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+(?:and|,)\s+[A-Z][a-z]+\s+[A-Z][a-z]+)*)'),
            # Mixed format with Jr., Sr., etc.
            re.compile(r'^([A-Z]\.\s*(?:[A-Z]\.\s*)?[A-Z][a-z]+(?:\s+(?:Jr\.|Sr\.|III|II))?(?:\s+(?:and|,)\s+[A-Z]\.\s*(?:[A-Z]\.\s*)?[A-Z][a-z]+(?:\s+(?:Jr\.|Sr\.|III|II))?)*)'),
        ]
        
        for pattern in author_patterns:
            match = pattern.match(clean_text)
            if match:
                authors = match.group(1)
                # Normalize separators
                authors = re.sub(r'\s*,\s*', ' and ', authors)
                authors = re.sub(r'\s+and\s+', ' and ', authors)
                return authors.strip()
        
        # Fallback: get text before first period if it looks like names
        first_part = clean_text.split('.')[0].strip()
        
        # Check if it contains typical name patterns
        if re.match(r'^[A-Z]', first_part) and len(first_part) < 100:
            # Must have at least one space (indicating first/last name)
            if ' ' in first_part:
                # Check for name-like patterns
                if re.search(r'[A-Z][a-z]+', first_part):  # Has capitalized words
                    return first_part.strip()
        
        return None
    
    def _looks_like_authors(self, text: str) -> bool:
        """Check if text looks like author names."""
        # Simple heuristic: starts with capital letter and contains at least one space or comma
        return bool(re.match(r'^[A-Z]', text) and (' ' in text or ',' in text))
    
    def _extract_title(self, text: str, has_authors: bool) -> Optional[str]:
        """Extract title from text."""
        working_text = text
        
        # Remove author part if present
        if has_authors:
            # Find where authors end (usually at first period)
            first_period = text.find('.')
            if first_period > 0:
                working_text = text[first_period + 1:].strip()
        
        # Remove \newblock if present
        working_text = re.sub(r'\\newblock\s*', '', working_text)
        
        # Look for text in \emph{} or \textit{} (common for titles)
        emph_match = re.search(r'\\(?:emph|textit)\{([^}]+)\}', working_text)
        if emph_match:
            return emph_match.group(1)
        
        # Look for quoted text
        quote_match = re.search(r'["`]([^"`]+)["`]', working_text)
        if quote_match:
            return quote_match.group(1)
        
        # Look for text before next period (likely the title)
        # Split by period and take the first substantial part
        parts = working_text.split('.')
        for part in parts:
            part = part.strip()
            # Skip parts that look like journal/publisher info
            if len(part) > 10 and not any(kw in part.lower() for kw in ['journal', 'conference', 'proceedings', 'vol', 'pp', 'publisher', 'press', 'isbn']):
                # Clean up any remaining LaTeX commands
                part = re.sub(r'\\[a-zA-Z]+\{([^}]+)\}', r'\1', part)
                part = re.sub(r'\{([^}]+)\}', r'\1', part)
                return part.strip()
        
        return None
    
    def _extract_journal(self, text: str) -> Optional[str]:
        """Extract journal name from text."""
        # Look for text after "journal" keyword
        journal_match = re.search(r'(?:journal[:\s]+|in[:\s]+)([^,\d]+)(?:,|\d)', text, re.IGNORECASE)
        if journal_match:
            return journal_match.group(1).strip()
        
        # Look for italicized text that might be journal
        italic_match = re.search(r'\\(?:emph|textit)\{([^}]+)\}', text)
        if italic_match:
            journal = italic_match.group(1)
            if not any(kw in journal.lower() for kw in ['proceedings', 'conference']):
                return journal
        
        return None
    
    def _extract_booktitle(self, text: str) -> Optional[str]:
        """Extract book title or proceedings name."""
        # Look for "In" or "Proceedings of"
        patterns = [
            re.compile(r'(?:In|in)[:\s]+([^,]+)(?:,|\.)', re.IGNORECASE),
            re.compile(r'Proceedings of[:\s]+([^,]+)(?:,|\.)', re.IGNORECASE),
        ]
        
        for pattern in patterns:
            match = pattern.search(text)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_publisher(self, text: str) -> Optional[str]:
        """Extract publisher from text."""
        # Common publisher names
        publishers = [
            'Springer', 'Elsevier', 'Wiley', 'IEEE', 'ACM', 'MIT Press',
            'Cambridge University Press', 'Oxford University Press',
            'Academic Press', 'Addison-Wesley', 'McGraw-Hill'
        ]
        
        text_lower = text.lower()
        for pub in publishers:
            if pub.lower() in text_lower:
                return pub
        
        # Look for "Publisher:" or similar
        pub_match = re.search(r'(?:publisher|press)[:\s]+([^,]+)(?:,|\.)', text, re.IGNORECASE)
        if pub_match:
            return pub_match.group(1).strip()
        
        return None
