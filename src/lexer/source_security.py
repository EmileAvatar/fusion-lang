"""Source-level attack defenses for the Fusion lexer (Task 19.6).

Two attacks are blocked here, both verified to work against Fusion before this module
existed (2026-10-07):

1. Trojan Source (CVE-2021-42574): invisible bidirectional-control or zero-width Unicode
   characters make source code *display* differently from how it *compiles* - a reviewer
   reads one thing, the compiler builds another. These characters are rejected anywhere in a
   source file, including inside comments and string literals. A string that genuinely needs
   one writes it visibly with a \\uXXXX escape instead.

2. Confusable (homoglyph) identifiers: e.g. CYRILLIC SMALL LETTER A (U+0430) looks
   identical to Latin 'a', so a name spelled with it and the all-Latin `age` can be two
   different variables that look the same. Identifiers are ASCII-only by default.
   A project can opt in to Unicode identifiers via fusion.toml
   ([source] allow_unicode_identifiers = true); in that mode, identifiers mixing look-alike
   scripts, or containing compatibility characters (fullwidth/mathematical letters), are
   still rejected.

Known limitation: full Unicode TR39 confusable detection (the approach Rust's compiler uses)
needs a large data table and is deferred. In Unicode-identifier mode, two identifiers written
entirely in different look-alike scripts (all-Cyrillic vs all-Latin) are not caught - which
is exactly why ASCII-only is the default.
"""

import unicodedata
from typing import Optional, Tuple


# Bidirectional controls - can reorder how text displays without changing what it means
_BIDI_CONTROLS = {
    0x202A, 0x202B, 0x202C, 0x202D, 0x202E,  # LRE, RLE, PDF, LRO, RLO
    0x2066, 0x2067, 0x2068, 0x2069,          # LRI, RLI, FSI, PDI
    0x200E, 0x200F,                          # LRM, RLM
    0x061C,                                  # ARABIC LETTER MARK
}

# Invisible / zero-width characters - can hide content or split identifiers invisibly
_INVISIBLE = {
    0x200B,  # ZERO WIDTH SPACE
    0x200C,  # ZERO WIDTH NON-JOINER
    0x200D,  # ZERO WIDTH JOINER
    0x2060,  # WORD JOINER
    0xFEFF,  # ZERO WIDTH NO-BREAK SPACE (a byte-order mark is only legitimate at the very
             # start of a file - the Lexer strips it there before this check runs)
}

DISALLOWED_CODEPOINTS = _BIDI_CONTROLS | _INVISIBLE

# Scripts containing letters that look like letters of the other scripts in this set
CONFUSABLE_SCRIPTS = ("LATIN", "CYRILLIC", "GREEK", "ARMENIAN", "CHEROKEE", "COPTIC")

BYTE_ORDER_MARK = "\ufeff"


def describe_char(ch: str) -> str:
    """Return a readable description of a character, e.g. 'U+202E (RIGHT-TO-LEFT OVERRIDE)'."""
    return f"U+{ord(ch):04X} ({unicodedata.name(ch, 'UNNAMED CHARACTER')})"


def find_disallowed_character(source: str) -> Optional[Tuple[int, str]]:
    """Find the first invisible or bidirectional control character in the source.

    Returns:
        (index, character) of the first disallowed character, or None if the source is clean.
    """
    for index, ch in enumerate(source):
        if ord(ch) in DISALLOWED_CODEPOINTS:
            return index, ch
    return None


def disallowed_character_message(ch: str) -> str:
    """Build the error message for a disallowed character found in source."""
    return (
        f"invisible/bidirectional control character {describe_char(ch)} - can make code "
        f"display differently than it compiles (Trojan Source). Write \\u{ord(ch):04X} "
        f"inside a string literal if this character is intended"
    )


def _script_of(ch: str) -> Optional[str]:
    """Return the confusable-prone script a letter belongs to, if any.

    Derived from the Unicode character name (Python's stdlib has no script property), e.g.
    'CYRILLIC SMALL LETTER A' -> 'CYRILLIC', 'FULLWIDTH LATIN CAPITAL LETTER A' -> 'LATIN'.
    """
    for word in unicodedata.name(ch, "").split():
        if word in CONFUSABLE_SCRIPTS:
            return word
    return None


def check_identifier(name: str, allow_unicode: bool) -> Optional[str]:
    """Check an identifier against the homoglyph rules.

    Args:
        name: The identifier text
        allow_unicode: True if the project opted in to Unicode identifiers

    Returns:
        An error message if the identifier is rejected, or None if it is allowed.
    """
    if not allow_unicode:
        for ch in name:
            if ord(ch) > 0x7F:
                return (
                    f"identifier '{name}' contains non-ASCII character {describe_char(ch)}. "
                    f"Identifiers are ASCII-only by default, because look-alike characters "
                    f"from other scripts can make two different names appear identical. Set "
                    f"[source] allow_unicode_identifiers = true in fusion.toml to allow "
                    f"Unicode identifiers"
                )
        return None

    # Unicode identifiers allowed - still reject the clearly dangerous cases

    # Compatibility characters (fullwidth, mathematical styled letters, ...) are visual
    # duplicates of ordinary letters; NFKC normalization changes them
    if unicodedata.normalize("NFKC", name) != name:
        return (
            f"identifier '{name}' contains compatibility characters (e.g. fullwidth or "
            f"mathematical letters) that look like ordinary letters - use the plain form "
            f"'{unicodedata.normalize('NFKC', name)}'"
        )

    scripts = {s for s in (_script_of(ch) for ch in name if ch.isalpha()) if s}
    if len(scripts) > 1:
        return (
            f"identifier '{name}' mixes letters from look-alike scripts "
            f"({', '.join(sorted(scripts))}) - this is how homoglyph attacks make two "
            f"different names look identical"
        )

    return None
