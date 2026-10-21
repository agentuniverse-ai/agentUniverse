"""Tests for HtmlAuditTool: unit coverage, OWASP vector corpus, and
parse oracles (lxml.html census/text parity with stdlib reference
fallback) plus hand-verified line-number accuracy."""

import json
import os
import random
import re
import unittest
from collections import Counter
from html.parser import HTMLParser

from agentuniverse.agent.action.tool.common_tool import html_audit_tool as html_audit_module
from agentuniverse.agent.action.tool.common_tool.html_audit_tool import HtmlAuditTool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.configer import Configer

try:
    import lxml.html as lxml_html
    HAVE_LXML = True
except ImportError:  # pragma: no cover - oracle availability guard
    HAVE_LXML = False

YAML_PATH = os.path.join(os.path.dirname(html_audit_module.__file__), "html_audit_tool.yaml")


def codes_of(result):
    """Return the multiset of finding codes in an audit result."""
    return [f["code"] for f in result["findings"]]


def codeset(result):
    """Return the set of finding codes in an audit result."""
    return {f["code"] for f in result["findings"]}


def finding_tuples(result, codes):
    """Return {(line, code)} for findings whose code is in ``codes``."""
    return {(f["line"], f["code"]) for f in result["findings"] if f["code"] in codes}


class _ReferenceCensusParser(HTMLParser):
    """Independent minimal html.parser census (second oracle where lxml
    applies different error recovery than the stdlib tokenizer)."""

    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.tags = Counter()
        self.attrs = Counter()

    def handle_starttag(self, tag, attrs):
        self._count(tag, attrs)

    def handle_startendtag(self, tag, attrs):
        self._count(tag, attrs)

    def _count(self, tag, attrs):
        self.tags[tag] += 1
        seen = set()
        for name, _value in attrs:
            if name in seen:
                continue
            seen.add(name)
            self.attrs[name] += 1


def reference_census(fragment):
    parser = _ReferenceCensusParser()
    parser.feed(fragment)
    parser.close()
    return dict(parser.tags), dict(parser.attrs)


def lxml_census(fragment):
    root = lxml_html.fragment_fromstring(fragment, create_parent=True)
    tags = Counter()
    attrs = Counter()
    for element in root.iter():
        if element is root or not isinstance(element.tag, str):
            continue
        tags[element.tag] += 1
        for name in element.attrib:
            attrs[name] += 1
    return dict(tags), dict(attrs)


def normalize_ws(text):
    return re.sub(r"\s+", " ", text).strip()


def lxml_visible_text(fragment):
    root = lxml_html.fragment_fromstring(fragment, create_parent=True)
    for element in root.iter("script", "style"):
        element.drop_tree()
    return normalize_ws(root.text_content())


# ---------------------------------------------------------------------------
# Fragment generators (seeded, deterministic).
# ---------------------------------------------------------------------------

_WORDS = ["alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta"]
_SAFE_URLS = [
    "https://example.test/a?b=1", "http://example.test/b", "/relative/path",
    "#fragment", "mailto:user@example.test", "tel:+15551234",
    "data:image/png;base64,iVBORw0KGgo=", "ftp://files.example.test/x",
]
_SAFE_ENTITIES = [
    "&amp;", "&lt;", "&gt;", "&quot;", "&apos;", "&copy;", "&nbsp;",
    "&#58;", "&#x3a;", "&colon;", "&Tab;", "&NewLine;", "&hellip;",
]


class FragmentGenerator:
    """Seeded generator of HTML fragments for oracle parity corpora."""

    def __init__(self, seed):
        self.rng = random.Random(seed)

    def word(self):
        return self.rng.choice(_WORDS)

    def text(self):
        parts = [self.word() for _ in range(self.rng.randint(1, 4))]
        if self.rng.random() < 0.4:
            parts.insert(self.rng.randint(0, len(parts)), self.rng.choice(_SAFE_ENTITIES))
        return " ".join(parts)

    def _quote(self, value):
        if self.rng.random() < 0.5:
            return f'"{value}"'
        if "'" not in value:
            return f"'{value}'"
        return f'"{value}"'

    def _attr_string(self, attrs, case_flip=False, extra_space=False):
        if not attrs:
            return ""
        chunks = []
        for name, value in attrs:
            if value is None:
                chunks.append(name)
            else:
                chunks.append(f"{name}={self._quote(value)}")
        joiner = "  " if extra_space else " "
        rendered = joiner.join(chunks)
        return " " + rendered

    def _tag(self, name, attrs=None, inner="", self_close=False,
             case_flip=False, extra_space=False):
        attrs = attrs or []
        tag_name = name.upper() if case_flip and self.rng.random() < 0.5 else name
        attr_part = self._attr_string(attrs, extra_space=extra_space)
        if self_close:
            return f"<{tag_name}{attr_part}/>"
        return f"<{tag_name}{attr_part}>{inner}</{name}>"

    def inline(self, depth=0):
        choice = self.rng.random()
        if choice < 0.3:
            return self._tag("b", inner=self.text())
        if choice < 0.5:
            return self._tag("i", inner=self.text())
        if choice < 0.6:
            return self._tag("em", inner=self.text() if self.rng.random() < 0.7 else self.text() + " " + self._tag("strong", inner=self.word()))
        if choice < 0.75:
            return self._tag("span", attrs=[("class", self.word()), ("title", self.text())], inner=self.text())
        if choice < 0.9 and depth < 3:
            return self._tag("a", attrs=[("href", self.rng.choice(_SAFE_URLS[:5])), ("title", self.word())],
                             inner=self.inline(depth + 1))
        return self.text()

    def block(self, depth=0):
        choice = self.rng.random()
        if choice < 0.25:
            inner = " ".join(self.inline(depth + 1) for _ in range(self.rng.randint(1, 3)))
            return self._tag("p", inner=inner)
        if choice < 0.45:
            inner = "".join(f"<li>{self.inline(depth + 1)}</li>" for _ in range(self.rng.randint(1, 3)))
            return self._tag("ul", inner=inner)
        if choice < 0.6 and depth < 3:
            cells = "".join(f"<td>{self.text()}</td>" for _ in range(self.rng.randint(1, 3)))
            row = f"<tr>{cells}</tr>"
            return self._tag("table", attrs=[("class", "data")], inner=row)
        if choice < 0.75 and depth < 3:
            inner = self.block(depth + 1)
            return self._tag("div", attrs=[("class", self.word()), ("id", self.word())], inner=inner)
        if choice < 0.85:
            attrs = [("src", self.rng.choice(_SAFE_URLS[:4])), ("alt", self.text())]
            return self._tag("img", attrs=attrs, self_close=True)
        if choice < 0.95:
            heading = self._tag(f"h{self.rng.randint(1, 3)}", inner=self.text())
            return heading + self._tag("br", self_close=True)
        fields = [
            self._tag("label", inner=self.word()),
            self._tag("input", attrs=[("type", "text"), ("name", self.word()), ("value", self.word())], self_close=True),
            self._tag("button", attrs=[("type", "submit")], inner=self.word()),
        ]
        return self._tag("form", attrs=[("action", "/submit"), ("method", "post")], inner="".join(fields))

    def fragment(self):
        parts = []
        for _ in range(self.rng.randint(1, 4)):
            parts.append(self.block())
            if self.rng.random() < 0.3:
                parts.append(self.inline())
            if self.rng.random() < 0.2:
                parts.append(f"<!-- note {self.word()} -->")
        return "".join(parts)

    def mutate_benign(self, fragment):
        """Apply parser-transparent mutations (newlines, case, spacing)."""
        mutated = fragment
        if self.rng.random() < 0.7:
            mutated = mutated.replace(">", ">\n", self.rng.randint(1, 3))
        if self.rng.random() < 0.4:
            mutated = mutated.replace("<", "\n<", 1)
        if self.rng.random() < 0.5:
            mutated = re.sub(r"<([a-z]+)", lambda m: f"<{m.group(1).upper()}", mutated)
        if self.rng.random() < 0.3:
            mutated = mutated.replace(" ", "  ", 2)
        return mutated

    def mutate_malformed(self, fragment):
        """Apply one recovery-sensitive mutation."""
        choice = self.rng.randint(0, 5)
        if choice == 0:  # drop the final close tag
            match = list(re.finditer(r"</[a-zA-Z][a-zA-Z0-9-]*>", fragment))
            if match:
                span = match[-1]
                return fragment[:span.start()] + fragment[span.end():]
            return fragment + "tail"
        if choice == 1:  # stray end tag
            return fragment + "</span>"
        if choice == 2:  # doubled angle bracket
            return fragment.replace("<p>", "<<p>", 1) if "<p>" in fragment else fragment.replace("<", "<<", 1)
        if choice == 3:  # chop the trailing '>'
            return fragment[:-1]
        if choice == 4:  # markup-like text inside an attribute value
            return fragment.replace("<p>", '<p title="a<b c">', 1)
        return fragment + "<div class=\"tail"  # unterminated tag at EOF


def tool_census(fragment):
    result = HtmlAuditTool().execute(fragment, mode="stats")
    assert result["status"] == "success", result
    return dict(result["tag_histogram"]), dict(result["attr_histogram"])


# ---------------------------------------------------------------------------
# Audit mode unit tests.
# ---------------------------------------------------------------------------

class AuditModeTest(unittest.TestCase):
    """Unit tests for HtmlAuditTool audit-mode detection rules."""

    def setUp(self):
        self.tool = HtmlAuditTool()

    def audit(self, html):
        result = self.tool.execute(html, mode="audit")
        self.assertEqual(result["status"], "success", result)
        return result

    def test_dangerous_tags_with_reasoning(self):
        cases = {
            "script": "<script src='a.js'></script>",
            "iframe": "<iframe src='a'></iframe>",
            "object": "<object data='a'></object>",
            "embed": "<embed src='a'>",
            "base": "<base href='https://x/'>",
            "svg": "<svg></svg>",
            "math": "<math></math>",
            "form": "<form action='/x'></form>",
            "input": "<input name='q'>",
            "link": "<link rel='stylesheet' href='/a.css'>",
            "meta": "<meta name='a' content='b'>",
        }
        for tag, html in cases.items():
            with self.subTest(tag=tag):
                result = self.audit(html)
                matches = [f for f in result["findings"]
                           if f["code"] == "DANGEROUS_TAG" and f["element"] == tag]
                self.assertEqual(len(matches), 1, result["findings"])
                self.assertTrue(matches[0]["reason"])
                self.assertEqual(matches[0]["line"], 1)

    def test_event_handler_full_sweep(self):
        for handler in ["onclick", "onerror", "onload", "onmouseover",
                        "ontoggle", "onfocus", "onanimationstart", "onwebkitanimationend", "oncustom"]:
            html = f"<div {handler}='x()'>t</div>"
            with self.subTest(handler=handler):
                result = self.audit(html)
                self.assertIn("EVENT_HANDLER_ATTR", codeset(result))
                finding = next(f for f in result["findings"] if f["code"] == "EVENT_HANDLER_ATTR")
                self.assertEqual(finding["attr"], handler)
                self.assertEqual(finding["severity"], "high")

    def test_dangerous_schemes(self):
        for url, code in [
            ("javascript:alert(1)", "DANGEROUS_URL_SCHEME"),
            ("JAVASCRIPT:alert(1)", "DANGEROUS_URL_SCHEME"),
            ("vbscript:msgbox(1)", "DANGEROUS_URL_SCHEME"),
            ("data:text/html;base64,PHNjcmlwdD4=", "DANGEROUS_URL_SCHEME"),
            ("data:image/svg+xml;base64,PHN2Zz4=", "DANGEROUS_URL_SCHEME"),
            ("data:image/png;base64,iVBOR", "DATA_URI"),
        ]:
            with self.subTest(url=url):
                result = self.audit(f'<a href="{url}">x</a>')
                self.assertIn(code, codeset(result))

    def test_scheme_obfuscation_probing(self):
        vectors = [
            "jav\tascript:alert(1)",
            "jav&#x09;ascript:alert(1)",
            "jav&#x0A;ascript:alert(1)",
            "jav&#x0D;ascript:alert(1)",
            "java&Tab;script:alert(1)",
            "java&NewLine;script:alert(1)",
            "javascript&#58;alert(1)",
            "javascript&colon;alert(1)",
            "&#106;&#97;&#118;&#97;&#115;&#99;&#114;&#105;&#112;&#116;:alert(1)",
            "&#x6A;&#x61;&#x76;&#x61;&#x73;&#x63;&#x72;&#x69;&#x70;&#x74;:alert(1)",
            " &#14; javascript:alert(1)",
            "\x01javascript:alert(1)",
            "JaVaScRiPt:alert(1)",
            "javas<!-- -->cript:alert(1)",
            "`javascript:alert(1)",
            "j&#97;v&#97;script&#58;alert(1)",
            "jav&#x0D;&#x0A;ascript:alert(1)",
        ]
        for value in vectors:
            with self.subTest(value=value):
                result = self.audit(f'<a href="{value}">x</a>')
                self.assertIn("DANGEROUS_URL_SCHEME", codeset(result),
                              f"missed obfuscation: {value}")

    def test_url_attribute_coverage(self):
        attrs = ["href", "src", "action", "formaction", "data", "poster",
                 "background", "cite", "longdesc", "dynsrc", "lowsrc", "xlink:href"]
        for attr in attrs:
            with self.subTest(attr=attr):
                result = self.audit(f'<div {attr}="javascript:alert(1)">x</div>')
                self.assertIn("DANGEROUS_URL_SCHEME", codeset(result))

    def test_srcset_candidates_probed(self):
        result = self.audit('<img src="a.png" srcset="javascript:alert(1) 1x, b.png 2x">')
        self.assertIn("DANGEROUS_URL_SCHEME", codeset(result))

    def test_param_url_value_probed(self):
        result = self.audit('<object><param name="url" value="javascript:alert(1)"></object>')
        self.assertIn("DANGEROUS_URL_SCHEME", codeset(result))

    def test_srcdoc_nested_html(self):
        result = self.audit('<iframe srcdoc="&lt;p&gt;ok&lt;/p&gt;"></iframe>')
        codes = {f["code"]: f for f in result["findings"]}
        self.assertIn("SRCDOC_ATTR", codes)
        self.assertNotIn("SRCDOC_DANGEROUS_CONTENT", codes)
        result = self.audit('<iframe srcdoc="&lt;script&gt;alert(1)&lt;/script&gt;"></iframe>')
        codes = {f["code"]: f for f in result["findings"]}
        self.assertEqual(codes["SRCDOC_DANGEROUS_CONTENT"]["severity"], "high")

    def test_srcdoc_chain_bounded(self):
        inner = "&lt;iframe srcdoc=&amp;quot;&amp;lt;script&amp;gt;alert(2)&amp;lt;/script&amp;gt;&amp;quot;&gt;&lt;/iframe&gt;"
        result = self.audit(f'<iframe srcdoc="{inner}"></iframe>')
        self.assertIn("SRCDOC_DANGEROUS_CONTENT", codeset(result))

    def test_style_traps(self):
        result = self.audit("<div style=\"background:url(javascript:alert(1))\">x</div>")
        self.assertIn("STYLE_JS_URL", codeset(result))
        result = self.audit("<div style='width:expression(alert(1))'>x</div>")
        self.assertIn("STYLE_EXPRESSION", codeset(result))
        result = self.audit("<style>li{list-style-image:url('javascript:alert(1)')}</style>")
        self.assertIn("STYLE_JS_URL", codeset(result))
        result = self.audit("<style>div{width:expression(alert(1))}</style>")
        self.assertIn("STYLE_EXPRESSION", codeset(result))
        result = self.audit('<div style="color:red">x</div>')
        self.assertNotIn("STYLE_JS_URL", codeset(result))
        self.assertNotIn("STYLE_EXPRESSION", codeset(result))

    def test_css_comment_obfuscated_expression(self):
        result = self.audit('<xss style="xss:expr/*XSS*/ession(alert(1))">')
        self.assertIn("STYLE_EXPRESSION", codeset(result))

    def test_target_blank_without_rel(self):
        result = self.audit('<a href="https://x.test" target="_blank">x</a>')
        self.assertIn("TARGET_NO_REL", codeset(result))
        result = self.audit('<a href="https://x.test" target="_blank" rel="noopener">x</a>')
        self.assertNotIn("TARGET_NO_REL", codeset(result))
        result = self.audit('<a href="https://x.test" target="_blank" rel="noreferrer">x</a>')
        self.assertNotIn("TARGET_NO_REL", codeset(result))
        result = self.audit('<a href="https://x.test">x</a>')
        self.assertNotIn("TARGET_NO_REL", codeset(result))

    def test_hidden_autofocused_input(self):
        result = self.audit('<form><input type="hidden" autofocus name="s"></form>')
        finding = next(f for f in result["findings"] if f["code"] == "HIDDEN_AUTOFOCUS")
        self.assertEqual(finding["severity"], "medium")
        result = self.audit('<input type="text" autofocus>')
        self.assertNotIn("HIDDEN_AUTOFOCUS", codeset(result))

    def test_meta_refresh_and_charset(self):
        result = self.audit('<meta http-equiv="refresh" content="5">')
        self.assertIn("META_REFRESH", codeset(result))
        result = self.audit('<meta http-equiv="refresh" content="0;url=javascript:alert(1)">')
        codes = codeset(result)
        self.assertIn("META_REFRESH", codes)
        self.assertIn("DANGEROUS_URL_SCHEME", codes)
        result = self.audit('<meta charset="ISO-8859-1">')
        self.assertIn("META_CHARSET", codeset(result))
        result = self.audit('<meta http-equiv="Content-Type" content="text/html; charset=utf-16">')
        self.assertIn("META_CHARSET", codeset(result))
        result = self.audit('<meta charset="utf-8">')
        self.assertNotIn("META_CHARSET", codeset(result))

    def test_sanitizer_defeating_markers(self):
        self.assertIn("PLAINTEXT_ELEMENT", codeset(self.audit("<plaintext>")))
        self.assertIn("XMP_ELEMENT", codeset(self.audit("<xmp>")))

    def test_ie_conditional_comments(self):
        result = self.audit("<!--[if gte IE 4]><p>x</p><![endif]-->")
        self.assertIn("IE_CONDITIONAL_COMMENT", codeset(result))
        result = self.audit("<!-- ordinary note -->")
        self.assertNotIn("IE_CONDITIONAL_COMMENT", codeset(result))

    def test_embedded_html_in_attr(self):
        result = self.audit('<t:set to="XSS&lt;SCRIPT DEFER&gt;alert(1)&lt;/SCRIPT&gt;">')
        self.assertIn("EMBEDDED_HTML_IN_ATTR", codeset(result))
        result = self.audit('<span title="use <b> tags">t</span>')
        self.assertNotIn("EMBEDDED_HTML_IN_ATTR", codeset(result))

    def test_unterminated_tag_recovered_from_raw_source(self):
        result = self.audit('<img src="x.png">\n<img src="javascript:alert(1)"')
        matches = [f for f in result["findings"] if f["code"] == "DANGEROUS_URL_SCHEME"]
        self.assertEqual(matches[0]["line"], 2)
        result = self.audit('<iframe src="https://x.test" <')
        self.assertIn(("DANGEROUS_TAG", ), [(f["code"],) for f in result["findings"]])

    def test_cdata_smuggling_detected(self):
        result = self.audit('<xml><c><![CDATA[<IMG SRC="javas]]><![CDATA[cript:alert(1);">]]></c></xml>')
        self.assertIn("DANGEROUS_URL_SCHEME", codeset(result))

    def test_benign_fragment_has_no_findings(self):
        html = "<div class='a'><p>hello &amp; welcome</p><a href='https://x.test/1' rel='noopener'>link</a></div>"
        result = self.audit(html)
        self.assertEqual(result["findings"], [])
        self.assertEqual(result["finding_counts"]["total"], 0)

    def test_findings_sorted_and_counted(self):
        html = "<b>1</b>\n<script>a()</script>\n<a href='javascript:x(1)'>c</a>"
        result = self.audit(html)
        lines = [f["line"] for f in result["findings"]]
        self.assertEqual(lines, sorted(lines))
        counts = result["finding_counts"]
        self.assertEqual(counts["total"], len(result["findings"]))
        self.assertEqual(counts["high"], sum(1 for f in result["findings"] if f["severity"] == "high"))

    def test_evidence_truncated(self):
        long_value = "x" * 500
        result = self.audit(f'<a href="javascript:alert(1)" title="{long_value}">y</a>')
        for finding in result["findings"]:
            self.assertLessEqual(len(finding["evidence"]), self.tool.max_evidence_chars)

    def test_max_findings_cap(self):
        tool = HtmlAuditTool(max_findings=3)
        html = "".join(f"<script></script>" for _ in range(10))
        result = tool.execute(html, mode="audit")
        self.assertEqual(result["status"], "success")
        self.assertLessEqual(len(result["findings"]), 3)
        self.assertTrue(result["truncated"])
        self.assertEqual(result["finding_counts"]["total"], 10)


# ---------------------------------------------------------------------------
# OWASP XSS filter-evasion cheat-sheet corpus (hand-embedded vectors from
# the published cheat sheet; every vector must be flagged in-category).
# ---------------------------------------------------------------------------

OWASP_VECTORS = [
    ("<SCRIPT SRC=http://xss.rocks/xss.js></SCRIPT>", {"DANGEROUS_TAG"}),
    ("<IMG SRC=\"javascript:alert('XSS');\">", {"DANGEROUS_URL_SCHEME"}),
    ("<IMG SRC=javascript:alert('XSS')>", {"DANGEROUS_URL_SCHEME"}),
    ("<IMG SRC=JaVaScRiPt:alert('XSS')>", {"DANGEROUS_URL_SCHEME"}),
    ("<IMG SRC=javascript:alert(&quot;XSS&quot;)>", {"DANGEROUS_URL_SCHEME"}),
    ("<IMG SRC=`javascript:alert('RSnake says, ''XSS''')`>", {"DANGEROUS_URL_SCHEME"}),
    ("<IMG SRC=`javascript:alert('XSS')`>", {"DANGEROUS_URL_SCHEME"}),
    ('<a onmouseover="alert(document.cookie)">xxs link</a>', {"EVENT_HANDLER_ATTR"}),
    ("<a onmouseover=alert(document.cookie)>xxs link</a>", {"EVENT_HANDLER_ATTR"}),
    ('<IMG """><SCRIPT>alert("XSS")</SCRIPT>">', {"DANGEROUS_TAG"}),
    ('<IMG SRC=# onmouseover="alert(\'xxs\')">', {"EVENT_HANDLER_ATTR"}),
    ('<IMG SRC= onmouseover="alert(\'xxs\')">', {"EVENT_HANDLER_ATTR"}),
    ('<IMG onmouseover="alert(\'xxs\')">', {"EVENT_HANDLER_ATTR"}),
    ('<IMG SRC=/ onerror="alert(String.fromCharCode(88,83,83))"></img>', {"EVENT_HANDLER_ATTR"}),
    ('<img src=x onerror="&#0000106&#0000097&#0000118&#0000097&#0000115&#0000099&#0000114&#0000105&#0000112&#0000116&#0000058&#0000097&#0000108&#0000101&#0000114&#0000116&#0000040&#0000039&#0000088&#0000083&#0000083&#0000039&#0000041">', {"EVENT_HANDLER_ATTR"}),
    ("<IMG SRC=&#106;&#97;&#118;&#97;&#115;&#99;&#114;&#105;&#112;&#116;&#58;&#97;&#108;&#101;&#114;&#116;&#40;&#39;&#88;&#83;&#83;&#39;&#41;>", {"DANGEROUS_URL_SCHEME"}),
    ("<IMG SRC=&#x6A&#x61&#x76&#x61&#x73&#x63&#x72&#x69&#x70&#x74&#x3A&#x61&#x6C&#x65&#x72&#x74&#x28&#x27&#x58&#x53&#x53&#x27&#x29>", {"DANGEROUS_URL_SCHEME"}),
    ("<IMG SRC=\"jav\tascript:alert('XSS');\">", {"DANGEROUS_URL_SCHEME"}),
    ("<IMG SRC=\"jav&#x09;ascript:alert('XSS');\">", {"DANGEROUS_URL_SCHEME"}),
    ("<IMG SRC=\"jav&#x0A;ascript:alert('XSS');\">", {"DANGEROUS_URL_SCHEME"}),
    ("<IMG SRC=\"jav&#x0D;ascript:alert('XSS');\">", {"DANGEROUS_URL_SCHEME"}),
    ("<IMG SRC=\" &#14;  javascript:alert('XSS');\">", {"DANGEROUS_URL_SCHEME"}),
    ('<SCRIPT/XSS SRC="http://xss.rocks/xss.js"></SCRIPT>', {"DANGEROUS_TAG"}),
    ('<BODY onload!#$%&()*~+-_.,:;?@[/|\\]^`=alert("XSS")>', {"EVENT_HANDLER_ATTR"}),
    ("<SCRIPT SRC=http://xss.rocks/xss.js?< B >", {"DANGEROUS_TAG"}),
    ("<<SCRIPT>alert(\"XSS\");//\\<</SCRIPT>", {"DANGEROUS_TAG"}),
    ("<SCRIPT SRC=//xss.rocks/.j>", {"DANGEROUS_TAG"}),
    ('<IMG SRC="javascript:alert(\'XSS\')"', {"DANGEROUS_URL_SCHEME"}),
    ("<iframe src=http://xss.rocks/scriptlet.html <", {"DANGEROUS_TAG"}),
    ('<BODY BACKGROUND="javascript:alert(\'XSS\')">', {"DANGEROUS_URL_SCHEME"}),
    ("<BODY ONLOAD=alert('XSS')>", {"EVENT_HANDLER_ATTR"}),
    ('<INPUT TYPE="IMAGE" SRC="javascript:alert(\'XSS\');">', {"DANGEROUS_URL_SCHEME", "DANGEROUS_TAG"}),
    ('<IMG DYNSRC="javascript:alert(\'XSS\')">', {"DANGEROUS_URL_SCHEME"}),
    ('<IMG LOWSRC="javascript:alert(\'XSS\')">', {"DANGEROUS_URL_SCHEME"}),
    ('<STYLE>li {list-style-image: url("javascript:alert(\'XSS\')");}</STYLE><UL><LI>XSS</br>', {"STYLE_JS_URL"}),
    ("<IMG SRC='vbscript:msgbox(\"XSS\")'>", {"DANGEROUS_URL_SCHEME"}),
    ("<svg/onload=alert('XSS')>", {"EVENT_HANDLER_ATTR", "DANGEROUS_TAG"}),
    ('<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>', {"DANGEROUS_TAG"}),
    ('<math><maction actiontype="statusline#http://google.com" xlink:href="javascript:alert(1)">CLICK</maction></math>', {"DANGEROUS_URL_SCHEME", "DANGEROUS_TAG"}),
    ("<iframe srcdoc=\"&lt;script&gt;alert(1)&lt;/script&gt;\"></iframe>", {"SRCDOC_DANGEROUS_CONTENT", "DANGEROUS_TAG", "SRCDOC_ATTR"}),
    ('"><script>alert(1)</script>', {"DANGEROUS_TAG"}),
    ("'><img src=x onerror=alert(1)>", {"EVENT_HANDLER_ATTR"}),
    ('<a href="jav&#x61;script:alert(1)">c</a>', {"DANGEROUS_URL_SCHEME"}),
    ('<a href="&#106;avascript:alert(1)">c</a>', {"DANGEROUS_URL_SCHEME"}),
    ('<a href="javascript&#58;alert(1)">c</a>', {"DANGEROUS_URL_SCHEME"}),
    ('<a href="java&Tab;script:alert(1)">c</a>', {"DANGEROUS_URL_SCHEME"}),
    ('<a href="java&NewLine;script:alert(1)">c</a>', {"DANGEROUS_URL_SCHEME"}),
    ('<a href=" &#14; javascript:alert(1)">c</a>', {"DANGEROUS_URL_SCHEME"}),
    ('<DIV STYLE="background-image: url(javascript:alert(\'XSS\'))">', {"STYLE_JS_URL"}),
    ('<DIV STYLE="background-image: url(&#1;javascript:alert(\'XSS\'))">', {"STYLE_JS_URL"}),
    ('<DIV STYLE="width: expression(alert(\'XSS\'));">', {"STYLE_EXPRESSION"}),
    ('<BASE HREF="javascript:alert(\'XSS\');//">', {"DANGEROUS_URL_SCHEME", "DANGEROUS_TAG"}),
    ('<OBJECT TYPE="text/x-scriptlet" DATA="http://xss.rocks/scriptlet.html"></OBJECT>', {"DANGEROUS_TAG"}),
    ('<EMBED SRC="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjxzY3JpcHQ+YWxlcnQoMSk8L3NjcmlwdD48L3N2Zz4=">', {"DANGEROUS_URL_SCHEME", "DANGEROUS_TAG"}),
    ('<EMBED SRC="data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pgo=">', {"DANGEROUS_URL_SCHEME", "DANGEROUS_TAG"}),
    ('<SCRIPT a=">" SRC="http://xss.rocks/xss.js"></SCRIPT>', {"DANGEROUS_TAG"}),
    ('<SCRIPT =">" SRC="http://xss.rocks/xss.js"></SCRIPT>', {"DANGEROUS_TAG"}),
    ('<SCRIPT a=">" \'\' SRC="http://xss.rocks/xss.js"></SCRIPT>', {"DANGEROUS_TAG"}),
    ('<SCRIPT "a=\'>\'" SRC="http://xss.rocks/xss.js"></SCRIPT>', {"DANGEROUS_TAG"}),
    ('<SCRIPT a=`>` SRC="http://xss.rocks/xss.js"></SCRIPT>', {"DANGEROUS_TAG"}),
    ('<SCRIPT>document.write("<SCRI");</SCRIPT>PT SRC="http://xss.rocks/xss.js"></SCRIPT>', {"DANGEROUS_TAG"}),
    ('<form action="javascript:alert(1)"><input type=submit></form>', {"DANGEROUS_URL_SCHEME", "DANGEROUS_TAG"}),
    ('<input type="hidden" autofocus onfocus=alert(1)>', {"HIDDEN_AUTOFOCUS", "EVENT_HANDLER_ATTR", "DANGEROUS_TAG"}),
    ('<meta http-equiv="refresh" content="0;url=javascript:alert(1)">', {"META_REFRESH", "DANGEROUS_URL_SCHEME", "DANGEROUS_TAG"}),
    ('<meta http-equiv="refresh" content="0;url=data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pgo=">', {"META_REFRESH", "DANGEROUS_URL_SCHEME", "DANGEROUS_TAG"}),
    ('<meta charset="utf-7">', {"META_CHARSET", "DANGEROUS_TAG"}),
    ("<plaintext>", {"PLAINTEXT_ELEMENT"}),
    ("<xmp>", {"XMP_ELEMENT"}),
    ("<!--[if gte IE 4]><SCRIPT>alert('XSS');</SCRIPT><![endif]-->", {"IE_CONDITIONAL_COMMENT"}),
    ('<XML ID="xss"><I><B><IMG SRC="javas<!-- -->cript:alert(\'XSS\')"></B></I></XML>', {"DANGEROUS_URL_SCHEME"}),
    ('<HTML><BODY><?xml:namespace prefix="t" ns="urn:schemas-microsoft-com:time"><?import namespace="t" implementation="#default#time2">'
     '<t:set attributeName="innerHTML" to="XSS&lt;SCRIPT DEFER&gt;alert(&quot;XSS&quot;)&lt;/SCRIPT&gt;">', {"EMBEDDED_HTML_IN_ATTR"}),
    ('<TABLE BACKGROUND="javascript:alert(\'XSS\')">', {"DANGEROUS_URL_SCHEME"}),
    ('<TABLE><TD BACKGROUND="javascript:alert(\'XSS\')">', {"DANGEROUS_URL_SCHEME"}),
    ('<XSS STYLE="xss:expr/*XSS*/ession(alert(\'XSS\'))">', {"STYLE_EXPRESSION"}),
    ('<IMG STYLE="xss:expr/*XSS*/ession(alert(\'XSS\'))">', {"STYLE_EXPRESSION"}),
    ('<LINK REL="stylesheet" HREF="javascript:alert(\'XSS\');">', {"DANGEROUS_URL_SCHEME", "DANGEROUS_TAG"}),
    ('<LINK REL="stylesheet" HREF="http://xss.rocks/xss.css">', {"DANGEROUS_TAG"}),
    ('<IFRAME SRC=# onmouseover="alert(document.cookie)"></IFRAME>', {"EVENT_HANDLER_ATTR", "DANGEROUS_TAG"}),
    ('<FRAMESET><FRAME SRC="javascript:alert(\'XSS\');"></FRAMESET>', {"DANGEROUS_URL_SCHEME"}),
    ("<OBJECT classid=clsid:ae24fdae-03c6-11d1-8b76-0080c744f389>"
     "<param name=url value=javascript:alert('XSS')></OBJECT>", {"DANGEROUS_URL_SCHEME", "DANGEROUS_TAG"}),
    ('<XML ID=I><X><C><![CDATA[<IMG SRC="javas]]><![CDATA[cript:alert(\'XSS\');">]]></C></X></xml>', {"DANGEROUS_URL_SCHEME"}),
    ("<isindex type=image src=1 onerror=alert(1)>", {"EVENT_HANDLER_ATTR"}),
    ("<marquee onstart=alert(1)>x</marquee>", {"EVENT_HANDLER_ATTR"}),
    ('<video><source onerror="alert(1)"></video>', {"EVENT_HANDLER_ATTR"}),
    ("<audio src=x onerror=alert(1)>", {"EVENT_HANDLER_ATTR"}),
    ("<details open ontoggle=alert(1)>", {"EVENT_HANDLER_ATTR"}),
    ('<object data="javascript:alert(1)">', {"DANGEROUS_URL_SCHEME", "DANGEROUS_TAG"}),
    ('<a href="vbscript:msgbox(1)">x</a>', {"DANGEROUS_URL_SCHEME"}),
    ('<a href="data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pgo=">x</a>', {"DANGEROUS_URL_SCHEME"}),
    ("<iframe srcdoc=\"&lt;iframe srcdoc=&amp;quot;&amp;lt;script&amp;gt;alert(2)&amp;lt;/script&amp;gt;&amp;quot;&gt;&lt;/iframe&gt;\"></iframe>", {"SRCDOC_DANGEROUS_CONTENT", "DANGEROUS_TAG"}),
    ('<img src="x" srcset="javascript:alert(1) 1x, b.png 2x">', {"DANGEROUS_URL_SCHEME"}),
    ('<DIV STYLE="background-image: url(\\6a\\61\\76\\61\\73\\63\\72\\69\\70\\74:alert(1))">', {"STYLE_JS_URL"}),
]


class OwaspVectorCorpusTest(unittest.TestCase):
    """Every embedded OWASP filter-evasion vector must be flagged in-category."""

    def test_every_vector_flagged_in_category(self):
        tool = HtmlAuditTool()
        self.assertGreaterEqual(len(OWASP_VECTORS), 60)
        for index, (vector, expected) in enumerate(OWASP_VECTORS):
            with self.subTest(index=index, vector=vector[:60]):
                result = tool.execute(vector, mode="audit")
                self.assertEqual(result["status"], "success", result)
                missing = expected - codeset(result)
                self.assertEqual(missing, set(),
                                 f"vector #{index} missed {missing}: {vector}")

    def test_corpus_covers_all_high_value_categories(self):
        corpus_codes = set()
        for vector, expected in OWASP_VECTORS:
            corpus_codes |= expected
        for code in ("DANGEROUS_TAG", "EVENT_HANDLER_ATTR", "DANGEROUS_URL_SCHEME",
                     "STYLE_JS_URL", "STYLE_EXPRESSION", "SRCDOC_DANGEROUS_CONTENT",
                     "META_REFRESH", "HIDDEN_AUTOFOCUS", "IE_CONDITIONAL_COMMENT",
                     "PLAINTEXT_ELEMENT", "XMP_ELEMENT", "EMBEDDED_HTML_IN_ATTR",
                     "META_CHARSET"):
            self.assertIn(code, corpus_codes, code)


# ---------------------------------------------------------------------------
# allowlist_diff / text / stats modes.
# ---------------------------------------------------------------------------

class AllowlistDiffTest(unittest.TestCase):
    """Unit tests for the audit-only allowlist diff mode."""

    def setUp(self):
        self.tool = HtmlAuditTool()

    def test_diff_basic(self):
        html = "<div><p>a</p><script>x()</script><span>b</span><script>y()</script></div>"
        result = self.tool.execute(html, mode="allowlist_diff", allowed_tags=["div", "p", "span"])
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["allowed_tags"], ["div", "p", "span"])
        self.assertEqual(result["used_tags"], ["div", "p", "script", "span"])
        disallowed = result["disallowed_tags"]
        self.assertEqual(disallowed[0]["tag"], "script")
        self.assertEqual(disallowed[0]["count"], 2)
        self.assertEqual(disallowed[0]["lines"], [1])
        self.assertEqual(result["unknown_allowed_tags"], [])
        self.assertEqual(result["stats"]["disallowed_total"], 2)

    def test_diff_lines_capped_and_sorted(self):
        html = "\n".join(f"<b>{i}</b><i>x</i>" for i in range(8))
        result = self.tool.execute(html, mode="allowlist_diff", allowed_tags={"b"})
        self.assertEqual([d["tag"] for d in result["disallowed_tags"]], ["i"])
        self.assertEqual(result["disallowed_tags"][0]["lines"], [1, 2, 3, 4, 5])
        self.assertEqual(result["disallowed_tags"][0]["count"], 8)
        self.assertEqual(result["unknown_allowed_tags"], [])

    def test_diff_unknown_allowed(self):
        result = self.tool.execute("<p>x</p>", mode="allowlist_diff", allowed_tags={"p", "table", "td"})
        self.assertEqual(result["unknown_allowed_tags"], ["table", "td"])

    def test_diff_is_audit_only_no_mutation(self):
        html = "<div><script>a()</script></div>"
        original = html
        result = self.tool.execute(html, mode="allowlist_diff", allowed_tags=["div"])
        self.assertEqual(html, original)
        self.assertNotIn("html", result)  # the fragment is never echoed or rewritten

    def test_diff_normalizes_case_and_duplicates(self):
        result = self.tool.execute("<P>x</P>", mode="allowlist_diff", allowed_tags=["P", "p "])
        self.assertEqual(result["allowed_tags"], ["p"])
        self.assertEqual(result["disallowed_tags"], [])

    def test_diff_validation(self):
        for bad in [None, "div", "", [""], ["<b>"], ["a b"], [1], []]:
            with self.subTest(bad=bad):
                result = self.tool.execute("<p>x</p>", mode="allowlist_diff", allowed_tags=bad)
                self.assertEqual(result["status"], "error", bad)
                self.assertEqual(result["error_type"], "validation_error")


class TextModeTest(unittest.TestCase):
    """Unit tests for visible-text extraction."""

    def setUp(self):
        self.tool = HtmlAuditTool()

    def test_basic_extraction(self):
        result = self.tool.execute("<div><p>Hello  &amp;   welcome</p><b>back</b></div>", mode="text")
        self.assertEqual(result["status"], "success")
        # No whitespace exists across the </p><b> boundary, matching the
        # DOM text layout (and the lxml oracle) exactly.
        self.assertEqual(result["text"], "Hello & welcomeback")

    def test_script_and_style_dropped_and_reported(self):
        html = "<div>a<script>alert(1)</script>b<style>p{color:red}</style>c</div>"
        result = self.tool.execute(html, mode="text")
        self.assertEqual(result["text"], "abc")
        self.assertEqual(result["skipped_invisible"],
                         [{"element": "script", "count": 1}, {"element": "style", "count": 1}])

    def test_entity_decode_once_honesty(self):
        result = self.tool.execute("<p>&amp;amp;</p>", mode="text")
        self.assertEqual(result["text"], "&amp;")
        result = self.tool.execute("<p>&amp;lt;</p>", mode="text")
        self.assertEqual(result["text"], "&lt;")

    def test_numeric_and_named_entities(self):
        result = self.tool.execute("<p>&#58;&#x3a;&colon;&copy;</p>", mode="text")
        self.assertEqual(result["text"], ":::©")

    def test_comments_not_in_text(self):
        result = self.tool.execute("<p>before<!-- hidden -->after</p>", mode="text")
        self.assertEqual(result["text"], "beforeafter")

    def test_whitespace_normalized(self):
        result = self.tool.execute("<p>one\ntwo\t\tthree   four</p>", mode="text")
        self.assertEqual(result["text"], "one two three four")

    def test_text_truncation(self):
        tool = HtmlAuditTool(max_text_chars=10)
        result = tool.execute("<p>" + "word " * 20 + "</p>", mode="text")
        self.assertTrue(result["truncated"])
        self.assertLessEqual(len(result["text"]), 10)
        self.assertGreater(result["text_chars"], 10)


class StatsModeTest(unittest.TestCase):
    """Unit tests for the statistics mode."""

    def setUp(self):
        self.tool = HtmlAuditTool()

    def test_histograms_sorted_by_count_then_name(self):
        html = "<div><p>a</p><p>b</p><i>c</i><span class='x' id='y'>d</span></div>"
        result = self.tool.execute(html, mode="stats")
        self.assertEqual(list(result["tag_histogram"]), ["p", "div", "i", "span"])
        self.assertEqual(result["attr_histogram"], {"class": 1, "id": 1})

    def test_max_depth(self):
        result = self.tool.execute("<div><div><div><p>x</p></div></div></div>", mode="stats")
        self.assertEqual(result["max_depth"], 4)

    def test_form_inventory(self):
        html = ("<form action='/login' method='POST'>"
                "<input type='text' name='u'><input type='password' name='p'>"
                "</form><input type='hidden' name='o'>")
        result = self.tool.execute(html, mode="stats")
        form = result["forms"][0]
        self.assertEqual(form["action"], "/login")
        self.assertEqual(form["method"], "post")
        self.assertEqual(form["input_count"], 2)
        self.assertEqual([i["type"] for i in form["inputs"]], ["text", "password"])
        self.assertEqual(result["orphan_input_count"], 1)

    def test_link_scheme_census(self):
        html = ("<a href='https://a.test/1'>1</a>"
                "<a href='http://a.test/2'>2</a>"
                "<a href='/rel'>3</a>"
                "<a href='javascript:x(1)'>4</a>"
                "<a href='mailto:a@b.c'>5</a>"
                "<img src='data:image/png;base64,iVBOR'>")
        result = self.tool.execute(html, mode="stats")
        by_scheme = result["link_inventory"]["by_scheme"]
        self.assertEqual(by_scheme["https"], 1)
        self.assertEqual(by_scheme["http"], 1)
        self.assertEqual(by_scheme["relative"], 1)
        self.assertEqual(by_scheme["javascript"], 1)
        self.assertEqual(by_scheme["mailto"], 1)
        self.assertEqual(by_scheme["data"], 1)
        self.assertEqual(result["link_inventory"]["total"], 6)

    def test_entity_census(self):
        result = self.tool.execute("<p>&amp; &amp; &#58; &copy;</p>", mode="stats")
        self.assertEqual(result["entity_census"], {"&amp;": 2, "&#58;": 1, "&copy;": 1})


# ---------------------------------------------------------------------------
# Validation, caps, determinism.
# ---------------------------------------------------------------------------

class ValidationAndCapsTest(unittest.TestCase):
    """Unit tests for strict validation, caps, and determinism."""

    def setUp(self):
        self.tool = HtmlAuditTool()

    def test_mode_validation(self):
        for bad_mode in ["nope", "", None, 1]:
            result = self.tool.execute("<p>x</p>", mode=bad_mode)
            self.assertEqual(result["status"], "error", bad_mode)
            self.assertEqual(result["error_type"], "validation_error")
        self.assertEqual(self.tool.execute("<p>x</p>", mode=" Audit ")["status"], "success")

    def test_html_validation(self):
        for bad in [None, 123, b"<p>", "   ", ""]:
            result = self.tool.execute(bad, mode="audit")
            self.assertEqual(result["status"], "error", bad)
            self.assertEqual(result["error_type"], "validation_error")

    def test_input_size_cap(self):
        tool = HtmlAuditTool(max_input_chars=100)
        result = tool.execute("<p>" + "x" * 200 + "</p>", mode="audit")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "validation_error")
        self.assertIn("max_input_chars", result["error"])

    def test_tag_count_cap(self):
        tool = HtmlAuditTool(max_tags=10)
        html = "".join("<div>" for _ in range(11))
        result = tool.execute(html, mode="audit")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "input_too_large")
        self.assertIn("max_tags", result["error"])

    def test_depth_cap(self):
        tool = HtmlAuditTool(max_depth=5)
        html = "".join("<div>" for _ in range(6)) + "x"
        result = tool.execute(html, mode="audit")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "input_too_large")
        self.assertIn("max_depth", result["error"])

    def test_config_validation(self):
        result = HtmlAuditTool(max_findings=0).execute("<p>x</p>", mode="audit")
        self.assertEqual(result["status"], "error")
        self.assertIn("max_findings", result["error"])
        result = HtmlAuditTool(max_tags=-5).execute("<p>x</p>", mode="audit")
        self.assertEqual(result["status"], "error")
        self.assertIn("max_tags", result["error"])

    def test_determinism(self):
        html = ("<div>\n<script>a()</script>\n<a href='javascript:x(1)' onclick='y()'>c</a>\n"
                "<iframe srcdoc='&lt;b&gt;&lt;/b&gt;'></iframe>\n&copy; &#58;\n</div>")
        first = self.tool.execute(html, mode="audit")
        for _ in range(3):
            self.assertEqual(json.dumps(self.tool.execute(html, mode="audit")), json.dumps(first))
        stats = self.tool.execute(html, mode="stats")
        self.assertEqual(json.dumps(self.tool.execute(html, mode="stats")), json.dumps(stats))

    def test_stdlib_only_runtime(self):
        for banned in ("lxml", "bs4", "requests", "BeautifulSoup"):
            self.assertFalse(hasattr(html_audit_module, banned))


# ---------------------------------------------------------------------------
# Oracle A: tag/attribute census parity against lxml (300 fragments).
# ---------------------------------------------------------------------------

CENSUS_SEED = 20251021
CENSUS_SIZE = 300


class CensusOracleTest(unittest.TestCase):
    """Parse-oracle parity: tool census vs lxml.html walks, with the
    stdlib tokenizer as the pinned second oracle where lxml's recovery
    differs (malformed fragments)."""

    def setUp(self):
        if not HAVE_LXML:
            self.skipTest("lxml.html not installed; parse oracle unavailable")
        self.tool = HtmlAuditTool()

    def test_census_parity_300_seeded_fragments(self):
        generator = FragmentGenerator(CENSUS_SEED)
        fragments = [(generator.fragment(), "valid") for _ in range(90)]
        fragments += [(generator.mutate_benign(generator.fragment()), "mutated") for _ in range(110)]
        fragments += [(generator.mutate_malformed(generator.fragment()), "malformed") for _ in range(100)]
        self.assertEqual(len(fragments), CENSUS_SIZE)
        lxml_agreements = 0
        reference_agreements = 0
        lxml_failures = 0
        for index, (fragment, klass) in enumerate(fragments):
            result = self.tool.execute(fragment, mode="stats")
            self.assertEqual(result["status"], "success", (index, fragment))
            tool_tags = dict(result["tag_histogram"])
            tool_attrs = dict(result["attr_histogram"])
            try:
                lxml_tags, lxml_attrs = lxml_census(fragment)
            except Exception:
                lxml_failures += 1
                ref_tags, ref_attrs = reference_census(fragment)
                self.assertEqual((tool_tags, tool_attrs), (ref_tags, ref_attrs), (index, fragment))
                reference_agreements += 1
                continue
            if (tool_tags, tool_attrs) == (lxml_tags, lxml_attrs):
                lxml_agreements += 1
                continue
            self.assertEqual(klass, "malformed",
                             f"valid/mutated fragment #{index} diverged from lxml: {fragment!r}")
            ref_tags, ref_attrs = reference_census(fragment)
            self.assertEqual((tool_tags, tool_attrs), (ref_tags, ref_attrs),
                             f"malformed fragment #{index} diverged from both oracles: {fragment!r}")
            self.assertNotEqual((ref_tags, ref_attrs), (lxml_tags, lxml_attrs),
                                f"fragment #{index} claimed divergent but oracles agree: {fragment!r}")
            reference_agreements += 1
        self.assertGreater(lxml_agreements, 150)
        self.assertGreater(reference_agreements + lxml_agreements, 250)

    def test_pinned_divergence_unterminated_tag_at_eof(self):
        # libxml2 recovers an unterminated tag as an element with junk
        # attributes; the stdlib tokenizer drops it. The tool follows the
        # tokenizer and flags the drop via the raw-source cross-check.
        fragment = '<IMG SRC="javascript:alert(1)"'
        tool_tags, tool_attrs = tool_census(fragment)
        lxml_tags, lxml_attrs = lxml_census(fragment)
        self.assertEqual(tool_tags, {})
        self.assertEqual(lxml_tags, {"img": 1})
        ref_tags, _ = reference_census(fragment)
        self.assertEqual(tool_tags, ref_tags)
        audit = self.tool.execute(fragment, mode="audit")
        self.assertIn("DANGEROUS_URL_SCHEME", codeset(audit))

    def test_pinned_divergence_markup_swallowed_into_attr(self):
        # '<div class="a" <span>x' — libxml2 keeps '<span' as an attribute
        # name; the stdlib tokenizer reports it as a separate dropped tag.
        fragment = '<div class="a" <span>x</div>'
        tool_tags, tool_attrs = tool_census(fragment)
        lxml_tags, lxml_attrs = lxml_census(fragment)
        ref_tags, ref_attrs = reference_census(fragment)
        self.assertEqual(tool_tags, ref_tags)
        self.assertEqual(tool_tags, {"div": 1})
        self.assertIn("<span", lxml_attrs)
        audit = self.tool.execute(fragment, mode="audit")
        self.assertIn("MALFORMED_MARKUP", codeset(audit))

    def test_pinned_agreement_on_classic_recoveries(self):
        # These recovery classes look divergent but agree on the census:
        # unclosed tags at EOF, sibling <p> recovery, <<script>, stray
        # end tags, duplicate attributes (first wins on both sides).
        cases = [
            "<b>x<i>y",
            "<b>1<b>2",
            "<p>a<p>b",
            "<<script>alert(1);//<</script>",
            "stray</div>text",
            '<div a=1 A=2>t</div>',
            "<ul><li>a<li>b</ul>",
            "<bare><td>x</td></bare>",
        ]
        for fragment in cases:
            with self.subTest(fragment=fragment):
                tool_tags, tool_attrs = tool_census(fragment)
                lxml_tags, lxml_attrs = lxml_census(fragment)
                self.assertEqual((tool_tags, tool_attrs), (lxml_tags, lxml_attrs), fragment)


# ---------------------------------------------------------------------------
# Oracle C: visible-text parity against lxml text_content (200 fragments).
# ---------------------------------------------------------------------------

TEXT_SEED = 20261021
TEXT_SIZE = 200


class TextParityOracleTest(unittest.TestCase):
    """Text extraction parity vs lxml.html text_content() with script and
    style subtrees dropped, after identical whitespace normalization."""

    def setUp(self):
        if not HAVE_LXML:
            self.skipTest("lxml.html not installed; text oracle unavailable")
        self.tool = HtmlAuditTool()

    def _text_fragments(self):
        generator = FragmentGenerator(TEXT_SEED)
        fragments = []
        for _ in range(110):
            fragments.append(generator.fragment())
        for _ in range(70):
            fragments.append(generator.mutate_benign(generator.fragment()))
        for _ in range(20):
            body = generator.fragment()
            fragments.append(body + "<script>var x = 1;</script>" + body
                             + "<style>a{b:c}</style>")
        return fragments

    def test_text_parity_200_seeded_fragments(self):
        tool = HtmlAuditTool()
        fragments = self._text_fragments()
        self.assertEqual(len(fragments), TEXT_SIZE)
        for index, fragment in enumerate(fragments):
            with self.subTest(index=index):
                result = tool.execute(fragment, mode="text")
                self.assertEqual(result["status"], "success", fragment)
                self.assertEqual(result["text"], lxml_visible_text(fragment),
                                 fragment)

    def test_pinned_text_divergences(self):
        tool = HtmlAuditTool()
        # Simple CDATA sections: libxml2 treats them as bogus comments and
        # drops them; the stdlib tokenizer reports them as unknown
        # declarations and also drops them. Parity.
        self.assertEqual(tool.execute("<p>a<![CDATA[x]]>b</p>", mode="text")["text"], "ab")
        self.assertEqual(lxml_visible_text("<p>a<![CDATA[x]]>b</p>"), "ab")
        # CDATA containing '>': libxml2's bogus comment ends at the first
        # '>' and the remainder leaks into visible text; the stdlib
        # tokenizer consumes through ']]>' instead. Divergence pinned.
        self.assertEqual(tool.execute("<p>a<![CDATA[im>g]]>b</p>", mode="text")["text"], "ab")
        self.assertEqual(lxml_visible_text("<p>a<![CDATA[im>g]]>b</p>"), "ag]]>b")
        # Unterminated tag at EOF: both sides drop the construct (parity).
        result = tool.execute("<p>ok</p><img src=\"javascript:x(1)\"", mode="text")
        self.assertEqual(result["text"], "ok")
        self.assertEqual(result["text"], lxml_visible_text("<p>ok</p><img src=\"javascript:x(1)\""))
        # Entity-terminator reconstruction parity for '&notit;'-class refs.
        result = tool.execute("<p>&notit;</p>", mode="text")
        self.assertEqual(result["text"], lxml_visible_text("<p>&notit;</p>"))


# ---------------------------------------------------------------------------
# Oracle D: line-number accuracy on 30 hand-crafted multi-line fragments.
# Every expected (line, code) pair below was hand-counted from the source.
# ---------------------------------------------------------------------------

LINE_FRAGMENTS = [
    # (html, {(line, code), ...}) — restricted to the codes of interest.
    ("<div>\n  <p>text</p>\n  <script>alert(1)</script>\n</div>", {(3, "DANGEROUS_TAG")}),
    ("<div>\n<a href=\"javascript:alert(1)\">x</a>\n</div>", {(2, "DANGEROUS_URL_SCHEME")}),
    ("<img src=\"ok.png\" alt=\"i\">\n<img src=\"x\" onerror=\"alert(1)\">", {(2, "EVENT_HANDLER_ATTR")}),
    ("<section>\n<iframe src=\"https://ok.test\"></iframe>\n</section>", {(2, "DANGEROUS_TAG")}),
    ("<p>a</p>\n<object data=\"x.swf\"></object>\n<p>b</p>", {(2, "DANGEROUS_TAG")}),
    ("<div>\n<embed src=\"x.svg\">\n</div>", {(2, "DANGEROUS_TAG")}),
    ("<form action=\"/login\" method=\"post\">\n<input type=\"hidden\" name=\"t\" value=\"1\">\n</form>",
     {(1, "DANGEROUS_TAG"), (2, "DANGEROUS_TAG")}),
    ("<head>\n<link rel=\"stylesheet\" href=\"/a.css\">\n<base href=\"https://x.test/\">\n</head>",
     {(2, "DANGEROUS_TAG"), (3, "DANGEROUS_TAG")}),
    ("<body>\n<svg width=\"10\"><circle r=\"1\"/></svg>\n</body>", {(2, "DANGEROUS_TAG")}),
    ("<div>\n<math><mi>x</mi></math>\n</div>", {(2, "DANGEROUS_TAG")}),
    ("<meta http-equiv=\"refresh\" content=\"5\">", {(1, "META_REFRESH"), (1, "DANGEROUS_TAG")}),
    ("<div>\n<meta charset=\"utf-7\">\n</div>", {(2, "META_CHARSET"), (2, "DANGEROUS_TAG")}),
    ("<div>\n<a href=\"https://x.test\" target=\"_blank\">y</a>\n</div>", {(2, "TARGET_NO_REL")}),
    ("<form>\n<input type=\"hidden\" autofocus name=\"s\">\n<input type=\"text\" name=\"q\">\n</form>",
     {(2, "HIDDEN_AUTOFOCUS")}),
    ("<div>\n<plaintext>\nanything", {(2, "PLAINTEXT_ELEMENT")}),
    ("<div>\n<xmp>\nraw", {(2, "XMP_ELEMENT")}),
    ("<!-- normal note -->\n<!--[if IE]><p>old</p><![endif]-->\n<div>x</div>", {(2, "IE_CONDITIONAL_COMMENT")}),
    ("<div>\n<div>\n<a href=\"jav&#x09;ascript:alert(1)\">x</a>\n</div>\n</div>", {(3, "DANGEROUS_URL_SCHEME")}),
    ("<p>\n<IMG SRC=JaVaScRiPt:alert('XSS')>\n</p>", {(2, "DANGEROUS_URL_SCHEME")}),
    ("<div>\n<div style=\"background:url(javascript:alert(1))\">x</div>\n</div>", {(2, "STYLE_JS_URL")}),
    ("<div>\n<style>\nli { color: red }\n</style>\n</div>", set()),
    ("<div>\n<iframe srcdoc=\"&lt;script&gt;alert(1)&lt;/script&gt;\"></iframe>\n</div>",
     {(2, "DANGEROUS_TAG"), (2, "SRCDOC_ATTR"), (2, "SRCDOC_DANGEROUS_CONTENT")}),
    ("text\nmore <b>bold</b>\n<img src=\"javascript:alert(1)\">", {(3, "DANGEROUS_URL_SCHEME")}),
    ("<div>\n\n  <a href=\"vbscript:msgbox(1)\">v</a>\n\n</div>", {(3, "DANGEROUS_URL_SCHEME")}),
    ("<div>\n  <p>\n    <b>\n      <a href=\" &#14; javascript:alert(1)\">d</a>\n    </b>\n  </p>\n</div>",
     {(4, "DANGEROUS_URL_SCHEME")}),
    ("<div>\n<img src=\"x.png\">\n<img src=\"javascript:alert(1)\"", {(3, "DANGEROUS_URL_SCHEME")}),
    ("<ul>\n<li>one</li>\n<li><a href=\"/x\" target=\"_blank\">two</a></li>\n</ul>", {(3, "TARGET_NO_REL")}),
    ("<div>\n<object>\n<param name=\"movie\" value=\"javascript:alert(1)\">\n</object>\n</div>",
     {(2, "DANGEROUS_TAG"), (3, "DANGEROUS_URL_SCHEME")}),
    ("<p>x</p>\n<input type=\"image\" src=\"javascript:alert(1)\">\n<p>y</p>", {(2, "DANGEROUS_URL_SCHEME")}),
    ("<div>\n<a href=\"data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pgo=\">d</a>\n</div>",
     {(2, "DANGEROUS_URL_SCHEME")}),
]


class LineAccuracyTest(unittest.TestCase):
    """Every finding line must match the hand-counted line in the source."""

    def test_line_numbers_hand_verified(self):
        tool = HtmlAuditTool()
        self.assertEqual(len(LINE_FRAGMENTS), 30)
        for index, (html, expected) in enumerate(LINE_FRAGMENTS):
            with self.subTest(index=index):
                result = tool.execute(html, mode="audit")
                self.assertEqual(result["status"], "success", html)
                codes_of_interest = {code for _line, code in expected}
                actual = finding_tuples(result, codes_of_interest)
                self.assertEqual(actual, expected,
                                 f"fragment #{index}: expected {expected}, got {actual}")

    def test_columns_also_reported(self):
        result = HtmlAuditTool().execute("text\n  <script>a()</script>", mode="audit")
        finding = next(f for f in result["findings"] if f["code"] == "DANGEROUS_TAG")
        self.assertEqual(finding["line"], 2)
        self.assertEqual(finding["col"], 2)


# ---------------------------------------------------------------------------
# Component registration.
# ---------------------------------------------------------------------------

class HtmlAuditToolRegistrationTest(unittest.TestCase):
    """Unit tests for registering the shipped html_audit_tool.yaml."""

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
        self.assertEqual(component.metadata_class, "HtmlAuditTool")

    def test_manager(self):
        configer = ToolConfiger().load_by_configer(self.config)
        app = AppConfiger()
        app.tool_configer_map = {configer.name: configer}
        ApplicationConfigManager().app_configer = app
        tool = ToolManager().get_instance_obj(configer.name)
        self.assertIsInstance(tool, HtmlAuditTool)
        self.assertEqual(tool.input_keys, ["html", "mode"])

    def test_package_export(self):
        from agentuniverse.agent.action.tool.common_tool import HtmlAuditTool as Exported
        self.assertIs(Exported, HtmlAuditTool)


if __name__ == "__main__":
    unittest.main()
