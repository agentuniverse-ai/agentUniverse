"""Unit tests for XmlCanonTool canonicalization, comparison, and explain modes.

The canonicalization results are byte-verified against lxml's C14N
implementation (`etree.tostring(method="c14n")`, C14N 1.0 and the exclusive
variant) on a 400-document seeded corpus, on hand-embedded W3C spec examples,
on 200 semantically-equal cosmetic pairs, and on 100 semantically-mutated
pairs. lxml is a test-only oracle; the tool itself is standard-library only.
"""

import io
import os
import random
import re
import time
import unittest

from agentuniverse.agent.action.tool.common_tool import xml_canon_tool as canon_module
from agentuniverse.agent.action.tool.common_tool.xml_canon_tool import XmlCanonTool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.configer import Configer

try:
    from lxml import etree as lxml_etree

    LXML_AVAILABLE = True
except ImportError:  # pragma: no cover - lxml is the pinned test oracle
    LXML_AVAILABLE = False

YAML_PATH = os.path.join(os.path.dirname(canon_module.__file__), "xml_canon_tool.yaml")

CORPUS_SIZE = 400
EQUAL_PAIRS = 200
MUTATED_PAIRS = 100

URIS = ["http://example.com/ns/alpha", "http://example.com/ns/beta", "urn:example:gamma", "tag:example.com,2026:delta"]
PREFIXES = ["p", "q", "r"]
WORDS = ["catalog", "section", "item", "price", "label", "note", "guide", "index"]
UNICODE_TEXTS = ["plain text", "日本語のテキスト", "emoji \U0001f600 tail", "mixed caf\u00e9 text", "a > b"]
TEXT_POOL = [*UNICODE_TEXTS, "x < y && z", "marks: \"quoted\" & 'single'", "raw <tag> body"]


def lxml_c14n(xml_text, **kwargs):
    """Oracle: lxml C14N 1.0 (tool kwargs translated to lxml's option names)."""
    lxml_kwargs = dict(kwargs)
    if "variant" in lxml_kwargs:
        variant = lxml_kwargs.pop("variant")
        lxml_kwargs["exclusive"] = variant == "exclusive"
    if "inclusive_prefixes" in lxml_kwargs:
        lxml_kwargs["inclusive_ns_prefixes"] = lxml_kwargs.pop("inclusive_prefixes")
    tree = lxml_etree.parse(io.BytesIO(xml_text.encode("utf-8")))
    return lxml_etree.tostring(tree, method="c14n", with_comments=False, **lxml_kwargs).decode("utf-8")


def _encode_chars(value, rng, attribute):
    """Encode a string with randomly chosen equivalent references.

    The encodings are interchangeable: they parse to the same characters, so
    two serializations of one logical tree stay canonically equal. Whitespace
    inside attribute values is always a character reference so both sides
    survive attribute-value normalization identically.
    """
    out = []
    for char in value:
        options = {"&": ["&amp;"], "<": ["&lt;"], ">": ["&gt;"]}.get(char, [])
        if attribute:
            options = options or {'"': ["&quot;"], "'": ["&apos;", "&#39;"], "\t": ["&#x9;"], "\n": ["&#xA;"]}.get(
                char, []
            )
        if options:
            out.append(rng.choice(options))
        elif ord(char) > 32 and rng.random() < 0.3:
            out.append(rng.choice([f"&#{ord(char)};", f"&#x{ord(char):x};"]))
        else:
            out.append(char)
    return "".join(out)


def _attr_value(rng):
    return rng.choice(
        [
            "1",
            "value",
            "x>y",
            "it's",
            'say "hi"',
            "café",
            "日本語",
            "tab\tinside",
            "line\ninside",
            "a&amp;b",
            "lead  pad",
        ]
    )


class _Node:
    """One generated element; cosmetic serialization choices stay external."""

    def __init__(self, rng, prefixes, depth, under_default_ns):
        self.name = rng.choice(WORDS)
        self.prefix = rng.choice(prefixes) if prefixes and rng.random() < 0.7 else None
        self.in_default = under_default_ns and rng.random() < 0.5
        attr_names: list[str] = []
        while len(attr_names) < rng.randint(0, 4):
            candidate = rng.choice(WORDS) + rng.choice(["", "-id", "_v", "2", ".x"])
            if candidate not in attr_names:
                attr_names.append(candidate)
        self.attrs = [(name, _attr_value(rng)) for name in attr_names]
        self.text = rng.choice(TEXT_POOL + WORDS) if rng.random() < 0.6 else None
        self.children = []
        if depth > 0 and rng.random() < 0.8:
            self.children = [_Node(rng, prefixes, depth - 1, under_default_ns) for _ in range(rng.randint(1, 3))]
        # Gaps between children are text nodes, so they are fixed per tree.
        self.gaps = [rng.choice(["", "", "\n  ", " "]) for _ in self.children]
        # PIs are canonical-visible: their target and data are fixed per tree.
        self.pi = (
            rng.choice(
                [
                    ("render", "pass"),
                    ("render", 'questions=" "'),
                    ("audit", "step=1"),
                    ("audit", "tail?"),
                ]
            )
            if rng.random() < 0.15
            else None
        )

    @property
    def qname(self):
        return f"{self.prefix}:{self.name}" if self.prefix else self.name


def _serialize_node(node, rng):
    """Serialize a fixed logical tree applying cosmetic choices from rng."""
    parts = []
    if rng.random() < 0.2:
        parts.append(f"<!-- note {rng.choice(WORDS)} -->")
    attr_bits = []
    for attr_name, value in node.attrs:
        quote = rng.choice(['"', "'"])
        attr_bits.append(f"{attr_name}={quote}{_encode_chars(value, rng, attribute=True)}{quote}")
    separator = rng.choice([" ", "  ", "\n  "])
    opening = "<" + node.qname
    if attr_bits:
        opening += separator + separator.join(attr_bits)
    if not node.children and node.text is None and node.pi is None and rng.random() < 0.7:
        parts.append(opening + rng.choice(["/>", " />"]))
        return "".join(parts)
    parts.append(opening + ">")
    if node.text is not None:
        if "]]" not in node.text and rng.random() < 0.3:
            parts.append(f"<![CDATA[{node.text}]]>")
        else:
            parts.append(_encode_chars(node.text, rng, attribute=False))
    if node.pi is not None:
        target, data = node.pi
        parts.append(f"<?{target} {data}?>")
    for index, child in enumerate(node.children):
        parts.append(_serialize_node(child, rng))
        parts.append(node.gaps[index])
    parts.append(f"</{node.qname}>")
    return "".join(parts)


def _root_declarations(rng, chosen, use_default, unused):
    """Namespace declarations with distinct absolute URIs, in random order."""
    uris = rng.sample(URIS, len(chosen) + 1)
    decls = [f'xmlns:{prefix}="{uris[index]}"' for index, prefix in enumerate(chosen)]
    if use_default:
        decls.append(f'xmlns="{uris[-1]}"')
    if unused:
        decls.append('xmlns:unused="http://example.com/ns/unused"')
    rng.shuffle(decls)
    return decls


def _inject_root_declarations(body, root, decls):
    marker = "<" + root.qname
    position = body.index(marker) + len(marker)
    return body[:position] + " " + " ".join(decls) + body[position:]


def _generate_document(seed):
    """Build one seeded document exercising the supported input classes."""
    rng = random.Random(seed)  # noqa: S311 (seeded deterministic test data)
    chosen = rng.sample(PREFIXES, rng.randint(1, 3))
    use_default = rng.random() < 0.5
    root = _Node(rng, chosen, rng.randint(1, 4), under_default_ns=use_default)
    decls = _root_declarations(rng, chosen, use_default, unused=rng.random() < 0.4)
    body = _inject_root_declarations(_serialize_node(root, rng), root, decls)
    header = '<?xml version="1.0"?>\n' if rng.random() < 0.4 else ""
    pre_pi = (
        rng.choice(["", '<?xml-stylesheet href="http://example.com/x" type="text/xml"?>\n', "<?target data?>\n"])
        if rng.random() < 0.25
        else ""
    )
    post_pi = "\n<?after done?>" if rng.random() < 0.2 else ""
    return header + pre_pi + body + post_pi


def _pair_documents(seed):
    """Two cosmetically different serializations of one logical tree."""
    rng = random.Random(seed)  # noqa: S311 (seeded deterministic test data)
    chosen = rng.sample(PREFIXES, rng.randint(1, 2))
    use_default = rng.random() < 0.5
    root = _Node(rng, chosen, rng.randint(1, 3), under_default_ns=use_default)
    # Namespace URIs are semantic: assign them once per tree.
    fixed_decls = _root_declarations(rng, chosen, use_default, unused=False)
    documents = []
    for variant_seed in (seed * 7 + 1, seed * 7 + 2):
        serializer = random.Random(variant_seed)  # noqa: S311 (seeded deterministic test data)
        decls = list(fixed_decls)
        serializer.shuffle(decls)
        documents.append(_inject_root_declarations(_serialize_node(root, serializer), root, decls))
    return documents[0], documents[1]


def _tag_end_outside_quotes(text, start):
    """Index of the '>' closing the tag opened at start, honoring quotes."""
    quote = None
    index = start
    while index < len(text):
        char = text[index]
        if quote is not None:
            if char == quote:
                quote = None
        elif char in "\"'":
            quote = char
        elif char == ">":
            return index
        index += 1
    return len(text) - 1


def _mutate_document(seed):
    """Build a base document and a c14n10-guaranteed-different counterpart."""
    rng = random.Random(seed)  # noqa: S311 (seeded deterministic test data)
    base = _generate_document(seed)
    kind = rng.choice(["attr", "element", "uri", "rename"])

    def append_attribute(document):
        first_tag = re.search(r"<[A-Za-z]", document)
        position = _tag_end_outside_quotes(document, first_tag.start())
        if document[position - 1] == "/":  # keep self-closing roots well-formed
            position -= 1
        return document[:position] + ' extra="1"' + document[position:]

    if kind == "attr":  # append an attribute to the root start tag
        return base, append_attribute(base)
    if kind == "element" and "</" in base:  # insert a child before the root end tag
        position = base.rindex("</")
        return base, base[:position] + "<zeta/>" + base[position:]
    if kind == "uri":  # rewrite the first namespace URI to another absolute URI
        match = re.search(r'xmlns(?::\w+)?="([^"]+)"', base)
        return base, base[: match.start(1)] + "urn:example:mutated" + base[match.end(1) :]
    match = re.search(r"<([A-Za-z][\w.-]*)(?=[\s/>])", base)  # rename one element kind
    if match is None:  # every element is prefixed; fall back to the attr mutation
        return base, append_attribute(base)
    name = match.group(1)
    mutated = re.sub(rf"<{name}(?=[\s/>])", f"<{name}X", base)
    return base, mutated.replace(f"</{name}>", f"</{name}X>")


# ---------------------------------------------------------------------------
# Basic behavior (no lxml dependency)
# ---------------------------------------------------------------------------


class XmlCanonToolBasicTest(unittest.TestCase):
    """Unit tests for mode dispatch, errors, caps, and deterministic output."""

    def setUp(self):
        self.tool = XmlCanonTool()

    def test_canonicalize_output_shape(self):
        result = self.tool.execute(mode="canonicalize", xml_text='<r b="2" a="1"><c/></r>')
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["mode"], "canonicalize")
        self.assertEqual(result["variant"], "c14n10")
        self.assertEqual(result["canonical"], '<r a="1" b="2"><c></c></r>')
        self.assertEqual(result["canonical_length"], len(result["canonical"]))
        self.assertEqual(result["stats"]["elements"], 2)
        self.assertEqual(result["stats"]["attributes"], 2)

    def test_deterministic_output(self):
        document = _generate_document(11)
        self.assertEqual(
            self.tool.execute(mode="canonicalize", xml_text=document),
            self.tool.execute(mode="canonicalize", xml_text=document),
        )
        self.assertEqual(
            self.tool.execute(mode="canonicalize", xml_text=document, variant="exclusive"),
            self.tool.execute(mode="canonicalize", xml_text=document, variant="exclusive"),
        )

    def test_compare_demo_cosmetic_differences_erased(self):
        # Attribute order, inter-attribute whitespace, quote style, and
        # CDATA-versus-escaping are all erased by canonicalization.
        left = "<list a=\"1\" b='2'><item><![CDATA[x < y]]></item></list>"
        right = "<list b='2'\n     a=\"1\"><item>x &lt; y</item></list>"
        result = self.tool.execute(mode="compare", xml_text=left, xml_text_b=right)
        self.assertEqual(result["status"], "success")
        self.assertTrue(result["canonically_equal"])
        erased = {entry["type"] for entry in result["erased_differences"]}
        self.assertIn("quote_normalization", erased)
        self.assertIn("cdata_unescaping", erased)
        self.assertIn("entity_normalization", erased)
        self.assertNotIn("first_difference", result)

    def test_compare_reports_first_difference(self):
        result = self.tool.execute(mode="compare", xml_text='<r a="1"><c>t</c></r>', xml_text_b='<r a="2"><c>t</c></r>')
        self.assertFalse(result["canonically_equal"])
        difference = result["first_difference"]
        self.assertEqual(difference["offset"], 6)
        self.assertIn('a="1"', difference["context_a"])
        self.assertIn('a="2"', difference["context_b"])

    def test_compare_prefix_case(self):
        # A document-level PI makes one canonical form a strict prefix of the other.
        result = self.tool.execute(mode="compare", xml_text="<r>t</r>", xml_text_b="<r>t</r><?pi x?>")
        self.assertFalse(result["canonically_equal"])
        difference = result["first_difference"]
        self.assertEqual(difference["reason"], "one canonical form is a prefix of the other")
        self.assertEqual(difference["offset"], len("<r>t</r>"))
        self.assertIn("\n<?pi x?>", difference["context_b"])

    def test_explain_lists_applicable_transformations(self):
        document = "<r b='2' a='1'><!-- c --><c><![CDATA[x<y]]></c><e/></r>"
        result = self.tool.execute(mode="explain", xml_text=document)
        self.assertEqual(result["status"], "success")
        applicable = {entry["type"] for entry in result["applicable_transformations"] if entry["applicable"]}
        for name in (
            "attribute_reordering",
            "comment_removal",
            "cdata_unescaping",
            "empty_element_expansion",
            "quote_normalization",
        ):
            self.assertIn(name, applicable)
        self.assertEqual(len(result["applicable_transformations"]), 8)
        self.assertEqual(result["stats"]["elements"], 3)

    def test_transformation_log_bounded_examples(self):
        document = "<r a='1' b='2' c='3'>" + "".join(f"<e v='{index}'/>" for index in range(50)) + "</r>"
        result = self.tool.execute(mode="canonicalize", xml_text=document)
        self.assertLessEqual(len(result["transformations"]), 8)
        for entry in result["transformations"]:
            example = entry.get("example")
            if isinstance(example, dict):
                for snippet in example.values():
                    if isinstance(snippet, str):
                        self.assertLessEqual(len(snippet), self.tool.max_example_chars)

    def test_not_supported_dtd(self):
        for document in (
            "<!DOCTYPE r><r/>",
            "<!DOCTYPE r [<!ELEMENT r EMPTY>]><r/>",
            '<!DOCTYPE r SYSTEM "http://example.com/d"><r/>',
        ):
            result = self.tool.execute(mode="canonicalize", xml_text=document)
            self.assertEqual(result["status"], "error", document)
            self.assertEqual(result["error_type"], "not_supported")
            self.assertIn("DTD", result["error"])

    def test_not_supported_out_of_subset_inputs(self):
        cases = {
            "relative namespace URI": '<r xmlns:p="relative-uri"><p:c/></r>',
            "relative default URI": '<r xmlns="relative"/>',
            "empty prefixed URI": '<r xmlns:p=""><p:c/></r>',
            "xml prefix rebinding": '<r xmlns:xml="http://example.com/other"/>',
            "xmlns prefix redeclaration": '<r xmlns:xmlns="http://example.com/x"/>',
        }
        for label, document in cases.items():
            result = self.tool.execute(mode="canonicalize", xml_text=document)
            self.assertEqual(result["error_type"], "not_supported", label)

    def test_parse_errors(self):
        for document in ("<r", "<r><c></r>", "plain text", "<r/><r/>", "<r>&undefined;</r>", ""):
            result = self.tool.execute(mode="canonicalize", xml_text=document)
            self.assertEqual(result["status"], "error", document)
            self.assertIn(result["error_type"], {"parse_error", "validation_error"})

    def test_validation_errors(self):
        checks = [
            {"mode": "bogus"},
            {"mode": "canonicalize", "xml_text": "<r/>", "variant": "c14n20"},
            {"mode": "canonicalize", "xml_text": "<r/>", "inclusive_prefixes": ["p"]},
            {"mode": "compare", "xml_text": "<r/>"},
            {"mode": "canonicalize"},
        ]
        for kwargs in checks:
            result = self.tool.execute(**kwargs)
            self.assertEqual(result["status"], "error", kwargs)
            self.assertEqual(result["error_type"], "validation_error")

    def test_inclusive_prefixes_accepted_for_exclusive(self):
        result = self.tool.execute(
            mode="canonicalize", xml_text='<p:r xmlns:p="http://e/p"/>', variant="exclusive", inclusive_prefixes=["p"]
        )
        self.assertEqual(result["status"], "success")
        bad = self.tool.execute(mode="canonicalize", xml_text="<r/>", inclusive_prefixes=[3])
        self.assertEqual(bad["error_type"], "validation_error")

    def test_limit_caps(self):
        wide = "<r>" + "<i/>" * 50 + "</r>"
        self.assertEqual(
            XmlCanonTool(max_nodes=10).execute(mode="canonicalize", xml_text=wide)["error_type"], "limit_exceeded"
        )
        deep = "<a>" * 100 + "</a>" * 100
        self.assertEqual(
            XmlCanonTool(max_depth=50).execute(mode="canonicalize", xml_text=deep)["error_type"], "limit_exceeded"
        )
        self.assertEqual(
            XmlCanonTool(max_xml_chars=50).execute(mode="canonicalize", xml_text=wide * 5)["error_type"],
            "limit_exceeded",
        )

    def test_pathological_ten_thousand_elements_fast(self):
        document = "<r>" + '<item kind="book">text</item>' * 10_000 + "</r>"
        started = time.perf_counter()
        result = self.tool.execute(mode="canonicalize", xml_text=document)
        elapsed = time.perf_counter() - started
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["stats"]["elements"], 10_001)
        self.assertLess(elapsed, 2.0, f"10k elements took {elapsed:.2f}s")

    def test_pathological_one_megabyte_bounded(self):
        filler = '<item note="padding-text">' + "data " * 40 + "</item>"
        document = "<r>" + filler * (995_000 // len(filler)) + "</r>"
        self.assertGreater(len(document), 900_000)
        self.assertLess(len(document), 1_000_000)
        started = time.perf_counter()
        result = self.tool.execute(mode="canonicalize", xml_text=document)
        elapsed = time.perf_counter() - started
        self.assertEqual(result["status"], "success")
        self.assertGreater(result["canonical_length"], 900_000)
        self.assertLess(elapsed, 10.0)
        oversized = XmlCanonTool(max_xml_chars=len(document) - 1).execute(mode="canonicalize", xml_text=document)
        self.assertEqual(oversized["error_type"], "limit_exceeded")

    def test_runtime_is_stdlib_only(self):
        source = os.path.join(os.path.dirname(canon_module.__file__), "xml_canon_tool.py")
        with open(source, encoding="utf-8") as handle:
            self.assertNotIn("lxml", handle.read())


# ---------------------------------------------------------------------------
# W3C C14N 1.0 spec examples (adapted: DTD-free, comments dropped)
# ---------------------------------------------------------------------------

W3C_EXAMPLES = [
    # Spec section 3.1 adapted: the DTD-supplied attribute default is explicit.
    (
        '<?xml version="1.0"?>\n'
        '<?xml-stylesheet href="http://www.w3.org/TR/WD-xsl" type="text/xml"?>\n'
        "<doc>\n"
        '  <e xml:space="preserve"></e>\n'
        '  <?fury questions=" "?>\n'
        "</doc>\n"
        "<?pi-without-data?>",
        '<?xml-stylesheet href="http://www.w3.org/TR/WD-xsl" type="text/xml"?>\n'
        "<doc>\n"
        '  <e xml:space="preserve"></e>\n'
        '  <?fury questions=" "?>\n'
        "</doc>\n"
        "<?pi-without-data?>",
    ),
    # Spec section 3.2 adapted: whitespace in and around text is preserved verbatim.
    (
        "<doc>\n"
        "   <clean>   </clean>\n"
        "   <dirty>   A   B   </dirty>\n"
        "   <mixed>\n"
        "      A\n"
        "      <clean>   </clean>\n"
        "      B\n"
        "      <dirty>   A   B   </dirty>\n"
        "   </mixed>\n"
        "</doc>",
        "<doc>\n"
        "   <clean>   </clean>\n"
        "   <dirty>   A   B   </dirty>\n"
        "   <mixed>\n"
        "      A\n"
        "      <clean>   </clean>\n"
        "      B\n"
        "      <dirty>   A   B   </dirty>\n"
        "   </mixed>\n"
        "</doc>",
    ),
    # Spec section 3.3 adapted: character references survive attribute-value
    # normalization; a literal newline becomes a space.
    (
        '<doc attr="   x\ny   &#xD;&#xA;&#x9;  "/>',
        '<doc attr="   x y   &#xD;&#xA;&#x9;  "></doc>',
    ),
    # Spec section 3.4 adapted: CDATA becomes escaped text.
    ("<doc><![CDATA[x <y z> & w]]></doc>", "<doc>x &lt;y z&gt; &amp; w</doc>"),
    # Sections 3.5-3.6 adapted DTD-free: references resolve to characters.
    ("<doc>&#65;&#x42;&amp;&lt;&gt;&quot;&apos;</doc>", "<doc>AB&amp;&lt;&gt;\"'</doc>"),
]

EXCLUSIVE_EXAMPLES = [
    # Exclusive C14N spec section 4.3: only visibly utilized prefixes remain.
    (
        '<n1:elem1 xmlns:n1="http://b" xmlns:n2="http://x" xmlns:n3="http://c">'
        '<n2:elem2 xmlns:n2="http://a"><n3:elem3/></n2:elem2></n1:elem1>',
        '<n1:elem1 xmlns:n1="http://b">'
        '<n2:elem2 xmlns:n2="http://a"><n3:elem3 xmlns:n3="http://c"></n3:elem3></n2:elem2></n1:elem1>',
    ),
    # Nested same-prefix bindings render once; changed bindings re-render.
    (
        '<n:a xmlns:n="http://u1"><n:b xmlns:n="http://u2"/></n:a>',
        '<n:a xmlns:n="http://u1"><n:b xmlns:n="http://u2"></n:b></n:a>',
    ),
    # Default namespace undeclaration is materialized in both variants.
    ('<x xmlns="http://u"><y xmlns=""/></x>', '<x xmlns="http://u"><y xmlns=""></y></x>'),
]

INCLUSIVE_PREFIX_EXAMPLES = [
    (
        '<n1:elem1 xmlns:n1="http://b" xmlns:n2="http://x" xmlns:n3="http://c">'
        '<n2:elem2 xmlns:n2="http://a"><n3:elem3/></n2:elem2></n1:elem1>',
        ["n3"],
        '<n1:elem1 xmlns:n1="http://b" xmlns:n3="http://c">'
        '<n2:elem2 xmlns:n2="http://a"><n3:elem3></n3:elem3></n2:elem2></n1:elem1>',
    ),
    (
        '<r xmlns="http://d" xmlns:a="http://a"><a:c/></r>',
        ["a"],
        '<r xmlns="http://d" xmlns:a="http://a"><a:c></a:c></r>',
    ),
    (
        '<r xmlns="http://d" xmlns:a="http://a"><a:c/></r>',
        ["#default"],
        '<r xmlns="http://d"><a:c xmlns:a="http://a"></a:c></r>',
    ),
]


@unittest.skipUnless(LXML_AVAILABLE, "lxml is required as the canonicalization test oracle")
class XmlCanonToolOracleTest(unittest.TestCase):
    """Byte-equality tests against lxml C14N on seeded corpora and spec examples."""

    def setUp(self):
        self.tool = XmlCanonTool()

    def assert_matches_lxml(self, document, **kwargs):
        ours = self.tool.execute(mode="canonicalize", xml_text=document, **kwargs)
        self.assertEqual(ours["status"], "success", f"input: {document!r} error: {ours.get('error')}")
        expected = lxml_c14n(document, **kwargs)
        self.assertEqual(ours["canonical"], expected, f"input: {document!r}")
        return ours

    def test_seeded_corpus_both_variants(self):
        """400 seeded documents must byte-match lxml in C14N 1.0 and exclusive."""
        for seed in range(CORPUS_SIZE):
            with self.subTest(seed=seed):
                document = _generate_document(seed)
                self.assert_matches_lxml(document)
                self.assert_matches_lxml(document, variant="exclusive")

    def test_w3c_spec_examples(self):
        """Hand-embedded W3C C14N 1.0 spec examples match their canonical form."""
        for document, expected in W3C_EXAMPLES:
            with self.subTest(document=document[:40]):
                ours = self.assert_matches_lxml(document)
                self.assertEqual(ours["canonical"], expected)

    def test_exclusive_spec_examples(self):
        """Exclusive C14N spec examples match their canonical form."""
        for document, expected in EXCLUSIVE_EXAMPLES:
            with self.subTest(document=document[:40]):
                ours = self.assert_matches_lxml(document, variant="exclusive")
                self.assertEqual(ours["canonical"], expected)

    def test_inclusive_prefixes_behavior(self):
        """inclusive_prefixes (including #default) matches lxml byte for byte."""
        for document, prefixes, expected in INCLUSIVE_PREFIX_EXAMPLES:
            with self.subTest(prefixes=prefixes):
                ours = self.assert_matches_lxml(document, variant="exclusive", inclusive_prefixes=prefixes)
                self.assertEqual(ours["canonical"], expected)

    def test_seeded_corpus_inclusive_prefixes(self):
        """Randomized inclusive prefix lists also byte-match lxml.

        The "#default" token is excluded here: libxml2 (lxml) ignores it while
        the W3C Exclusive C14N specification defines it as the default
        namespace; the tool implements the specification and pins the
        divergence in test_inclusive_prefixes_default_token_spec_behavior.
        """
        for seed in range(60):
            rng = random.Random(9_000 + seed)  # noqa: S311 (seeded deterministic test data)
            document = _generate_document(5_000 + seed)
            prefixes = rng.sample(["p", "q", "r", "unused", "missing"], rng.randint(0, 3))
            with self.subTest(seed=seed, prefixes=prefixes):
                self.assert_matches_lxml(document, variant="exclusive", inclusive_prefixes=prefixes or None)

    def test_inclusive_prefixes_default_token_spec_behavior(self):
        """The spec-defined #default token pulls the default namespace in.

        lxml/libxml2 ignores "#default" (it renders `<k:r xmlns:k=.../>`
        only), which is why the seeded corpus above omits the token; the tool
        follows the W3C Exclusive C14N specification instead.
        """
        document = '<k:r xmlns="http://u" xmlns:k="http://k"><k:c/></k:r>'
        result = self.tool.execute(
            mode="canonicalize", xml_text=document, variant="exclusive", inclusive_prefixes=["#default"]
        )
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["canonical"], '<k:r xmlns="http://u" xmlns:k="http://k"><k:c></k:c></k:r>')
        without = self.tool.execute(mode="canonicalize", xml_text=document, variant="exclusive")
        self.assertEqual(without["canonical"], '<k:r xmlns:k="http://k"><k:c></k:c></k:r>')

    def test_compare_equal_pairs(self):
        """200 seeded cosmetic pairs must always compare canonically equal."""
        for seed in range(EQUAL_PAIRS):
            with self.subTest(seed=seed):
                left, right = _pair_documents(3_000 + seed)
                result = self.tool.execute(mode="compare", xml_text=left, xml_text_b=right)
                self.assertEqual(
                    result["status"], "success", f"left={left!r} right={right!r} error={result.get('error')}"
                )
                self.assertTrue(result["canonically_equal"], f"left={left!r} right={right!r}")

    def test_compare_equal_pairs_exclusive(self):
        """The same pairs stay equal under the exclusive variant."""
        for seed in range(40):
            left, right = _pair_documents(3_500 + seed)
            result = self.tool.execute(mode="compare", xml_text=left, xml_text_b=right, variant="exclusive")
            self.assertTrue(result["canonically_equal"], f"left={left!r} right={right!r}")

    def test_compare_mutated_pairs(self):
        """100 mutated pairs must be unequal with the correct first difference."""
        for seed in range(MUTATED_PAIRS):
            with self.subTest(seed=seed):
                left, right = _mutate_document(4_000 + seed)
                result = self.tool.execute(mode="compare", xml_text=left, xml_text_b=right)
                self.assertEqual(result["status"], "success", f"left={left!r} right={right!r}")
                self.assertFalse(result["canonically_equal"], f"left={left!r} right={right!r}")
                expected_left = lxml_c14n(left)
                expected_right = lxml_c14n(right)
                offset = next(
                    (
                        index
                        for index in range(min(len(expected_left), len(expected_right)))
                        if expected_left[index] != expected_right[index]
                    ),
                    min(len(expected_left), len(expected_right)),
                )
                self.assertEqual(result["first_difference"]["offset"], offset)
                self.assertEqual(result["canonical_a_length"], len(expected_left))
                self.assertEqual(result["canonical_b_length"], len(expected_right))

    def test_corpus_documents_are_diverse(self):
        """Guard: the corpus generator must not collapse to identical inputs."""
        canonicals = {
            self.tool.execute(mode="canonicalize", xml_text=_generate_document(seed))["canonical"]
            for seed in range(CORPUS_SIZE)
        }
        self.assertGreater(len(canonicals), 100)


class XmlCanonRegistrationTest(unittest.TestCase):
    """Unit tests for registering the shipped xml_canon_tool.yaml as a tool component."""

    def setUp(self):
        self.config = Configer(path=os.path.abspath(YAML_PATH)).load()
        try:
            self.previous = ApplicationConfigManager().app_configer
        except ValueError:
            self.previous = None

    def tearDown(self):
        ApplicationConfigManager().app_configer = self.previous

    def test_schema(self):
        component = ComponentConfiger().load_by_configer(self.config)
        self.assertEqual(component.get_component_config_type(), ComponentEnum.TOOL.value)
        self.assertEqual(component.metadata_class, "XmlCanonTool")

    def test_manager(self):
        configer = ToolConfiger().load_by_configer(self.config)
        app = AppConfiger()
        app.tool_configer_map = {configer.name: configer}
        ApplicationConfigManager().app_configer = app
        tool = ToolManager().get_instance_obj(configer.name)
        self.assertIsInstance(tool, XmlCanonTool)
        self.assertEqual(tool.input_keys, ["mode", "xml_text"])
        self.assertEqual(tool.max_xml_chars, 1_000_000)


if __name__ == "__main__":
    unittest.main()
