"""
Shared data preparation for both classifiers.

WHY THIS FILE EXISTS AND WHY IT IS NOT OPTIONAL
-----------------------------------------------
Both datasets are LLM-generated. LLM-generated corpora reliably contain
near-duplicate rows - the model reaches for the same sentence frame twice.
If a near-duplicate pair straddles the train/test split, the test set is
partly memorised and your reported macro-F1 is inflated. You then quote that
number to a judge, they ask "how did you validate it", and the answer is
embarrassing.

Confirmed in the shipped data:
  field_intensity  5 near-duplicate pairs at Jaccard >= 0.6
                   1 genuine LABEL CONFLICT (FI091 vs FI092)
So this is not a hypothetical.

The fix is three steps, in order:
  1. drop exact duplicates
  2. group near-duplicates into blocks
  3. split on BLOCKS, not rows, so a duplicate pair can never straddle

Step 3 is what makes the held-out score honest. Do not skip it to save
four lines.
"""

from __future__ import annotations

import csv
import hashlib
import re
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# Jaccard at or above this counts as "near-duplicate" for blocking purposes.
# 0.60 was chosen by inspecting the actual pairs it catches in this corpus:
# at 0.60 it catches the five real restatements; at 0.35 it drowns in false
# positives on Devanagari, because \w+ under-splits Hindi and short Hindi
# rows produce tiny token sets that inflate Jaccard.
NEAR_DUP_JACCARD = 0.60
MIN_TOKENS_FOR_DUP_CHECK = 5


# ---------------------------------------------------------------------------
# text normalisation
# ---------------------------------------------------------------------------

def normalise(text: str) -> str:
    """Light normalisation for the ENCODER. Deliberately conservative -
    the multilingual model wants real text, so we do not strip stopwords,
    lowercase Devanagari, or remove diacritics.

    NFC matters: Devanagari can be encoded decomposed or precomposed, and
    two visually identical Hindi strings with different normal forms embed
    to different vectors. One line, prevents a whole class of confusion."""
    text = unicodedata.normalize("NFC", text)
    text = text.replace("​", "").replace("﻿", "")   # zero-width, BOM
    return re.sub(r"\s+", " ", text).strip()


def _dup_tokens(text: str) -> set[str]:
    """Tokens for DUPLICATE DETECTION only - never for the model.
    Devanagari-aware: \\w+ keeps Devanagari as word characters, so Hindi
    tokenises on whitespace/punctuation, which is good enough for Jaccard."""
    return set(re.findall(r"\w+", normalise(text).lower()))


def _jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


# ---------------------------------------------------------------------------
# loading
# ---------------------------------------------------------------------------

@dataclass
class Row:
    id: str
    text: str
    label: str
    language: str = "unknown"
    block: int = -1          # near-duplicate group id; the split unit


@dataclass
class PrepReport:
    total_in: int = 0
    exact_dupes: int = 0
    near_dup_pairs: int = 0
    label_conflicts: list = field(default_factory=list)
    blocks: int = 0
    label_counts: dict = field(default_factory=dict)
    language_counts: dict = field(default_factory=dict)

    def render(self) -> str:
        lines = [
            f"  rows in                {self.total_in}",
            f"  exact duplicates       {self.exact_dupes} (dropped)",
            f"  near-duplicate pairs   {self.near_dup_pairs} (grouped, never split apart)",
            f"  split blocks           {self.blocks}",
            f"  labels                 {dict(sorted(self.label_counts.items()))}",
        ]
        if self.language_counts:
            lines.append(f"  languages              {dict(sorted(self.language_counts.items()))}")
        if self.label_conflicts:
            lines.append(f"  ?? REVIEW              {len(self.label_conflicts)} high-overlap pairs with different labels:")
            for a, la, b, lb, j in self.label_conflicts:
                lines.append(f"       J={j:.2f}  {a}[{la}]  vs  {b}[{lb}]")
            lines.append("       Each is EITHER a mislabel OR two rows sharing an LLM sentence frame")
            lines.append("       while describing genuinely different things. Both occur in this")
            lines.append("       corpus, so read them before changing anything. A real mislabel caps")
            lines.append("       your achievable accuracy; a shared frame is harmless and is in fact")
            lines.append("       useful training signal - it forces the model to learn content words")
            lines.append("       rather than the template.")
        return "\n".join(lines)


def load_csv(path: Path, label_col: str) -> list[Row]:
    rows = []
    with open(path, encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            text = normalise(r["text"])
            if not text:
                continue
            rows.append(Row(
                id=r.get("id", ""),
                text=text,
                label=r[label_col].strip(),
                language=r.get("language", "unknown").strip() or "unknown",
            ))
    return rows


# ---------------------------------------------------------------------------
# dedup + blocking
# ---------------------------------------------------------------------------

def dedupe_and_block(rows: list[Row]) -> tuple[list[Row], PrepReport]:
    """Drop exact duplicates, then union-find near-duplicates into blocks."""
    rep = PrepReport(total_in=len(rows))

    # --- 1. exact duplicates (on normalised text) -------------------------
    seen: dict[str, Row] = {}
    kept: list[Row] = []
    for r in rows:
        h = hashlib.sha256(r.text.encode()).hexdigest()
        if h in seen:
            rep.exact_dupes += 1
            continue
        seen[h] = r
        kept.append(r)

    # --- 2. near-duplicates -> union-find ---------------------------------
    parent = list(range(len(kept)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i, j):
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[rj] = ri

    toks = [_dup_tokens(r.text) for r in kept]

    # Inverted index so we compare only rows sharing a rare-ish token,
    # instead of all n^2 pairs. At n=1320 brute force is fine (~870k pairs,
    # under a second) but this keeps it linear-ish as the corpus grows with
    # real submissions - which is the whole point of the feedback loop.
    index: dict[str, list[int]] = defaultdict(list)
    for i, ts in enumerate(toks):
        for t in ts:
            index[t].append(i)

    candidates: set[tuple[int, int]] = set()
    for postings in index.values():
        if len(postings) > 60:        # skip stopword-like tokens
            continue
        for a in range(len(postings)):
            for b in range(a + 1, len(postings)):
                candidates.add((postings[a], postings[b]))

    for i, j in candidates:
        if len(toks[i]) < MIN_TOKENS_FOR_DUP_CHECK or len(toks[j]) < MIN_TOKENS_FOR_DUP_CHECK:
            continue
        j_score = _jaccard(toks[i], toks[j])
        if j_score >= NEAR_DUP_JACCARD:
            rep.near_dup_pairs += 1
            union(i, j)
            if kept[i].label != kept[j].label:
                rep.label_conflicts.append(
                    (kept[i].id, kept[i].label, kept[j].id, kept[j].label, j_score))

    for i, r in enumerate(kept):
        r.block = find(i)

    rep.blocks = len({r.block for r in kept})
    rep.label_counts = dict(Counter(r.label for r in kept))
    langs = Counter(r.language for r in kept)
    if set(langs) != {"unknown"}:
        rep.language_counts = dict(langs)
    return kept, rep


# ---------------------------------------------------------------------------
# split
# ---------------------------------------------------------------------------

def stratified_block_split(rows: list[Row], test_size: float = 0.2, seed: int = 42
                           ) -> tuple[list[Row], list[Row]]:
    """Stratify by label, but assign whole BLOCKS so near-duplicates cannot
    straddle the boundary.

    Blocks are assigned to the split by their majority label. A block that
    mixes labels (i.e. contains a label conflict) is a data bug, already
    reported; it goes to train so it cannot corrupt the test score.
    """
    import random
    rng = random.Random(seed)

    by_block: dict[int, list[Row]] = defaultdict(list)
    for r in rows:
        by_block[r.block].append(r)

    per_label: dict[str, list[int]] = defaultdict(list)
    mixed_blocks: list[int] = []
    for bid, members in by_block.items():
        labels = Counter(m.label for m in members)
        if len(labels) > 1:
            mixed_blocks.append(bid)
        else:
            per_label[members[0].label].append(bid)

    train_blocks, test_blocks = set(mixed_blocks), set()
    for label, bids in per_label.items():
        bids = sorted(bids)
        rng.shuffle(bids)
        # count by ROWS, not blocks, so a big block does not skew the ratio
        target = test_size * sum(len(by_block[b]) for b in bids)
        acc = 0
        for b in bids:
            if acc < target:
                test_blocks.add(b)
                acc += len(by_block[b])
            else:
                train_blocks.add(b)

    train = [r for r in rows if r.block in train_blocks]
    test = [r for r in rows if r.block in test_blocks]
    return train, test


def prepare(path: Path, label_col: str, test_size: float = 0.2, seed: int = 42):
    """Full pipeline: load -> dedupe -> block -> split. Returns (train, test, report)."""
    rows = load_csv(path, label_col)
    rows, report = dedupe_and_block(rows)
    train, test = stratified_block_split(rows, test_size, seed)
    return train, test, report
