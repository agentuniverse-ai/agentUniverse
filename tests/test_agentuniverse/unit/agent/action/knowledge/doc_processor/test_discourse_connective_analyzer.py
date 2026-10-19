# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @FileName: test_discourse_connective_analyzer.py

import unittest

from agentuniverse.agent.action.knowledge.doc_processor.discourse_connective_analyzer import DiscourseConnectiveAnalyzer
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer

# --------------------------------------------------------------------- #
# Fixtures — every expected number below was counted by hand.
# --------------------------------------------------------------------- #

# 4 sentences, 4 contrast connectives (however, but, yet, although);
# density 100.0; reasoning share 4/4 -> argumentative; dominant contrast.
EN_CONTRAST = (
    "However, the plan changed. But nobody objected. "
    "Yet the risks remained. Although time was short, the team succeeded."
)

# 3 sentences, 3 contrast connectives (但是, 然而, 虽然); density 100.0.
ZH_CONTRAST = (
    "计划改变了，但是没有人反对。然而风险仍然存在。"
    "虽然时间紧张，团队还是成功了。"
)

# 4 sentences, 4 cause connectives (because, therefore, 由于, 因此).
MIXED_CAUSE = (
    "The launch slipped because of weather. Therefore the review moved. "
    "由于暴雨，发射推迟。因此评审改期。"
)

# 6 sentences, 6 addition connectives (moreover, furthermore, also,
# 此外, 另外, 而且); density 100.0; reasoning 0 -> descriptive.
ADDITION_TEXT = (
    "Moreover, sales grew. Furthermore, margins improved. "
    "The launch also succeeded. 此外，销售额增长。另外，利润率提高。"
    "而且客户留存上升。"
)

# 13 sentences (7 EN + 6 ZH), 13 sequence connectives; density 100.0;
# sequence share 13/13 -> procedural.
SEQUENCE_TEXT = (
    "First, preheat the oven. Next, mix the batter. "
    "Then bake for thirty minutes. Finally, cool completely. "
    "Subsequently, pack the cakes. Meanwhile, clean the bench. "
    "Afterwards, rest. 首先，预热烤箱。然后混合面糊。接着烘烤。"
    "最后冷却。与此同时，清洁台面。其次准备模具。"
)

# 8 sentences (5 EN + 3 ZH), 8 exemplification connectives; the "as"
# inside "such as" is consumed and must NOT also count as cause.
EXEMPLIFICATION_TEXT = (
    "Many fruits, for example apples, ripen late. "
    "Some crops, for instance figs, need sun. "
    "Citrus, such as oranges, thrives. E.g., lemons sour quickly. "
    "One fruit, namely the pear, bruises. 例如，苹果很甜。"
    "譬如，梨易碰伤。比如橙子多汁。"
)

# 6 sentences (3 EN + 3 ZH), 7 concession connectives — one sentence
# carries two ("Granted ... despite ..."); the "though" inside
# "even though" is consumed and must NOT also count as contrast;
# density round(7/6*100, 2) = 116.67.
CONCESSION_TEXT = (
    "Despite the rain, the match continued. Even though it was late, "
    "play resumed. Granted, the pitch was wet, despite the mud. "
    "尽管下雨，比赛继续。即使很晚，比赛恢复。纵然球场湿滑，比赛仍未取消。"
)

# 5 sentences, zero connectives: every near-miss must be rejected by the
# whole-word guard (butterfly/butter vs but, cast/broadcast vs as,
# firstly vs first, henceforth vs hence).
BOUNDARY_GUARD_TEXT = (
    "The butterfly spread butter on toast. The cable snapped at the "
    "cast. Firstly, the castanets played. Henceforth it held. "
    "The broadcast resumed."
)

# Positive control for the same guard: "But" and "However" count while
# "butter" and "butterfly" do not; 2 sentences, 2 contrast connectives.
BOUNDARY_POSITIVE = "But the butter melted. However the butterfly flew."

# 1 sentence, cause 1 (因为 as a substring, no spaces needed).
ZH_SUBSTRING = "我们因为天气原因取消了行程。"

# 1 sentence, zero connectives: the bare 因 inside 原因 matches nothing.
ZH_NO_MATCH = "原因很明确。"

# 1 sentence, 2 cause connectives (因为, 因此); density 200.0.
ZH_DENSE = "因为下雨，因此比赛取消。"

# 10 sentences, 3 connectives (but, however, because); density 30.0.
ARITH_10_3 = (
    "He ran. She walked. The dog barked. Birds flew. Wind blew. "
    "Rain fell. Doors closed. Lights dimmed. But one window stayed lit. "
    "However the keeper slept, because night had fallen."
)

# 7 sentences, 3 connectives (but, because, however);
# density round(3/7*100, 2) = 42.86 — exercises rounding.
ARITH_7_3 = (
    "He ran. She walked. The dog barked. Birds flew. But wind blew. "
    "Rain fell because clouds gathered. However night came."
)

# 10 sentences, zero connectives; density 0.0 -> narrative.
NARRATIVE_EN = (
    "The girl opened the door. The hallway was dark. She touched the "
    "wall. A stair creaked underfoot. The cat ran ahead. Moonlight lit "
    "the landing. A clock struck twice. She reached the attic. Dust "
    "covered the boxes. One box stood open."
)

# 6 sentences, zero connectives; density 0.0 -> narrative.
NARRATIVE_ZH = (
    "女孩推开门。走廊很暗。她摸着墙走。楼梯吱呀作响。猫跑在前面。"
    "月光照亮楼梯口。"
)

# 10 sentences, one connective each: contrast 3, cause 3, addition 1,
# sequence 1, exemplification 1, concession 1; density 100.0; reasoning
# share exactly 6/10 = 60% (inclusive boundary) -> argumentative; the
# 3-3 tie between cause and contrast must resolve alphabetically to
# "cause".
ARGUMENTATIVE_60 = (
    "However, the engine stalled. But the crew persisted. Because fuel "
    "ran low, the pilot landed. Therefore the log recorded a diversion. "
    "Although tired, the team debriefed. Since dusk neared, the tower "
    "lit the strip. Moreover, the weather cleared. First, the mechanics "
    "inspected the frame. For example, a cracked panel was found. "
    "Despite the damage, the flight resumed."
)

# Same shape with one cause sentence swapped for a sequence one:
# contrast 3, cause 2, addition 1, sequence 2, exemplification 1,
# concession 1; reasoning share 50% -> descriptive.
DESCRIPTIVE_50 = (
    "However, the engine stalled. But the crew persisted. Because fuel "
    "ran low, the pilot landed. Therefore the log recorded a diversion. "
    "Although tired, the team debriefed. Meanwhile the radar spun. "
    "Moreover, the weather cleared. First, the mechanics inspected the "
    "frame. For example, a cracked panel was found. Despite the damage, "
    "the flight resumed."
)

# 10 sentences, 8 connectives: sequence 5, addition 1, exemplification
# 1, concession 1; density 80.0; sequence share 5/8 = 62.5% ->
# procedural.
PROCEDURAL_TEXT = (
    "First, wash the rice. Next, add water. Then cover the pot. "
    "Finally, fluff the grains. Meanwhile, chop the vegetables. "
    "Moreover, salt enhances flavor. For example, basmati works well. "
    "Despite the steam, the lid stays on. The kitchen smells good. "
    "Dinner is ready soon."
)

# 10 sentences, one connective each: sequence 4, addition 2,
# exemplification 2, concession 2; sequence share exactly 4/10 = 40%
# (inclusive boundary) -> procedural.
PROCEDURAL_40 = (
    "First, preheat. Then bake. Next, frost. Finally, serve. "
    "Moreover, it keeps well. Also, it freezes well. For example, "
    "chocolate sells. For instance, vanilla appeals. Despite the cost, "
    "bakers order it. Granted, it is laborious."
)

# One sequence sentence swapped for an addition one: sequence 3,
# addition 3, exemplification 2, concession 2; sequence share 30% ->
# descriptive.
PROCEDURAL_30 = (
    "First, preheat. Then bake. Next, frost. Also, garnish simply. "
    "Moreover, it keeps well. Also, it freezes well. For example, "
    "chocolate sells. For instance, vanilla appeals. Despite the cost, "
    "bakers order it. Granted, it is laborious."
)

# 10 sentences, one connective each: contrast 3, cause 3, sequence 4;
# reasoning share 60% AND sequence share 40% both hold — the documented
# rule order must let argumentative win.
ARG_OVER_PROC = (
    "However, the claim failed. But the data disagreed. Because bias "
    "existed, results shifted. Therefore the study restarted. Although "
    "small, the sample spoke. Since funds flowed, work continued. "
    "First, the team recalibrated. Then the fit improved. Next, the "
    "auditor signed off. Finally, the paper shipped."
)

# 6 sentences, 7 reasoning connectives (contrast 3: 然而/但是/虽然;
# cause 4: 因为/所以/因此/由于); density round(7/6*100, 2) = 116.67 ->
# argumentative; dominant cause (4 > 3).
ZH_ARGUMENTATIVE = (
    "然而，数据不支持该结论。但是，样本量太小。因为偏差存在，所以结果存疑。"
    "因此需要重新实验。由于经费充足，研究可以继续。虽然争议仍在，团队依然推进。"
)

# 6 sentences, 6 sequence connectives; density 100.0 -> procedural.
ZH_PROCEDURAL = (
    "首先，收集数据。其次，清洗数据。然后，训练模型。接着，评估效果。"
    "最后，部署上线。与此同时，监控开启。"
)

# 3 sentences, addition/cause/concession one each; dominant tie across
# three categories resolves alphabetically to "addition".
DOMINANT_TIE = (
    "Moreover, it rained. Because floods came, roads closed. "
    "Despite this, we drove."
)

# Case-insensitivity fixture: 2 sentences, contrast 1 (HOWEVER) and
# cause 1 (BECAUSE).
UPPER_CASE_TEXT = "HOWEVER the sky cleared. BECAUSE wind rose."


def _doc(text: str, **metadata) -> Document:
    """Build a Document carrying `text` and optional metadata."""
    return Document(text=text, metadata=dict(metadata) or None)


def _ticks(plain: int, connected: str) -> str:
    """`plain` copies of a connective-free sentence plus one sentence
    carrying exactly one connective ("But it stopped.")."""
    return " ".join(["The clock ticked."] * plain + [connected])


class TestDiscourseConnectiveAnalyzer(unittest.TestCase):
    """Comprehensive test suite for DiscourseConnectiveAnalyzer."""

    def setUp(self):
        self.analyzer = DiscourseConnectiveAnalyzer()
        self.query = Query(query_str="discourse")

    def _create_configer(self, config_dict):
        """Create a ComponentConfiger from a plain dictionary."""
        cfg = Configer()
        cfg.value = config_dict
        configer = ComponentConfiger()
        configer.load_by_configer(cfg)
        return configer

    def _analyze(self, text: str):
        """Run the analyzer core on one text and return its dict."""
        return self.analyzer._analyze(text)

    def _profile_of(self, text: str):
        """Convenience: the profile label for one text."""
        return self._analyze(text)[1]

    # ========== Initialization tests ==========

    def test_default_configuration(self):
        """Defaults: narrative<2, argumentative>=5 at 60% share,
        procedural at 40% share, 'discourse'/'discourse_profile' keys."""
        a = DiscourseConnectiveAnalyzer()
        self.assertEqual(a.narrative_max_density, 2.0)
        self.assertEqual(a.argumentative_min_density, 5.0)
        self.assertEqual(a.argumentative_min_share, 0.6)
        self.assertEqual(a.procedural_min_share, 0.4)
        self.assertEqual(a.discourse_key, "discourse")
        self.assertEqual(a.profile_key, "discourse_profile")

    def test_initialize_by_component_configer(self):
        """YAML-provided parameters are applied on initialization."""
        configer = self._create_configer({
            'name': 'discourse_connective_analyzer',
            'description': 'connective analyzer',
            'narrative_max_density': 10,
            'argumentative_min_density': 1.5,
            'argumentative_min_share': 0.5,
            'procedural_min_share': 0.9,
            'discourse_key': 'rhetoric',
            'profile_key': 'rhetoric_profile',
        })
        a = DiscourseConnectiveAnalyzer()
        a._initialize_by_component_configer(configer)
        self.assertEqual(a.narrative_max_density, 10.0)
        self.assertEqual(a.argumentative_min_density, 1.5)
        self.assertEqual(a.argumentative_min_share, 0.5)
        self.assertEqual(a.procedural_min_share, 0.9)
        self.assertEqual(a.discourse_key, 'rhetoric')
        self.assertEqual(a.profile_key, 'rhetoric_profile')
        self.assertEqual(a.name, 'discourse_connective_analyzer')

    def test_invalid_configuration_raises(self):
        """Negative densities, out-of-range shares, non-numeric values
        (bools included) and non-string keys all fail at load time."""
        base = {
            'name': 'a', 'description': 'd',
            'narrative_max_density': 2.0,
            'argumentative_min_density': 5.0,
            'argumentative_min_share': 0.6,
            'procedural_min_share': 0.4,
            'discourse_key': 'discourse',
            'profile_key': 'discourse_profile',
        }
        for key, value in (
            ('narrative_max_density', -1),
            ('narrative_max_density', 'two'),
            ('narrative_max_density', True),
            ('argumentative_min_density', -0.5),
            ('argumentative_min_density', 'high'),
            ('argumentative_min_share', 0),
            ('argumentative_min_share', 1.5),
            ('argumentative_min_share', True),
            ('procedural_min_share', 0),
            ('procedural_min_share', 2),
            ('procedural_min_share', False),
            ('discourse_key', 5),
            ('profile_key', ['x']),
        ):
            config = dict(base, **{key: value})
            with self.assertRaises(ValueError, msg=f"{key}={value!r}"):
                DiscourseConnectiveAnalyzer()._initialize_by_component_configer(
                    self._create_configer(config))

    # ========== Per-category counting (EN + ZH) ==========

    def test_contrast_counted_en_and_zh(self):
        """Contrast entries from both scripts are counted one by one."""
        for text, sentences in ((EN_CONTRAST, 4), (ZH_CONTRAST, 3)):
            discourse, _ = self._analyze(text)
            self.assertEqual(discourse["contrast"], sentences,
                             text[:20])
            self.assertEqual(discourse["total"], sentences)
            self.assertEqual(discourse["sentence_count"], sentences)
            self.assertEqual(discourse["dominant"], "contrast")

    def test_cause_counted_mixed_en_zh(self):
        """because / therefore (EN) and 由于 / 因此 (ZH) all count."""
        discourse, _ = self._analyze(MIXED_CAUSE)
        self.assertEqual(discourse["cause"], 4)
        self.assertEqual(discourse["sentence_count"], 4)
        self.assertEqual(discourse["dominant"], "cause")

    def test_addition_counted_en_and_zh(self):
        """moreover / furthermore / also and 此外 / 另外 / 而且 count."""
        discourse, _ = self._analyze(ADDITION_TEXT)
        self.assertEqual(discourse["addition"], 6)
        self.assertEqual(discourse["sentence_count"], 6)
        self.assertEqual(discourse["dominant"], "addition")

    def test_sequence_counted_en_and_zh(self):
        """All seven EN and six ZH sequence entries count; 首先 through
        与此同时 behave exactly like first through afterwards."""
        discourse, _ = self._analyze(SEQUENCE_TEXT)
        self.assertEqual(discourse["sequence"], 13)
        self.assertEqual(discourse["sentence_count"], 13)
        self.assertEqual(discourse["dominant"], "sequence")

    def test_exemplification_counted_and_as_consumed(self):
        """for example / for instance / such as / e.g. / namely and
        例如 / 譬如 / 比如 count; the "as" inside "such as" is consumed
        by the longer phrase and never double-counted as cause."""
        discourse, _ = self._analyze(EXEMPLIFICATION_TEXT)
        self.assertEqual(discourse["exemplification"], 8)
        self.assertEqual(discourse["cause"], 0)
        self.assertEqual(discourse["sentence_count"], 8)
        self.assertEqual(discourse["dominant"], "exemplification")

    def test_concession_counted_and_though_consumed(self):
        """despite / in spite of / even though / granted and 尽管 /
        即使 / 纵然 count; the "though" inside "even though" is consumed
        and never double-counted as contrast."""
        discourse, _ = self._analyze(CONCESSION_TEXT)
        self.assertEqual(discourse["concession"], 7)
        self.assertEqual(discourse["contrast"], 0)
        self.assertEqual(discourse["sentence_count"], 6)

    def test_eg_counted_without_splitting_sentence(self):
        """"e.g." counts as one exemplification connective while the
        conservative splitter keeps its sentence whole (single-letter
        initial guard), so the density denominator stays 1."""
        discourse, profile = self._analyze("See e.g. Smith 2001 for details.")
        self.assertEqual(discourse["sentence_count"], 1)
        self.assertEqual(discourse["exemplification"], 1)
        self.assertEqual(discourse["density_per_100_sentences"], 100.0)
        self.assertEqual(profile, "descriptive")

    def test_case_insensitive_matching(self):
        """Uppercase connectives count exactly like lowercase ones."""
        discourse, _ = self._analyze(UPPER_CASE_TEXT)
        self.assertEqual(discourse["contrast"], 1)
        self.assertEqual(discourse["cause"], 1)
        self.assertEqual(discourse["sentence_count"], 2)

    # ========== Word-boundary guards ==========

    def test_en_whole_word_guard_blocks_embedded_matches(self):
        """"but" does not fire inside butterfly/butter, "as" not inside
        cast/broadcast, "first" not inside firstly, "hence" not inside
        henceforth: the whole text yields zero connectives."""
        discourse, profile = self._analyze(BOUNDARY_GUARD_TEXT)
        self.assertEqual(discourse["sentence_count"], 5)
        self.assertEqual(discourse["total"], 0)
        for category in ("addition", "cause", "concession", "contrast",
                         "exemplification", "sequence"):
            self.assertEqual(discourse[category], 0, category)
        self.assertIsNone(discourse["dominant"])

    def test_en_whole_word_guard_admits_real_words(self):
        """The same guards admit a real "But" and "However" while still
        ignoring butter/butterfly in the same sentences."""
        discourse, _ = self._analyze(BOUNDARY_POSITIVE)
        self.assertEqual(discourse["contrast"], 2)
        self.assertEqual(discourse["total"], 2)
        self.assertEqual(discourse["sentence_count"], 2)
        self.assertEqual(discourse["density_per_100_sentences"], 100.0)

    def test_zh_substring_matching_semantics(self):
        """ZH matching is substring-based: 因为 fires glued inside a
        longer run, a bare 因 inside 原因 fires nothing, and two glued
        cause connectives in one sentence both count (density 200.0)."""
        discourse, _ = self._analyze(ZH_SUBSTRING)
        self.assertEqual(discourse["cause"], 1)
        self.assertEqual(discourse["sentence_count"], 1)

        discourse, _ = self._analyze(ZH_NO_MATCH)
        self.assertEqual(discourse["total"], 0)

        discourse, _ = self._analyze(ZH_DENSE)
        self.assertEqual(discourse["cause"], 2)
        self.assertEqual(discourse["density_per_100_sentences"], 200.0)

    # ========== Density arithmetic ==========

    def test_density_arithmetic_hand_verified(self):
        """3 connectives over 10 sentences -> exactly 30.0 per 100."""
        discourse, _ = self._analyze(ARITH_10_3)
        self.assertEqual(discourse["sentence_count"], 10)
        self.assertEqual(discourse["total"], 3)
        self.assertEqual(discourse["density_per_100_sentences"], 30.0)

    def test_density_rounding_hand_verified(self):
        """3 connectives over 7 sentences: 42.857... rounds to 42.86."""
        discourse, _ = self._analyze(ARITH_7_3)
        self.assertEqual(discourse["sentence_count"], 7)
        self.assertEqual(discourse["total"], 3)
        self.assertEqual(discourse["density_per_100_sentences"], 42.86)

    def test_density_uneven_denominator_hand_verified(self):
        """7 connectives over 6 sentences: 116.66... rounds to 116.67."""
        discourse, _ = self._analyze(CONCESSION_TEXT)
        self.assertEqual(discourse["density_per_100_sentences"], 116.67)

    def test_total_equals_sum_of_categories(self):
        """The stamped total is the sum of the six category counts."""
        discourse, _ = self._analyze(ARGUMENTATIVE_60)
        per_category = sum(discourse[c] for c in
                           ("addition", "cause", "concession", "contrast",
                            "exemplification", "sequence"))
        self.assertEqual(discourse["total"], per_category)

    # ========== Profile classification ==========

    def test_profile_narrative_en_and_zh(self):
        """Connective-free storytelling yields density 0.0, dominant
        None and the narrative profile in both languages."""
        for text in (NARRATIVE_EN, NARRATIVE_ZH):
            discourse, profile = self._analyze(text)
            self.assertEqual(profile, "narrative", text[:20])
            self.assertEqual(discourse["total"], 0)
            self.assertEqual(discourse["density_per_100_sentences"], 0.0)
            self.assertIsNone(discourse["dominant"])

    def test_profile_argumentative_en(self):
        """contrast+cause exactly 60% with density 100 -> argumentative."""
        discourse, profile = self._analyze(ARGUMENTATIVE_60)
        self.assertEqual(profile, "argumentative")
        self.assertEqual(discourse["contrast"], 3)
        self.assertEqual(discourse["cause"], 3)
        self.assertEqual(discourse["density_per_100_sentences"], 100.0)

    def test_profile_argumentative_zh(self):
        """然而/但是/虽然 plus 因为/所以/因此/由于 -> argumentative."""
        discourse, profile = self._analyze(ZH_ARGUMENTATIVE)
        self.assertEqual(profile, "argumentative")
        self.assertEqual(discourse["contrast"], 3)
        self.assertEqual(discourse["cause"], 4)
        self.assertEqual(discourse["density_per_100_sentences"], 116.67)
        self.assertEqual(discourse["dominant"], "cause")

    def test_profile_procedural_en_and_zh(self):
        """Sequence-heavy instructions yield the procedural profile in
        both languages."""
        for text in (PROCEDURAL_TEXT, ZH_PROCEDURAL):
            discourse, profile = self._analyze(text)
            self.assertEqual(profile, "procedural", text[:20])
            self.assertEqual(discourse["dominant"], "sequence")

    def test_profile_descriptive_mixed(self):
        """Mixed rhetoric with reasoning below 60% and sequence below
        40% lands on descriptive, not narrative (density >= 2)."""
        discourse, profile = self._analyze(DESCRIPTIVE_50)
        self.assertEqual(profile, "descriptive")
        self.assertEqual(discourse["total"], 10)
        self.assertEqual(discourse["density_per_100_sentences"], 100.0)

    def test_profile_descriptive_non_reasoning(self):
        """Addition/exemplification/concession-heavy text (reasoning
        share 0) is descriptive, not argumentative."""
        self.assertEqual(self._profile_of(EXEMPLIFICATION_TEXT),
                         "descriptive")
        self.assertEqual(self._profile_of(ADDITION_TEXT), "descriptive")

    # ========== Profile boundary thresholds ==========

    def test_boundary_density_exactly_narrative_max_is_not_narrative(self):
        """Density exactly 2.0 (1 connective / 50 sentences) fails the
        strict '<' narrative test; reasoning share is 100% but density
        2.0 < 5 blocks argumentative -> descriptive."""
        text = _ticks(49, "But it stopped.")
        discourse, profile = self._analyze(text)
        self.assertEqual(discourse["sentence_count"], 50)
        self.assertEqual(discourse["density_per_100_sentences"], 2.0)
        self.assertEqual(profile, "descriptive")

    def test_boundary_density_just_below_narrative_max(self):
        """1 connective / 51 sentences -> 1.96 < 2 -> narrative."""
        text = _ticks(50, "But it stopped.")
        discourse, profile = self._analyze(text)
        self.assertEqual(discourse["sentence_count"], 51)
        self.assertEqual(discourse["density_per_100_sentences"], 1.96)
        self.assertEqual(profile, "narrative")

    def test_boundary_density_exactly_argumentative_min(self):
        """Density exactly 5.0 (1 connective / 20 sentences) with a
        100% reasoning share meets the inclusive '>= 5' rule ->
        argumentative."""
        text = _ticks(19, "However it stopped.")
        discourse, profile = self._analyze(text)
        self.assertEqual(discourse["sentence_count"], 20)
        self.assertEqual(discourse["density_per_100_sentences"], 5.0)
        self.assertEqual(profile, "argumentative")

    def test_boundary_reasoning_share_exactly_sixty_percent(self):
        """6 reasoning connectives out of 10 total hit the inclusive
        60% share rule -> argumentative (covered by ARGUMENTATIVE_60,
        re-asserted with explicit numbers here)."""
        discourse, profile = self._analyze(ARGUMENTATIVE_60)
        self.assertEqual(discourse["contrast"] + discourse["cause"], 6)
        self.assertEqual(discourse["total"], 10)
        self.assertEqual(profile, "argumentative")

    def test_boundary_sequence_share_exactly_forty_percent(self):
        """4 sequence connectives out of 10 total hit the inclusive 40%
        share rule -> procedural."""
        discourse, profile = self._analyze(PROCEDURAL_40)
        self.assertEqual(discourse["sequence"], 4)
        self.assertEqual(discourse["total"], 10)
        self.assertEqual(profile, "procedural")

    def test_boundary_sequence_share_thirty_percent_is_descriptive(self):
        """3 sequence connectives out of 10 total miss the 40% rule ->
        descriptive."""
        discourse, profile = self._analyze(PROCEDURAL_30)
        self.assertEqual(discourse["sequence"], 3)
        self.assertEqual(profile, "descriptive")

    def test_argumentative_takes_precedence_over_procedural(self):
        """When reasoning share is 60% and sequence share is 40% at
        once, the documented evaluation order lets argumentative win."""
        discourse, profile = self._analyze(ARG_OVER_PROC)
        self.assertEqual(discourse["contrast"] + discourse["cause"], 6)
        self.assertEqual(discourse["sequence"], 4)
        self.assertEqual(discourse["total"], 10)
        self.assertEqual(profile, "argumentative")

    def test_thresholds_are_configurable(self):
        """Moving each knob flips a known fixture to a different
        profile, proving the thresholds actually drive classification."""
        # narrative ceiling high enough to swallow density 100.
        self.analyzer.narrative_max_density = 200.0
        self.assertEqual(self._profile_of(ARGUMENTATIVE_60), "narrative")

        # reasoning share bar above 60% falls through to descriptive.
        self.analyzer = DiscourseConnectiveAnalyzer()
        self.analyzer.argumentative_min_share = 0.9
        self.assertEqual(self._profile_of(ARGUMENTATIVE_60), "descriptive")

        # density bar above 100 blocks argumentative.
        self.analyzer = DiscourseConnectiveAnalyzer()
        self.analyzer.argumentative_min_density = 150.0
        self.assertEqual(self._profile_of(ARGUMENTATIVE_60), "descriptive")

        # sequence share bar above 62.5% blocks procedural.
        self.analyzer = DiscourseConnectiveAnalyzer()
        self.analyzer.procedural_min_share = 0.9
        self.assertEqual(self._profile_of(PROCEDURAL_TEXT), "descriptive")

    def test_zero_narrative_ceiling_with_no_connectives(self):
        """With narrative_max_density 0 a connective-free text (density
        0.0) is not narrative; the empty-tally guard classifies it
        descriptive instead of dividing by zero."""
        self.analyzer.narrative_max_density = 0.0
        discourse, profile = self._analyze(NARRATIVE_EN)
        self.assertEqual(discourse["total"], 0)
        self.assertEqual(profile, "descriptive")

    # ========== Dominant category ==========

    def test_dominant_is_highest_count_category(self):
        """The dominant label follows the highest count."""
        discourse, _ = self._analyze(PROCEDURAL_TEXT)
        self.assertEqual(discourse["sequence"], 5)
        self.assertEqual(discourse["dominant"], "sequence")

    def test_dominant_tie_broken_alphabetically(self):
        """A 3-3 cause/contrast tie resolves to 'cause'; a three-way
        addition/cause/concession tie resolves to 'addition'."""
        discourse, _ = self._analyze(ARGUMENTATIVE_60)
        self.assertEqual(discourse["cause"], discourse["contrast"])
        self.assertEqual(discourse["dominant"], "cause")

        discourse, _ = self._analyze(DOMINANT_TIE)
        self.assertEqual(discourse["addition"], 1)
        self.assertEqual(discourse["cause"], 1)
        self.assertEqual(discourse["concession"], 1)
        self.assertEqual(discourse["dominant"], "addition")

    # ========== Empty and blank documents ==========

    def test_empty_document_profile_is_none(self):
        """Empty, whitespace-only and punctuation-only texts have no
        word-bearing sentence: counts are zeroed, density 0.0, dominant
        None and the profile is None (documented choice: no discourse
        signal, no guessed label)."""
        for text in ("", "   ", "？！。"):
            discourse, profile = self._analyze(text)
            self.assertEqual(discourse["sentence_count"], 0)
            self.assertEqual(discourse["total"], 0)
            self.assertEqual(discourse["density_per_100_sentences"], 0.0)
            self.assertIsNone(discourse["dominant"])
            self.assertIsNone(profile, repr(text))

        # The None-text path is exercised directly on the core.
        discourse, profile = self.analyzer._analyze(None)
        self.assertEqual(discourse["sentence_count"], 0)
        self.assertIsNone(profile)

    def test_empty_batch_returns_empty_list(self):
        """An empty document list processes to an empty list."""
        self.assertEqual(
            self.analyzer.process_docs([], self.query), [])

    # ========== Sentence splitter (density denominator) ==========

    def test_splitter_abbreviation_and_initial_guards(self):
        """"Dr." and "Ms." do not split: two sentences, not four."""
        sentences = self.analyzer._sentences(
            "Dr. Smith arrived. Ms. Lee left.")
        self.assertEqual(len(sentences), 2)

    def test_splitter_decimal_and_ellipsis_guards(self):
        """A decimal dot never splits; an ellipsis splits once at its
        final dot; a terminal-free tail still counts as a sentence."""
        self.assertEqual(len(self.analyzer._sentences(
            "Pi is 3.14 exactly.")), 1)
        self.assertEqual(len(self.analyzer._sentences(
            "Wait... really? Yes.")), 3)
        self.assertEqual(len(self.analyzer._sentences(
            "no terminal here")), 1)
        self.assertEqual(self.analyzer._sentences("？！"), [])

    def test_splitter_cjk_terminals(self):
        """。！？ terminate CJK sentences exactly like . ! ?."""
        sentences = self.analyzer._sentences(ZH_PROCEDURAL)
        self.assertEqual(len(sentences), 6)

    # ========== Pipeline and metadata behavior ==========

    def test_all_documents_pass_through_in_order(self):
        """The analyzer is not a filter: every document survives, in
        order, with text and id untouched."""
        docs = [_doc(NARRATIVE_EN), _doc(PROCEDURAL_TEXT),
                _doc(ARGUMENTATIVE_60)]
        ids = [d.id for d in docs]
        result = self.analyzer.process_docs(docs, self.query)
        self.assertEqual(len(result), 3)
        self.assertEqual([d.id for d in result], ids)
        self.assertEqual(result[1].text, PROCEDURAL_TEXT)

    def test_metadata_recorded_for_each_document(self):
        """Each document gains the counts dict and the profile label
        under the default keys."""
        doc = _doc(PROCEDURAL_TEXT)
        result = self.analyzer.process_docs([doc], self.query)
        discourse = result[0].metadata["discourse"]
        self.assertEqual(sorted(discourse), sorted({
            "sentence_count", "addition", "cause", "concession",
            "contrast", "exemplification", "sequence", "total",
            "density_per_100_sentences", "dominant"}))
        self.assertEqual(discourse["dominant"], "sequence")
        self.assertEqual(result[0].metadata["discourse_profile"],
                         "procedural")

    def test_pre_existing_metadata_preserved_and_copy_on_write(self):
        """Pre-existing metadata entries survive; stamping writes
        through a copied mapping, so the caller's original dict never
        gains keys in place."""
        doc = _doc(ARGUMENTATIVE_60, source="journal", rank=7)
        meta_ref = doc.metadata
        result = self.analyzer.process_docs([doc], self.query)
        self.assertEqual(result[0].metadata["source"], "journal")
        self.assertEqual(result[0].metadata["rank"], 7)
        self.assertIn("discourse", result[0].metadata)
        self.assertIn("discourse_profile", result[0].metadata)
        self.assertNotIn("discourse", meta_ref)
        self.assertNotIn("discourse_profile", meta_ref)
        self.assertIsNot(result[0].metadata, meta_ref)

    def test_custom_metadata_keys(self):
        """discourse_key / profile_key relocate the stamps."""
        self.analyzer.discourse_key = "rhetoric"
        self.analyzer.profile_key = "rhetoric_profile"
        doc = _doc(NARRATIVE_EN)
        result = self.analyzer.process_docs([doc], self.query)
        self.assertNotIn("discourse", result[0].metadata)
        self.assertIn("rhetoric", result[0].metadata)
        self.assertEqual(result[0].metadata["rhetoric_profile"],
                         "narrative")

    def test_empty_keys_disable_stamps(self):
        """Empty key values disable the corresponding stamps entirely."""
        self.analyzer.discourse_key = ""
        self.analyzer.profile_key = ""
        doc = _doc(ARGUMENTATIVE_60, source="journal")
        meta_ref = doc.metadata
        result = self.analyzer.process_docs([doc], self.query)
        self.assertEqual(result[0].metadata, {"source": "journal"})
        self.assertEqual(meta_ref, {"source": "journal"})

    # ========== Determinism ==========

    def test_deterministic_across_instances_and_runs(self):
        """Same text, same metadata: across instances and repeated
        runs — the analysis has no randomness or order dependence."""
        first = DiscourseConnectiveAnalyzer()
        second = DiscourseConnectiveAnalyzer()
        for text in (ARGUMENTATIVE_60, PROCEDURAL_TEXT, CONCESSION_TEXT,
                     ZH_ARGUMENTATIVE, NARRATIVE_ZH, ARITH_7_3):
            one = first._analyze(text)
            self.assertEqual(one, second._analyze(text), text[:20])
            self.assertEqual(one, first._analyze(text), text[:20])

        doc_a = _doc(MIXED_CAUSE)
        doc_b = _doc(MIXED_CAUSE)
        out_a = first.process_docs([doc_a], self.query)
        out_b = second.process_docs([doc_b], self.query)
        self.assertEqual(out_a[0].metadata, out_b[0].metadata)

    def test_mixed_batch_profiles(self):
        """A batch of different registers yields one label per document
        without cross-talk."""
        docs = [_doc(NARRATIVE_EN), _doc(ARGUMENTATIVE_60),
                _doc(PROCEDURAL_TEXT), _doc(DESCRIPTIVE_50), _doc("")]
        result = self.analyzer.process_docs(docs, self.query)
        self.assertEqual([d.metadata["discourse_profile"] for d in result],
                         ["narrative", "argumentative", "procedural",
                          "descriptive", None])


if __name__ == '__main__':
    unittest.main()
