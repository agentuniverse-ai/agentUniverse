#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: test_slack_mrkdwn_tool.py

"""Offline unit tests for SlackMrkdwnTool.

The tool is built purely on the standard library (re) and never touches
the network, so this suite runs fully offline. Every assertion is a
literal ground truth: both conversion directions are checked against
hand-written expected strings for every supported construct, the
emphasis disambiguation matrix covers delimiter-count edge cases
(literal double stars / underscores / tildes in mrkdwn pass through),
detect is checked on exact scores, and the documented round-trip
property — ``to_mrkdwn(to_markdown(x))`` is a fixed point of the same
cycle for the supported subset — is asserted as a property test.
"""

import unittest

from agentuniverse.agent.action.tool.common_tool import SlackMrkdwnTool
from agentuniverse.agent.action.tool.common_tool.slack_mrkdwn_tool import (
    SlackMrkdwnTool as DirectSlackMrkdwnTool,
)

FENCED = "```\ncode *x* _y_ ~z~ [a](b)\n```"
COMBINED_MRKDWN = "\n".join(
    [
        "*Alert* from <#C123|general>",
        "_urgent_ ~deprecated~ `*raw*`",
        ">>> summary line",
        "<https://example.com|docs> and <@U123ABC>",
        "- item one",
    ]
)
COMBINED_MARKDOWN = "\n".join(
    [
        "**Alert** from #general",
        "*urgent* ~~deprecated~~ `*raw*`",
        "> summary line",
        "> [docs](https://example.com) and @U123ABC",
        "> - item one",
    ]
)
# to_mrkdwn(COMBINED_MARKDOWN): channel ids cannot be re-wrapped from
# names offline and '>>>' is represented as per-line '>' quotes, so the
# combined document round trips to this normalized mrkdwn form.
COMBINED_MRKDWN_NORMALIZED = "\n".join(
    [
        "*Alert* from #general",
        "_urgent_ ~deprecated~ `*raw*`",
        "> summary line",
        "> <https://example.com|docs> and <@U123ABC>",
        "> - item one",
    ]
)


class SlackMrkdwnToolToMarkdownTest(unittest.TestCase):
    """Ground-truth cases for mode='to_markdown' (mrkdwn -> Markdown)."""

    def setUp(self) -> None:
        self.tool = SlackMrkdwnTool()

    def convert(self, text: str) -> str:
        return self.tool.execute(mode="to_markdown", text=text)["result"]

    # ------------------------------------------------------------------ #
    # Emphasis: delimiter disambiguation matrix (by char, not by count)
    # ------------------------------------------------------------------ #

    def test_bold_single_star(self) -> None:
        self.assertEqual(self.convert("*bold*"), "**bold**")

    def test_italic_single_underscore(self) -> None:
        self.assertEqual(self.convert("_italic_"), "*italic*")

    def test_strike_single_tilde(self) -> None:
        self.assertEqual(self.convert("~strike~"), "~~strike~~")

    def test_literal_double_stars_pass_through(self) -> None:
        self.assertEqual(self.convert("**literal stars**"), "**literal stars**")

    def test_literal_double_underscores_pass_through(self) -> None:
        self.assertEqual(
            self.convert("__literal underscores__"), "__literal underscores__"
        )

    def test_literal_double_tildes_pass_through(self) -> None:
        self.assertEqual(
            self.convert("~~literal tildes~~"), "~~literal tildes~~"
        )

    def test_triple_stars_pass_through(self) -> None:
        self.assertEqual(self.convert("***triple***"), "***triple***")

    def test_nested_italic_inside_bold(self) -> None:
        self.assertEqual(
            self.convert("*bold with _italic_ inside*"),
            "**bold with *italic* inside**",
        )

    def test_multiple_emphasis_on_one_line(self) -> None:
        self.assertEqual(
            self.convert("*a* and _b_ and ~c~"),
            "**a** and *b* and ~~c~~",
        )

    def test_space_adjacent_star_is_not_emphasis(self) -> None:
        self.assertEqual(self.convert("* spaced *"), "* spaced *")

    def test_snake_case_underscores_untouched(self) -> None:
        self.assertEqual(self.convert("my_var_name"), "my_var_name")

    def test_intraword_star_bolds_like_commonmark(self) -> None:
        # Documented CommonMark-aligned consequence: intraword '*' pairs
        # emphasize in both dialects, so 2*3*4 becomes bold-3.
        self.assertEqual(self.convert("2*3*4"), "2**3**4")

    def test_multiplication_with_spaces_untouched(self) -> None:
        self.assertEqual(self.convert("2 * 3 * 4"), "2 * 3 * 4")

    # ------------------------------------------------------------------ #
    # Code protection
    # ------------------------------------------------------------------ #

    def test_inline_code_span_untouched(self) -> None:
        self.assertEqual(
            self.convert("`*not bold* _not italic_ ~not strike~`"),
            "`*not bold* _not italic_ ~not strike~`",
        )

    def test_fenced_block_untouched(self) -> None:
        self.assertEqual(self.convert(FENCED), FENCED)

    def test_fenced_block_shields_line_structure(self) -> None:
        text = "before\n```\n*fenced*\n```\nafter *real*"
        self.assertEqual(
            self.convert(text), "before\n```\n*fenced*\n```\nafter **real**"
        )

    # ------------------------------------------------------------------ #
    # Links
    # ------------------------------------------------------------------ #

    def test_labelled_angle_link(self) -> None:
        self.assertEqual(
            self.convert("<https://example.com|text>"),
            "[text](https://example.com)",
        )

    def test_bare_angle_link_is_valid_autolink(self) -> None:
        self.assertEqual(
            self.convert("<https://example.com>"), "<https://example.com>"
        )

    # ------------------------------------------------------------------ #
    # URL integrity: delimiters inside URLs never become emphasis
    # ------------------------------------------------------------------ #

    def test_bare_angle_url_with_underscore_pair_unchanged(self) -> None:
        # "_foo_" would be a well-formed mrkdwn italic span in prose,
        # but inside a URL it must never be rewritten — the documented
        # "bare autolink unchanged" behaviour.
        self.assertEqual(
            self.convert("<https://example.com/_foo_>"),
            "<https://example.com/_foo_>",
        )

    def test_labelled_angle_url_with_underscore_pair_intact(self) -> None:
        self.assertEqual(
            self.convert("<https://example.com/_foo_|label>"),
            "[label](https://example.com/_foo_)",
        )

    def test_plain_url_with_underscore_pair_intact(self) -> None:
        self.assertEqual(
            self.convert("see https://example.com/_foo_ now"),
            "see https://example.com/_foo_ now",
        )
        self.assertEqual(
            self.convert("see https://example.com/_foo_."),
            "see https://example.com/_foo_.",
        )

    def test_url_with_star_and_tilde_pairs_intact(self) -> None:
        self.assertEqual(
            self.convert("<https://ex.com/*star*|l>"), "[l](https://ex.com/*star*)"
        )
        self.assertEqual(
            self.convert("<https://ex.com/~tilde~>"), "<https://ex.com/~tilde~>"
        )

    def test_emphasis_still_works_around_urls(self) -> None:
        self.assertEqual(
            self.convert("_real ital_ and https://example.com/a_b_"),
            "*real ital* and https://example.com/a_b_",
        )

    def test_mailto_labelled_link(self) -> None:
        self.assertEqual(
            self.convert("<mailto:alice@example.com|Alice>"),
            "[Alice](mailto:alice@example.com)",
        )

    def test_empty_label_angle_link_unchanged(self) -> None:
        self.assertEqual(self.convert("<https://x|>"), "<https://x|>")

    def test_empty_and_junk_angle_tokens_unchanged(self) -> None:
        self.assertEqual(self.convert("<> <>"), "<> <>")

    # ------------------------------------------------------------------ #
    # Mentions, channels and specials
    # ------------------------------------------------------------------ #

    def test_user_mention_raw_id(self) -> None:
        self.assertEqual(self.convert("<@U123ABC>"), "@U123ABC")

    def test_user_mention_with_label_uses_label(self) -> None:
        self.assertEqual(self.convert("<@U123ABC|alice>"), "@alice")

    def test_at_here_token(self) -> None:
        self.assertEqual(self.convert("<@here>"), "@here")

    def test_channel_with_label(self) -> None:
        self.assertEqual(self.convert("<#C123ABC|general>"), "#general")

    def test_channel_without_label_keeps_raw_id(self) -> None:
        self.assertEqual(self.convert("<#C123ABC>"), "#C123ABC")

    def test_specials_here_channel_everyone(self) -> None:
        self.assertEqual(self.convert("<!here>"), "@here")
        self.assertEqual(self.convert("<!channel>"), "@channel")
        self.assertEqual(self.convert("<!everyone>"), "@everyone")

    def test_unsupported_specials_unchanged(self) -> None:
        for token in ("<!date^1700000000|not now>", "<!subteam^S1|devs>"):
            with self.subTest(token=token):
                self.assertEqual(self.convert(token), token)

    # ------------------------------------------------------------------ #
    # Blockquotes and lists
    # ------------------------------------------------------------------ #

    def test_single_quote_lines_preserved(self) -> None:
        text = "> quoted line\n> another line"
        self.assertEqual(self.convert(text), text)

    def test_triple_quote_prefixes_each_line(self) -> None:
        self.assertEqual(
            self.convert(">>> deep quote\nsecond line\nthird"),
            "> deep quote\n> second line\n> third",
        )

    def test_triple_quote_alone_on_line(self) -> None:
        self.assertEqual(
            self.convert("before\n>>>\nafter"),
            "before\n>\n> after",
        )

    def test_triple_quote_empty_line_gets_bare_marker(self) -> None:
        self.assertEqual(
            self.convert(">>> head\n\nnext"),
            "> head\n>\n> next",
        )

    def test_triple_quote_keeps_fenced_blocks_verbatim(self) -> None:
        # Documented limitation: fenced code after '>>>' stays verbatim
        # so the code content is never corrupted with quote prefixes.
        text = ">>> start\n```\ncode\n```\ntail"
        self.assertEqual(
            self.convert(text), "> start\n```\ncode\n```\n> tail",
        )

    def test_numbered_list_preserved(self) -> None:
        self.assertEqual(self.convert("1. one\n2. two"), "1. one\n2. two")

    def test_bullet_lists_preserved(self) -> None:
        self.assertEqual(self.convert("- dash bullet"), "- dash bullet")
        self.assertEqual(self.convert("* star bullet"), "* star bullet")

    # ------------------------------------------------------------------ #
    # Combined document
    # ------------------------------------------------------------------ #

    def test_combined_document(self) -> None:
        self.assertEqual(self.convert(COMBINED_MRKDWN), COMBINED_MARKDOWN)


class SlackMrkdwnToolToMrkdwnTest(unittest.TestCase):
    """Ground-truth cases for mode='to_mrkdwn' (Markdown -> mrkdwn)."""

    def setUp(self) -> None:
        self.tool = SlackMrkdwnTool()

    def convert(self, text: str) -> str:
        return self.tool.execute(mode="to_mrkdwn", text=text)["result"]

    # ------------------------------------------------------------------ #
    # Emphasis (inverse mapping)
    # ------------------------------------------------------------------ #

    def test_double_star_bold(self) -> None:
        self.assertEqual(self.convert("**bold**"), "*bold*")

    def test_single_star_italic(self) -> None:
        self.assertEqual(self.convert("*italic*"), "_italic_")

    def test_underscore_italic_already_valid(self) -> None:
        self.assertEqual(self.convert("_italic_"), "_italic_")

    def test_double_tilde_strike(self) -> None:
        self.assertEqual(self.convert("~~strike~~"), "~strike~")

    def test_single_tilde_literal_in_markdown(self) -> None:
        self.assertEqual(self.convert("~single~"), "~single~")

    def test_triple_stars_pass_through(self) -> None:
        self.assertEqual(self.convert("***bold italic***"), "***bold italic***")

    def test_mixed_emphasis_one_line(self) -> None:
        self.assertEqual(
            self.convert("**bold** and *italic* and ~~strike~~"),
            "*bold* and _italic_ and ~strike~",
        )

    def test_bold_containing_italic(self) -> None:
        self.assertEqual(
            self.convert("**a _b_ c**"), "*a _b_ c*"
        )

    def test_space_adjacent_stars_untouched(self) -> None:
        self.assertEqual(self.convert("** spaced **"), "** spaced **")

    # ------------------------------------------------------------------ #
    # Links (inverse mapping)
    # ------------------------------------------------------------------ #

    def test_inline_link_to_angle_link(self) -> None:
        self.assertEqual(
            self.convert("[text](https://example.com)"),
            "<https://example.com|text>",
        )

    def test_empty_label_link_to_bare_angle(self) -> None:
        self.assertEqual(
            self.convert("[](https://example.com)"), "<https://example.com>"
        )

    def test_autolink_already_valid_mrkdwn(self) -> None:
        self.assertEqual(
            self.convert("<https://example.com>"), "<https://example.com>"
        )

    def test_image_link_untouched(self) -> None:
        self.assertEqual(
            self.convert("![alt](https://example.com/i.png)"),
            "![alt](https://example.com/i.png)",
        )

    def test_emphasis_inside_link_label_converted(self) -> None:
        self.assertEqual(
            self.convert("[**bold label**](https://x)"),
            "<https://x|*bold label*>",
        )

    # ------------------------------------------------------------------ #
    # URL integrity (inverse mapping)
    # ------------------------------------------------------------------ #

    def test_link_target_with_balanced_parentheses(self) -> None:
        # CommonMark allows one level of balanced parentheses in a link
        # destination — the Wikipedia URL shape.
        self.assertEqual(
            self.convert(
                "[Python](https://en.wikipedia.org/wiki/Python_(programming_language))"
            ),
            "<https://en.wikipedia.org/wiki/Python_(programming_language)|Python>",
        )
        self.assertEqual(
            self.convert("[t](https://ex.com/a(b)c)"),
            "<https://ex.com/a(b)c|t>",
        )

    def test_mention_lookalikes_inside_urls_not_wrapped(self) -> None:
        self.assertEqual(
            self.convert("see https://x.com/@here and https://ex.com/@U123ABC"),
            "see https://x.com/@here and https://ex.com/@U123ABC",
        )

    def test_image_url_with_underscores_intact(self) -> None:
        self.assertEqual(
            self.convert("![alt](https://ex.com/_pic_.png)"),
            "![alt](https://ex.com/_pic_.png)",
        )

    def test_label_emphasis_and_url_integrity_together(self) -> None:
        self.assertEqual(
            self.convert("[**b** _i_](https://ex.com/_keep_)"),
            "<https://ex.com/_keep_|*b* _i_>",
        )

    # ------------------------------------------------------------------ #
    # Mentions (inverse mapping, best-effort)
    # ------------------------------------------------------------------ #

    def test_raw_user_id_wrapped(self) -> None:
        self.assertEqual(self.convert("@U123ABC"), "<@U123ABC>")

    def test_raw_new_style_user_id_wrapped(self) -> None:
        self.assertEqual(self.convert("@W08LV1R4J2P"), "<@W08LV1R4J2P>")

    def test_plain_handle_not_wrapped(self) -> None:
        # Documented best-effort limit: mrkdwn mentions need the raw
        # workspace id, so '@alice' cannot be wrapped.
        self.assertEqual(self.convert("@alice"), "@alice")

    def test_special_mentions_wrapped(self) -> None:
        self.assertEqual(self.convert("@here"), "<!here>")
        self.assertEqual(self.convert("@channel"), "<!channel>")
        self.assertEqual(self.convert("@everyone"), "<!everyone>")

    def test_intraword_at_not_wrapped(self) -> None:
        self.assertEqual(self.convert("user@U123ABC.com"), "user@U123ABC.com")

    def test_already_wrapped_mention_untouched(self) -> None:
        self.assertEqual(self.convert("<@U123ABC>"), "<@U123ABC>")

    # ------------------------------------------------------------------ #
    # Code, quotes, lists
    # ------------------------------------------------------------------ #

    def test_inline_code_untouched(self) -> None:
        self.assertEqual(self.convert("`**not bold**`"), "`**not bold**`")

    def test_fenced_block_untouched(self) -> None:
        text = "```python\nprint('**x**')\n```"
        self.assertEqual(self.convert(text), text)

    def test_quote_lines_preserved(self) -> None:
        text = "> quoted line"
        self.assertEqual(self.convert(text), text)

    def test_heading_preserved(self) -> None:
        self.assertEqual(self.convert("# Heading"), "# Heading")

    def test_lists_preserved(self) -> None:
        self.assertEqual(self.convert("- item\n1. one"), "- item\n1. one")

    def test_combined_document(self) -> None:
        self.assertEqual(self.convert(COMBINED_MARKDOWN), COMBINED_MRKDWN_NORMALIZED)


class SlackMrkdwnToolDetectTest(unittest.TestCase):
    """Exact-score cases for mode='detect'."""

    def setUp(self) -> None:
        self.tool = SlackMrkdwnTool()

    def detect(self, text: str) -> dict:
        return self.tool.execute(mode="detect", text=text)

    def test_mrkdwn_signatures_win(self) -> None:
        result = self.detect("hello *bold* world <@U123ABC>")
        self.assertTrue(result["is_mrkdwn"])
        self.assertEqual(result["verdict"], "mrkdwn")
        self.assertEqual(result["mrkdwn_score"], 5)  # 2 star + 3 angle
        self.assertEqual(result["markdown_score"], 0)
        self.assertEqual(result["signals"]["single_star_emphasis"], 1)
        self.assertEqual(result["signals"]["angle_mention_tokens"], 1)

    def test_markdown_signatures_win(self) -> None:
        result = self.detect("**bold** and [link](https://x)")
        self.assertFalse(result["is_mrkdwn"])
        self.assertEqual(result["verdict"], "markdown")
        self.assertEqual(result["markdown_score"], 5)  # 2 bold + 3 link
        self.assertEqual(result["mrkdwn_score"], 0)

    def test_plain_text_inconclusive(self) -> None:
        result = self.detect("plain text with no signatures at all")
        self.assertFalse(result["is_mrkdwn"])
        self.assertEqual(result["verdict"], "inconclusive")
        self.assertEqual(result["mrkdwn_score"], 0)
        self.assertEqual(result["markdown_score"], 0)

    def test_pipe_angle_link_is_mrkdwn(self) -> None:
        result = self.detect("<https://example.com|docs>")
        self.assertEqual(result["verdict"], "mrkdwn")
        self.assertEqual(result["signals"]["angle_pipe_links"], 1)
        self.assertEqual(result["mrkdwn_score"], 3)

    def test_channel_token_is_mrkdwn(self) -> None:
        result = self.detect("posted in <#C123|general>")
        self.assertTrue(result["is_mrkdwn"])
        self.assertEqual(result["signals"]["angle_mention_tokens"], 1)

    def test_special_token_is_mrkdwn(self) -> None:
        result = self.detect("attention <!here>")
        self.assertEqual(result["verdict"], "mrkdwn")

    def test_double_tilde_is_markdown(self) -> None:
        result = self.detect("~~gone~~")
        self.assertEqual(result["verdict"], "markdown")
        self.assertEqual(result["markdown_score"], 2)

    def test_atx_heading_is_markdown(self) -> None:
        result = self.detect("# Title\nbody")
        self.assertEqual(result["verdict"], "markdown")
        self.assertEqual(result["signals"]["atx_headings"], 1)

    def test_hash_without_space_is_not_heading(self) -> None:
        result = self.detect("#general channel")
        self.assertEqual(result["verdict"], "inconclusive")

    def test_triple_quote_is_mrkdwn(self) -> None:
        result = self.detect(">>> quoted to the end")
        self.assertEqual(result["verdict"], "mrkdwn")
        self.assertEqual(result["signals"]["triple_quote_blocks"], 1)

    def test_tie_goes_to_mrkdwn(self) -> None:
        # *a* is mrkdwn-bold (+2), **b** is markdown-bold (+2): tie -> mrkdwn.
        result = self.detect("*a* **b**")
        self.assertTrue(result["is_mrkdwn"])
        self.assertEqual(result["mrkdwn_score"], 2)
        self.assertEqual(result["markdown_score"], 2)

    def test_stronger_markdown_score_wins(self) -> None:
        # Two markdown-bold spans (d=4) beat one angle mention (m=3).
        result = self.detect("**b1** **b2** <@U1>")
        self.assertEqual(result["verdict"], "markdown")
        self.assertEqual(result["mrkdwn_score"], 3)
        self.assertEqual(result["markdown_score"], 4)

    def test_code_content_ignored(self) -> None:
        result = self.detect("```\n**x** [y](z)\n```")
        self.assertEqual(result["verdict"], "inconclusive")

    def test_inline_code_ignored(self) -> None:
        result = self.detect("hello `**code**` world")
        self.assertEqual(result["verdict"], "inconclusive")

    def test_result_field_matches_verdict(self) -> None:
        for text, expected in (
            ("*a*", "mrkdwn"),
            ("**a**", "markdown"),
            ("nothing", "inconclusive"),
        ):
            with self.subTest(text=text):
                result = self.detect(text)
                self.assertEqual(result["result"], expected)
                self.assertEqual(result["mode"], "detect")


class SlackMrkdwnToolRoundTripTest(unittest.TestCase):
    """The documented round-trip property of the supported subset."""

    def setUp(self) -> None:
        self.tool = SlackMrkdwnTool()

    def to_markdown(self, text: str) -> str:
        return self.tool.execute(mode="to_markdown", text=text)["result"]

    def to_mrkdwn(self, text: str) -> str:
        return self.tool.execute(mode="to_mrkdwn", text=text)["result"]

    def test_exact_round_trip_samples(self) -> None:
        # For these constructs the cycle returns the original mrkdwn
        # character for character.
        samples = [
            "*bold text*",
            "_italic text_",
            "~strike text~",
            "`code span`",
            FENCED,
            "<https://example.com|label>",
            "<https://example.com>",
            "<@U123ABC>",
            "<!here>",
            "<!channel>",
            "> quoted line",
            "1. one\n2. two",
            "- bullet item",
            "* star bullet",
            "__literal underscores__",
            "snake_case_name",
        ]
        for sample in samples:
            with self.subTest(sample=sample):
                self.assertEqual(self.to_mrkdwn(self.to_markdown(sample)), sample)

    def test_normalized_round_trip_samples(self) -> None:
        # Labelled mentions/channels normalize to their display form on
        # the first cycle (the raw id cannot be recovered offline); a
        # literal double-star span in mrkdwn reads as markdown bold and
        # comes back as genuine single-star mrkdwn bold.
        cases = [
            ("<#C123ABC|general>", "#general"),
            ("<@U123ABC|alice>", "@alice"),
            ("**literal stars**", "*literal stars*"),
            ("~~literal tildes~~", "~literal tildes~"),
        ]
        for original, expected in cases:
            with self.subTest(original=original):
                once = self.to_mrkdwn(self.to_markdown(original))
                self.assertEqual(once, expected)

    def test_cycle_is_fixed_point_for_supported_subset(self) -> None:
        # Property: y = to_mrkdwn(to_markdown(x)) is stable — applying
        # the same cycle to y yields y again.
        samples = [
            "*bold* and _italic_ and ~strike~",
            "`code` and `nested **x**` spans",
            "<https://example.com|text> plus <@U123ABC>",
            ">>> quoted *bold* head\nquoted _italic_ tail",
            "> quote\nnormal line\n- bullet\n1. numbered",
            "**literal stars** and ~~literal tildes~~",
            "<#C123|general> <@U456|bob> <!here>",
            COMBINED_MRKDWN,
        ]
        for sample in samples:
            with self.subTest(sample=sample):
                once = self.to_mrkdwn(self.to_markdown(sample))
                twice = self.to_mrkdwn(self.to_markdown(once))
                self.assertEqual(twice, once)

    def test_cycle_is_stable_from_the_markdown_side(self) -> None:
        # Symmetric property: md = to_markdown(x); y = to_mrkdwn(md);
        # converting y forward and back returns md again.
        samples = [COMBINED_MRKDWN, "*b* _i_ ~s~", "<https://x|y> <!here>"]
        for sample in samples:
            with self.subTest(sample=sample):
                md = self.to_markdown(sample)
                back = self.to_mrkdwn(md)
                self.assertEqual(self.to_markdown(back), md)

    # ------------------------------------------------------------------ #
    # Randomized corpus over the supported constructs (fixed seed).
    # ------------------------------------------------------------------ #

    _WORDS = (
        "deploy", "finished", "the", "pipeline", "alert", "fired",
        "again", "please", "review", "asap", "ok", "5", "v2.1", "note:",
    )
    _IDS = ("U123ABC", "U9XZ3KQ", "W08LV1R4J2P", "USLACKBOT", "U1")
    _CHANNELS = ("C123ABC", "C0123ABCD", "C1")
    _URLS = (
        "https://example.com",
        "https://example.com/_foo_",
        "https://example.com/a_b_c",
        "https://en.wikipedia.org/wiki/United_States",
        "https://ex.com/p?q=_v_&x=1",
        "http://insecure.example.net/x",
        "https://ex.com/*star*",
        "https://ex.com/~tilde~",
        "https://ex.com/@here",
        "https://ex.com/path-(paren)",
        "https://en.wikipedia.org/wiki/Python_(programming_language)",
    )

    def _random_atom(self, rng: "random.Random") -> str:
        kind = rng.randrange(12)
        word = rng.choice(self._WORDS)
        url = rng.choice(self._URLS)
        if kind == 0:
            return rng.choice(self._WORDS)
        if kind in (1, 2, 3):  # emphasis, with adversarial shapes
            char = rng.choice("*_~")
            style = rng.randrange(4)
            if style == 0:
                return f"{char}{word}{char}"
            if style == 1:
                return f"{char}{word} and {word}{char}"
            if style == 2:
                return f"{char * 2}{word}{char * 2}"  # literal double
            return f"x{char}{word}{char}y"  # intraword
        if kind == 4:
            return f"<{url}>"
        if kind == 5:
            return f"<{url}|{word}>"
        if kind == 6:
            return f"<@{rng.choice(self._IDS)}>"
        if kind == 7:
            return f"<@{rng.choice(self._IDS)}|{word.replace(' ', '_')}>"
        if kind == 8:
            return f"<#{rng.choice(self._CHANNELS)}|{word.replace(' ', '_')}>"
        if kind == 9:
            return f"[{word}]({url})"
        if kind == 10:
            return url
        return f"`{rng.choice(('*x*', '_y_', 'code', 'https://ex.com/_a_'))}`"

    def _random_line(self, rng: "random.Random") -> str:
        kind = rng.randrange(9)
        atoms = " ".join(self._random_atom(rng) for _ in range(rng.randrange(1, 4)))
        if kind == 0:
            return atoms
        if kind == 1:
            return "> " + atoms
        if kind == 2:
            return f"{rng.randrange(1, 4)}. " + atoms
        if kind == 3:
            return "- " + atoms
        if kind == 4:
            return "```"
        if kind == 5:
            return ">>> " + atoms
        if kind == 6:
            return rng.choice(("* * *", "---"))
        if kind == 7:
            return f"![{rng.choice(self._WORDS)}]({rng.choice(self._URLS)})"
        return atoms

    def test_randomized_corpus_fixed_point_and_url_integrity(self) -> None:
        # 200 deterministic random documents built from the supported
        # constructs: (a) the documented fixed-point property holds and
        # (b) every URL embedded in the input survives to_markdown,
        # to_mrkdwn and the full cycle verbatim.
        import random

        rng = random.Random(20261020)
        for case in range(200):
            text = "\n".join(
                self._random_line(rng) for _ in range(rng.randrange(1, 5))
            )
            with self.subTest(case=case, text=text):
                markdown = self.to_markdown(text)
                once = self.to_mrkdwn(markdown)
                self.assertEqual(self.to_mrkdwn(self.to_markdown(once)), once)
                self.assertNotIn("\x00", markdown)
                self.assertNotIn("\x00", once)
                for url in self._URLS:
                    if url in text:
                        self.assertIn(url, markdown)
                        self.assertIn(url, self.to_mrkdwn(text))
                        self.assertIn(url, once)


class SlackMrkdwnToolValidationTest(unittest.TestCase):
    """Invalid inputs raise ValueError (strict validation)."""

    def setUp(self) -> None:
        self.tool = SlackMrkdwnTool()

    def assert_invalid(self, **kwargs) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    def test_invalid_mode(self) -> None:
        for bad in ("convert", None, 123, "TO_MARKDOWN", ""):
            with self.subTest(mode=bad):
                self.assert_invalid(mode=bad, text="*x*")

    def test_invalid_text_type(self) -> None:
        for bad in (None, 123, True, b"*x*", ["*x*"]):
            with self.subTest(text=bad):
                for mode in ("to_markdown", "to_mrkdwn", "detect"):
                    self.assert_invalid(mode=mode, text=bad)

    def test_empty_text_rejected(self) -> None:
        for mode in ("to_markdown", "to_mrkdwn", "detect"):
            with self.subTest(mode=mode):
                self.assert_invalid(mode=mode, text="")

    def test_text_length_limit(self) -> None:
        oversized = "a" * 100_001
        self.assert_invalid(mode="to_markdown", text=oversized)
        ok = self.tool.execute(mode="detect", text="a" * 100_000)
        self.assertEqual(ok["verdict"], "inconclusive")

    def test_nul_character_rejected(self) -> None:
        self.assert_invalid(mode="to_markdown", text="bad\x00text")

    def test_result_context_echoes_mode(self) -> None:
        for mode in ("to_markdown", "to_mrkdwn"):
            with self.subTest(mode=mode):
                result = self.tool.execute(mode=mode, text="plain")
                self.assertEqual(result["mode"], mode)
                self.assertEqual(result["result"], "plain")


class SlackMrkdwnToolPackagingTest(unittest.TestCase):
    """Packaging / registration."""

    def test_class_defaults_and_export(self) -> None:
        tool = SlackMrkdwnTool()
        self.assertIs(DirectSlackMrkdwnTool, SlackMrkdwnTool)
        self.assertEqual(tool.name, "slack_mrkdwn_tool")
        self.assertIn("mrkdwn", tool.description)
        from agentuniverse.agent.action.tool.common_tool import __all__

        self.assertIn("SlackMrkdwnTool", __all__)


if __name__ == "__main__":
    unittest.main()
