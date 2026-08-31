import re
import unicodedata

# Compilation of regular expressions for matching boilerplate lines
BOILERPLATE_PATTERNS = [
    re.compile(r"^\s*CONFIDENTIAL\s*-\s*SCHEME\s*ASSISTANT\s*SYSTEM\s*$", re.IGNORECASE),
    re.compile(r"^\s*CONFIDENTIAL\s*-\s*GOVERNMENT\s*OF\s*INDIA\s*$", re.IGNORECASE),
    re.compile(r"^\s*Page\s+\d+\s+of\s+\d+\s*$", re.IGNORECASE),
    re.compile(r"^\s*Page\s+\d+\s*$", re.IGNORECASE),
    re.compile(r"^\s*All\s+Rights\s+Reserved\s*$", re.IGNORECASE),
    re.compile(r"^\s*Navigation:\s+Home\s*\|\s*Schemes\s*\|\s*About\s+Us\s*$", re.IGNORECASE),
]

def normalize_unicode_and_quotes(text: str) -> str:
    """
    Applies Unicode NFKC normalization and maps curly quotes
    to standard straight ASCII representation.
    """
    if not text:
        return ""
    
    # Unicode compatibility normalisation
    text = unicodedata.normalize("NFKC", text)
    
    # Map smart/curly quotes and other common anomalies to straight ascii quotes
    curly_quotes = {
        '“': '"', '”': '"',  # double quotes
        '‘': "'", '’': "'",  # single quotes
        '„': '"', '‟': '"',
        '‚': "'", '‛': "'",
        '\u200b': '',        # zero-width space
        '\xa0': ' ',         # non-breaking space
    }
    
    for curly, straight in curly_quotes.items():
        text = text.replace(curly, straight)
        
    return text

def remove_boilerplate_lines(lines: list[str]) -> list[str]:
    """
    Filters out lines that match repetitive headers, footers,
    or navigation page numbers.
    """
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        # Check if the line matches any known boilerplate regex patterns
        is_boilerplate = any(pattern.match(stripped) for pattern in BOILERPLATE_PATTERNS)
        if not is_boilerplate:
            cleaned_lines.append(line)
    return cleaned_lines

def normalize_whitespace(text: str) -> str:
    """
    Collapses multiple spaces to a single space, strips individual lines,
    and limits blank line runs to at most one empty line.
    """
    # Split text into lines, trim each line, and filter boilerplate
    lines = text.splitlines()
    lines = remove_boilerplate_lines(lines)
    
    processed_lines = []
    last_was_empty = False
    
    for line in lines:
        # Collapse multiple spaces or tabs inside the line
        cleaned_line = re.sub(r"[ \t]+", " ", line).strip()
        
        if cleaned_line == "":
            if not last_was_empty:
                processed_lines.append("")
                last_was_empty = True
        else:
            processed_lines.append(cleaned_line)
            last_was_empty = False
            
    # Remove leading/trailing blank lines in the list
    if processed_lines and processed_lines[0] == "":
        processed_lines.pop(0)
    if processed_lines and processed_lines[-1] == "":
        processed_lines.pop()
        
    return "\n".join(processed_lines)

def clean_text(raw_text: str) -> str:
    """
    Runs raw text through the full cleaning pipeline.
    """
    if not raw_text:
        return ""
    
    text = normalize_unicode_and_quotes(raw_text)
    text = normalize_whitespace(text)
    return text
