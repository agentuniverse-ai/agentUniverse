#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: user_agent_tool.py

"""Offline User-Agent string parser — browsers, engines, OS and devices.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency User-Agent analyzer
agents can call when they must understand a ``User-Agent`` header:
which browser family and version claims to be behind it, which
rendering engine that implies, which operating system it reports and
whether the client is a desktop browser, a phone, a tablet or a bot.

This tool complements ``LogParserTool``: that tool parses *log lines*
in which the User-Agent is one opaque quoted field, while this tool
parses the User-Agent *string itself* into structured components.

Two modes, all built purely on the standard library:

* ``parse`` — User-Agent string → a structured result with
  ``browser`` (``name`` + ``version``), ``engine`` (``name`` +
  ``version``), ``os`` (``name`` + ``version``), ``device``
  (``type`` + optional ``vendor`` / ``model``), the raw input under
  ``raw``, an ``is_bot`` flag and a ``short`` one-liner.

* ``short`` — User-Agent string → just the one-liner, e.g.
  ``"Chrome 120 / Windows 10 / desktop"`` (browser major version /
  OS major version / device type; unknown parts read ``unknown``).

Detection order (each step only runs on what the previous steps have
not already claimed — the order IS the disambiguation):

1. **Bots first.** A case-insensitive hint scan for
   ``bot|crawl|spider|slurp|bingpreview|headlesschrome`` plus the
   common non-browser HTTP clients (``curl``, ``wget``,
   ``python-requests``, ``python-urllib``, ``go-http-client``,
   ``postmanruntime``, ``axios``, ``okhttp``, ``dalvik``,
   ``httpclient``) marks ``is_bot=true`` and ``device.type=bot``
   *before* any browser matching, so compatibility tokens embedded in
   bot strings (Googlebot carries ``Chrome/`` and ``Safari/``) are
   never misread as the browser. The bot's own token
   (``Googlebot/2.1``, ``curl/8.4.0``) is reported as the browser
   name/version when present.

2. **Browsers.** Priority order: ``SamsungBrowser/`` → Samsung
   Internet; ``Edg/``, ``EdgA/`` (Android) or ``EdgiOS/`` → the
   Chromium-based Edge; ``Edge/`` → legacy EdgeHTML Edge;
   ``OPR/``, ``OPiOS/`` or ``Opera/`` → Opera; ``IEMobile/`` /
   ``MSIE`` → Internet Explorer; ``Firefox/`` / ``FxiOS/`` →
   Firefox; a ``Chromium`` token → Chromium; ``CriOS/`` or
   ``Chrome/`` → Chrome — reached only when no Chromium-family
   sibling has already claimed the string, which is exactly the
   documented rule *``Chrome/`` without ``Edg/``, ``OPR/`` or
   ``Chromium`` means Chrome*; finally ``Safari/`` without any
   Chrome-family token → Safari, whose version comes from the
   ``Version/`` token. A ``Trident/`` + ``rv:`` string without
   ``MSIE`` is the IE 11 shape. Legacy Opera froze ``Opera/`` at
   9.80 and carried the real version in ``Version/``; that unfreezing
   is applied.

3. **Engines.** ``Trident/`` → Trident (checked first because in
   IE 11 the ``rv:`` token is the *browser* version, not the
   engine's); legacy ``Edge/`` → EdgeHTML (no version token of its
   own); ``Presto/`` → Presto; ``rv:`` → Gecko with that version;
   ``AppleWebKit/x … Chrome/y Safari/z`` → **Blink, version None** —
   a documented heuristic: Chromium-based browsers are the only
   WebKit-applewebkit bearers that also carry a Chrome-family browser
   token, and they actually render with Blink, a WebKit fork that has
   no version token of its own (the ``AppleWebKit/537.36`` build
   number they carry is frozen compatibility noise). On iOS the same
   browsers (``CriOS/``, ``FxiOS/``, ``EdgiOS/``, ``OPiOS/``) report
   **WebKit** instead, because Apple requires WebKit there. Bare
   ``AppleWebKit/x`` (Safari) → WebKit with that build version. A
   ``Gecko/`` date token not preceded by ``like`` → Gecko without a
   version; the ``like Gecko`` compatibility marker alone never
   implies the Gecko engine.

4. **Operating systems.** ``Windows Phone`` is checked *before*
   ``Android`` (Lumia strings carry both) and before ``Windows NT``.
   ``Windows NT`` versions map through a fixed table
   (``6.1``→7, ``6.2``→8, ``6.3``→8.1, ``6.0``→Vista, ``5.1``/``5.2``
   →XP, ``5.0``→2000, ``10.0``→10 — Windows 11 is deliberately
   reported as 10 because its User-Agent is byte-identical on NT
   ``10.0``; the distinction is not honestly derivable from the
   string). ``Android 13`` → Android 13 with the device model taken
   from the token that follows (``Android 13; SM-G991B`` → vendor
   Samsung, model ``SM-G991B``; a glued `` Build/…`` suffix and
   placeholder tokens like ``K``, ``Mobile``, ``wv`` are skipped).
   ``CPU iPhone OS 17_1`` → iOS 17.1 (underscores become dots);
   ``iPad; CPU OS 16_6`` → iPadOS 16.6; ``Mac OS X 10_15_7`` →
   10.15.7; ``CrOS <arch> N`` → ChromeOS N; ``Ubuntu``/``Fedora``
   tokens are named; a bare ``Linux``/``X11`` → Linux (Android is
   matched earlier).

5. **Device.** bot → ``bot``; ``iPad`` or a ``Tablet`` token or
   Android *without* the ``Mobile`` token → ``tablet`` (Android
   tablet User-Agents simply omit ``Mobile``); ``iPhone``, any
   ``Mobile`` token, Windows Phone or Opera Mini → ``mobile``; a
   desktop OS token (Windows / Mac OS X / Linux / ChromeOS) →
   ``desktop``; otherwise ``unknown``. Vendors: Apple for
   iPhone/iPad/Mac, a documented prefix table for Android models
   (``SM-``/``GT-``/``SC-``→Samsung, ``Pixel``→Google, ``LG-``/
   ``LM-``→LG, ``Redmi``/``POCO``/``MIX``/``Mi ``→Xiaomi, ``moto``→
   Motorola, ``CPH``/``OPPO``→OPPO, ``vivo``/``iQOO``→vivo,
   ``ONEPLUS``→OnePlus, ``HUAWEI``/``Honor``→Huawei, ``Nokia``→
   Nokia), and Nokia/Microsoft for Windows Phone Lumias.

Honest limitations (documented, not hidden): User-Agent strings are
freely spoofable client-supplied text — this tool reports what the
string *claims*, never a verified identity; no Client Hints
(``Sec-CH-UA``) are consulted because there is no header access
offline; version maps (Windows NT, frozen macOS/iOS versions, legacy
Opera) are best-effort snapshots of how real User-Agents are frozen
today; vendor/model extraction only knows the documented prefix
table; and anything unrecognised is reported as ``unknown`` rather
than guessed.

Input validation is strict and happens before any computation: a
missing or unknown ``mode``, a ``user_agent`` that is not a string
(not-a-number, booleans, lists), empty or whitespace-only, longer
than the size cap, or containing control characters (a User-Agent is
a single header line — NUL, CR, LF, TAB and other C0 controls are
rejected) raise a ``ValueError``, mirroring the other common tools.
Everything is deterministic: no randomness, no clock, no network.
"""

import re
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# Input size cap. Real User-Agent headers are well under 1 KB; 8,192
# characters leaves generous headroom for padded-but-legal strings.
_MAX_USER_AGENT_CHARS = 8_192

# Bots and non-browser HTTP clients. The first line is the documented
# hint set from the issue; the second line covers library clients that
# are unambiguously not interactive browsers (curl has no "bot" in it
# yet is a command-line client, so it needs its own token).
_BOT_HINT_RE = re.compile(
    r"bot|crawl|spider|slurp|bingpreview|headlesschrome"
    r"|curl|wget|python-requests|python-urllib|go-http-client"
    r"|postmanruntime|axios|okhttp|dalvik|httpclient|httpcomponent",
    re.IGNORECASE,
)
# A bot's own name/version token, e.g. "Googlebot/2.1".
_BOT_TOKEN_RE = re.compile(
    r"([A-Za-z0-9_.+-]*(?:bot|crawl(?:er)?|spider|slurp"
    r"|bingpreview|headlesschrome)[A-Za-z0-9_.+-]*)"
    r"/([0-9][\w.+-]*)",
    re.IGNORECASE,
)
# Library clients with a version token but no bot-ish suffix.
_LIB_TOKEN_RE = re.compile(
    r"\b(curl|wget|python-requests|python-urllib|go-http-client"
    r"|postmanruntime|axios|okhttp|dalvik|java|apache-httpclient)"
    r"/([0-9][\w.+-]*)",
    re.IGNORECASE,
)

# Browser token extractors (version in group 1 of each).
_RE_SAMSUNG = re.compile(r"SamsungBrowser/([0-9][0-9.]*)")
_RE_EDGE_NEW = re.compile(r"\bEdg(?:A|iOS)?/([0-9][0-9.]*)")
_RE_EDGE_OLD = re.compile(r"\bEdge/([0-9][0-9.]*)")
_RE_OPR = re.compile(r"OPR/([0-9][0-9.]*)")
_RE_OPIOS = re.compile(r"OPiOS/([0-9][0-9.]*)")
_RE_OPERA_OLD = re.compile(r"Opera[/ ]([0-9][0-9.]*)")
_RE_IEMOBILE = re.compile(r"IEMobile/([0-9][0-9.]*)")
_RE_MSIE = re.compile(r"MSIE\s+([0-9][0-9.]*)")
_RE_FIREFOX = re.compile(r"Firefox/([0-9][0-9.]*)")
_RE_FXIOS = re.compile(r"FxiOS/([0-9][0-9.]*)")
_RE_CHROMIUM = re.compile(r"Chromium/([0-9][0-9.]*)")
_RE_CHROMIUM_WORD = re.compile(r"Chromium", re.IGNORECASE)
_RE_CRIOS = re.compile(r"CriOS/([0-9][0-9.]*)")
_RE_CHROME = re.compile(r"Chrome/([0-9][0-9.]*)")
_RE_SAFARI = re.compile(r"Safari/[0-9.]+")
_RE_VERSION = re.compile(r"Version/([0-9][0-9.]*)")
_RE_RV = re.compile(r"rv:([0-9][0-9.]*)")

# Engine token extractors.
_RE_TRIDENT = re.compile(r"Trident/([0-9][0-9.]*)")
_RE_PRESTO = re.compile(r"Presto/([0-9][0-9.]*)")
_RE_APPLEWEBKIT = re.compile(r"AppleWebKit/([0-9][0-9.]*)")
# A real Gecko date token ("Gecko/20100101"), never the frozen
# compatibility marker "like Gecko".
_RE_GECKO_DATE = re.compile(r"(?<![Ll]ike )Gecko/([0-9][0-9.]*)")

# OS token extractors.
_RE_WINDOWS_PHONE = re.compile(r"Windows Phone(?: OS)?\s+([0-9][0-9.]*)")
_RE_ANDROID = re.compile(r"Android\s+([0-9][0-9.]*)")
# The parenthesized platform segment after the Android version; one
# level of nested parentheses is tolerated because real model names
# such as "moto g(8) power" contain them.
_RE_ANDROID_SEG = re.compile(r"Android\s+[0-9.]+;((?:[^()]|\([^)]*\))*)\)")
_RE_IPHONE_OS = re.compile(r"(?:CPU\s+)?iPhone\s+OS\s+([0-9_]+)")
_RE_IPAD_OS = re.compile(r"CPU\s+OS\s+([0-9_]+)")
_RE_MAC_OS = re.compile(r"Mac\s+OS\s+X\s*([0-9_.]+)")
_RE_WINDOWS_NT = re.compile(r"Windows\s+NT\s+([0-9.]+)")
_RE_CROS = re.compile(r"CrOS\s+\S+\s+([0-9][0-9.]*)")
_RE_LUMIA = re.compile(r"(Lumia\s+[0-9][0-9A-Za-z]*)", re.IGNORECASE)

# Windows NT → marketing-name map. Windows 11 is NOT in the map on
# purpose: its User-Agent is identical to Windows 10's (NT 10.0).
_WINDOWS_NT_MAP: Dict[str, str] = {
    "5.0": "2000",
    "5.1": "XP",
    "5.2": "XP",
    "6.0": "Vista",
    "6.1": "7",
    "6.2": "8",
    "6.3": "8.1",
    "6.4": "10",
    "10.0": "10",
}

# Chromium-family browsers whose AppleWebKit token implies Blink.
_BLINK_BROWSERS = frozenset(
    {"Chrome", "Chromium", "Edge", "Opera", "Samsung Internet"}
)
# iOS-only browser tokens: Apple mandates WebKit, never Blink.
_IOS_BROWSER_TOKEN_RE = re.compile(r"CriOS/|FxiOS/|EdgiOS/|OPiOS/")

# Android model tokens that are placeholders, never device models.
_NON_MODEL_TOKENS = frozenset(
    {"mobile", "tablet", "tv", "build", "wv", "webview", "k", "u"}
)

# Documented Android model prefix → vendor table (longest first so
# "POCO" beats a hypothetical "P..." rule; evaluated in order).
_ANDROID_VENDOR_PREFIXES: Tuple[Tuple[str, str], ...] = (
    ("SM-", "Samsung"),
    ("GT-", "Samsung"),
    ("SC-", "Samsung"),
    ("SCH-", "Samsung"),
    ("Pixel", "Google"),
    ("LG-", "LG"),
    ("LM-", "LG"),
    ("Redmi", "Xiaomi"),
    ("POCO", "Xiaomi"),
    ("MIX", "Xiaomi"),
    ("Mi ", "Xiaomi"),
    ("MI ", "Xiaomi"),
    ("moto", "Motorola"),
    ("CPH", "OPPO"),
    ("OPPO", "OPPO"),
    ("iQOO", "vivo"),
    ("vivo", "vivo"),
    ("ONEPLUS", "OnePlus"),
    ("OnePlus", "OnePlus"),
    ("HUAWEI", "Huawei"),
    ("Honor", "Huawei"),
    ("Nokia", "Nokia"),
)


def _search_group(pattern: "re.Pattern[str]", text: str) -> Optional[str]:
    """Return group(1) of the first match, or None."""
    match = pattern.search(text)
    return match.group(1) if match else None


def _undots(version: Optional[str]) -> Optional[str]:
    """Turn ``17_1`` style OS versions into ``17.1``."""
    return version.replace("_", ".") if version is not None else None


class UserAgentTool(Tool):
    """Offline User-Agent string parser (browser / engine / OS / device).

    Attributes:
        max_user_agent_chars (int): Upper bound on the ``user_agent``
            input length.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "user_agent_tool"
    description: str = (
        "User-Agent string parser — offline browser/engine/OS/device "
        "detection from User-Agent strings, pure Python stdlib, no "
        "network, no Client Hints. mode='parse' returns structured "
        "components (browser name+version, engine name+version, os "
        "name+version, device type+vendor+model, is_bot, short "
        "one-liner, raw input); mode='short' returns just the one-"
        "liner (e.g. 'Chrome 120 / Windows 10 / desktop'). Bots are "
        "detected first so compatibility tokens inside bot strings "
        "are never misread; Chromium-family AppleWebKit strings are "
        "reported as Blink (WebKit on iOS); Windows 11 is honestly "
        "reported as Windows 10 because its User-Agent is "
        "indistinguishable. User-Agent strings are freely spoofable — "
        "this tool reports claims, not verified identity."
    )

    MODES: ClassVar[tuple] = ("parse", "short")

    max_user_agent_chars: int = _MAX_USER_AGENT_CHARS

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: Any = None,
        user_agent: Any = None,
    ) -> Dict[str, Any]:
        """Run one User-Agent analysis.

        Args:
            mode (str): One of ``parse`` / ``short``.
            user_agent (str): The User-Agent string to analyze.

        Returns:
            Dict[str, Any]: ``parse`` — ``raw``, ``is_bot``,
                ``browser`` / ``engine`` / ``os`` / ``device``
                dictionaries and a ``short`` one-liner; ``short`` —
                ``raw``, ``is_bot`` and the ``short`` one-liner.

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        ua = self._validate_user_agent(user_agent)
        is_bot = _BOT_HINT_RE.search(ua) is not None
        browser, engine_family = self._detect_browser(ua)
        os_name, os_version = self._detect_os(ua)
        engine = self._detect_engine(ua, browser, engine_family, os_name)
        device = self._detect_device(ua, os_name, is_bot)
        short = self._format_short(browser, os_name, os_version, device)
        if mode == "short":
            return {"mode": "short", "raw": ua, "is_bot": is_bot, "short": short}
        return {
            "mode": "parse",
            "raw": ua,
            "is_bot": is_bot,
            "browser": browser,
            "engine": engine,
            "os": {"name": os_name, "version": os_version},
            "device": device,
            "short": short,
        }

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"user_agent_tool: {message}")

    @classmethod
    def _validate_user_agent(cls, user_agent: Any) -> str:
        """Validate the ``user_agent`` input."""
        if (
            user_agent is None
            or isinstance(user_agent, bool)
            or not isinstance(user_agent, str)
        ):
            cls._invalid(
                f"user_agent must be a string (got {user_agent!r})"
            )
        if not user_agent.strip():
            cls._invalid("user_agent must not be empty or whitespace-only")
        if len(user_agent) > _MAX_USER_AGENT_CHARS:
            cls._invalid(
                f"user_agent exceeds the {_MAX_USER_AGENT_CHARS:,}-character "
                f"limit (got {len(user_agent):,} characters)"
            )
        control = re.search(r"[\x00-\x1f\x7f]", user_agent)
        if control is not None:
            cls._invalid(
                "user_agent must not contain control characters (a "
                "User-Agent is a single header line; found "
                f"{control.group(0)!r} at position {control.start()})"
            )
        return user_agent

    # ------------------------------------------------------------------ #
    # Detection step 1 + 2: bots first, then browsers
    # ------------------------------------------------------------------ #

    @classmethod
    def _detect_bot(cls, ua: str) -> Optional[Dict[str, Any]]:
        """Return the bot's browser dict, or None if not a bot."""
        if _BOT_HINT_RE.search(ua) is None:
            return None
        token = _BOT_TOKEN_RE.search(ua) or _LIB_TOKEN_RE.search(ua)
        if token is not None:
            return {"name": token.group(1), "version": token.group(2)}
        hint = _BOT_HINT_RE.search(ua)
        return {"name": hint.group(0), "version": None}

    @classmethod
    def _detect_browser(
        cls, ua: str
    ) -> Tuple[Dict[str, Any], Optional[str]]:
        """Detect the browser (bots first) and its engine family.

        The second return value is the engine family hint:
        ``"chromium"`` (Blink candidate), ``"edgehtml"``, or None.
        """
        bot = cls._detect_bot(ua)
        if bot is not None:
            return bot, None

        def browser(name: str, version: Optional[str]) -> Dict[str, Any]:
            return {"name": name, "version": version}

        # Samsung Internet embeds a Chrome token; it must win.
        version = _search_group(_RE_SAMSUNG, ua)
        if version is not None:
            return browser("Samsung Internet", version), "chromium"
        # New Chromium-based Edge (Edg/ on desktop, EdgA/ on Android,
        # EdgiOS/ on iOS). The \b + optional-suffix shape cannot match
        # the legacy "Edge/" token.
        version = _search_group(_RE_EDGE_NEW, ua)
        if version is not None:
            return browser("Edge", version), "chromium"
        version = _search_group(_RE_EDGE_OLD, ua)
        if version is not None:
            return browser("Edge", version), "edgehtml"
        # Opera: current OPR/, iOS OPiOS/, and legacy Opera/x — which
        # was frozen at 9.80 with the real version in Version/.
        version = _search_group(_RE_OPR, ua)
        if version is None:
            version = _search_group(_RE_OPIOS, ua)
        if version is not None:
            return browser("Opera", version), "chromium"
        opera_legacy = _search_group(_RE_OPERA_OLD, ua)
        if opera_legacy is not None:
            real = _search_group(_RE_VERSION, ua)
            if opera_legacy == "9.80" and real is not None:
                opera_legacy = real
            return browser("Opera", opera_legacy), None
        version = _search_group(_RE_IEMOBILE, ua)
        if version is not None:
            return browser("Internet Explorer Mobile", version), None
        version = _search_group(_RE_MSIE, ua)
        if version is not None:
            return browser("Internet Explorer", version), None
        version = _search_group(_RE_FXIOS, ua)
        if version is None:
            version = _search_group(_RE_FIREFOX, ua)
        if version is not None:
            return browser("Firefox", version), None
        if _RE_CHROMIUM_WORD.search(ua) is not None:
            version = _search_group(_RE_CHROMIUM, ua)
            if version is None:
                version = _search_group(_RE_CHROME, ua)
            return browser("Chromium", version), "chromium"
        # Chrome proper: reached only when no Chromium-family sibling
        # (Edge / OPR / SamsungBrowser / Chromium) claimed the string
        # first — that ordering IS the documented disambiguation.
        version = _search_group(_RE_CRIOS, ua)
        if version is None:
            version = _search_group(_RE_CHROME, ua)
        if version is not None:
            return browser("Chrome", version), "chromium"
        if _RE_SAFARI.search(ua) is not None:
            return browser("Safari", _search_group(_RE_VERSION, ua)), None
        # IE 11 shape: Trident/ + rv: without an MSIE token.
        if _RE_TRIDENT.search(ua) is not None:
            return browser("Internet Explorer", _search_group(_RE_RV, ua)), None
        return browser("unknown", None), None

    # ------------------------------------------------------------------ #
    # Detection step 4: operating systems
    # ------------------------------------------------------------------ #

    @classmethod
    def _detect_os(cls, ua: str) -> Tuple[str, Optional[str]]:
        """Detect the operating system name and version."""
        # Windows Phone first: Lumia strings also carry "Android".
        version = _search_group(_RE_WINDOWS_PHONE, ua)
        if version is not None:
            return "Windows Phone", version
        # Android (before generic Linux — Android strings say Linux).
        version = _search_group(_RE_ANDROID, ua)
        if version is not None:
            return "Android", version
        if "iPad" in ua:
            return "iPadOS", _undots(_search_group(_RE_IPAD_OS, ua))
        version = _undots(_search_group(_RE_IPHONE_OS, ua))
        if version is not None:
            return "iOS", version
        version = _undots(_search_group(_RE_MAC_OS, ua))
        if version is not None:
            return "Mac OS X", version
        nt = _search_group(_RE_WINDOWS_NT, ua)
        if nt is not None:
            return "Windows", _WINDOWS_NT_MAP.get(nt, nt)
        version = _search_group(_RE_CROS, ua)
        if version is not None:
            return "ChromeOS", version
        if re.search(r"Ubuntu", ua) is not None:
            return "Ubuntu", None
        if re.search(r"Fedora", ua) is not None:
            return "Fedora", None
        if "Macintosh" in ua:
            return "Mac OS X", None
        # Case-insensitive: library clients report "linux-gnu" in
        # lowercase build triples.
        if re.search(r"(?i)\blinux\b", ua) or "X11" in ua:
            return "Linux", None
        return "unknown", None

    # ------------------------------------------------------------------ #
    # Detection step 3: engines
    # ------------------------------------------------------------------ #

    @classmethod
    def _detect_engine(
        cls,
        ua: str,
        browser: Dict[str, Any],
        engine_family: Optional[str],
        os_name: str,
    ) -> Dict[str, Any]:
        """Detect the rendering engine name and version."""
        # Trident wins over rv: — in IE 11 "rv:" is the browser
        # version, not the engine's.
        version = _search_group(_RE_TRIDENT, ua)
        if version is not None:
            return {"name": "Trident", "version": version}
        if engine_family == "edgehtml":
            return {"name": "EdgeHTML", "version": None}
        version = _search_group(_RE_PRESTO, ua)
        if version is not None:
            return {"name": "Presto", "version": version}
        version = _search_group(_RE_RV, ua)
        if version is not None:
            return {"name": "Gecko", "version": version}
        webkit_build = _search_group(_RE_APPLEWEBKIT, ua)
        if webkit_build is not None:
            on_ios = os_name in ("iOS", "iPadOS") or bool(
                _IOS_BROWSER_TOKEN_RE.search(ua)
            )
            if engine_family == "chromium" and not on_ios:
                # Blink heuristic: AppleWebKit + a Chromium-family
                # browser token outside iOS. Blink has no version
                # token of its own; the AppleWebKit build number is
                # frozen compatibility noise.
                return {"name": "Blink", "version": None}
            return {"name": "WebKit", "version": webkit_build}
        date = _search_group(_RE_GECKO_DATE, ua)
        if date is not None:
            return {"name": "Gecko", "version": None}
        return {"name": "unknown", "version": None}

    # ------------------------------------------------------------------ #
    # Detection step 5: device type, vendor and model
    # ------------------------------------------------------------------ #

    @classmethod
    def _detect_device(
        cls, ua: str, os_name: str, is_bot: bool
    ) -> Dict[str, Any]:
        """Detect the device type plus optional vendor and model."""
        vendor: Optional[str] = None
        model: Optional[str] = None
        is_android = os_name == "Android" or _RE_ANDROID.search(ua) is not None

        if is_bot:
            # Bots first: a bot's device type is "bot", and whatever
            # phone model its string embeds (Googlebot crawls from
            # phones) is not the caller's device.
            device_type = "bot"
        elif os_name == "Windows Phone":
            device_type = "mobile"
            if re.search(r"(?i)\bnokia\b", ua) is not None:
                vendor = "Nokia"
            elif re.search(r"(?i)\bmicrosoft\b", ua) is not None:
                vendor = "Microsoft"
            lumia = _RE_LUMIA.search(ua)
            if lumia is not None:
                model = lumia.group(1)
                if vendor is None:
                    vendor = "Microsoft"
        elif is_android:
            model, vendor = cls._extract_android_model(ua)
            # Android tablet User-Agents simply omit the Mobile token.
            device_type = (
                "mobile" if re.search(r"(?i)\bmobile\b", ua) else "tablet"
            )
        elif "iPad" in ua or re.search(r"(?i)\btablet\b", ua) is not None:
            device_type = "tablet"
            vendor = "Apple" if "iPad" in ua else None
        elif (
            "iPhone" in ua
            or re.search(r"(?i)\bmobile\b", ua) is not None
            or "Opera Mini" in ua
        ):
            device_type = "mobile"
            vendor = "Apple" if "iPhone" in ua else None
        elif os_name in ("Windows", "Mac OS X", "Linux", "Ubuntu",
                         "Fedora", "ChromeOS"):
            device_type = "desktop"
            vendor = "Apple" if os_name == "Mac OS X" else None
        else:
            device_type = "unknown"
        return {"type": device_type, "vendor": vendor, "model": model}

    @classmethod
    def _extract_android_model(
        cls, ua: str
    ) -> Tuple[Optional[str], Optional[str]]:
        """Extract the device model token after the Android version.

        The token that follows ``Android <version>;`` inside the same
        parentheses is the device model on real strings. Placeholder
        tokens (``K``, ``Mobile``, ``wv``, ``Build``, ``rv:…``) and a
        glued `` Build/<build-id>`` suffix are skipped, and the vendor
        is looked up through the documented prefix table.
        """
        segment = _RE_ANDROID_SEG.search(ua)
        if segment is None:
            return None, None
        for raw_token in segment.group(1).split(";"):
            token = raw_token.strip()
            if not token:
                continue
            token = token.split(" Build/")[0].strip()
            lowered = token.lower()
            if (
                not token
                or "/" in token
                or lowered in _NON_MODEL_TOKENS
                or lowered.startswith("rv:")
                or (" " in token and lowered.split(" ")[0] in _NON_MODEL_TOKENS)
            ):
                continue
            for prefix, table_vendor in _ANDROID_VENDOR_PREFIXES:
                if token.startswith(prefix):
                    return token, table_vendor
            return token, None
        return None, None

    # ------------------------------------------------------------------ #
    # Short one-liner
    # ------------------------------------------------------------------ #

    @staticmethod
    def _major(version: Optional[str]) -> Optional[str]:
        """Reduce a version to its major component."""
        if version is None:
            return None
        head = version.split(".")[0]
        return head if head else None

    @classmethod
    def _format_short(
        cls,
        browser: Dict[str, Any],
        os_name: str,
        os_version: Optional[str],
        device: Dict[str, Any],
    ) -> str:
        """Format the ``Name major / OS major / type`` one-liner."""
        if browser["name"] == "unknown":
            browser_part = "unknown"
        else:
            major = cls._major(browser["version"])
            browser_part = (
                f"{browser['name']} {major}" if major else browser["name"]
            )
        if os_name == "unknown":
            os_part = "unknown"
        else:
            major = cls._major(os_version)
            os_part = f"{os_name} {major}" if major else os_name
        return f"{browser_part} / {os_part} / {device['type']}"
