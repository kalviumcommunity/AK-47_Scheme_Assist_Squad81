import re
import math
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional

try:
    import tiktoken
    _TIKTOKEN_AVAILABLE = True
    _ENCODER = tiktoken.get_encoding("cl100k_base")
except ImportError:
    _TIKTOKEN_AVAILABLE = False
    _ENCODER = None


def estimate_tokens(text: str) -> int:
    """
    Estimates token count using tiktoken if available,
    otherwise falls back to rule-of-thumb (4 characters per token).
    """
    if not text:
        return 0
    if _TIKTOKEN_AVAILABLE and _ENCODER:
        try:
            return len(_ENCODER.encode(text))
        except Exception:
            pass
    return max(1, math.ceil(len(text) / 4.0))


@dataclass
class Chunk:
    """
    Standard Chunk data structure holding chunk payload, coordinates, and metadata.
    """
    chunk_id: str
    text: str
    source_doc: str = ""
    strategy: str = ""
    start_char: int = 0
    end_char: int = 0
    char_count: int = 0
    word_count: int = 0
    token_count_estimate: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.char_count:
            self.char_count = len(self.text)
        if not self.word_count:
            self.word_count = len(self.text.split())
        if not self.token_count_estimate:
            self.token_count_estimate = estimate_tokens(self.text)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# =====================================================================
# Strategy 1: Fixed-Size Naive (No Overlap)
# =====================================================================
def fixed_size_chunks(
    text: str,
    size: int = 500,
    overlap: int = 0,
    source_doc: str = "doc"
) -> List[Chunk]:
    """
    Splits text into fixed-width character slices.
    If overlap=0, slice boundaries are strictly adjacent without shared context.
    """
    if not text or not text.strip():
        return []

    text = text.strip()
    chunks = []
    i = 0
    chunk_index = 1
    step = size if overlap <= 0 else max(1, size - overlap)

    while i < len(text):
        chunk_text = text[i : i + size]
        if not chunk_text.strip():
            i += step
            continue

        chunk = Chunk(
            chunk_id=f"{source_doc}_fixed_{chunk_index:03d}",
            text=chunk_text,
            source_doc=source_doc,
            strategy="Fixed-Size (Naive)" if overlap == 0 else "Fixed-Size (Overlap)",
            start_char=i,
            end_char=i + len(chunk_text),
            metadata={"size_param": size, "overlap_param": overlap}
        )
        chunks.append(chunk)
        chunk_index += 1
        i += step

    return chunks


# =====================================================================
# Strategy 2: Fixed-Size with Sliding Window Overlap
# =====================================================================
def fixed_size_overlap_chunks(
    text: str,
    size: int = 500,
    overlap: int = 80,
    source_doc: str = "doc"
) -> List[Chunk]:
    """
    Splits text into fixed-width character slices with sliding window overlap
    to prevent losing entities or key clauses at chunk boundaries.
    """
    return fixed_size_chunks(text, size=size, overlap=overlap, source_doc=source_doc)


# =====================================================================
# Strategy 3: Paragraph-Based Chunking
# =====================================================================
def paragraph_chunks(
    text: str,
    max_size: int = 1000,
    source_doc: str = "doc"
) -> List[Chunk]:
    """
    Splits text by double newlines (\n\n), respecting structural paragraph breaks.
    If a paragraph is excessively long (> max_size), it is partitioned.
    Adjacent small paragraphs may optionally be bundled.
    """
    if not text or not text.strip():
        return []

    raw_paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    chunk_index = 1
    current_char_offset = 0

    for p in raw_paragraphs:
        p_start = text.find(p, current_char_offset)
        if p_start == -1:
            p_start = current_char_offset
        p_end = p_start + len(p)
        current_char_offset = p_end

        if len(p) <= max_size:
            chunks.append(
                Chunk(
                    chunk_id=f"{source_doc}_para_{chunk_index:03d}",
                    text=p,
                    source_doc=source_doc,
                    strategy="Paragraph-Based",
                    start_char=p_start,
                    end_char=p_end,
                    metadata={"paragraph_number": chunk_index}
                )
            )
            chunk_index += 1
        else:
            # If a single paragraph is too large, split it with fixed overlap
            sub_chunks = fixed_size_overlap_chunks(p, size=max_size, overlap=100, source_doc=source_doc)
            for sc in sub_chunks:
                sc.chunk_id = f"{source_doc}_para_{chunk_index:03d}"
                sc.strategy = "Paragraph-Based (Split)"
                sc.start_char = p_start + sc.start_char
                sc.end_char = p_start + sc.end_char
                chunks.append(sc)
                chunk_index += 1

    return chunks


# =====================================================================
# Strategy 4: Sentence-Based Chunking with Sentence Overlap
# =====================================================================
def sentence_chunks(
    text: str,
    max_size: int = 600,
    overlap_sentences: int = 1,
    source_doc: str = "doc"
) -> List[Chunk]:
    """
    Splits text into complete grammatical sentences using regex delimiters.
    Accumulates sentences into chunks up to max_size characters, with an overlap
    of `overlap_sentences` between consecutive chunks.
    """
    if not text or not text.strip():
        return []

    # Regex splitting on sentence boundaries (. ! ? followed by space or newline)
    raw_sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    sentences = [s.strip() for s in raw_sentences if s.strip()]

    if not sentences:
        return []

    chunks = []
    chunk_index = 1
    i = 0

    while i < len(sentences):
        accumulated_sentences = []
        current_len = 0
        j = i

        while j < len(sentences):
            cand_sent = sentences[j]
            cand_len = len(cand_sent) + (1 if accumulated_sentences else 0)
            if current_len + cand_len > max_size and accumulated_sentences:
                break
            accumulated_sentences.append(cand_sent)
            current_len += cand_len
            j += 1

        chunk_text = " ".join(accumulated_sentences)
        start_char = text.find(accumulated_sentences[0]) if accumulated_sentences else 0
        end_char = (
            text.find(accumulated_sentences[-1], start_char) + len(accumulated_sentences[-1])
            if accumulated_sentences
            else len(chunk_text)
        )

        chunks.append(
            Chunk(
                chunk_id=f"{source_doc}_sent_{chunk_index:03d}",
                text=chunk_text,
                source_doc=source_doc,
                strategy="Sentence-Based",
                start_char=max(0, start_char),
                end_char=max(start_char + len(chunk_text), end_char),
                metadata={
                    "sentence_count": len(accumulated_sentences),
                    "start_sentence_idx": i,
                    "end_sentence_idx": j - 1,
                }
            )
        )
        chunk_index += 1

        if j >= len(sentences):
            break

        # Step forward preserving sentence overlap
        i = max(i + 1, j - overlap_sentences)

    return chunks


# =====================================================================
# Strategy 5: Recursive Character Text Splitting (Semantic / Hierarchical)
# =====================================================================
def recursive_character_chunks(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 80,
    separators: Optional[List[str]] = None,
    source_doc: str = "doc"
) -> List[Chunk]:
    """
    Splits text hierarchically using a prioritized list of separators
    (double newlines -> single newlines -> sentence periods -> spaces -> raw characters).
    Maintains semantic paragraphs/headings together whenever possible,
    splitting only when necessary, while maintaining chunk_overlap.
    """
    if not text or not text.strip():
        return []

    if separators is None:
        separators = ["\n\n", "\n", ". ", " ", ""]

    def _split_into_atomic_pieces(txt: str, sep_list: List[str]) -> List[str]:
        if not txt:
            return []
        if len(txt) <= chunk_size:
            return [txt]

        # Find first matching separator
        sep = ""
        new_sep_list = []
        for i, s in enumerate(sep_list):
            if s == "":
                sep = ""
                new_sep_list = []
                break
            if s in txt:
                sep = s
                new_sep_list = sep_list[i + 1 :]
                break

        if not sep:
            # Fallback to character splitting
            step = max(1, chunk_size - chunk_overlap)
            return [txt[k : k + chunk_size] for k in range(0, len(txt), step)]

        parts = txt.split(sep)
        atomic = []
        for idx, part in enumerate(parts):
            if not part:
                continue
            # Restore separator token except for last item
            p_text = part if (idx == len(parts) - 1 or not sep) else part + sep
            if len(p_text) <= chunk_size:
                atomic.append(p_text)
            else:
                sub_atomic = _split_into_atomic_pieces(p_text, new_sep_list)
                atomic.extend(sub_atomic)
        return atomic

    # 1. Get flat list of pieces where each piece <= chunk_size
    atomic_splits = _split_into_atomic_pieces(text.strip(), separators)

    # 2. Merge atomic pieces into final chunks with chunk_overlap
    final_chunks: List[str] = []
    current_chunk_parts: List[str] = []
    current_length = 0

    for piece in atomic_splits:
        piece_len = len(piece)
        if current_length + piece_len > chunk_size and current_chunk_parts:
            merged = "".join(current_chunk_parts).strip()
            if merged:
                final_chunks.append(merged)

            # Slide window back for overlap
            overlap_parts: List[str] = []
            overlap_len = 0
            for p in reversed(current_chunk_parts):
                if overlap_len + len(p) <= chunk_overlap:
                    overlap_parts.insert(0, p)
                    overlap_len += len(p)
                else:
                    break

            current_chunk_parts = overlap_parts
            current_length = sum(len(p) for p in current_chunk_parts)

        current_chunk_parts.append(piece)
        current_length += piece_len

    if current_chunk_parts:
        merged = "".join(current_chunk_parts).strip()
        if merged:
            final_chunks.append(merged)

    chunks = []
    current_char_offset = 0

    for idx, c_text in enumerate(final_chunks, start=1):
        c_text = c_text.strip()
        if not c_text:
            continue
        c_start = text.find(c_text, current_char_offset)
        if c_start == -1:
            c_start = current_char_offset
        c_end = c_start + len(c_text)
        current_char_offset = max(c_start, current_char_offset)

        chunks.append(
            Chunk(
                chunk_id=f"{source_doc}_rec_{idx:03d}",
                text=c_text,
                source_doc=source_doc,
                strategy="Recursive Character",
                start_char=c_start,
                end_char=c_end,
                metadata={"chunk_size_target": chunk_size, "overlap": chunk_overlap}
            )
        )

    return chunks


# =====================================================================
# Statistical Analysis & Comparison Engine
# =====================================================================
@dataclass
class StrategyStats:
    strategy_name: str
    chunk_count: int
    total_characters: int
    min_char_size: int
    max_char_size: int
    avg_char_size: float
    median_char_size: float
    avg_word_size: float
    avg_token_size: float
    mid_sentence_cuts: int
    chunks: List[Chunk] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "strategy_name": self.strategy_name,
            "chunk_count": self.chunk_count,
            "total_characters": self.total_characters,
            "min_char_size": self.min_char_size,
            "max_char_size": self.max_char_size,
            "avg_char_size": round(self.avg_char_size, 2),
            "median_char_size": round(self.median_char_size, 2),
            "avg_word_size": round(self.avg_word_size, 2),
            "avg_token_size": round(self.avg_token_size, 2),
            "mid_sentence_cuts": self.mid_sentence_cuts,
        }


def count_mid_sentence_cuts(chunks: List[Chunk]) -> int:
    """
    Heuristic to detect unnatural chunk boundaries:
    A chunk cuts mid-sentence if it does not end with terminal punctuation
    (. ! ? : ; \" ' ) or markdown headers, and the next chunk starts in lowercase or mid-clause.
    """
    cuts = 0
    terminal_punct = {".", "!", "?", ":", "\"", "'", "}", "]", "#"}
    for c in chunks:
        stripped = c.text.strip()
        if stripped and stripped[-1] not in terminal_punct:
            cuts += 1
    return cuts


def analyze_chunks(chunks: List[Chunk], strategy_name: str) -> StrategyStats:
    """
    Computes summary statistics across generated chunks.
    """
    if not chunks:
        return StrategyStats(
            strategy_name=strategy_name,
            chunk_count=0,
            total_characters=0,
            min_char_size=0,
            max_char_size=0,
            avg_char_size=0.0,
            median_char_size=0.0,
            avg_word_size=0.0,
            avg_token_size=0.0,
            mid_sentence_cuts=0,
            chunks=[]
        )

    char_sizes = [c.char_count for c in chunks]
    word_sizes = [c.word_count for c in chunks]
    token_sizes = [c.token_count_estimate for c in chunks]

    sorted_chars = sorted(char_sizes)
    n = len(sorted_chars)
    median_char = (
        sorted_chars[n // 2]
        if n % 2 != 0
        else (sorted_chars[n // 2 - 1] + sorted_chars[n // 2]) / 2.0
    )

    return StrategyStats(
        strategy_name=strategy_name,
        chunk_count=len(chunks),
        total_characters=sum(char_sizes),
        min_char_size=min(char_sizes),
        max_char_size=max(char_sizes),
        avg_char_size=sum(char_sizes) / len(char_sizes),
        median_char_size=median_char,
        avg_word_size=sum(word_sizes) / len(word_sizes),
        avg_token_size=sum(token_sizes) / len(token_sizes),
        mid_sentence_cuts=count_mid_sentence_cuts(chunks),
        chunks=chunks
    )


def compare_all_strategies(
    text: str,
    source_doc: str = "sample_doc.md"
) -> Dict[str, StrategyStats]:
    """
    Executes and benchmarks all defined chunking strategies against the input text.
    """
    strategies = {
        "Fixed-Size (Naive 500 chars, no overlap)": fixed_size_chunks(
            text, size=500, overlap=0, source_doc=source_doc
        ),
        "Fixed-Size (500 chars, 80 char overlap)": fixed_size_overlap_chunks(
            text, size=500, overlap=80, source_doc=source_doc
        ),
        "Paragraph-Based (Natural paragraph breaks)": paragraph_chunks(
            text, max_size=1000, source_doc=source_doc
        ),
        "Sentence-Based (600 char max, 1 sentence overlap)": sentence_chunks(
            text, max_size=600, overlap_sentences=1, source_doc=source_doc
        ),
        "Recursive Character (500 chars, 80 char overlap)": recursive_character_chunks(
            text, chunk_size=500, chunk_overlap=80, source_doc=source_doc
        ),
    }

    results = {}
    for name, chunk_list in strategies.items():
        results[name] = analyze_chunks(chunk_list, strategy_name=name)

    return results


def format_comparison_table(stats_map: Dict[str, StrategyStats]) -> str:
    """
    Generates a formatted ASCII comparison table for console & log reports.
    """
    lines = []
    lines.append("=" * 115)
    lines.append(
        f"{'Strategy Name':<42} | {'Count':<6} | {'Avg Chars':<10} | {'Min-Max Chars':<14} | {'Avg Tokens':<11} | {'Mid-Cuts':<8}"
    )
    lines.append("=" * 115)

    for name, s in stats_map.items():
        min_max_str = f"{s.min_char_size}-{s.max_char_size}"
        lines.append(
            f"{name:<42} | {s.chunk_count:<6} | {s.avg_char_size:<10.1f} | {min_max_str:<14} | {s.avg_token_size:<11.1f} | {s.mid_sentence_cuts:<8}"
        )

    lines.append("=" * 115)
    return "\n".join(lines)
