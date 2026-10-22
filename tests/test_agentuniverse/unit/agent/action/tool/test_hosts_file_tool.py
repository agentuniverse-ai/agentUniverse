# !/usr/bin/env python3
# ruff: noqa: S311
# (S311: random.Random is used for seeded, deterministic test corpora,
#  never for cryptographic purposes.)

"""Offline unit tests for the HostsFileTool (hosts(5) file analysis).

Six oracle batteries plus targeted unit tests, all fully offline and
deterministic:

* (a) ``ipaddress`` oracle — 600 seeded address tokens; the tool's
  parse verdicts must equal ``ipaddress.ip_address`` accept/reject and
  the normalized form must be byte-equal to ``str(ip_address(...))``.
  Zone-ID tokens (valid IPv6 + ``%zone``) are asserted separately:
  ``ipaddress`` accepts them, the tool must reject them.
* (b) hostname grammar oracle — 400 seeded hostnames checked against an
  independent label-grammar implementation in this file.
* (c) lookup first-wins oracle — 200 seeded hosts files with duplicate
  and conflicting mappings; expectations computed by an independent
  line scanner implementing the POSIX first-match-wins contract.
* (d) generate/parse round trip on 300 mappings.
* (e) 10 real-world-shaped corpora including a 5000-line Pi-hole-style
  synthetic blocklist (parse budget: under 2 seconds).
* (f) a comment / tabs / CRLF tolerance battery.
"""

import ipaddress
import random
import re
import time

import pytest

from agentuniverse.agent.action.tool.common_tool.hosts_file_tool import HostsFileTool

# --------------------------------------------------------------------- #
# Independent reference implementations (oracles)
# --------------------------------------------------------------------- #

_LABEL_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?$")
_LABEL_US_RE = re.compile(r"^[A-Za-z0-9_](?:[A-Za-z0-9_-]*[A-Za-z0-9_])?$")


def ref_hostname_verdict(token: str) -> str:
    """Independent hostname grammar: 'valid' | 'underscore' | 'invalid'."""
    if any(ord(c) > 127 for c in token):
        return "invalid"
    if len(token) > 253:
        return "invalid"
    if token.startswith(".") or token.endswith("."):
        return "invalid"
    labels = token.split(".")
    if any(len(label) > 63 for label in labels):
        return "invalid"
    if "_" in token:
        us_ok = all(_LABEL_US_RE.match(label) for label in labels)
        return "underscore" if us_ok else "invalid"
    ok = all(_LABEL_RE.match(label) for label in labels)
    return "valid" if ok else "invalid"


def ref_lookup(text: str, query: str, family=None):
    """Independent first-match-wins resolver over a hosts text.

    Returns ``(ordered_winners, overridden)`` where winners are tuples
    ``(family, ip, line, first_name_token)`` and overridden are the
    later same-family matches in file order.
    """
    matches = []
    for lineno, line in enumerate(text.split("\n"), start=1):
        if line.endswith("\r"):
            line = line[:-1]
        toks = line.split("#", 1)[0].split()
        if not toks:
            continue
        try:
            addr = ipaddress.ip_address(toks[0])
        except ValueError:
            continue
        names = [t.lower() for t in toks[1:]]
        if query.lower() in names:
            matches.append((addr.version, str(addr), lineno, toks[1]))
    if family is not None:
        fid = int(family[1])
        matches = [m for m in matches if m[0] == fid]
    winners: dict[int, tuple] = {}
    overridden = []
    for m in matches:
        if m[0] in winners:
            overridden.append(m)
        else:
            winners[m[0]] = m
    ordered = sorted(winners.values(), key=lambda m: m[2])
    return ordered, overridden


# --------------------------------------------------------------------- #
# Seeded corpus builders
# --------------------------------------------------------------------- #


def _add_unique(tokens: list, seen: set, token: str, bucket: str) -> None:
    """Append (token, bucket) once, skipping duplicates."""
    if token not in seen:
        seen.add(token)
        tokens.append((token, bucket))


def _random_v4(rng: random.Random) -> str:
    return f"{rng.randrange(256)}.{rng.randrange(256)}.{rng.randrange(256)}.{rng.randrange(256)}"


def _random_v6(rng: random.Random) -> str:
    style = rng.randrange(4)
    if style == 0:
        return ":".join(f"{rng.randrange(65536):x}" for _ in range(8))
    if style == 1:
        groups = [f"{rng.randrange(65536):x}" for _ in range(8)]
        cut = rng.randrange(1, 7)
        return ":".join(groups[:cut]) + "::" + ":".join(groups[cut + 2 :])
    if style == 2:
        return "::ffff:" + _random_v4_no_lead(rng)
    return ":".join(f"{rng.randrange(65536):X}" for _ in range(4)) + "::" + f"{rng.randrange(65536):x}"


def _random_v4_no_lead(rng: random.Random) -> str:
    return f"{rng.randrange(256)}.{rng.randrange(256)}.{rng.randrange(256)}.{rng.randrange(256)}"


def _random_zone_v6(rng: random.Random) -> str:
    groups = [f"{rng.randrange(65536):x}" for _ in range(8)]
    groups[rng.randrange(8)] = "0"
    return ":".join(groups) + f"%eth{rng.randrange(3)}"


def build_ip_tokens() -> list[tuple[str, str]]:
    """600 seeded address tokens tagged valid-v4 / valid-v6 / zone / invalid."""
    rng = random.Random(20261021)
    tokens: list[tuple[str, str]] = []
    seen: set[str] = set()

    def fill(bucket: str, want: int, maker) -> None:
        while sum(1 for _, b in tokens if b == bucket) < want:
            _add_unique(tokens, seen, maker(rng), bucket)

    fill("v4", 150, _random_v4)
    fill("v6", 120, _random_v6)
    fill("zone", 30, _random_zone_v6)

    mutations = [
        "010.1.1.1", "192.168.001.1", "1.2.3.4.5", "1.2.3", "256.1.1.1",
        "1.2.3.999", "-1.2.3.4", "1.2.3.4.", ".1.2.3.4", "1..2.3",
        "1234", "4294967295", "1.2.3.4:80", "1:2:3:4:5:6:7:8:9", "1::2::3",
        "::g", "1:2:3:4:5:6:7:gg", "fe80::", ":::", "1:2:3:4:5:6:7",
        "1:2:3:4:5:6:1.2.3.4.5", "2001:db8::1:", ":2001:db8::1",
        "0:1:2:3:4:5:6:7:8", "1.2.3.4:", "::ffff:999.1.2.3",
        "0x1.2.3.4", "1.2.3.+4", "١.٢.٣.٤",  # noqa: RUF001 (intentional confusable)
    ]

    def random_invalid() -> str:
        base = rng.choice(mutations)
        if rng.randrange(3) == 0:
            return base
        return f"{base}x{rng.randrange(10**6)}"

    fill("invalid", 300, lambda r: random_invalid())
    assert len(tokens) == 600
    return tokens


def _add_hostname(tokens: list[str], seen: set[str], token: str) -> None:
    """Append one hostname token once, skipping whitespace/duplicates."""
    if token and token not in seen and not any(c.isspace() for c in token):
        seen.add(token)
        tokens.append(token)


def _legal_hostname_batches() -> list:
    """Yield (count, maker) batches of legal and tolerated hostnames."""
    return [
        (60, lambda i: f"host{i}" if i % 3 else f"Host{i}.Example"),
        (50, lambda i: f"srv{i - 50 if i < 25 else i}.corp{i}.example"),
        (30, lambda i: f"my-{i}-app-{i * 7 % 13}-service.example"),
        (20, lambda i: f"{i}{i * 3 % 10}.{100 + i}"),
        (30, lambda i: f"xn--{i:04d}".ljust(10, "s") if i % 2 else f"www.xn--{i}npi.example"),
        (20, lambda i: f"{('a' * 30) + format(i, '02d') + ('b' * 30)}.example"),
        (10, lambda i: ".".join(["x" * 60] * 3) + f".tail{i}.example"),
        (30, lambda i: f"my_host_{i}.example" if i % 2 else f"svc{i}.my_host"),
    ]


def _illegal_hostname_batches() -> list:
    """Yield (count, maker) batches of illegal hostnames."""
    patterns = [
        "-bad{}", "bad{}-", "-bad{}.example", "a.-b{}.c", "a.b{}-.c",
        ".a{}.b", "a{}.b.", "a..b{}", "bad@host{}", "bad:host{}",
        "bad,host{}", "bad~host{}", "exämple{}.com", "日本{}.jp",
        "bad;host{}", "bad*host{}",
    ]

    def maker(i: int) -> str:
        pattern = patterns[i % len(patterns)]
        if i // len(patterns) == 0:
            return pattern.format(i)
        if i // len(patterns) == 1:
            return pattern.format(f"{i}x")
        if i % 2:
            return ("l" * 64) + f".{i}.example"  # label of 64 characters
        return ".".join(["y" * 63] * 4) + f".{i}"  # total over 253

    return [(150, maker)]


def build_hostname_tokens() -> list[str]:
    """400 seeded unique hostname tokens across grammar buckets."""
    tokens: list[str] = []
    seen: set[str] = set()

    for count, maker in _legal_hostname_batches() + _illegal_hostname_batches():
        for i in range(count):
            _add_hostname(tokens, seen, maker(i))
    assert len(tokens) == 400
    return tokens


def build_lookup_fixtures() -> list[dict]:
    """200 seeded hosts files with duplicate/conflicting target mappings."""
    rng = random.Random(2026)
    fixtures = []
    for i in range(200):
        lines = []
        noise = rng.randrange(2, 5)
        for j in range(noise):
            lines.append(
                f"10.{rng.randrange(256)}.{rng.randrange(256)}.{rng.randrange(1, 255)} "
                f"noise{i}-{j}.example"
            )
        target = f"target{i}.example"
        alias = f"alias{i}.example"
        target_lines = []
        v4_pool = [f"9.{i % 250 + 1}.0.{k + 1}" for k in range(4)]
        v6_pool = [f"2606:4700::{i + 1:x}:{k + 1:x}" for k in range(3)]
        for _ in range(rng.randrange(2, 5)):
            fam = rng.choice(("v4", "v6"))
            ip = rng.choice(v4_pool if fam == "v4" else v6_pool)
            shape = rng.randrange(3)
            if shape == 0:
                line = f"{ip} {target}"
            elif shape == 1:
                line = f"{ip} {target} {alias}"
            else:
                line = f"{ip} other{i}.example {target}"
            target_lines.append(line)
        pos = rng.randrange(0, len(lines) + 1)
        lines = lines[:pos] + target_lines + lines[pos:]
        query = rng.choice((target, alias, target.upper()))
        fixtures.append({"text": "\n".join(lines) + "\n", "query": query, "seed": i})
    return fixtures


# --------------------------------------------------------------------- #
# Shared helpers
# --------------------------------------------------------------------- #

TOOL = HostsFileTool()


def parse_text(text: str) -> dict:
    return TOOL.execute(mode="parse", hosts_text=text)


def entry_by_line(result: dict) -> dict:
    return {e["line"]: e for e in result["entries"]}


def codes_by_line(result: dict) -> dict:
    mapping: dict[int, set[str]] = {}
    for f in result["findings"]:
        mapping.setdefault(f["line"], set()).add(f["code"])
    return mapping


# --------------------------------------------------------------------- #
# (a) ipaddress oracle — 600 seeded address tokens
# --------------------------------------------------------------------- #


class TestIpAddressOracle:
    @pytest.fixture(scope="class")
    def oracle_results(self):
        tokens = build_ip_tokens()
        results = []
        chunk_size = 120
        for start in range(0, len(tokens), chunk_size):
            chunk = tokens[start : start + chunk_size]
            text = "\n".join(f"{tok} probe{start + k}" for k, (tok, _) in enumerate(chunk)) + "\n"
            result = parse_text(text)
            lines = entry_by_line(result)
            codes = codes_by_line(result)
            for k, (tok, bucket) in enumerate(chunk):
                results.append((tok, bucket, lines[k + 1], codes.get(k + 1, set())))
        return results

    def test_count(self, oracle_results):
        assert len(oracle_results) == 600

    def test_verdicts_match_ipaddress_accept_reject(self, oracle_results):
        # Every non-zone token: tool verdict == ipaddress accept/reject.
        checked = 0
        for tok, bucket, entry, _ in oracle_results:
            if bucket == "zone":
                continue
            try:
                expected = str(ipaddress.ip_address(tok))
                accepted = True
            except ValueError:
                accepted = False
            accepted_tool = entry["ip"] is not None
            assert accepted_tool == accepted, tok
            if accepted:
                assert entry["ip"] == expected, (tok, entry["ip"], expected)
            checked += 1
        assert checked == 570

    def test_zone_ids_rejected_with_dedicated_code(self, oracle_results):
        zones = [(tok, entry, codes) for tok, b, entry, codes in oracle_results if b == "zone"]
        assert len(zones) == 30
        for tok, entry, codes in zones:
            assert entry["ip"] is None, tok
            assert "ip_zone_id" in codes, tok

    def test_ip_version_reported(self, oracle_results):
        for tok, _bucket, entry, _unused in oracle_results:
            if entry["ip"] is not None:
                assert entry["ip_version"] == (4 if ":" not in entry["ip"] else 6), tok

    def test_malformed_ip_is_error_severity(self):
        result = parse_text("999.888.777.666 h1\n")
        assert result["entries"][0]["ip"] is None
        assert result["findings"][0]["severity"] == "error"
        assert result["findings"][0]["code"] == "malformed_ip"

    def test_leading_zero_octet_rejected(self):
        result = parse_text("192.168.001.1 h1\n")
        assert result["entries"][0]["ip"] is None
        assert "malformed_ip" in codes_by_line(result).get(1, set())

    def test_embedded_v4_ipv6_normalized(self):
        result = parse_text("::ffff:192.168.1.1 h1\n")
        # str(ipaddress.IPv6Address) keeps the dotted embedded-IPv4 form
        assert result["entries"][0]["ip"] == "::ffff:192.168.1.1"
        assert result["entries"][0]["ip_version"] == 6

    def test_ipv6_compressed_lowercase_form(self):
        result = parse_text("FE80:0000:0000:0000:0000:0000:0000:0001 h1\n")
        assert result["entries"][0]["ip"] == "fe80::1"

    def test_zone_id_message_explains_hosts_scope(self):
        result = parse_text("fe80::1%eth0 h1\n")
        finding = result["findings"][0]
        assert finding["code"] == "ip_zone_id"
        assert "zone" in finding["message"].lower()


# --------------------------------------------------------------------- #
# (b) hostname grammar oracle — 400 seeded hostnames
# --------------------------------------------------------------------- #


class TestHostnameGrammarOracle:
    @pytest.fixture(scope="class")
    def oracle_results(self):
        tokens = build_hostname_tokens()
        results = []
        chunk_size = 200
        for start in range(0, len(tokens), chunk_size):
            chunk = tokens[start : start + chunk_size]
            text = "\n".join(f"203.0.113.7 {tok}" for tok in chunk) + "\n"
            result = parse_text(text)
            lines = entry_by_line(result)
            codes = codes_by_line(result)
            for k, tok in enumerate(chunk):
                results.append((tok, lines[k + 1], codes.get(k + 1, set())))
        return results

    def test_count(self, oracle_results):
        assert len(oracle_results) == 400

    def test_verdicts_match_independent_checker(self, oracle_results):
        for tok, entry, codes in oracle_results:
            expected = ref_hostname_verdict(tok)
            accepted = entry["canonical_hostname"] is not None
            if expected == "invalid":
                assert not accepted, tok
                assert any(h["token"] == tok for h in entry["invalid_hostnames"]), tok
            else:
                assert accepted, tok
                assert entry["canonical_hostname"] == tok
            if expected == "underscore":
                assert "underscore_hostname" in codes, tok
            else:
                assert "underscore_hostname" not in codes, tok

    def test_valid_buckets_summary(self, oracle_results):
        verdicts = [ref_hostname_verdict(t) for t, _, _ in oracle_results]
        assert verdicts.count("valid") == 220
        assert verdicts.count("underscore") == 30
        assert verdicts.count("invalid") == 150

    def test_unicode_hostname_guides_to_punycode(self):
        result = parse_text("1.2.3.4 exämple.com\n")
        codes = codes_by_line(result)
        assert "invalid_hostname" in codes.get(1, set())
        assert any("punycode" in f["message"] for f in result["findings"])

    def test_punycode_is_valid_ascii(self):
        result = parse_text("1.2.3.4 xn--fiqs8s www.xn--80akhbyknj4f\n")
        entry = result["entries"][0]
        assert entry["canonical_hostname"] == "xn--fiqs8s"
        assert entry["aliases"] == ["www.xn--80akhbyknj4f"]

    def test_label_length_boundaries(self):
        ok63 = "a" * 63
        bad64 = "a" * 64
        result = parse_text(f"1.2.3.4 {ok63}.example\n5.6.7.8 {bad64}.example\n")
        entries = entry_by_line(result)
        assert entries[1]["canonical_hostname"] == f"{ok63}.example"
        assert entries[2]["canonical_hostname"] is None

    def test_total_length_boundary(self):
        ok253 = ".".join(["a" * 63, "b" * 63, "c" * 63, "d" * 61])  # 253 chars
        assert len(ok253) == 253
        bad254 = ok253 + "x"
        result = parse_text(f"1.2.3.4 {ok253}\n5.6.7.8 {bad254}\n")
        entries = entry_by_line(result)
        assert entries[1]["canonical_hostname"] == ok253
        assert entries[2]["canonical_hostname"] is None

    def test_dot_and_hyphen_edges(self):
        result = parse_text(
            "1.2.3.4 .a.b\n5.6.7.8 a.b.\n9.9.9.9 -x.y\n8.8.8.8 x-.y\n7.7.7.7 a..b\n"
        )
        entries = entry_by_line(result)
        for line in (1, 2, 3, 4, 5):
            assert entries[line]["canonical_hostname"] is None
            assert entries[line]["invalid_hostnames"], line
        codes = [h["code"] for h in entries[1]["invalid_hostnames"]]
        assert codes == ["leading_dot"]

    def test_alias_equal_canonical_flagged(self):
        result = parse_text("1.2.3.4 web.example web.example\n")
        assert result["entries"][0]["aliases"] == []
        assert "alias_equals_canonical" in codes_by_line(result).get(1, set())


# --------------------------------------------------------------------- #
# (c) lookup first-wins oracle — 200 seeded files
# --------------------------------------------------------------------- #


class TestLookupFirstWinsOracle:
    def test_two_hundred_seeded_files(self):
        fixtures = build_lookup_fixtures()
        assert len(fixtures) == 200
        for fixture in fixtures:
            text, query = fixture["text"], fixture["query"]
            expected_winners, expected_overridden = ref_lookup(text, query)
            result = TOOL.execute(mode="lookup", hosts_text=text, hostname=query)
            assert result["not_found"] == (not expected_winners), fixture["seed"]
            assert result["addresses"] == [w[1] for w in expected_winners], fixture["seed"]
            if expected_winners:
                assert result["from_line"] == expected_winners[0][2], fixture["seed"]
                assert result["canonical"] == (
                    expected_winners[0][3].lower() == query.lower()
                ), fixture["seed"]
            assert [(o["ip"], o["line"]) for o in result["overridden_by_earlier"]] == [
                (o[1], o[2]) for o in expected_overridden
            ], fixture["seed"]

    def test_family_filters_match_reference(self):
        fixtures = build_lookup_fixtures()
        for fixture in fixtures[::4]:  # 50 fixtures x both families
            for family in ("v4", "v6"):
                text, query = fixture["text"], fixture["query"]
                winners, _overridden = ref_lookup(text, query, family)
                result = TOOL.execute(
                    mode="lookup", hosts_text=text, hostname=query, family=family
                )
                assert result["addresses"] == [w[1] for w in winners], (
                    fixture["seed"], family
                )
                assert all(
                    f"v{ipaddress.ip_address(a).version}" == family
                    for a in result["addresses"]
                )

    def test_first_wins_documented_contract(self):
        text = "10.0.0.5 ghost.example\n10.0.0.6 ghost.example\n::1 ghost.example\n"
        result = TOOL.execute(mode="lookup", hosts_text=text, hostname="ghost.example")
        # First per family wins; IPv4+IPv6 coexist; the later v4 loses.
        assert result["addresses"] == ["10.0.0.5", "::1"]
        assert result["from_line"] == 1
        assert result["canonical"] is True
        assert result["overridden_by_earlier"] == [
            {"ip": "10.0.0.6", "line": 2, "family": "v4"}
        ]

    def test_lookup_via_alias(self):
        text = "10.1.2.3 canonical.example alias.example\n"
        result = TOOL.execute(mode="lookup", hosts_text=text, hostname="alias.example")
        assert result["addresses"] == ["10.1.2.3"]
        assert result["canonical"] is False
        assert result["aliases"] == ["alias.example"]

    def test_lookup_case_insensitive(self):
        text = "10.1.2.3 Example.COM\n"
        result = TOOL.execute(mode="lookup", hosts_text=text, hostname="example.com")
        assert result["addresses"] == ["10.1.2.3"]
        assert result["hostname_key"] == "example.com"

    def test_lookup_not_found(self):
        text = "10.0.0.1 other.example\n"
        result = TOOL.execute(mode="lookup", hosts_text=text, hostname="missing.example")
        assert result["not_found"] is True
        assert result["addresses"] == []
        assert result["from_line"] is None
        assert result["canonical"] is None

    def test_lookup_ignores_invalid_ip_lines(self):
        text = "999.1.1.1 target.example\n10.0.0.9 target.example\n"
        result = TOOL.execute(mode="lookup", hosts_text=text, hostname="target.example")
        assert result["addresses"] == ["10.0.0.9"]
        assert result["from_line"] == 2


# --------------------------------------------------------------------- #
# (d) generate/parse round trip — 300 mappings
# --------------------------------------------------------------------- #


class TestGenerateParseRoundTrip:
    @pytest.fixture(scope="class")
    def roundtrip(self):
        mapping = {}
        for i in range(300):
            if i % 5 == 0:
                host = f"Host{i}.Example.COM"
            elif i % 5 == 1:
                host = f"xn--{i:04d}npi.example"
            elif i % 5 == 2:
                host = f"my-{i}-svc.corp{i}.internal"
            elif i % 5 == 3:
                host = f"host{i}"
            else:
                host = f"{i}.{i * 7 % 100}"
            if i % 3 == 0:
                ip = f"10.{i % 256}.{(i * 13) % 256}.{(i * 7) % 254 + 1}"
            elif i % 3 == 1:
                ip = f"2001:DB8::{i:x}"
            else:
                ip = "::ffff:" + f"192.0.{i % 256}.{(i * 3) % 255 + 1}"
            mapping[host] = ip
        generated = TOOL.execute(mode="generate", mapping=mapping)
        parsed = parse_text(generated["hosts_text"])
        return mapping, generated, parsed

    def test_mapping_size(self, roundtrip):
        mapping, _, _ = roundtrip
        assert len(mapping) == 300

    def test_generate_succeeds(self, roundtrip):
        _, generated, _ = roundtrip
        assert "error" not in generated
        assert generated["entry_count"] == 300

    def test_round_trip_recovers_mapping_exactly(self, roundtrip):
        mapping, _generated, parsed = roundtrip
        assert parsed["entries_total"] == 300
        entries = parsed["entries"]
        assert len(entries) == 300
        assert not parsed["entries_truncated"]
        for entry, (host, ip) in zip(entries, mapping.items(), strict=True):
            assert entry["canonical_hostname"] == host
            assert entry["aliases"] == []
            assert entry["ip"] == str(ipaddress.ip_address(ip))
            assert entry["valid"] is True

    def test_generate_deterministic(self, roundtrip):
        mapping, generated, _ = roundtrip
        again = TOOL.execute(mode="generate", mapping=mapping)
        assert again["hosts_text"] == generated["hosts_text"]

    def test_generate_format(self, roundtrip):
        _, generated, _ = roundtrip
        lines = generated["hosts_text"].splitlines()
        assert lines[0] == "# generated by hosts_file_tool"
        assert len(lines) == 301
        assert all(line.count(" ") == 1 for line in lines[1:])


# --------------------------------------------------------------------- #
# (e) real-world-shaped corpora — 10 files
# --------------------------------------------------------------------- #

MACOS_STYLE = (
    "##\n"
    "# Host Database\n"
    "#\n"
    "# localhost is used to configure the loopback interface\n"
    "# when no other entry matches.\n"
    "##\n"
    "127.0.0.1\tlocalhost\n"
    "255.255.255.255\tbroadcasthost\n"
    "::1\tlocalhost\n"
)

LINUX_MINIMAL = (
    "127.0.0.1 localhost\n"
    "::1 localhost ip6-localhost ip6-loopback\n"
    "ff02::1 ip6-allnodes\n"
    "ff02::2 ip6-allrouters\n"
    "127.0.1.1 mymachine\n"
)

DEV_OVERRIDES = (
    "# dev overrides\n"
    "10.0.0.5 ghost.example\n"
    "10.0.0.6 ghost.example\n"
    "::1 ghost.example\n"
    "10.0.0.9 web.local web\n"
    "10.0.0.9 web.local web\n"
)

DOCKER_TABS = (
    "127.0.0.1\tlocalhost\n"
    "172.17.0.2\tdb.internal\tdb\n"
    "172.17.0.3\tcache.internal\n"
)

CRLF_FILE = (
    "127.0.0.1 localhost\r\n"
    "10.0.0.9 web.example\r\n"
    "# a comment\r\n"
)

COMMENT_HEAVY = (
    "# header comment\n"
    "\n"
    "   # indented comment\n"
    "10.0.0.1 a.example # trailing comment on a\n"
    "10.0.0.2 b.example#tight comment\n"
    "\t\n"
    "10.0.0.3 c.example\n"
)

MIXED_ALIASES = (
    "10.0.0.5 web web.local api\n"
    "10.0.0.5 db\n"
    "2001:db8::5 web\n"
)

BLOCKING_127 = (
    "127.0.0.1 localhost\n"
    "127.0.0.1 ads.example.net\n"
    "0.0.0.0 tracker.example\n"
)

DUAL_STACK_DUPS = (
    "10.0.0.1 svc\n"
    "10.0.0.1 svc\n"
    "2001:db8::1 svc\n"
    "2001:db8::1 svc\n"
)


def build_pihole_sample() -> str:
    lines = ["# Pi-hole-style synthetic blocklist sample (not real data)"]
    lines.append("127.0.0.1 localhost")
    lines.append("::1 localhost")
    lines.extend(f"0.0.0.0 ad{i}.example.test" for i in range(5000))
    return "\n".join(lines) + "\n"


CORPORA = [
    "macos", MACOS_STYLE,
    "linux", LINUX_MINIMAL,
    "pihole", None,  # built lazily
    "dev", DEV_OVERRIDES,
    "docker", DOCKER_TABS,
    "crlf", CRLF_FILE,
    "comments", COMMENT_HEAVY,
    "aliases", MIXED_ALIASES,
    "blocking", BLOCKING_127,
    "dupstack", DUAL_STACK_DUPS,
]


class TestRealShapedCorpora:
    def test_corpora_count(self):
        assert len(CORPORA) == 20  # 10 names + 10 bodies
        texts = [b for b in CORPORA[1::2] if b is not None] + [build_pihole_sample()]
        assert len(texts) == 10

    def test_macos_style(self):
        result = parse_text(MACOS_STYLE)
        assert result["total_lines"] == 9
        assert result["comment_lines"] == 6
        assert result["entries_total"] == 3
        assert result["crlf_lines"] == 0
        entries = entry_by_line(result)
        assert entries[8]["canonical_hostname"] == "broadcasthost"
        assert entries[8]["ip"] == "255.255.255.255"
        # tabs tolerated (info only)
        assert all(f["severity"] == "info" for f in result["findings"])

    def test_linux_minimal_clean(self):
        result = parse_text(LINUX_MINIMAL)
        assert result["findings"] == []
        assert result["summary"]["unique_hostnames"] == 6
        assert result["summary"]["valid_entries"] == 5

    def test_pihole_5k_parse_under_two_seconds(self):
        text = build_pihole_sample()
        start = time.perf_counter()
        result = parse_text(text)
        elapsed = time.perf_counter() - start
        assert elapsed < 2.0, f"parse took {elapsed:.3f}s"
        assert result["entries_total"] == 5002
        assert result["entries_truncated"] is True
        assert len(result["entries"]) == TOOL.max_entries_listed
        assert result["findings"] == []
        assert result["summary"]["unique_hostnames"] == 5001

    def test_pihole_analyze(self):
        text = build_pihole_sample()
        result = TOOL.execute(mode="analyze", hosts_text=text)
        assert result["unique_hosts"] == 5001
        assert result["per_host_truncated"] is True
        assert len(result["per_host"]) == TOOL.max_per_host
        assert result["blocking_entries"]["count"] == 5000
        assert len(result["blocking_entries"]["sample"]) == TOOL.max_blocking_sample
        assert result["localhost_coverage"] == {
            "ipv4": True, "ipv6": True, "recommendations": [],
        }
        assert result["ipv6_readiness"]["ipv6_entries"] == 1
        assert result["stats"]["ipv4_entries"] == 5001

    def test_dev_overrides_conflicts_and_duplicates(self):
        result = parse_text(DEV_OVERRIDES)
        codes = codes_by_line(result)
        assert "conflicting_entry" in codes.get(3, set())
        assert "duplicate_hostname_ip" in codes.get(6, set())
        assert result["summary"]["warning"] >= 2
        # aliases web + web.local share line 5
        entries = entry_by_line(result)
        assert entries[5]["aliases"] == ["web"]

    def test_docker_tabs(self):
        result = parse_text(DOCKER_TABS)
        tab = [f for f in result["findings"] if f["code"] == "tab_separator"]
        assert len(tab) == 1 and tab[0]["line"] is None  # aggregated, file-level
        entries = entry_by_line(result)
        assert entries[2]["canonical_hostname"] == "db.internal"
        assert entries[2]["aliases"] == ["db"]

    def test_crlf_tolerated_and_counted(self):
        result = parse_text(CRLF_FILE)
        assert result["crlf_lines"] == 3
        assert result["entries_total"] == 2
        assert result["findings"] == []

    def test_comment_heavy(self):
        result = parse_text(COMMENT_HEAVY)
        assert result["comment_lines"] == 2
        assert result["blank_lines"] == 2
        assert result["entries_total"] == 3
        entries = entry_by_line(result)
        assert entries[4]["comment_attached"] == "trailing comment on a"
        assert entries[5]["comment_attached"] == "tight comment"
        assert entries[7]["comment_attached"] is None

    def test_mixed_aliases(self):
        result = parse_text(MIXED_ALIASES)
        assert result["summary"]["unique_hostnames"] == 4  # web, web.local, api, db
        hit = TOOL.execute(mode="lookup", hosts_text=MIXED_ALIASES, hostname="api")
        assert hit["addresses"] == ["10.0.0.5"]
        assert hit["aliases"] == ["web.local", "api"]
        assert hit["canonical"] is False

    def test_blocking_127_analyze(self):
        result = TOOL.execute(mode="analyze", hosts_text=BLOCKING_127)
        assert result["blocking_entries"]["count"] == 2
        names = {s["hostname"] for s in result["blocking_entries"]["sample"]}
        assert names == {"ads.example.net", "tracker.example"}
        assert "neutral" in result["blocking_entries"]["note"]

    def test_dual_stack_duplicates(self):
        result = parse_text(DUAL_STACK_DUPS)
        assert result["summary"]["warning"] == 2  # two duplicate pairs
        hit = TOOL.execute(
            mode="lookup", hosts_text=DUAL_STACK_DUPS, hostname="svc", family="v4"
        )
        assert hit["addresses"] == ["10.0.0.1"]
        assert hit["overridden_by_earlier"] == [
            {"ip": "10.0.0.1", "line": 2, "family": "v4"}
        ]


# --------------------------------------------------------------------- #
# (f) comment / tabs / CRLF tolerance battery
# --------------------------------------------------------------------- #


class TestToleranceBattery:
    def test_full_line_comment(self):
        result = parse_text("# just a comment\n10.0.0.1 a.example\n")
        assert result["comments"] == [{"line": 1, "text": "just a comment"}]
        assert result["entries_total"] == 1

    def test_comment_text_truncated(self):
        result = parse_text("# " + "c" * 500 + "\n")
        assert result["comments"][0]["text"].endswith("...")
        assert len(result["comments"][0]["text"]) == 120

    def test_raw_line_truncated(self):
        result = parse_text("10.0.0.1 " + "a" * 200 + ".example\n")
        assert result["entries"][0]["raw"].endswith("...")
        assert len(result["entries"][0]["raw"]) == 80

    def test_blank_and_whitespace_lines(self):
        result = parse_text("\n   \n\t\n10.0.0.1 a.example\n")
        assert result["blank_lines"] == 3
        assert result["total_lines"] == 4

    def test_leading_whitespace_before_ip(self):
        result = parse_text("   10.0.0.1   a.example\n")
        assert result["entries"][0]["ip"] == "10.0.0.1"
        assert result["findings"] == []

    def test_hash_without_space_splits_comment(self):
        result = parse_text("10.0.0.1 a.example#note\n")
        assert result["entries"][0]["comment_attached"] == "note"

    def test_semicolon_comment_line_flagged_and_parsed_as_data(self):
        result = parse_text("; a semicolon comment\n")
        codes = codes_by_line(result)
        assert "semicolon_comment" in codes.get(1, set())
        # POSIX treats only '#' as a comment, so the ';' is data: an
        # invalid address token plus the informational note.
        assert "malformed_ip" in codes.get(1, set())
        assert result["entries"][0]["ip_raw"] == ";"

    def test_semicolon_stats(self):
        result = parse_text("; one\n; two\n10.0.0.1 a.example\n")
        assert result["stats"]["semicolon_comment_lines"] == 2

    def test_crlf_only_terminators(self):
        result = parse_text("10.0.0.1 a.example\r\n10.0.0.2 b.example\r\n")
        assert result["crlf_lines"] == 2
        assert result["entries_total"] == 2
        assert result["findings"] == []

    def test_terminating_newline_no_phantom_line(self):
        assert parse_text("10.0.0.1 a.example\n")["total_lines"] == 1
        assert parse_text("10.0.0.1 a.example")["total_lines"] == 1

    def test_uppercase_aggregated_info(self):
        result = parse_text("10.0.0.1 Web.Example\n10.0.0.2 OTHER.Example\n")
        upper = [f for f in result["findings"] if f["code"] == "uppercase_hostname"]
        assert len(upper) == 1
        assert upper[0]["line"] is None
        assert result["stats"]["uppercase_hostname_lines"] == 2
        entries = entry_by_line(result)
        assert entries[1]["canonical_hostname"] == "Web.Example"  # raw preserved

    def test_tab_stats(self):
        result = parse_text("10.0.0.1\ta.example\n10.0.0.2\tb.example\n")
        assert result["stats"]["tab_lines"] == 2
        assert result["summary"]["valid_entries"] == 2


# --------------------------------------------------------------------- #
# parse findings: conflicts, duplicates, localhost conventions
# --------------------------------------------------------------------- #


class TestFindings:
    def test_conflict_reports_both_and_winner(self):
        result = parse_text("10.0.0.5 svc\n10.0.0.6 svc\n")
        finding = next(f for f in result["findings"] if f["code"] == "conflicting_entry")
        assert finding["line"] == 2
        assert "10.0.0.5" in finding["message"] and "10.0.0.6" in finding["message"]
        assert "line 1" in finding["message"]

    def test_cross_family_coexistence_not_a_conflict(self):
        result = parse_text("10.0.0.5 svc\n2001:db8::1 svc\n")
        assert not any(f["code"] == "conflicting_entry" for f in result["findings"])

    def test_duplicate_identical_pair_flagged(self):
        result = parse_text("10.0.0.5 svc\n10.0.0.5 svc\n10.0.0.5 svc\n")
        dups = [f for f in result["findings"] if f["code"] == "duplicate_hostname_ip"]
        assert [d["line"] for d in dups] == [2, 3]

    def test_missing_hostname(self):
        result = parse_text("10.0.0.1\n")
        assert "missing_hostname" in codes_by_line(result).get(1, set())
        entry = result["entries"][0]
        assert entry["ip"] == "10.0.0.1"  # address still reported
        assert entry["canonical_hostname"] is None
        assert entry["valid"] is False

    def test_loopback_without_localhost(self):
        result = parse_text("127.0.0.1 mymachine\n")
        assert "loopback_without_localhost" in codes_by_line(result).get(1, set())

    def test_localhost_as_alias(self):
        result = parse_text("127.0.0.1 mymachine localhost\n")
        assert "localhost_not_canonical" in codes_by_line(result).get(1, set())

    def test_localhost_non_loopback_warning(self):
        result = parse_text("10.0.0.9 localhost\n")
        assert "localhost_non_loopback" in codes_by_line(result).get(1, set())

    def test_clean_localhost_lines_no_findings(self):
        result = parse_text("127.0.0.1 localhost\n::1 localhost\n")
        assert result["findings"] == []

    def test_invalid_alias_but_valid_canonical(self):
        result = parse_text("10.0.0.9 good.example bad!name\n")
        entry = result["entries"][0]
        assert entry["canonical_hostname"] == "good.example"
        assert entry["aliases"] == []
        assert entry["invalid_hostnames"] == [{"token": "bad!name", "code": "invalid_chars"}]
        assert entry["valid"] is False
        # the valid canonical is still resolvable
        hit = TOOL.execute(mode="lookup", hosts_text="10.0.0.9 good.example bad!name\n",
                           hostname="good.example")
        assert hit["addresses"] == ["10.0.0.9"]

    def test_severity_totals_exact(self):
        result = parse_text(
            "999.1.1.1 a\n10.0.0.1 b b\n10.0.0.2 c\n; semi\n10.0.0.3 D.Example\n"
        )
        assert result["summary"]["error"] >= 2  # malformed ip + missing hostname + ...
        assert result["summary"]["warning"] >= 1
        assert result["summary"]["info"] >= 1
        total = (result["summary"]["error"] + result["summary"]["warning"]
                 + result["summary"]["info"])
        assert total == result["findings_total"] >= len(result["findings"])

    def test_findings_cap_and_exact_total(self):
        text = "\n".join(f"999.{i % 9}.{i % 7}.{i % 5} h{i}" for i in range(250)) + "\n"
        result = parse_text(text)
        assert len(result["findings"]) == TOOL.max_findings
        assert result["findings_truncated"] is True
        assert result["findings_total"] == 250

    def test_comments_cap(self):
        text = "\n".join(f"# c{i}" for i in range(2500)) + "\n10.0.0.1 a\n"
        result = parse_text(text)
        assert len(result["comments"]) == TOOL.max_comments_listed
        assert result["comments_truncated"] is True
        assert result["comments_total"] == 2500

    def test_parse_deterministic(self):
        text = MACOS_STYLE + LINUX_MINIMAL + DEV_OVERRIDES
        assert parse_text(text) == parse_text(text)


# --------------------------------------------------------------------- #
# analyze mode
# --------------------------------------------------------------------- #


class TestAnalyzeMode:
    def test_per_host_summary(self):
        result = TOOL.execute(mode="analyze", hosts_text=DEV_OVERRIDES)
        ghost = result["per_host"]["ghost.example"]
        assert ghost["ips"] == ["10.0.0.5", "10.0.0.6", "::1"]
        assert ghost["families"] == ["v4", "v6"]
        assert ghost["lines"] == [2, 3, 4]
        conflict = ghost["conflicts"][0]
        assert conflict["family"] == "v4"
        assert conflict["winner"] == {"ip": "10.0.0.5", "line": 2}
        assert conflict["losers"] == [{"ip": "10.0.0.6", "line": 3}]

    def test_localhost_coverage_recommendations(self):
        result = TOOL.execute(mode="analyze", hosts_text="10.0.0.1 only.example\n")
        coverage = result["localhost_coverage"]
        assert coverage["ipv4"] is False and coverage["ipv6"] is False
        assert len(coverage["recommendations"]) == 2
        assert any("127.0.0.1" in r for r in coverage["recommendations"])
        assert any("::1" in r for r in coverage["recommendations"])

    def test_ipv6_readiness(self):
        result = TOOL.execute(mode="analyze", hosts_text=LINUX_MINIMAL)
        readiness = result["ipv6_readiness"]
        assert readiness["ipv6_entries"] == 3
        assert readiness["has_ipv6_localhost"] is True
        assert readiness["distinct_ipv6_hosts"] == 5
        assert readiness["ipv4_only_hosts"] == 1  # mymachine

    def test_blocking_excludes_localhost(self):
        result = TOOL.execute(mode="analyze", hosts_text="0.0.0.0 localhost\n0.0.0.0 ads.example\n")
        assert result["blocking_entries"]["count"] == 1

    def test_stats_block(self):
        result = TOOL.execute(mode="analyze", hosts_text=DOCKER_TABS)
        stats = result["stats"]
        assert stats["total_entries"] == 3
        assert stats["unique_ips"] == 3
        assert stats["tab_lines"] == 3


# --------------------------------------------------------------------- #
# diff mode
# --------------------------------------------------------------------- #


class TestDiffMode:
    def test_added_removed_changed(self):
        a = "10.0.0.1 keep.example\n10.0.0.2 drop.example\n10.0.0.3 move.example\n"
        b = "10.0.0.1 keep.example\n10.0.0.9 move.example\n10.0.0.4 add.example\n"
        result = TOOL.execute(mode="diff", hosts_text_a=a, hosts_text_b=b)
        assert [i["hostname"] for i in result["added"]] == ["add.example"]
        assert [i["hostname"] for i in result["removed"]] == ["drop.example"]
        assert [i["hostname"] for i in result["changed"]] == ["move.example"]
        assert result["counts"] == {"added": 1, "removed": 1, "changed": 1, "unchanged": 1}
        changed = result["changed"][0]
        assert changed["a"]["v4"] == {"ip": "10.0.0.3", "line": 3}
        assert changed["b"]["v4"] == {"ip": "10.0.0.9", "line": 2}

    def test_family_gain_is_a_change(self):
        a = "10.0.0.1 dual.example\n"
        b = "10.0.0.1 dual.example\n2001:db8::1 dual.example\n"
        result = TOOL.execute(mode="diff", hosts_text_a=a, hosts_text_b=b)
        assert result["counts"]["changed"] == 1
        assert result["changed"][0]["b"]["v6"] == {"ip": "2001:db8::1", "line": 2}
        assert result["changed"][0]["a"]["v6"] is None

    def test_diff_uses_first_winner_per_side(self):
        a = "10.0.0.1 svc\n10.0.0.2 svc\n"
        b = "10.0.0.1 svc\n10.0.0.3 svc\n"
        result = TOOL.execute(mode="diff", hosts_text_a=a, hosts_text_b=b)
        assert result["counts"]["changed"] == 0
        assert result["counts"]["unchanged"] == 1

    def test_alias_view_of_diff(self):
        a = "10.0.0.1 web\n"
        b = "10.0.0.1 other web\n"
        result = TOOL.execute(mode="diff", hosts_text_a=a, hosts_text_b=b)
        # 'web' maps to the same first-winner address on both sides, so it
        # is unchanged; only the new canonical name is added.
        assert [i["hostname"] for i in result["added"]] == ["other"]
        assert result["removed"] == []
        assert result["counts"]["unchanged"] == 1

    def test_diff_caps(self):
        a = "10.0.0.1 base.example\n"
        b = "10.0.0.1 base.example\n" + "".join(
            f"10.0.1.{i % 250 + 1} extra{i}.example\n" for i in range(600)
        )
        result = TOOL.execute(mode="diff", hosts_text_a=a, hosts_text_b=b)
        assert len(result["added"]) == TOOL.max_diff_items
        assert result["added_truncated"] is True
        assert result["counts"]["added"] == 600

    def test_diff_deterministic_order(self):
        a = "10.0.0.1 z.example\n10.0.0.2 a.example\n"
        b = "10.0.0.1 z.example\n10.0.0.2 a.example\n"
        r1 = TOOL.execute(mode="diff", hosts_text_a=a, hosts_text_b=b)
        assert r1["counts"]["unchanged"] == 2
        assert r1["added"] == [] and r1["removed"] == [] and r1["changed"] == []


# --------------------------------------------------------------------- #
# generate mode errors
# --------------------------------------------------------------------- #


class TestGenerateErrors:
    def test_invalid_ip_payload(self):
        result = TOOL.execute(mode="generate", mapping={"web": "999.999.1.1"})
        assert result["error"]["type"] == "invalid_ip"
        assert result["error"]["input"] == "999.999.1.1"
        assert result["error"]["hostname"] == "web"

    def test_zone_id_ip_payload(self):
        result = TOOL.execute(mode="generate", mapping={"web": "fe80::1%eth0"})
        assert result["error"]["type"] == "invalid_ip"
        assert result["error"]["code"] == "ip_zone_id"

    def test_invalid_hostname_payload(self):
        result = TOOL.execute(mode="generate", mapping={"-bad.example": "10.0.0.1"})
        assert result["error"]["type"] == "invalid_hostname"
        assert result["error"]["code"] == "label_hyphen_edge"

    def test_unicode_hostname_payload(self):
        result = TOOL.execute(mode="generate", mapping={"exämple.com": "10.0.0.1"})
        assert result["error"]["type"] == "invalid_hostname"
        assert result["error"]["code"] == "non_ascii"
        assert "punycode" in result["error"]["message"]

    def test_underscore_hostname_rejected_in_generate(self):
        result = TOOL.execute(mode="generate", mapping={"my_host": "10.0.0.1"})
        assert result["error"]["type"] == "invalid_hostname"
        assert result["error"]["code"] == "underscore"

    def test_ip_normalized_in_output(self):
        result = TOOL.execute(mode="generate", mapping={"web": "2001:0DB8::0001"})
        assert result["hosts_text"].splitlines()[1] == "2001:db8::1 web"

    def test_mapping_order_preserved(self):
        mapping = {"z.example": "10.0.0.1", "a.example": "10.0.0.2", "m.example": "10.0.0.3"}
        result = TOOL.execute(mode="generate", mapping=mapping)
        assert result["hostnames"] == ["z.example", "a.example", "m.example"]


# --------------------------------------------------------------------- #
# parameter validation
# --------------------------------------------------------------------- #


class TestParameterValidation:
    def test_unknown_mode(self):
        with pytest.raises(ValueError, match="hosts_file_tool"):
            TOOL.execute(mode="nope", hosts_text="10.0.0.1 a\n")

    def test_missing_hosts_text(self):
        with pytest.raises(ValueError, match="hosts_text"):
            TOOL.execute(mode="parse")
        with pytest.raises(ValueError, match="hosts_text_a"):
            TOOL.execute(mode="diff", hosts_text_b="10.0.0.1 a\n")

    def test_blank_hosts_text(self):
        with pytest.raises(ValueError, match="non-empty"):
            TOOL.execute(mode="parse", hosts_text="   \n ")

    def test_wrong_type_hosts_text(self):
        with pytest.raises(ValueError, match="hosts_text"):
            TOOL.execute(mode="parse", hosts_text=["10.0.0.1 a\n"])

    def test_line_limit(self):
        text = "a\n" * 200000 + "a"
        with pytest.raises(ValueError, match="line limit"):
            TOOL.execute(mode="parse", hosts_text=text)

    def test_bad_family(self):
        with pytest.raises(ValueError, match="family"):
            TOOL.execute(mode="lookup", hosts_text="10.0.0.1 a\n", hostname="a", family="ipv9")
        with pytest.raises(ValueError, match="family"):
            TOOL.execute(mode="lookup", hosts_text="10.0.0.1 a\n", hostname="a", family="IPV4")

    def test_missing_lookup_hostname(self):
        with pytest.raises(ValueError, match="hostname"):
            TOOL.execute(mode="lookup", hosts_text="10.0.0.1 a\n", hostname="  ")

    def test_mapping_type_and_emptiness(self):
        with pytest.raises(ValueError, match="mapping"):
            TOOL.execute(mode="generate", mapping="not-a-dict")
        with pytest.raises(ValueError, match="mapping"):
            TOOL.execute(mode="generate", mapping={})

    def test_mapping_cap(self):
        mapping = {f"h{i}.example": "10.0.0.1" for i in range(1001)}
        with pytest.raises(ValueError, match="1000-entry limit"):
            TOOL.execute(mode="generate", mapping=mapping)

    def test_mapping_case_collision(self):
        with pytest.raises(ValueError, match="case-insensitively"):
            TOOL.execute(mode="generate", mapping={"web.example": "10.0.0.1", "Web.Example": "10.0.0.2"})

    def test_mapping_value_type(self):
        with pytest.raises(ValueError, match="IP for"):
            TOOL.execute(mode="generate", mapping={"web.example": 5})


# --------------------------------------------------------------------- #
# package export / registration
# --------------------------------------------------------------------- #


class TestRegistration:
    def test_exported_from_package(self):
        from agentuniverse.agent.action.tool.common_tool import HostsFileTool as Exported
        assert Exported is HostsFileTool

    def test_tool_metadata(self):
        assert TOOL.name == "hosts_file_tool"
        assert set(TOOL.MODES) == {"parse", "lookup", "analyze", "diff", "generate"}
