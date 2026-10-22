#!/usr/bin/env python3
"""Offline Unicode casing analysis for agents.

The tool exposes four deterministic modes built strictly on the Python
standard library (``str`` case methods and ``unicodedata``):

* ``case_map``       - map text through upper/lower/title/casefold/swapcase and
                       explain every non-obvious mapping (expansions, final
                       sigma, locale caveats, compatibility collisions).
* ``equivalence``    - compare two strings case-insensitively via casefold (the
                       correct way), via lower (shown to diverge where it does)
                       and via NFC+casefold (the canonical identifier form).
* ``style_audit``    - detect the naming style of an identifier (snake_case,
                       camelCase, PascalCase, SCREAMING_SNAKE, kebab-case,
                       mixed) with per-word evidence, audit it against a target
                       style, and produce the deterministic rename.
* ``char_case_info`` - full case profile of a single character: name, category,
                       cased/upper/lower/title mirrors, all five mappings and a
                       simple-vs-full mapping explanation.

Semantics notes:

* Python case mapping is locale-independent (there is no Turkish/Azeri mode);
  the tool documents those divergences instead of emulating them.
* ``per_char`` entries show each character's *isolated* mapping (the result of
  the same ``str`` method on that character alone). Two position-dependent
  behaviors make isolated and in-context results differ: ``title()`` by
  definition (only word-initial characters uppercase) and capital sigma under
  ``lower()`` (the Final_Sigma rule). Those positions carry a
  ``mapped_in_context`` field whenever offset accounting is safe (every target
  except ``title``).
* ``changed_count`` counts characters whose isolated mapping differs; for
  ``upper``/``lower``/``casefold``/``swapcase`` this matches the characters
  that actually differ between input and result.
"""

# Public execute() converts validation exceptions into structured tool errors.
# The notes intentionally quote the confusable Unicode characters (sigma,
# dotless i, long s, Greek mu) that this tool documents.
# ruff: noqa: TRY003, RUF001, RUF003

import bisect
import functools
import unicodedata
from typing import Any, ClassVar

from agentuniverse.agent.action.tool.tool import Tool

# Frozen Case_Ignorable ranges (Unicode 14.0, mirroring the stdlib Unicode
# database shipped with the supported Python versions). Derived from the
# Final_Sigma context rule of SpecialCasing.txt: a character X is
# Case_Ignorable iff the capital sigma in "AS"+X+"A" still lowercases
# medially (to 'σ', because an ignorable run between sigma and a cased letter
# does not end the word) while "AS"+X keeps the word-final form (to 'ς').
# Stored as inclusive (low, high) codepoint pairs.
_CASE_IGNORABLE_RANGES: tuple[tuple[int, int], ...] = (
    (0x0027, 0x0027),
    (0x002E, 0x002E),
    (0x003A, 0x003A),
    (0x005E, 0x005E),
    (0x0060, 0x0060),
    (0x00A8, 0x00A8),
    (0x00AD, 0x00AD),
    (0x00AF, 0x00AF),
    (0x00B4, 0x00B4),
    (0x00B7, 0x00B8),
    (0x02B0, 0x036F),
    (0x0374, 0x0375),
    (0x037A, 0x037A),
    (0x0384, 0x0385),
    (0x0387, 0x0387),
    (0x0483, 0x0489),
    (0x0559, 0x0559),
    (0x055F, 0x055F),
    (0x0591, 0x05BD),
    (0x05BF, 0x05BF),
    (0x05C1, 0x05C2),
    (0x05C4, 0x05C5),
    (0x05C7, 0x05C7),
    (0x05F4, 0x05F4),
    (0x0600, 0x0605),
    (0x0610, 0x061A),
    (0x061C, 0x061C),
    (0x0640, 0x0640),
    (0x064B, 0x065F),
    (0x0670, 0x0670),
    (0x06D6, 0x06DD),
    (0x06DF, 0x06E8),
    (0x06EA, 0x06ED),
    (0x070F, 0x070F),
    (0x0711, 0x0711),
    (0x0730, 0x074A),
    (0x07A6, 0x07B0),
    (0x07EB, 0x07F5),
    (0x07FA, 0x07FA),
    (0x07FD, 0x07FD),
    (0x0816, 0x082D),
    (0x0859, 0x085B),
    (0x0888, 0x0888),
    (0x0890, 0x0891),
    (0x0898, 0x089F),
    (0x08C9, 0x0902),
    (0x093A, 0x093A),
    (0x093C, 0x093C),
    (0x0941, 0x0948),
    (0x094D, 0x094D),
    (0x0951, 0x0957),
    (0x0962, 0x0963),
    (0x0971, 0x0971),
    (0x0981, 0x0981),
    (0x09BC, 0x09BC),
    (0x09C1, 0x09C4),
    (0x09CD, 0x09CD),
    (0x09E2, 0x09E3),
    (0x09FE, 0x09FE),
    (0x0A01, 0x0A02),
    (0x0A3C, 0x0A3C),
    (0x0A41, 0x0A42),
    (0x0A47, 0x0A48),
    (0x0A4B, 0x0A4D),
    (0x0A51, 0x0A51),
    (0x0A70, 0x0A71),
    (0x0A75, 0x0A75),
    (0x0A81, 0x0A82),
    (0x0ABC, 0x0ABC),
    (0x0AC1, 0x0AC5),
    (0x0AC7, 0x0AC8),
    (0x0ACD, 0x0ACD),
    (0x0AE2, 0x0AE3),
    (0x0AFA, 0x0AFF),
    (0x0B01, 0x0B01),
    (0x0B3C, 0x0B3C),
    (0x0B3F, 0x0B3F),
    (0x0B41, 0x0B44),
    (0x0B4D, 0x0B4D),
    (0x0B55, 0x0B56),
    (0x0B62, 0x0B63),
    (0x0B82, 0x0B82),
    (0x0BC0, 0x0BC0),
    (0x0BCD, 0x0BCD),
    (0x0C00, 0x0C00),
    (0x0C04, 0x0C04),
    (0x0C3C, 0x0C3C),
    (0x0C3E, 0x0C40),
    (0x0C46, 0x0C48),
    (0x0C4A, 0x0C4D),
    (0x0C55, 0x0C56),
    (0x0C62, 0x0C63),
    (0x0C81, 0x0C81),
    (0x0CBC, 0x0CBC),
    (0x0CBF, 0x0CBF),
    (0x0CC6, 0x0CC6),
    (0x0CCC, 0x0CCD),
    (0x0CE2, 0x0CE3),
    (0x0D00, 0x0D01),
    (0x0D3B, 0x0D3C),
    (0x0D41, 0x0D44),
    (0x0D4D, 0x0D4D),
    (0x0D62, 0x0D63),
    (0x0D81, 0x0D81),
    (0x0DCA, 0x0DCA),
    (0x0DD2, 0x0DD4),
    (0x0DD6, 0x0DD6),
    (0x0E31, 0x0E31),
    (0x0E34, 0x0E3A),
    (0x0E46, 0x0E4E),
    (0x0EB1, 0x0EB1),
    (0x0EB4, 0x0EBC),
    (0x0EC6, 0x0EC6),
    (0x0EC8, 0x0ECD),
    (0x0F18, 0x0F19),
    (0x0F35, 0x0F35),
    (0x0F37, 0x0F37),
    (0x0F39, 0x0F39),
    (0x0F71, 0x0F7E),
    (0x0F80, 0x0F84),
    (0x0F86, 0x0F87),
    (0x0F8D, 0x0F97),
    (0x0F99, 0x0FBC),
    (0x0FC6, 0x0FC6),
    (0x102D, 0x1030),
    (0x1032, 0x1037),
    (0x1039, 0x103A),
    (0x103D, 0x103E),
    (0x1058, 0x1059),
    (0x105E, 0x1060),
    (0x1071, 0x1074),
    (0x1082, 0x1082),
    (0x1085, 0x1086),
    (0x108D, 0x108D),
    (0x109D, 0x109D),
    (0x10FC, 0x10FC),
    (0x135D, 0x135F),
    (0x1712, 0x1714),
    (0x1732, 0x1733),
    (0x1752, 0x1753),
    (0x1772, 0x1773),
    (0x17B4, 0x17B5),
    (0x17B7, 0x17BD),
    (0x17C6, 0x17C6),
    (0x17C9, 0x17D3),
    (0x17D7, 0x17D7),
    (0x17DD, 0x17DD),
    (0x180B, 0x180F),
    (0x1843, 0x1843),
    (0x1885, 0x1886),
    (0x18A9, 0x18A9),
    (0x1920, 0x1922),
    (0x1927, 0x1928),
    (0x1932, 0x1932),
    (0x1939, 0x193B),
    (0x1A17, 0x1A18),
    (0x1A1B, 0x1A1B),
    (0x1A56, 0x1A56),
    (0x1A58, 0x1A5E),
    (0x1A60, 0x1A60),
    (0x1A62, 0x1A62),
    (0x1A65, 0x1A6C),
    (0x1A73, 0x1A7C),
    (0x1A7F, 0x1A7F),
    (0x1AA7, 0x1AA7),
    (0x1AB0, 0x1ACE),
    (0x1B00, 0x1B03),
    (0x1B34, 0x1B34),
    (0x1B36, 0x1B3A),
    (0x1B3C, 0x1B3C),
    (0x1B42, 0x1B42),
    (0x1B6B, 0x1B73),
    (0x1B80, 0x1B81),
    (0x1BA2, 0x1BA5),
    (0x1BA8, 0x1BA9),
    (0x1BAB, 0x1BAD),
    (0x1BE6, 0x1BE6),
    (0x1BE8, 0x1BE9),
    (0x1BED, 0x1BED),
    (0x1BEF, 0x1BF1),
    (0x1C2C, 0x1C33),
    (0x1C36, 0x1C37),
    (0x1C78, 0x1C7D),
    (0x1CD0, 0x1CD2),
    (0x1CD4, 0x1CE0),
    (0x1CE2, 0x1CE8),
    (0x1CED, 0x1CED),
    (0x1CF4, 0x1CF4),
    (0x1CF8, 0x1CF9),
    (0x1D2C, 0x1D6A),
    (0x1D78, 0x1D78),
    (0x1D9B, 0x1DFF),
    (0x1FBD, 0x1FBD),
    (0x1FBF, 0x1FC1),
    (0x1FCD, 0x1FCF),
    (0x1FDD, 0x1FDF),
    (0x1FED, 0x1FEF),
    (0x1FFD, 0x1FFE),
    (0x200B, 0x200F),
    (0x2018, 0x2019),
    (0x2024, 0x2024),
    (0x2027, 0x2027),
    (0x202A, 0x202E),
    (0x2060, 0x2064),
    (0x2066, 0x206F),
    (0x2071, 0x2071),
    (0x207F, 0x207F),
    (0x2090, 0x209C),
    (0x20D0, 0x20F0),
    (0x2C7C, 0x2C7D),
    (0x2CEF, 0x2CF1),
    (0x2D6F, 0x2D6F),
    (0x2D7F, 0x2D7F),
    (0x2DE0, 0x2DFF),
    (0x2E2F, 0x2E2F),
    (0x3005, 0x3005),
    (0x302A, 0x302D),
    (0x3031, 0x3035),
    (0x303B, 0x303B),
    (0x3099, 0x309E),
    (0x30FC, 0x30FE),
    (0xA015, 0xA015),
    (0xA4F8, 0xA4FD),
    (0xA60C, 0xA60C),
    (0xA66F, 0xA672),
    (0xA674, 0xA67D),
    (0xA67F, 0xA67F),
    (0xA69C, 0xA69F),
    (0xA6F0, 0xA6F1),
    (0xA700, 0xA721),
    (0xA770, 0xA770),
    (0xA788, 0xA78A),
    (0xA7F2, 0xA7F4),
    (0xA7F8, 0xA7F9),
    (0xA802, 0xA802),
    (0xA806, 0xA806),
    (0xA80B, 0xA80B),
    (0xA825, 0xA826),
    (0xA82C, 0xA82C),
    (0xA8C4, 0xA8C5),
    (0xA8E0, 0xA8F1),
    (0xA8FF, 0xA8FF),
    (0xA926, 0xA92D),
    (0xA947, 0xA951),
    (0xA980, 0xA982),
    (0xA9B3, 0xA9B3),
    (0xA9B6, 0xA9B9),
    (0xA9BC, 0xA9BD),
    (0xA9CF, 0xA9CF),
    (0xA9E5, 0xA9E6),
    (0xAA29, 0xAA2E),
    (0xAA31, 0xAA32),
    (0xAA35, 0xAA36),
    (0xAA43, 0xAA43),
    (0xAA4C, 0xAA4C),
    (0xAA70, 0xAA70),
    (0xAA7C, 0xAA7C),
    (0xAAB0, 0xAAB0),
    (0xAAB2, 0xAAB4),
    (0xAAB7, 0xAAB8),
    (0xAABE, 0xAABF),
    (0xAAC1, 0xAAC1),
    (0xAADD, 0xAADD),
    (0xAAEC, 0xAAED),
    (0xAAF3, 0xAAF4),
    (0xAAF6, 0xAAF6),
    (0xAB5B, 0xAB5F),
    (0xAB69, 0xAB6B),
    (0xABE5, 0xABE5),
    (0xABE8, 0xABE8),
    (0xABED, 0xABED),
    (0xFB1E, 0xFB1E),
    (0xFBB2, 0xFBC2),
    (0xFE00, 0xFE0F),
    (0xFE13, 0xFE13),
    (0xFE20, 0xFE2F),
    (0xFE52, 0xFE52),
    (0xFE55, 0xFE55),
    (0xFEFF, 0xFEFF),
    (0xFF07, 0xFF07),
    (0xFF0E, 0xFF0E),
    (0xFF1A, 0xFF1A),
    (0xFF3E, 0xFF3E),
    (0xFF40, 0xFF40),
    (0xFF70, 0xFF70),
    (0xFF9E, 0xFF9F),
    (0xFFE3, 0xFFE3),
    (0xFFF9, 0xFFFB),
    (0x101FD, 0x101FD),
    (0x102E0, 0x102E0),
    (0x10376, 0x1037A),
    (0x10780, 0x10785),
    (0x10787, 0x107B0),
    (0x107B2, 0x107BA),
    (0x10A01, 0x10A03),
    (0x10A05, 0x10A06),
    (0x10A0C, 0x10A0F),
    (0x10A38, 0x10A3A),
    (0x10A3F, 0x10A3F),
    (0x10AE5, 0x10AE6),
    (0x10D24, 0x10D27),
    (0x10EAB, 0x10EAC),
    (0x10F46, 0x10F50),
    (0x10F82, 0x10F85),
    (0x11001, 0x11001),
    (0x11038, 0x11046),
    (0x11070, 0x11070),
    (0x11073, 0x11074),
    (0x1107F, 0x11081),
    (0x110B3, 0x110B6),
    (0x110B9, 0x110BA),
    (0x110BD, 0x110BD),
    (0x110C2, 0x110C2),
    (0x110CD, 0x110CD),
    (0x11100, 0x11102),
    (0x11127, 0x1112B),
    (0x1112D, 0x11134),
    (0x11173, 0x11173),
    (0x11180, 0x11181),
    (0x111B6, 0x111BE),
    (0x111C9, 0x111CC),
    (0x111CF, 0x111CF),
    (0x1122F, 0x11231),
    (0x11234, 0x11234),
    (0x11236, 0x11237),
    (0x1123E, 0x1123E),
    (0x112DF, 0x112DF),
    (0x112E3, 0x112EA),
    (0x11300, 0x11301),
    (0x1133B, 0x1133C),
    (0x11340, 0x11340),
    (0x11366, 0x1136C),
    (0x11370, 0x11374),
    (0x11438, 0x1143F),
    (0x11442, 0x11444),
    (0x11446, 0x11446),
    (0x1145E, 0x1145E),
    (0x114B3, 0x114B8),
    (0x114BA, 0x114BA),
    (0x114BF, 0x114C0),
    (0x114C2, 0x114C3),
    (0x115B2, 0x115B5),
    (0x115BC, 0x115BD),
    (0x115BF, 0x115C0),
    (0x115DC, 0x115DD),
    (0x11633, 0x1163A),
    (0x1163D, 0x1163D),
    (0x1163F, 0x11640),
    (0x116AB, 0x116AB),
    (0x116AD, 0x116AD),
    (0x116B0, 0x116B5),
    (0x116B7, 0x116B7),
    (0x1171D, 0x1171F),
    (0x11722, 0x11725),
    (0x11727, 0x1172B),
    (0x1182F, 0x11837),
    (0x11839, 0x1183A),
    (0x1193B, 0x1193C),
    (0x1193E, 0x1193E),
    (0x11943, 0x11943),
    (0x119D4, 0x119D7),
    (0x119DA, 0x119DB),
    (0x119E0, 0x119E0),
    (0x11A01, 0x11A0A),
    (0x11A33, 0x11A38),
    (0x11A3B, 0x11A3E),
    (0x11A47, 0x11A47),
    (0x11A51, 0x11A56),
    (0x11A59, 0x11A5B),
    (0x11A8A, 0x11A96),
    (0x11A98, 0x11A99),
    (0x11C30, 0x11C36),
    (0x11C38, 0x11C3D),
    (0x11C3F, 0x11C3F),
    (0x11C92, 0x11CA7),
    (0x11CAA, 0x11CB0),
    (0x11CB2, 0x11CB3),
    (0x11CB5, 0x11CB6),
    (0x11D31, 0x11D36),
    (0x11D3A, 0x11D3A),
    (0x11D3C, 0x11D3D),
    (0x11D3F, 0x11D45),
    (0x11D47, 0x11D47),
    (0x11D90, 0x11D91),
    (0x11D95, 0x11D95),
    (0x11D97, 0x11D97),
    (0x11EF3, 0x11EF4),
    (0x13430, 0x13438),
    (0x16AF0, 0x16AF4),
    (0x16B30, 0x16B36),
    (0x16B40, 0x16B43),
    (0x16F4F, 0x16F4F),
    (0x16F8F, 0x16F9F),
    (0x16FE0, 0x16FE1),
    (0x16FE3, 0x16FE4),
    (0x1AFF0, 0x1AFF3),
    (0x1AFF5, 0x1AFFB),
    (0x1AFFD, 0x1AFFE),
    (0x1BC9D, 0x1BC9E),
    (0x1BCA0, 0x1BCA3),
    (0x1CF00, 0x1CF2D),
    (0x1CF30, 0x1CF46),
    (0x1D167, 0x1D169),
    (0x1D173, 0x1D182),
    (0x1D185, 0x1D18B),
    (0x1D1AA, 0x1D1AD),
    (0x1D242, 0x1D244),
    (0x1DA00, 0x1DA36),
    (0x1DA3B, 0x1DA6C),
    (0x1DA75, 0x1DA75),
    (0x1DA84, 0x1DA84),
    (0x1DA9B, 0x1DA9F),
    (0x1DAA1, 0x1DAAF),
    (0x1E000, 0x1E006),
    (0x1E008, 0x1E018),
    (0x1E01B, 0x1E021),
    (0x1E023, 0x1E024),
    (0x1E026, 0x1E02A),
    (0x1E130, 0x1E13D),
    (0x1E2AE, 0x1E2AE),
    (0x1E2EC, 0x1E2EF),
    (0x1E8D0, 0x1E8D6),
    (0x1E944, 0x1E94B),
    (0x1F3FB, 0x1F3FF),
    (0xE0001, 0xE0001),
    (0xE0020, 0xE007F),
    (0xE0100, 0xE01EF),
)
_CASE_IGNORABLE_LOWS = tuple(low for low, _ in _CASE_IGNORABLE_RANGES)

# Frozen Cased ranges (Unicode 14.0): Cased = Lu|Ll|Lt plus Other_Cased
# (ordinal indicators, circled/squared letters, Roman numerals, letterlike
# symbols, math alphanumerics). Derived from the same Final_Sigma probe used
# for the Case_Ignorable table: a character is Cased exactly when it makes a
# preceding capital sigma lowercase medially in both "AS"+X and "AS"+X+"A".
# This is exact rather than heuristic: U+0345 has case mappings yet is
# Case_Ignorable (not cased), while U+00AA is cased with no case mappings.
_CASED_RANGES: tuple[tuple[int, int], ...] = (
    (0x41, 0x5A),
    (0x61, 0x7A),
    (0xAA, 0xAA),
    (0xB5, 0xB5),
    (0xBA, 0xBA),
    (0xC0, 0xD6),
    (0xD8, 0xF6),
    (0xF8, 0x1BA),
    (0x1BC, 0x1BF),
    (0x1C4, 0x293),
    (0x295, 0x2AF),
    (0x370, 0x373),
    (0x376, 0x377),
    (0x37B, 0x37D),
    (0x37F, 0x37F),
    (0x386, 0x386),
    (0x388, 0x38A),
    (0x38C, 0x38C),
    (0x38E, 0x3A1),
    (0x3A3, 0x3F5),
    (0x3F7, 0x481),
    (0x48A, 0x52F),
    (0x531, 0x556),
    (0x560, 0x588),
    (0x10A0, 0x10C5),
    (0x10C7, 0x10C7),
    (0x10CD, 0x10CD),
    (0x10D0, 0x10FA),
    (0x10FD, 0x10FF),
    (0x13A0, 0x13F5),
    (0x13F8, 0x13FD),
    (0x1C80, 0x1C88),
    (0x1C90, 0x1CBA),
    (0x1CBD, 0x1CBF),
    (0x1D00, 0x1D2B),
    (0x1D6B, 0x1D77),
    (0x1D79, 0x1D9A),
    (0x1E00, 0x1F15),
    (0x1F18, 0x1F1D),
    (0x1F20, 0x1F45),
    (0x1F48, 0x1F4D),
    (0x1F50, 0x1F57),
    (0x1F59, 0x1F59),
    (0x1F5B, 0x1F5B),
    (0x1F5D, 0x1F5D),
    (0x1F5F, 0x1F7D),
    (0x1F80, 0x1FB4),
    (0x1FB6, 0x1FBC),
    (0x1FBE, 0x1FBE),
    (0x1FC2, 0x1FC4),
    (0x1FC6, 0x1FCC),
    (0x1FD0, 0x1FD3),
    (0x1FD6, 0x1FDB),
    (0x1FE0, 0x1FEC),
    (0x1FF2, 0x1FF4),
    (0x1FF6, 0x1FFC),
    (0x2102, 0x2102),
    (0x2107, 0x2107),
    (0x210A, 0x2113),
    (0x2115, 0x2115),
    (0x2119, 0x211D),
    (0x2124, 0x2124),
    (0x2126, 0x2126),
    (0x2128, 0x2128),
    (0x212A, 0x212D),
    (0x212F, 0x2134),
    (0x2139, 0x2139),
    (0x213C, 0x213F),
    (0x2145, 0x2149),
    (0x214E, 0x214E),
    (0x2160, 0x217F),
    (0x2183, 0x2184),
    (0x24B6, 0x24E9),
    (0x2C00, 0x2C7B),
    (0x2C7E, 0x2CE4),
    (0x2CEB, 0x2CEE),
    (0x2CF2, 0x2CF3),
    (0x2D00, 0x2D25),
    (0x2D27, 0x2D27),
    (0x2D2D, 0x2D2D),
    (0xA640, 0xA66D),
    (0xA680, 0xA69B),
    (0xA722, 0xA76F),
    (0xA771, 0xA787),
    (0xA78B, 0xA78E),
    (0xA790, 0xA7CA),
    (0xA7D0, 0xA7D1),
    (0xA7D3, 0xA7D3),
    (0xA7D5, 0xA7D9),
    (0xA7F5, 0xA7F6),
    (0xA7FA, 0xA7FA),
    (0xAB30, 0xAB5A),
    (0xAB60, 0xAB68),
    (0xAB70, 0xABBF),
    (0xFB00, 0xFB06),
    (0xFB13, 0xFB17),
    (0xFF21, 0xFF3A),
    (0xFF41, 0xFF5A),
    (0x10400, 0x1044F),
    (0x104B0, 0x104D3),
    (0x104D8, 0x104FB),
    (0x10570, 0x1057A),
    (0x1057C, 0x1058A),
    (0x1058C, 0x10592),
    (0x10594, 0x10595),
    (0x10597, 0x105A1),
    (0x105A3, 0x105B1),
    (0x105B3, 0x105B9),
    (0x105BB, 0x105BC),
    (0x10C80, 0x10CB2),
    (0x10CC0, 0x10CF2),
    (0x118A0, 0x118DF),
    (0x16E40, 0x16E7F),
    (0x1D400, 0x1D454),
    (0x1D456, 0x1D49C),
    (0x1D49E, 0x1D49F),
    (0x1D4A2, 0x1D4A2),
    (0x1D4A5, 0x1D4A6),
    (0x1D4A9, 0x1D4AC),
    (0x1D4AE, 0x1D4B9),
    (0x1D4BB, 0x1D4BB),
    (0x1D4BD, 0x1D4C3),
    (0x1D4C5, 0x1D505),
    (0x1D507, 0x1D50A),
    (0x1D50D, 0x1D514),
    (0x1D516, 0x1D51C),
    (0x1D51E, 0x1D539),
    (0x1D53B, 0x1D53E),
    (0x1D540, 0x1D544),
    (0x1D546, 0x1D546),
    (0x1D54A, 0x1D550),
    (0x1D552, 0x1D6A5),
    (0x1D6A8, 0x1D6C0),
    (0x1D6C2, 0x1D6DA),
    (0x1D6DC, 0x1D6FA),
    (0x1D6FC, 0x1D714),
    (0x1D716, 0x1D734),
    (0x1D736, 0x1D74E),
    (0x1D750, 0x1D76E),
    (0x1D770, 0x1D788),
    (0x1D78A, 0x1D7A8),
    (0x1D7AA, 0x1D7C2),
    (0x1D7C4, 0x1D7CB),
    (0x1DF00, 0x1DF09),
    (0x1DF0B, 0x1DF1E),
    (0x1E900, 0x1E943),
    (0x1F130, 0x1F149),
    (0x1F150, 0x1F169),
    (0x1F170, 0x1F189),
)
_CASED_LOWS = tuple(low for low, _ in _CASED_RANGES)

# Curated notes for characters whose casing behavior is famously non-obvious.
_CHAR_NOTES: dict[int, str] = {
    0x00DF: (
        "SHARP S: upper() expands 1->2 to 'SS' while lower() keeps 'ß'; casefold() is "
        "'ss' - the classic casefold-vs-lower divergence."
    ),
    0x1E9E: "CAPITAL SHARP S: lower() is 'ß' but casefold() is 'ss' - case folding skips the capital form.",
    0x0130: (
        "I WITH DOT ABOVE: lower() expands 1->2 to 'i' + U+0307 combining dot above; "
        "Turkish/Azeri locale rules instead use plain dotless 'i' (Python is locale-independent)."
    ),
    0x0131: (
        "DOTLESS I: upper() is ASCII 'I'; Turkish/Azeri locale rules would produce 'İ' "
        "(U+0130) (Python is locale-independent)."
    ),
    0x0049: (
        "LATIN CAPITAL I: lower() is 'i'; under Turkish/Azeri locale rules it would be "
        "dotless 'ı' (U+0131). Python case mapping never varies by locale."
    ),
    0x0069: (
        "LATIN SMALL I: upper() is 'I'; under Turkish/Azeri locale rules it would be 'İ' "
        "(U+0130). Python case mapping never varies by locale."
    ),
    0x03A3: (
        "CAPITAL SIGMA: lower() is context-sensitive (Final_Sigma rule in SpecialCasing): "
        "word-final sigma becomes 'ς' ('ΑΣ'.lower() == 'ας') but word-medial stays 'σ' "
        "('ΑΣΑ'.lower() == 'ασα')."
    ),
    0x03C2: (
        "FINAL SIGMA: the word-final lowercase sigma produced by the Final_Sigma rule; "
        "upper() is 'Σ'. It and medial 'σ' (U+03C3) are two lowercase forms of one "
        "uppercase - casing is position-sensitive."
    ),
    0x03C3: "SMALL SIGMA: word-medial form; a re-cased string can turn it into final 'ς' (U+03C2).",
    0x212A: (
        "KELVIN SIGN: lower() and casefold() both yield ASCII 'k' - a distinct codepoint "
        "that collides with Latin k under any case-insensitive comparison."
    ),
    0x2126: (
        "OHM SIGN: casefold() is Greek 'ω' (U+03C9) - the compatibility symbol merges with "
        "OMEGA under case folding while remaining a separate codepoint."
    ),
    0x017F: (
        "LONG S: upper() is 'S' and casefold() is ASCII 's' - the historic long s disappears "
        "under case folding ('ſtraße' and 'strasse' compare equal after casefold)."
    ),
    0x00B5: (
        "MICRO SIGN: casefold() is Greek 'μ' (U+03BC) while upper() is 'Μ' (U+039C) - micro "
        "sign and Greek mu are distinct codepoints that collide under casefold."
    ),
    0x212B: "ANGSTROM SIGN: casefold() is 'å' (U+00E5) - merges with Latin a-ring under case folding.",
    0x0345: "COMBINING GREEK YPOGEGRAMMENI: a combining mark that is nevertheless cased; casefold() is 'ι' (U+03B9).",
    0xFB00: "ff LIGATURE: upper() expands 1->2 to 'FF'.",
    0xFB01: "fi LIGATURE: upper() expands 1->2 to 'FI'.",
    0xFB02: "fl LIGATURE: upper() expands 1->2 to 'FL'.",
    0xFB03: "ffi LIGATURE: upper() expands 1->3 to 'FFI'.",
    0xFB04: "ffl LIGATURE: upper() expands 1->3 to 'FFL'.",
    0x0149: "n PRECEDED BY APOSTROPHE: upper() and title() expand 1->2 to modifier apostrophe + 'N'.",
    0x01F0: "j WITH CARON: upper() and title() expand 1->2 to 'J' + U+030C combining caron.",
    0x1E96: "h WITH LINE BELOW: upper() expands 1->2 to 'H' + U+0331.",
    0x1E97: "t WITH DIAERESIS: upper() expands 1->2 to 'T' + U+0308.",
    0x1E98: "w WITH RING ABOVE: upper() expands 1->2 to 'W' + U+030A.",
    0x1E99: "y WITH RING ABOVE: upper() expands 1->2 to 'Y' + U+030A.",
    0x1E9A: "a WITH RING BELOW: upper() expands 1->2 to 'A' + U+0325.",
}

# Block notes for bicameral scripts whose case pairs are easy to misread.
_BLOCK_NOTES: tuple[tuple[int, int, str], ...] = (
    (
        0x13A0,
        0x13FF,
        "CHEROKEE uppercase block; its lowercase pairs live at U+AB70..U+ABBF "
        "(full bicameral Cherokee since Unicode 8.0).",
    ),
    (0xAB70, 0xABBF, "CHEROKEE lowercase block; uppercase pairs live at U+13A0..U+13FF."),
    (
        0x10400,
        0x1044F,
        "DESERET: a fully bicameral plane-1 script (U+10400..U+10427 uppercase, U+10428..U+1044F lowercase).",
    ),
    (0x104B0, 0x104FB, "OSAGE: bicameral plane-1 script (U+104B0..U+104D3 uppercase, U+104D8..U+104FB lowercase)."),
    (
        0x10C80,
        0x10CFF,
        "OLD HUNGARIAN: bicameral plane-1 script (U+10C80..U+10CB2 uppercase, U+10CC0..U+10CF2 lowercase).",
    ),
    (
        0x118A0,
        0x118FF,
        "WARANG CITI: bicameral plane-1 script (U+118A0..U+118BF uppercase, U+118C0..U+118DF lowercase).",
    ),
)

_STYLES = ("snake_case", "SCREAMING_SNAKE", "kebab-case", "camelCase", "PascalCase")


def _is_case_ignorable(codepoint: int) -> bool:
    """Return True when the codepoint is in the frozen Case_Ignorable table."""
    index = bisect.bisect_right(_CASE_IGNORABLE_LOWS, codepoint) - 1
    return index >= 0 and _CASE_IGNORABLE_RANGES[index][0] <= codepoint <= _CASE_IGNORABLE_RANGES[index][1]


def _is_cased(ch: str) -> bool:
    """Mirror the Unicode ``Cased`` property via the frozen probe-derived table.

    ``Cased`` is Lu|Ll|Lt plus Other_Cased (ordinal indicators, circled and
    squared letters, Roman numerals, math alphanumerics). The table is exact
    stdlib behavior, not a mapping heuristic: U+0345 carries case mappings
    yet is Case_Ignorable instead, while U+00AA/U+1F130 are cased with no
    case mappings at all.
    """
    codepoint = ord(ch)
    index = bisect.bisect_right(_CASED_LOWS, codepoint) - 1
    return index >= 0 and _CASED_RANGES[index][0] <= codepoint <= _CASED_RANGES[index][1]


def _block_note(codepoint: int) -> str | None:
    """Return the curated block note covering the codepoint, if any."""
    for low, high, note in _BLOCK_NOTES:
        if low <= codepoint <= high:
            return note
    return None


class UnicodeCaseTool(Tool):
    """Offline Unicode casing analysis: mappings, equivalence, and style audits."""

    max_text_chars: int = 1_048_576
    max_per_char_entries: int = 200
    max_interesting_mappings: int = 50
    max_differences: int = 100
    max_words: int = 200

    _MODES: ClassVar[tuple[str, ...]] = ("case_map", "equivalence", "style_audit", "char_case_info")
    _TARGETS: ClassVar[tuple[str, ...]] = ("upper", "lower", "title", "casefold", "swapcase")
    _STYLES: ClassVar[tuple[str, ...]] = _STYLES

    def execute(
        self,
        mode: str,
        text: str | None = None,
        target: str | None = None,
        text_a: str | None = None,
        text_b: str | None = None,
        identifier: str | None = None,
        target_style: str | None = None,
        char: str | None = None,
        codepoint: int | str | None = None,
    ) -> dict[str, Any]:
        try:
            self._validate_config()
            operation = self._mode(mode)
            extra = (text, target, text_a, text_b, identifier, target_style, char, codepoint)
            if operation == "case_map":
                return self._case_map(*extra)
            if operation == "equivalence":
                return self._equivalence(*extra)
            if operation == "style_audit":
                return self._style_audit(*extra)
            return self._char_case_info(*extra)
        except (TypeError, ValueError) as exc:
            return self._error(mode, "validation_error", str(exc))
        except Exception as exc:  # pragma: no cover - defensive catch-all
            return self._error(mode, "operation_error", f"Case analysis failed: {exc}")

    # ------------------------------------------------------------------
    # validation helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _error(mode: Any, kind: str, message: str) -> dict[str, Any]:
        return {"status": "error", "error_type": kind, "error": message, "mode": mode}

    def _validate_config(self) -> None:
        for name in (
            "max_text_chars",
            "max_per_char_entries",
            "max_interesting_mappings",
            "max_differences",
            "max_words",
        ):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")

    @staticmethod
    def _mode(value: Any) -> str:
        if not isinstance(value, str):
            raise TypeError("mode must be a string")
        mode = value.strip().lower()
        if mode not in UnicodeCaseTool._MODES:
            raise ValueError("mode must be case_map, equivalence, style_audit, or char_case_info")
        return mode

    @staticmethod
    def _reject_cross_mode(allowed: tuple[str, ...], **params: Any) -> None:
        """Reject parameters that do not belong to the selected mode."""
        for name, value in params.items():
            if value is not None and name not in allowed:
                raise ValueError(f"{name} is not accepted in this mode")

    def _text_param(self, value: Any, name: str) -> str:
        if not isinstance(value, str):
            raise TypeError(f"{name} must be a string")
        if len(value) > self.max_text_chars:
            raise ValueError(f"{name} exceeds max_text_chars ({self.max_text_chars})")
        return value

    @staticmethod
    def _target(value: Any) -> str:
        if value is None:
            return "upper"
        if not isinstance(value, str):
            raise TypeError("target must be a string")
        target = value.strip().lower()
        if target not in UnicodeCaseTool._TARGETS:
            raise ValueError("target must be upper, lower, title, casefold, or swapcase")
        return target

    # ------------------------------------------------------------------
    # case_map
    # ------------------------------------------------------------------

    def _case_map(
        self,
        text: Any,
        target: Any,
        text_a: Any,
        text_b: Any,
        identifier: Any,
        target_style: Any,
        char: Any,
        codepoint: Any,
    ) -> dict[str, Any]:
        self._reject_cross_mode(
            ("text", "target"),
            text_a=text_a,
            text_b=text_b,
            identifier=identifier,
            target_style=target_style,
            char=char,
            codepoint=codepoint,
        )
        value = self._text_param(text, "text")
        selected = self._target(target)
        method = getattr(str, selected)
        mapped = method(value)
        per_char: list[dict[str, Any]] = []
        interesting: list[dict[str, Any]] = []
        seen_interesting: set[int] = set()
        changed_count = 0
        offset = 0
        track_context = selected != "title"
        for index, ch in enumerate(value):
            isolated = method(ch)
            changed = isolated != ch
            if changed:
                changed_count += 1
            if len(per_char) < self.max_per_char_entries:
                entry: dict[str, Any] = {"index": index, "original": ch, "mapped": isolated, "changed": changed}
                if track_context and isolated != mapped[offset : offset + len(isolated)]:
                    entry["mapped_in_context"] = mapped[offset : offset + len(isolated)]
                per_char.append(entry)
            cp = ord(ch)
            if cp not in seen_interesting and self._is_interesting(ch):
                seen_interesting.add(cp)
                if len(interesting) < self.max_interesting_mappings:
                    interesting.append(self._interesting_entry(ch, cp, isolated))
            offset += len(isolated)
        return {
            "status": "success",
            "mode": "case_map",
            "target": selected,
            "length": len(value),
            "result_length": len(mapped),
            "changed_count": changed_count,
            "result": mapped,
            "per_char": per_char,
            "per_char_truncated": len(per_char) < len(value),
            "interesting_mappings": interesting,
            "interesting_mappings_truncated": len(seen_interesting) > len(interesting),
        }

    @staticmethod
    @functools.cache
    def _is_interesting(ch: str) -> bool:
        """Return True when the character has a non-obvious casing story.

        The decision is a pure function of the character, so the module-level
        cache keeps behavior deterministic while staying fast under sweeps.
        """
        if any(len(getattr(ch, name)()) != 1 for name in ("upper", "lower", "title", "casefold", "swapcase")):
            return True
        if ch.casefold() != ch.lower():
            return True
        if ord(ch) in _CHAR_NOTES:
            return True
        if _block_note(ord(ch)):
            return True
        return unicodedata.category(ch) == "Lt"

    @staticmethod
    def _interesting_entry(ch: str, cp: int, isolated: str) -> dict[str, Any]:
        notes: list[str] = []
        expansions = {
            name: len(getattr(ch, name)())
            for name in ("upper", "lower", "title", "casefold", "swapcase")
            if len(getattr(ch, name)()) != 1
        }
        if len(isolated) != 1:
            notes.append(f"length-changing mapping under this target: 1 -> {len(isolated)} ('{isolated}')")
        if expansions:
            notes.append(
                "expanding methods: " + ", ".join(f"{name} -> {length}" for name, length in sorted(expansions.items()))
            )
        curated = _CHAR_NOTES.get(cp)
        if curated:
            notes.append(curated)
        block = _block_note(cp)
        if block:
            notes.append(block)
        if unicodedata.category(ch) == "Lt":
            notes.append("titlecase digraph (category Lt): its upper and lower forms are separate ligature letters")
        if ch.casefold() != ch.lower():
            notes.append(f"casefold('{ch}') == '{ch.casefold()}' diverges from lower('{ch}') == '{ch.lower()}'")
        elif ch.casefold() != ch and ch.casefold().isascii():
            notes.append(f"non-ASCII character whose casefold is ASCII '{ch.casefold()}'")
        return {
            "char": ch,
            "codepoint": f"U+{cp:04X}",
            "mapped": isolated,
            "length_change": None if len(isolated) == 1 else {"from": 1, "to": len(isolated)},
            "note": " | ".join(notes),
        }

    # ------------------------------------------------------------------
    # equivalence
    # ------------------------------------------------------------------

    def _equivalence(
        self,
        text: Any,
        target: Any,
        text_a: Any,
        text_b: Any,
        identifier: Any,
        target_style: Any,
        char: Any,
        codepoint: Any,
    ) -> dict[str, Any]:
        self._reject_cross_mode(
            ("text_a", "text_b"),
            text=text,
            target=target,
            identifier=identifier,
            target_style=target_style,
            char=char,
            codepoint=codepoint,
        )
        first = self._text_param(text_a, "text_a")
        second = self._text_param(text_b, "text_b")
        folded_a = first.casefold()
        folded_b = second.casefold()
        nfc_a = unicodedata.normalize("NFC", unicodedata.normalize("NFC", first).casefold())
        nfc_b = unicodedata.normalize("NFC", unicodedata.normalize("NFC", second).casefold())
        differences: list[dict[str, Any]] = []
        total_differences = 0
        if folded_a != folded_b:
            shared = min(len(folded_a), len(folded_b))
            for index in range(shared):
                if folded_a[index] != folded_b[index]:
                    total_differences += 1
                    if len(differences) < self.max_differences:
                        differences.append(self._difference_entry(index, folded_a[index], folded_b[index]))
            if len(folded_a) != len(folded_b):
                total_differences += 1
                if len(differences) < self.max_differences:
                    longer, _shorter = (folded_a, folded_b) if len(folded_a) > len(folded_b) else (folded_b, folded_a)
                    differences.append(
                        {
                            "index": shared,
                            "a": "" if len(folded_a) < len(folded_b) else longer[shared:],
                            "b": "" if len(folded_a) > len(folded_b) else longer[shared:],
                            "note": (
                                f"length mismatch after casefold: text_a folds to {len(folded_a)} chars, "
                                f"text_b folds to {len(folded_b)}; remaining tail {longer[shared:]!r}"
                            ),
                        }
                    )
        casefold_equal = folded_a == folded_b
        lower_equal = first.lower() == second.lower()
        nfc_equal = nfc_a == nfc_b
        if casefold_equal:
            explanation = "Equal after casefold - the correct default for case-insensitive comparison."
            if not lower_equal:
                explanation += (
                    " The lower() comparison disagrees because lower() does not fold the expansions"
                    " that casefold() does (for example 'ß'.casefold() is 'ss' but 'ß'.lower() stays 'ß')."
                )
        else:
            explanation = "The strings differ even after casefold - they are not case-insensitive equal."
        return {
            "status": "success",
            "mode": "equivalence",
            "identical": first == second,
            "casefold_equal": casefold_equal,
            "lower_equal": lower_equal,
            "nfc_casefold_equal": nfc_equal,
            "length_a": len(first),
            "length_b": len(second),
            "casefold_length_a": len(folded_a),
            "casefold_length_b": len(folded_b),
            "differences": differences,
            "differences_truncated": total_differences > len(differences),
            "explanation": explanation,
        }

    @staticmethod
    def _difference_entry(index: int, a_char: str, b_char: str) -> dict[str, Any]:
        return {
            "index": index,
            "a": a_char,
            "b": b_char,
            "a_codepoint": f"U+{ord(a_char):04X}",
            "b_codepoint": f"U+{ord(b_char):04X}",
            "note": f"casefold of text_a[{index}] is {a_char!r}, casefold of text_b[{index}] is {b_char!r}",
        }

    # ------------------------------------------------------------------
    # style_audit
    # ------------------------------------------------------------------

    def _style_audit(
        self,
        text: Any,
        target: Any,
        text_a: Any,
        text_b: Any,
        identifier: Any,
        target_style: Any,
        char: Any,
        codepoint: Any,
    ) -> dict[str, Any]:
        self._reject_cross_mode(
            ("identifier", "target_style"),
            text=text,
            target=target,
            text_a=text_a,
            text_b=text_b,
            char=char,
            codepoint=codepoint,
        )
        name = self._text_param(identifier, "identifier")
        if target_style is not None and (not isinstance(target_style, str) or target_style not in self._STYLES):
            raise ValueError("target_style must be snake_case, camelCase, PascalCase, SCREAMING_SNAKE, or kebab-case")
        words, separators, evidence = self._extract_words(name)
        if not words:
            raise ValueError("identifier must contain at least one alphanumeric character")
        if len(words) > self.max_words:
            raise ValueError(f"identifier produces more than max_words ({self.max_words})")
        detected, ambiguous, compatible = self._detect_style(words, separators, evidence)
        result: dict[str, Any] = {
            "status": "success",
            "mode": "style_audit",
            "identifier": name,
            "detected_style": detected,
            "ambiguous": ambiguous,
            "compatible_styles": compatible,
            "words": words,
            "acronyms": [word for word in words if self._is_acronym(word)],
            "separators": separators,
            "evidence": evidence,
        }
        if target_style is not None:
            violations = self._violations(words, separators, target_style)
            result["target_style"] = target_style
            result["violations"] = violations
            result["conforms"] = not violations
            result["suggested_conversion"] = self._convert(words, target_style)
        return result

    def _extract_words(self, name: str) -> tuple[list[str], dict[str, Any], list[dict[str, str]]]:
        """Split an identifier into words with acronym-aware camel handling."""
        segments, separators = self._scan_segments(name)
        words: list[str] = []
        for segment in segments:
            words.extend(self._split_camel(segment))
        return words, separators, self._word_evidence(words, separators)

    @staticmethod
    def _scan_segments(name: str) -> tuple[list[str], dict[str, Any]]:
        """Split on non-alphanumeric runs, recording which separators appear."""
        segments: list[str] = []
        current: list[str] = []
        separators: dict[str, Any] = {"underscore": False, "hyphen": False, "space": False, "other": []}
        other_seen: set[str] = set()
        for ch in name:
            if ch.isalnum():
                current.append(ch)
                continue
            if current:
                segments.append("".join(current))
                current = []
            if ch == "_":
                separators["underscore"] = True
            elif ch == "-":
                separators["hyphen"] = True
            elif ch == " ":
                separators["space"] = True
            elif ch not in other_seen:
                other_seen.add(ch)
                separators["other"].append(ch)
        if current:
            segments.append("".join(current))
        return segments, separators

    def _word_evidence(self, words: list[str], separators: dict[str, Any]) -> list[dict[str, str]]:
        """Build the per-word and per-separator observations for style detection."""
        evidence: list[dict[str, str]] = [
            {"observation": f"word {position + 1} {word!r} is {self._word_shape(word)}"}
            for position, word in enumerate(words)
        ]
        if separators["underscore"]:
            evidence.append({"observation": "underscore separators between words"})
        if separators["hyphen"]:
            evidence.append({"observation": "hyphen separators between words"})
        if separators["space"]:
            evidence.append({"observation": "space separators between words (not an identifier convention)"})
        for ch in separators["other"]:
            evidence.append({"observation": f"separator {ch!r} (not an identifier convention)"})
        return evidence

    @staticmethod
    def _split_camel(segment: str) -> list[str]:
        """Split a separator-free segment on camel humps, keeping acronyms whole."""
        words: list[str] = []
        start = 0
        for j in range(1, len(segment)):
            previous, current = segment[j - 1], segment[j]
            if not current.isalpha() and not current.isdigit():
                continue
            acronym_end = previous.isupper() and j + 1 < len(segment) and segment[j + 1].islower()
            boundary = current.isupper() and (not previous.isupper() or acronym_end)
            if boundary:
                words.append(segment[start:j])
                start = j
        words.append(segment[start:])
        return [word for word in words if word]

    @staticmethod
    def _word_shape(word: str) -> str:
        """Classify a word as lower, upper, capitalized, acronym, digit, or mixed.

        Uncased scripts (CJK, Hangul, and similar) have no uppercase letters
        and therefore classify as "lower" - they are neutral for style rules.
        """
        letters = [ch for ch in word if ch.isalpha()]
        if not letters:
            return "digit"
        if all(ch.isupper() for ch in letters):
            return "acronym" if len(letters) >= 2 else "capitalized"
        if letters[0].isupper() and not any(ch.isupper() for ch in letters[1:]):
            return "capitalized"
        if not any(ch.isupper() for ch in letters):
            return "lower"
        return "mixed"

    @staticmethod
    def _is_acronym(word: str) -> bool:
        letters = [ch for ch in word if ch.isalpha()]
        return len(letters) >= 2 and all(ch.isupper() for ch in letters)

    def _detect_style(
        self,
        words: list[str],
        separators: dict[str, Any],
        evidence: list[dict[str, str]],
    ) -> tuple[str, bool, list[str]]:
        """Return (detected_style, ambiguous, compatible_styles) for the words."""
        shapes = [self._word_shape(word) for word in words]
        compatible = self._compatible_styles(words, shapes, separators)
        single = len(words) == 1
        joined = self._is_joined(separators)
        letters = [ch for word in words for ch in word if ch.isalpha()]
        all_lower = bool(letters) and not any(ch.isupper() for ch in letters)
        all_upper = bool(letters) and all(ch.isupper() for ch in letters)
        if single and all_lower and joined:
            compatible = ["snake_case", "camelCase", "kebab-case"]
            evidence.append(
                {"observation": "single lowercase word: snake_case, camelCase, and kebab-case are indistinguishable"}
            )
        elif single and all_upper and joined:
            compatible = ["SCREAMING_SNAKE", "PascalCase"]
            evidence.append(
                {"observation": "single acronym word: SCREAMING_SNAKE and PascalCase are indistinguishable"}
            )
        if not compatible:
            return "mixed", False, []
        for style in self._STYLES:
            if style in compatible:
                return style, len(compatible) > 1, compatible
        return "mixed", False, []

    @staticmethod
    def _is_joined(separators: dict[str, Any]) -> bool:
        """Return True when no separators at all appear between the words."""
        return (
            not separators["underscore"]
            and not separators["hyphen"]
            and not separators["space"]
            and not separators["other"]
        )

    def _compatible_styles(self, words: list[str], shapes: list[str], separators: dict[str, Any]) -> list[str]:
        """Return the multi-word styles the shapes and separators satisfy."""
        underscore, hyphen, space = separators["underscore"], separators["hyphen"], separators["space"]
        other = bool(separators["other"])
        joined = self._is_joined(separators)
        letters = [ch for word in words for ch in word if ch.isalpha()]
        all_lower = bool(letters) and not any(ch.isupper() for ch in letters)
        all_upper = bool(letters) and all(ch.isupper() for ch in letters)
        cased_words = [shape for shape in shapes if shape != "digit"]
        first_lower = bool(cased_words) and shapes[0] in ("lower", "digit")
        rest_capitalized = all(shape in ("capitalized", "acronym") for shape in shapes[1:])
        first_capitalized = bool(shapes) and shapes[0] in ("capitalized", "acronym")
        compatible: list[str] = []
        if underscore and not hyphen and not space and not other and all_lower:
            compatible.append("snake_case")
        if underscore and not hyphen and not space and not other and all_upper:
            compatible.append("SCREAMING_SNAKE")
        if hyphen and not underscore and not space and not other and all_lower:
            compatible.append("kebab-case")
        if joined and len(words) > 1 and first_lower and rest_capitalized:
            compatible.append("camelCase")
        if joined and first_capitalized and all(shape in ("capitalized", "acronym") for shape in shapes):
            compatible.append("PascalCase")
        return compatible

    @staticmethod
    def _violations(words: list[str], separators: dict[str, Any], target_style: str) -> list[dict[str, str]]:
        """List every deviation of the words/separators from the target style."""
        return UnicodeCaseTool._separator_violations(separators, target_style) + UnicodeCaseTool._word_violations(
            words, target_style
        )

    @staticmethod
    def _separator_violations(separators: dict[str, Any], target_style: str) -> list[dict[str, str]]:
        """Report separator usage that does not belong to the target style."""
        violations: list[dict[str, str]] = []
        wanted_separator = {"snake_case": "_", "SCREAMING_SNAKE": "_", "kebab-case": "-"}
        if target_style in wanted_separator:
            allowed = wanted_separator[target_style]
            allowed_detail = {"_": "underscore separator used", "-": "hyphen separator used"}[allowed]
            for detail, present in (
                ("underscore separator used", separators["underscore"]),
                ("hyphen separator used", separators["hyphen"]),
                ("space separator used", separators["space"]),
            ):
                if present and detail != allowed_detail:
                    violations.append({"kind": "separator", "detail": detail, "suggested": allowed})
        else:  # camelCase / PascalCase: no separators are allowed at all
            for detail, present in (
                ("underscore separator used", separators["underscore"]),
                ("hyphen separator used", separators["hyphen"]),
                ("space separator used", separators["space"]),
            ):
                if present:
                    violations.append(
                        {"kind": "separator", "detail": detail, "suggested": "none (use word boundaries)"}
                    )
        other_suggested = (
            "_"
            if target_style in ("snake_case", "SCREAMING_SNAKE")
            else ("-" if target_style == "kebab-case" else "none (use word boundaries)")
        )
        for ch in separators["other"]:
            violations.append({"kind": "separator", "detail": f"separator {ch!r} used", "suggested": other_suggested})
        return violations

    @staticmethod
    def _word_violations(words: list[str], target_style: str) -> list[dict[str, str]]:
        """Report word casing that does not belong to the target style."""
        violations: list[dict[str, str]] = []
        for position, word in enumerate(words):
            shape = UnicodeCaseTool._word_shape(word)
            if shape == "digit":
                continue
            detail = f"word {position + 1} {word!r} is {shape}"
            if target_style in ("snake_case", "kebab-case") and shape != "lower":
                violations.append({"kind": "word_case", "detail": detail, "suggested": word.lower()})
            elif target_style == "SCREAMING_SNAKE" and any(ch.islower() for ch in word):
                violations.append({"kind": "word_case", "detail": detail, "suggested": word.upper()})
            elif target_style == "camelCase" and position == 0 and shape not in ("lower", "digit"):
                violations.append(
                    {"kind": "first_word_case", "detail": f"first word {word!r} is {shape}", "suggested": word.lower()}
                )
            elif shape not in ("capitalized", "acronym") and (
                target_style == "PascalCase" or (target_style == "camelCase" and position > 0)
            ):
                violations.append(
                    {"kind": "word_case", "detail": detail, "suggested": UnicodeCaseTool._capitalize(word)}
                )
        return violations

    @staticmethod
    def _capitalize(word: str) -> str:
        """Lowercase the word, then uppercase its first alphabetic character."""
        lowered = word.lower()
        for index, ch in enumerate(lowered):
            if ch.isalpha():
                return lowered[:index] + ch.upper() + lowered[index + 1 :]
        return lowered

    @staticmethod
    def _convert(words: list[str], target_style: str) -> str:
        """Deterministically rename the extracted words into the target style."""
        if target_style == "snake_case":
            return "_".join(word.lower() for word in words)
        if target_style == "SCREAMING_SNAKE":
            return "_".join(word.upper() for word in words)
        if target_style == "kebab-case":
            return "-".join(word.lower() for word in words)
        if target_style == "camelCase":
            return words[0].lower() + "".join(UnicodeCaseTool._capitalize(word) for word in words[1:])
        return "".join(UnicodeCaseTool._capitalize(word) for word in words)

    # ------------------------------------------------------------------
    # char_case_info
    # ------------------------------------------------------------------

    def _char_case_info(
        self,
        text: Any,
        target: Any,
        text_a: Any,
        text_b: Any,
        identifier: Any,
        target_style: Any,
        char: Any,
        codepoint: Any,
    ) -> dict[str, Any]:
        self._reject_cross_mode(
            ("char", "codepoint"),
            text=text,
            target=target,
            text_a=text_a,
            text_b=text_b,
            identifier=identifier,
            target_style=target_style,
        )
        if char is not None and codepoint is not None:
            raise ValueError("provide either char or codepoint, not both")
        if char is not None:
            if not isinstance(char, str):
                raise TypeError("char must be a string")
            if len(char) != 1:
                raise ValueError("char must contain exactly one character")
            value = ord(char)
        elif codepoint is not None:
            value = self._parse_codepoint(codepoint)
        else:
            raise ValueError("one of char or codepoint is required")
        ch = chr(value)
        category = unicodedata.category(ch)
        try:
            character_name = unicodedata.name(ch)
        except ValueError:
            character_name = None
        mappings = {name: getattr(ch, name)() for name in ("upper", "lower", "title", "casefold", "swapcase")}
        note = _CHAR_NOTES.get(value) or _block_note(value)
        return {
            "status": "success",
            "mode": "char_case_info",
            "char": ch,
            "codepoint": f"U+{value:04X}",
            "decimal": value,
            "name": character_name,
            "category": category,
            "is_upper": ch.isupper(),
            "is_lower": ch.islower(),
            "is_title": category == "Lt" or (category == "Lu" and mappings["title"] == ch),
            "is_cased": _is_cased(ch),
            "is_case_ignorable": _is_case_ignorable(value),
            "mappings": {name: {"result": mapped, "length": len(mapped)} for name, mapped in mappings.items()},
            "simple_vs_full_explanation": self._mapping_kinds(ch, mappings, value, category),
            "note": note,
        }

    @staticmethod
    def _mapping_kinds(ch: str, mappings: dict[str, str], value: int, category: str) -> str:
        """Explain simple vs full mappings plus context rules for one character."""
        kind_parts: list[str] = []
        for name in ("upper", "lower", "title", "casefold"):
            mapped = mappings[name]
            if len(mapped) > 1:
                kind_parts.append(f"{name}: FULL mapping to {len(mapped)} characters ('{mapped}')")
            elif mapped != ch:
                kind_parts.append(f"{name}: simple single-character mapping to '{mapped}'")
            else:
                kind_parts.append(f"{name}: identity")
        if value in (0x03A3, 0x03C2, 0x03C3):
            kind_parts.append("lower is context-dependent (Final_Sigma): isolated 'Σ'.lower() is medial 'σ'")
        if category == "Lt":
            kind_parts.append("titlecase character (Lt): the simple title mapping is the identity")
        return "; ".join(kind_parts)

    @staticmethod
    def _parse_codepoint(value: Any) -> int:
        """Accept an int or U+XXXX / 0xXXXX / decimal string codepoint."""
        if isinstance(value, bool):
            raise TypeError("codepoint must be an integer or a U+XXXX string")
        if isinstance(value, int):
            parsed = value
        elif isinstance(value, str):
            text = value.strip()
            if text[:2].upper() == "U+" or text[:2].lower() == "0x":
                try:
                    parsed = int(text[2:], 16)
                except ValueError as exc:
                    raise ValueError(f"codepoint {value!r} is not a valid hexadecimal form") from exc
            elif text.isdecimal():
                parsed = int(text, 10)
            else:
                raise ValueError("codepoint must be an integer, U+XXXX, 0xXXXX, or a decimal string")
        else:
            raise TypeError("codepoint must be an integer or a string")
        if not 0 <= parsed <= 0x10FFFF:
            raise ValueError("codepoint must be between 0 and 0x10FFFF")
        if 0xD800 <= parsed <= 0xDFFF:
            raise ValueError("codepoint is in the surrogate block and is not a character")
        return parsed
