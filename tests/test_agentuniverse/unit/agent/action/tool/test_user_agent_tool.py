#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: test_user_agent_tool.py

"""Offline unit tests for UserAgentTool.

The tool is built purely on the standard library and never touches
the network, so this suite runs fully offline. Every assertion is
deterministic: ``parse`` results are checked against literal
real-world User-Agent ground truths (modern Chrome on Windows, macOS
and Android, iOS Safari via the ``Version/`` token, Firefox, new and
legacy Edge, Opera current and Presto, Samsung Internet, IE 6/9/11
including the Trident-over-rv: rule, Googlebot / bingbot / curl /
Wget / python-requests / HeadlessChrome / Yahoo! Slurp bots, Windows
Phone Lumia), plus the documented disambiguation matrix
(Chrome-with-Edg, Chrome-with-OPR, Chrome-with-SamsungBrowser,
Chromium, Safari-without-Chrome, CriOS-is-WebKit-not-Blink,
Windows-Phone-before-Android, bots-before-browsers), Android model
extraction (vendor prefix table, ``Build/`` suffix, ``K`` /
``Mobile`` / ``rv:`` placeholders), unknown-input behaviour, and the
full error matrix for malformed parameters.
"""

import os
import sys
import unittest

import yaml

from agentuniverse.agent.action.tool.common_tool import UserAgentTool
from agentuniverse.agent.action.tool.common_tool.user_agent_tool import (
    UserAgentTool as DirectUserAgentTool,
)

# --------------------------------------------------------------------- #
# Real-world User-Agent ground truths
# --------------------------------------------------------------------- #
# Each entry: (user agent, browser, engine, os, device, is_bot, short)
GROUND_TRUTHS = [
    # --- Modern Chrome, desktop Windows ---------------------------- #
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        ("Chrome", "120.0.0.0"),
        ("Blink", None),
        ("Windows", "10"),
        ("desktop", None, None),
        False,
        "Chrome 120 / Windows 10 / desktop",
    ),
    # --- Modern Chrome, desktop macOS (frozen 10_15_7) -------------- #
    (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 "
        "Safari/537.36",
        ("Chrome", "119.0.0.0"),
        ("Blink", None),
        ("Mac OS X", "10.15.7"),
        ("desktop", "Apple", None),
        False,
        "Chrome 119 / Mac OS X 10 / desktop",
    ),
    # --- Modern Chrome, Android phone with model -------------------- #
    (
        "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        ("Chrome", "120.0.0.0"),
        ("Blink", None),
        ("Android", "13"),
        ("mobile", "Samsung", "SM-G991B"),
        False,
        "Chrome 120 / Android 13 / mobile",
    ),
    # --- Older Chrome, Android with glued Build/ suffix ------------- #
    (
        "Mozilla/5.0 (Linux; Android 10; SM-A505F Build/QP1A.190711.020) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.5943.20 "
        "Mobile Safari/537.36",
        ("Chrome", "119.0.5943.20"),
        ("Blink", None),
        ("Android", "10"),
        ("mobile", "Samsung", "SM-A505F"),
        False,
        "Chrome 119 / Android 10 / mobile",
    ),
    # --- Android tablet: no Mobile token --------------------------- #
    (
        "Mozilla/5.0 (Linux; Android 13; SM-X710) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        ("Chrome", "120.0.0.0"),
        ("Blink", None),
        ("Android", "13"),
        ("tablet", "Samsung", "SM-X710"),
        False,
        "Chrome 120 / Android 13 / tablet",
    ),
    # --- Android with a Google Pixel model ------------------------- #
    (
        "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        ("Chrome", "120.0.0.0"),
        ("Blink", None),
        ("Android", "14"),
        ("mobile", "Google", "Pixel 8"),
        False,
        "Chrome 120 / Android 14 / mobile",
    ),
    # --- iOS Safari: version from the Version/ token ---------------- #
    (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 "
        "Mobile/15E148 Safari/604.1",
        ("Safari", "17.1"),
        ("WebKit", "605.1.15"),
        ("iOS", "17.1"),
        ("mobile", "Apple", None),
        False,
        "Safari 17 / iOS 17 / mobile",
    ),
    # --- iPad ------------------------------------------------------- #
    (
        "Mozilla/5.0 (iPad; CPU OS 16_6 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 "
        "Mobile/15E148 Safari/604.1",
        ("Safari", "16.6"),
        ("WebKit", "605.1.15"),
        ("iPadOS", "16.6"),
        ("tablet", "Apple", None),
        False,
        "Safari 16 / iPadOS 16 / tablet",
    ),
    # --- Desktop Safari --------------------------------------------- #
    (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 "
        "Safari/605.1.15",
        ("Safari", "17.1"),
        ("WebKit", "605.1.15"),
        ("Mac OS X", "10.15.7"),
        ("desktop", "Apple", None),
        False,
        "Safari 17 / Mac OS X 10 / desktop",
    ),
    # --- Old iPhone Safari without a Version/ token ----------------- #
    (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 8_1 like Mac OS X) "
        "AppleWebKit/600.1.4 (KHTML, like Gecko) Mobile/12B411 "
        "Safari/600.1.4",
        ("Safari", None),
        ("WebKit", "600.1.4"),
        ("iOS", "8.1"),
        ("mobile", "Apple", None),
        False,
        "Safari / iOS 8 / mobile",
    ),
    # --- Firefox on Windows (Gecko from rv:) ------------------------ #
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) "
        "Gecko/20100101 Firefox/120.0",
        ("Firefox", "120.0"),
        ("Gecko", "120.0"),
        ("Windows", "10"),
        ("desktop", None, None),
        False,
        "Firefox 120 / Windows 10 / desktop",
    ),
    # --- Firefox on Linux ------------------------------------------- #
    (
        "Mozilla/5.0 (X11; Linux x86_64; rv:119.0) Gecko/20100101 "
        "Firefox/119.0",
        ("Firefox", "119.0"),
        ("Gecko", "119.0"),
        ("Linux", None),
        ("desktop", None, None),
        False,
        "Firefox 119 / Linux / desktop",
    ),
    # --- Firefox on Ubuntu ------------------------------------------ #
    (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) "
        "Gecko/20100101 Firefox/121.0",
        ("Firefox", "121.0"),
        ("Gecko", "109.0"),
        ("Ubuntu", None),
        ("desktop", None, None),
        False,
        "Firefox 121 / Ubuntu / desktop",
    ),
    # --- Firefox on Android: Mobile and rv: are not models ---------- #
    (
        "Mozilla/5.0 (Android 13; Mobile; rv:120.0) Gecko/120.0 "
        "Firefox/120.0",
        ("Firefox", "120.0"),
        ("Gecko", "120.0"),
        ("Android", "13"),
        ("mobile", None, None),
        False,
        "Firefox 120 / Android 13 / mobile",
    ),
    # --- New Chromium Edge (Edg/ suffix) ---------------------------- #
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 "
        "Edg/120.0.2210.91",
        ("Edge", "120.0.2210.91"),
        ("Blink", None),
        ("Windows", "10"),
        ("desktop", None, None),
        False,
        "Edge 120 / Windows 10 / desktop",
    ),
    # --- Edge for Android (EdgA/ suffix) ---------------------------- #
    (
        "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36 "
        "EdgA/121.0.2380.0",
        ("Edge", "121.0.2380.0"),
        ("Blink", None),
        ("Android", "13"),
        ("mobile", "Samsung", "SM-G991B"),
        False,
        "Edge 121 / Android 13 / mobile",
    ),
    # --- Legacy EdgeHTML Edge (Edge/ token) ------------------------- #
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 "
        "Edge/12.10240",
        ("Edge", "12.10240"),
        ("EdgeHTML", None),
        ("Windows", "10"),
        ("desktop", None, None),
        False,
        "Edge 12 / Windows 10 / desktop",
    ),
    # --- Current Opera (OPR/) --------------------------------------- #
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 OPR/105.0.0.0",
        ("Opera", "105.0.0.0"),
        ("Blink", None),
        ("Windows", "10"),
        ("desktop", None, None),
        False,
        "Opera 105 / Windows 10 / desktop",
    ),
    # --- Legacy Opera: frozen Opera/9.80, real version in Version/ -- #
    (
        "Opera/9.80 (Windows NT 6.1; U; en) Presto/2.9.181 Version/10.00",
        ("Opera", "10.00"),
        ("Presto", "2.9.181"),
        ("Windows", "7"),
        ("desktop", None, None),
        False,
        "Opera 10 / Windows 7 / desktop",
    ),
    # --- Samsung Internet -------------------------------------------- #
    (
        "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 "
        "(KHTML, like Gecko) SamsungBrowser/23.0 Chrome/115.0.0.0 "
        "Mobile Safari/537.36",
        ("Samsung Internet", "23.0"),
        ("Blink", None),
        ("Android", "13"),
        ("mobile", "Samsung", "SM-G991B"),
        False,
        "Samsung Internet 23 / Android 13 / mobile",
    ),
    # --- IE 11: Trident wins over rv:, like Gecko is NOT Gecko ------ #
    (
        "Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko",
        ("Internet Explorer", "11.0"),
        ("Trident", "7.0"),
        ("Windows", "7"),
        ("desktop", None, None),
        False,
        "Internet Explorer 11 / Windows 7 / desktop",
    ),
    # --- IE 9 -------------------------------------------------------- #
    (
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)",
        ("Internet Explorer", "9.0"),
        ("Trident", "5.0"),
        ("Windows", "7"),
        ("desktop", None, None),
        False,
        "Internet Explorer 9 / Windows 7 / desktop",
    ),
    # --- IE 6 on XP, no engine token -------------------------------- #
    (
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)",
        ("Internet Explorer", "6.0"),
        ("unknown", None),
        ("Windows", "XP"),
        ("desktop", None, None),
        False,
        "Internet Explorer 6 / Windows XP / desktop",
    ),
    # --- IE Mobile on Windows Phone 8 (IEMobile beats MSIE) --------- #
    (
        "Mozilla/5.0 (compatible; MSIE 10.0; Windows Phone 8.0; "
        "Trident/6.0; IEMobile/10.0; ARM; Touch; NOKIA; Lumia 920)",
        ("Internet Explorer Mobile", "10.0"),
        ("Trident", "6.0"),
        ("Windows Phone", "8.0"),
        ("mobile", "Nokia", "Lumia 920"),
        False,
        "Internet Explorer Mobile 10 / Windows Phone 8 / mobile",
    ),
    # --- Windows Phone Edge mobile: WP before Android, Lumia model -- #
    (
        "Mozilla/5.0 (Windows Phone 10.0; Android 6.0.1; WebView/3.0; "
        "Microsoft; Lumia 950) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/46.0.2486.0 Mobile Safari/537.36 Edge/13.10560",
        ("Edge", "13.10560"),
        ("EdgeHTML", None),
        ("Windows Phone", "10.0"),
        ("mobile", "Microsoft", "Lumia 950"),
        False,
        "Edge 13 / Windows Phone 10 / mobile",
    ),
    # --- Chrome on iOS (CriOS): WebKit, never Blink ------------------ #
    (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/119.0.6045.109 "
        "Mobile/15E148 Safari/604.1",
        ("Chrome", "119.0.6045.109"),
        ("WebKit", "605.1.15"),
        ("iOS", "17.1"),
        ("mobile", "Apple", None),
        False,
        "Chrome 119 / iOS 17 / mobile",
    ),
    # --- Firefox on iOS (FxiOS): WebKit ------------------------------ #
    (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) FxiOS/115.0 "
        "Mobile/15E148 Safari/604.1",
        ("Firefox", "115.0"),
        ("WebKit", "605.1.15"),
        ("iOS", "16.6"),
        ("mobile", "Apple", None),
        False,
        "Firefox 115 / iOS 16 / mobile",
    ),
    # --- ChromeOS ---------------------------------------------------- #
    (
        "Mozilla/5.0 (X11; CrOS x86_64 14541.0.0) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        ("Chrome", "120.0.0.0"),
        ("Blink", None),
        ("ChromeOS", "14541.0.0"),
        ("desktop", None, None),
        False,
        "Chrome 120 / ChromeOS 14541 / desktop",
    ),
    # --- Android "K" placeholder: no model, no vendor --------------- #
    (
        "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        ("Chrome", "120.0.0.0"),
        ("Blink", None),
        ("Android", "10"),
        ("mobile", None, None),
        False,
        "Chrome 120 / Android 10 / mobile",
    ),
    # --- Bots -------------------------------------------------------- #
    (
        "Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.96 "
        "Mobile Safari/537.36 (compatible; Googlebot/2.1; "
        "+http://www.google.com/bot.html)",
        ("Googlebot", "2.1"),
        ("WebKit", "537.36"),
        ("Android", "6.0.1"),
        ("bot", None, None),
        True,
        "Googlebot 2 / Android 6 / bot",
    ),
    (
        "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; "
        "bingbot/2.0; +http://www.bing.com/bingbot.htm) "
        "Chrome/100.0.4896.127 Safari/537.36",
        ("bingbot", "2.0"),
        ("WebKit", "537.36"),
        ("unknown", None),
        ("bot", None, None),
        True,
        "bingbot 2 / unknown / bot",
    ),
    (
        "curl/8.4.0",
        ("curl", "8.4.0"),
        ("unknown", None),
        ("unknown", None),
        ("bot", None, None),
        True,
        "curl 8 / unknown / bot",
    ),
    (
        "Wget/1.21.3 (linux-gnu)",
        ("Wget", "1.21.3"),
        ("unknown", None),
        ("Linux", None),
        ("bot", None, None),
        True,
        "Wget 1 / Linux / bot",
    ),
    (
        "python-requests/2.31.0",
        ("python-requests", "2.31.0"),
        ("unknown", None),
        ("unknown", None),
        ("bot", None, None),
        True,
        "python-requests 2 / unknown / bot",
    ),
    (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) HeadlessChrome/119.0.6045.9 Safari/537.36",
        ("HeadlessChrome", "119.0.6045.9"),
        ("WebKit", "537.36"),
        ("Linux", None),
        ("bot", None, None),
        True,
        "HeadlessChrome 119 / Linux / bot",
    ),
    (
        "Mozilla/5.0 (compatible; Yahoo! Slurp; "
        "http://help.yahoo.com/help/us/ysearch/slurp)",
        ("Slurp", None),
        ("unknown", None),
        ("unknown", None),
        ("bot", None, None),
        True,
        "Slurp / unknown / bot",
    ),
    # --- Unknown client --------------------------------------------- #
    (
        "MyCustomAgent/1.0",
        ("unknown", None),
        ("unknown", None),
        ("unknown", None),
        ("unknown", None, None),
        False,
        "unknown / unknown / unknown",
    ),
    (
        "Mozilla/5.0",
        ("unknown", None),
        ("unknown", None),
        ("unknown", None),
        ("unknown", None, None),
        False,
        "unknown / unknown / unknown",
    ),
]

# Minimal disambiguation matrix: User-Agent snippets in which one
# Chrome-family token must win over the bare "Chrome/" token.
DISAMBIGUATION = [
    # Chrome + Edg suffix -> Edge
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
        "Edge",
    ),
    # Chrome + EdgA suffix -> Edge
    (
        "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36 "
        "EdgA/121.0.0.0",
        "Edge",
    ),
    # Chrome + OPR -> Opera
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 OPR/105.0.0.0",
        "Opera",
    ),
    # Chrome + SamsungBrowser -> Samsung Internet
    (
        "Mozilla/5.0 (Linux; Android 12; S21) AppleWebKit/537.36 "
        "(KHTML, like Gecko) SamsungBrowser/20.0 Chrome/106.0.5249.126 "
        "Mobile Safari/537.36",
        "Samsung Internet",
    ),
    # Chromium token -> Chromium (not Chrome)
    (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Ubuntu Chromium/78.0.3904.108 "
        "Chrome/78.0.3904.108 Safari/537.36",
        "Chromium",
    ),
    # Safari/ without Chrome/ -> Safari
    (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 "
        "Safari/605.1.15",
        "Safari",
    ),
]

# Error matrix: (kwargs, message fragment expected in the ValueError).
ERROR_CASES = [
    ({"mode": None, "user_agent": "curl/8.4.0"}, "mode must be one of"),
    ({"mode": "explain", "user_agent": "curl/8.4.0"}, "mode must be one of"),
    ({"mode": "parse", "user_agent": None}, "user_agent must be a string"),
    ({"mode": "parse", "user_agent": 123}, "user_agent must be a string"),
    ({"mode": "parse", "user_agent": True}, "user_agent must be a string"),
    ({"mode": "parse", "user_agent": ["curl/8.4.0"]}, "must be a string"),
    ({"mode": "parse", "user_agent": ""}, "must not be empty"),
    ({"mode": "parse", "user_agent": "   "}, "must not be empty"),
    ({"mode": "parse", "user_agent": "\t"}, "must not be empty"),
    ({"mode": "parse", "user_agent": "a" * 8193}, "exceeds the 8,192"),
    ({"mode": "parse", "user_agent": "curl/8.4.0\nx"}, "control characters"),
    ({"mode": "parse", "user_agent": "curl/8.4.0\r"}, "control characters"),
    ({"mode": "parse", "user_agent": "curl/8.4.0\td"}, "control characters"),
    ({"mode": "parse", "user_agent": "curl/8.4.0\x00"}, "control characters"),
    ({"mode": "parse", "user_agent": "curl/8.4.0\x7f"}, "control characters"),
]


class UserAgentToolTest(unittest.TestCase):
    """Offline deterministic test cases for UserAgentTool."""

    def setUp(self) -> None:
        self.tool = UserAgentTool()

    # ------------------------------------------------------------------ #
    # Registration and metadata
    # ------------------------------------------------------------------ #

    def test_package_export_and_defaults(self) -> None:
        self.assertIs(DirectUserAgentTool, UserAgentTool)
        self.assertEqual(self.tool.name, "user_agent_tool")
        self.assertEqual(DirectUserAgentTool.MODES, ("parse", "short"))
        self.assertIn("offline", self.tool.description)
        self.assertIn("spoofable", self.tool.description)

    def test_yaml_config_matches_module(self) -> None:
        module = sys.modules[DirectUserAgentTool.__module__]
        path = os.path.join(
            os.path.dirname(module.__file__), "user_agent_tool.yaml"
        )
        with open(path, "r", encoding="utf-8") as handle:
            config = yaml.safe_load(handle)
        self.assertEqual(config["name"], "user_agent_tool")
        self.assertEqual(
            config["metadata"]["module"],
            "agentuniverse.agent.action.tool.common_tool.user_agent_tool",
        )
        self.assertEqual(config["metadata"]["class"], "UserAgentTool")
        self.assertEqual(config["tool_type"], "api")
        self.assertEqual(config["input_keys"], ["mode"])
        self.assertEqual(
            config["args_model_schema"]["required"], ["mode", "user_agent"]
        )
        self.assertEqual(
            sorted(config["args_model_schema"]["properties"]["mode"]["enum"]),
            ["parse", "short"],
        )

    # ------------------------------------------------------------------ #
    # Real-world ground truths
    # ------------------------------------------------------------------ #

    def test_ground_truths(self) -> None:
        self.assertEqual(len(GROUND_TRUTHS), 38)
        for ua, browser, engine, os_, device, is_bot, short in GROUND_TRUTHS:
            with self.subTest(ua=ua):
                result = self.tool.execute(mode="parse", user_agent=ua)
                self.assertEqual(result["mode"], "parse")
                self.assertEqual(result["raw"], ua)
                self.assertEqual(result["is_bot"], is_bot)
                self.assertEqual(
                    result["browser"],
                    {"name": browser[0], "version": browser[1]},
                )
                self.assertEqual(
                    result["engine"],
                    {"name": engine[0], "version": engine[1]},
                )
                self.assertEqual(
                    result["os"], {"name": os_[0], "version": os_[1]}
                )
                self.assertEqual(
                    result["device"],
                    {
                        "type": device[0],
                        "vendor": device[1],
                        "model": device[2],
                    },
                )
                self.assertEqual(result["short"], short)

    def test_parse_result_key_set(self) -> None:
        result = self.tool.execute(mode="parse", user_agent="curl/8.4.0")
        self.assertEqual(
            set(result.keys()),
            {
                "mode",
                "raw",
                "is_bot",
                "browser",
                "engine",
                "os",
                "device",
                "short",
            },
        )
        self.assertEqual(set(result["browser"].keys()), {"name", "version"})
        self.assertEqual(set(result["engine"].keys()), {"name", "version"})
        self.assertEqual(set(result["os"].keys()), {"name", "version"})
        self.assertEqual(
            set(result["device"].keys()), {"type", "vendor", "model"}
        )

    # ------------------------------------------------------------------ #
    # Disambiguation matrix
    # ------------------------------------------------------------------ #

    def test_browser_disambiguation_matrix(self) -> None:
        for ua, expected_name in DISAMBIGUATION:
            with self.subTest(ua=ua):
                result = self.tool.execute(mode="parse", user_agent=ua)
                self.assertEqual(result["browser"]["name"], expected_name)

    def test_bots_before_browsers(self) -> None:
        # A bot hint must beat browser tokens embedded for compatibility.
        ua = (
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 "
            "Mobile/15E148 Safari/604.1 (compatible; FacebookBot/1.0)"
        )
        result = self.tool.execute(mode="parse", user_agent=ua)
        self.assertTrue(result["is_bot"])
        self.assertEqual(result["device"]["type"], "bot")
        self.assertEqual(result["browser"]["name"], "FacebookBot")

    def test_windows_phone_before_android(self) -> None:
        # Lumia strings carry both Windows Phone and Android tokens.
        ua = (
            "Mozilla/5.0 (Windows Phone 10.0; Android 6.0.1) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2486.0 "
            "Mobile Safari/537.36 Edge/13.10560"
        )
        result = self.tool.execute(mode="parse", user_agent=ua)
        self.assertEqual(
            result["os"], {"name": "Windows Phone", "version": "10.0"}
        )
        self.assertEqual(result["device"]["type"], "mobile")

    def test_trident_beats_rv_and_like_gecko_is_not_gecko(self) -> None:
        ua = "Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko"
        result = self.tool.execute(mode="parse", user_agent=ua)
        self.assertEqual(
            result["engine"], {"name": "Trident", "version": "7.0"}
        )
        self.assertNotEqual(result["engine"]["name"], "Gecko")

    def test_ios_browsers_are_webkit_not_blink(self) -> None:
        for ua in (
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/119.0 "
            "Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) EdgiOS/119.2207.5 "
            "Mobile/15E148 Safari/604.1",
        ):
            with self.subTest(ua=ua):
                result = self.tool.execute(mode="parse", user_agent=ua)
                self.assertEqual(result["engine"]["name"], "WebKit")
                self.assertEqual(result["engine"]["version"], "605.1.15")

    def test_windows_11_is_honestly_windows_10(self) -> None:
        # Windows 11 ships the same Windows NT 10.0 token; the tool
        # must not claim a distinction it cannot make.
        ua = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        result = self.tool.execute(mode="parse", user_agent=ua)
        self.assertEqual(result["os"], {"name": "Windows", "version": "10"})

    def test_windows_nt_version_map(self) -> None:
        cases = [
            ("Windows NT 5.0", "2000"),
            ("Windows NT 5.1", "XP"),
            ("Windows NT 5.2", "XP"),
            ("Windows NT 6.0", "Vista"),
            ("Windows NT 6.1", "7"),
            ("Windows NT 6.2", "8"),
            ("Windows NT 6.3", "8.1"),
            ("Windows NT 6.4", "10"),
            ("Windows NT 10.0", "10"),
        ]
        for token, expected in cases:
            ua = f"Mozilla/5.0 ({token}; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            with self.subTest(token=token):
                result = self.tool.execute(mode="parse", user_agent=ua)
                self.assertEqual(
                    result["os"], {"name": "Windows", "version": expected}
                )

    # ------------------------------------------------------------------ #
    # Android model extraction
    # ------------------------------------------------------------------ #

    def test_android_model_extraction(self) -> None:
        cases = [
            ("Android 13; SM-G991B)", "SM-G991B", "Samsung"),
            ("Android 10; SM-A505F Build/QP1A.190711.020)", "SM-A505F", "Samsung"),
            ("Android 12; SM-T870)", "SM-T870", "Samsung"),
            ("Android 14; Pixel 8 Pro)", "Pixel 8 Pro", "Google"),
            ("Android 12; LG-L555DL)", "LG-L555DL", "LG"),
            ("Android 11; LM-Q720)", "LM-Q720", "LG"),
            ("Android 13; Redmi Note 12)", "Redmi Note 12", "Xiaomi"),
            ("Android 11; POCO X3 Pro)", "POCO X3 Pro", "Xiaomi"),
            ("Android 10; moto g(8) power)", "moto g(8) power", "Motorola"),
            ("Android 12; CPH2451)", "CPH2451", "OPPO"),
            ("Android 13; vivo 1820)", "vivo 1820", "vivo"),
            ("Android 11; ONEPLUS A6013)", "ONEPLUS A6013", "OnePlus"),
            ("Android 12; HUAWEI PGT-AN10)", "HUAWEI PGT-AN10", "Huawei"),
            ("Android 11; Nokia G21)", "Nokia G21", "Nokia"),
        ]
        for segment, model, vendor in cases:
            ua = (
                "Mozilla/5.0 (Linux; " + segment + ") "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Mobile Safari/537.36"
            )
            with self.subTest(segment=segment):
                result = self.tool.execute(mode="parse", user_agent=ua)
                self.assertEqual(result["device"]["model"], model)
                self.assertEqual(result["device"]["vendor"], vendor)
                self.assertEqual(result["device"]["type"], "mobile")

    def test_android_placeholder_tokens_are_not_models(self) -> None:
        cases = [
            "Android 10; K)",
            "Android 13; Mobile)",
            "Android 12; wv)",
            "Android 13; Mobile; rv:120.0)",
        ]
        for segment in cases:
            ua = (
                "Mozilla/5.0 (Linux; " + segment + ") "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Mobile Safari/537.36"
            )
            with self.subTest(segment=segment):
                result = self.tool.execute(mode="parse", user_agent=ua)
                self.assertIsNone(result["device"]["model"])
                self.assertIsNone(result["device"]["vendor"])

    def test_unknown_android_model_has_no_vendor(self) -> None:
        ua = (
            "Mozilla/5.0 (Linux; Android 13; ZY9876X) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 "
            "Mobile Safari/537.36"
        )
        result = self.tool.execute(mode="parse", user_agent=ua)
        self.assertEqual(result["device"]["model"], "ZY9876X")
        self.assertIsNone(result["device"]["vendor"])

    # ------------------------------------------------------------------ #
    # Unknown inputs
    # ------------------------------------------------------------------ #

    def test_unknown_ua_reports_unknown_fields(self) -> None:
        for ua in ("MyCustomAgent/1.0", "Mozilla/5.0", "???"):
            with self.subTest(ua=ua):
                result = self.tool.execute(mode="parse", user_agent=ua)
                self.assertFalse(result["is_bot"])
                self.assertEqual(result["browser"]["name"], "unknown")
                self.assertIsNone(result["browser"]["version"])
                self.assertEqual(result["engine"]["name"], "unknown")
                self.assertIsNone(result["engine"]["version"])
                self.assertEqual(result["os"]["name"], "unknown")
                self.assertIsNone(result["os"]["version"])
                self.assertEqual(result["device"]["type"], "unknown")
                self.assertIsNone(result["device"]["vendor"])
                self.assertIsNone(result["device"]["model"])
                self.assertEqual(result["short"], "unknown / unknown / unknown")

    # ------------------------------------------------------------------ #
    # short mode
    # ------------------------------------------------------------------ #

    def test_short_mode_matches_parse_short(self) -> None:
        for ua, *_rest in GROUND_TRUTHS:
            with self.subTest(ua=ua):
                parsed = self.tool.execute(mode="parse", user_agent=ua)
                shorted = self.tool.execute(mode="short", user_agent=ua)
                self.assertEqual(shorted["mode"], "short")
                self.assertEqual(shorted["short"], parsed["short"])
                self.assertEqual(shorted["is_bot"], parsed["is_bot"])
                self.assertEqual(set(shorted.keys()), {"mode", "raw", "is_bot", "short"})

    def test_short_mode_example(self) -> None:
        result = self.tool.execute(
            mode="short",
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 "
                "Safari/537.36"
            ),
        )
        self.assertEqual(result["short"], "Chrome 120 / Windows 10 / desktop")

    # ------------------------------------------------------------------ #
    # Determinism
    # ------------------------------------------------------------------ #

    def test_deterministic(self) -> None:
        for ua, *_rest in GROUND_TRUTHS:
            with self.subTest(ua=ua):
                first = self.tool.execute(mode="parse", user_agent=ua)
                second = self.tool.execute(mode="parse", user_agent=ua)
                self.assertEqual(first, second)

    # ------------------------------------------------------------------ #
    # Error matrix
    # ------------------------------------------------------------------ #

    def test_error_matrix(self) -> None:
        for kwargs, fragment in ERROR_CASES:
            with self.subTest(**kwargs):
                with self.assertRaises(ValueError) as raised:
                    self.tool.execute(**kwargs)
                self.assertIn("user_agent_tool:", str(raised.exception))
                self.assertIn(fragment, str(raised.exception))

    def test_max_length_boundary_accepted(self) -> None:
        ua = "x" * 8192
        result = self.tool.execute(mode="short", user_agent=ua)
        self.assertEqual(result["short"], "unknown / unknown / unknown")

    def test_vendor_chromium_browsers(self) -> None:
        cases = [
            (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 YaBrowser/24.1.0.0 "
                "Safari/537.36",
                "Yandex Browser", "24.1.0.0",
            ),
            (
                "Mozilla/5.0 (Linux; Android 13; SM-A536B) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/108.0.0.0 UCBrowser/16.0.8.1420 "
                "Mobile Safari/537.36",
                "UC Browser", "16.0.8.1420",
            ),
            (
                "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/55.0.2883.87 UBrowser/6.2.4098.3 "
                "Safari/537.36",
                "UC Browser", "6.2.4098.3",
            ),
            (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36 "
                "QQBrowser/10.7.4313.400",
                "QQ Browser", "10.7.4313.400",
            ),
            (
                "Mozilla/5.0 (Linux; U; Android 13; en-us; 2210132C "
                "Build/TP1A.220624.014) AppleWebKit/537.36 (KHTML, like "
                "Gecko) Version/4.0 Chrome/103.0.5060.129 Mobile "
                "Safari/537.36 XiaoMi/MiuiBrowser/17.4.11",
                "MiuiBrowser", "17.4.11",
            ),
            (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 "
                "MicroMessenger/8.0.43.2580(0x83000E30) "
                "WindowsWechat(0x63090c33) XWEB/11275",
                "WeChat", "8.0.43.2580",
            ),
            (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 "
                "Vivaldi/6.5.3206.50",
                "Vivaldi", "6.5.3206.50",
            ),
            (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/108.0.0.0 Whale/3.21.232.18 "
                "Safari/537.36",
                "Whale", "3.21.232.18",
            ),
            (
                "Mozilla/5.0 (Linux; Android 12; Quest 2) AppleWebKit/537.36 "
                "(KHTML, like Gecko) OculusBrowser/27.0.0.2.24.676195627 "
                "Safari/537.36 VR",
                "Oculus Browser", "27.0.0.2.24.676195627",
            ),
            (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 "
                "Discord/1.0.9092 Electron/27.1.0",
                "Electron", "27.1.0",
            ),
        ]
        for ua, name, version in cases:
            with self.subTest(ua=ua):
                result = self.tool.execute(mode="parse", user_agent=ua)
                self.assertEqual(result["browser"]["name"], name)
                self.assertEqual(result["browser"]["version"], version)
                self.assertFalse(result["is_bot"])

    def test_silk_requires_android(self) -> None:
        fire = (
            "Mozilla/5.0 (Linux; Android 9; KFMAWI) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Silk/96.1.1 Chrome/96.0.4664.110 Mobile "
            "Safari/537.36"
        )
        result = self.tool.execute(mode="parse", user_agent=fire)
        self.assertEqual(result["browser"]["name"], "Amazon Silk")
        self.assertEqual(result["device"]["vendor"], "Amazon")
        vita = (
            "Mozilla/5.0 (PlayStation Vita 3.61) AppleWebKit/537.73 "
            "(KHTML, like Gecko) Silk/3.2"
        )
        result = self.tool.execute(mode="parse", user_agent=vita)
        self.assertEqual(result["browser"]["name"], "unknown")

    def test_opera_mini_and_touch(self) -> None:
        j2me = (
            "Opera/9.80 (J2ME/MIDP; Opera Mini/5.1.21214/19.916; U; en) "
            "Presto/2.5.25"
        )
        result = self.tool.execute(mode="parse", user_agent=j2me)
        self.assertEqual(
            result["browser"], {"name": "Opera Mini", "version": "5.1.21214"}
        )
        self.assertEqual(result["engine"]["name"], "Presto")
        self.assertEqual(result["device"]["type"], "mobile")
        android = (
            "Mozilla/5.0 (Linux; U; Android 10; en-us; K) "
            "AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 "
            "Opera Mini/28.0.2254/119540 Mobile Safari/534.30"
        )
        result = self.tool.execute(mode="parse", user_agent=android)
        self.assertEqual(
            result["browser"], {"name": "Opera Mini", "version": "28.0.2254"}
        )
        self.assertIsNone(result["device"]["model"])
        touch = (
            "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) OPT/2.6.1 "
            "Mobile/15E148 Safari/604.1"
        )
        result = self.tool.execute(mode="parse", user_agent=touch)
        self.assertEqual(result["browser"]["name"], "Opera")
        self.assertEqual(result["engine"]["name"], "WebKit")

    def test_aosp_android_browser(self) -> None:
        for ua in (
            "Mozilla/5.0 (Linux; U; Android 4.4.2; en-us; SCH-I535 "
            "Build/KOT49H) AppleWebKit/534.30 (KHTML, like Gecko) "
            "Version/4.0 Mobile Safari/534.30",
            "Mozilla/5.0 (Linux; U; Android 2.3.5; en-us; HTC Vision "
            "Build/GRI40) AppleWebKit/533.1 (KHTML, like Gecko) "
            "Version/4.0 Mobile Safari/533.1",
        ):
            with self.subTest(ua=ua):
                result = self.tool.execute(mode="parse", user_agent=ua)
                self.assertEqual(
                    result["browser"],
                    {"name": "Android Browser", "version": "4.0"},
                )
                self.assertEqual(result["engine"]["name"], "WebKit")
                self.assertEqual(result["device"]["type"], "mobile")

    def test_in_app_browsers(self) -> None:
        ios = (
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/21B74 "
            "[FBAN/FBIOS;FBDV/iPhone14,2;FBMD/iPhone;FBSN/iOS;FBSV/17.1]"
        )
        result = self.tool.execute(mode="parse", user_agent=ios)
        self.assertEqual(result["browser"]["name"], "Facebook")
        self.assertIsNone(result["browser"]["version"])
        self.assertEqual(result["engine"]["name"], "WebKit")
        self.assertEqual(result["device"]["type"], "mobile")
        android = (
            "Mozilla/5.0 (Linux; Android 13; SM-G991B Build/TP1A.220624.014) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 "
            "Chrome/118.0.0.0 Mobile Safari/537.36 "
            "[FB_IAB/FB4A;FBAV/444.0.0.32.118;]"
        )
        result = self.tool.execute(mode="parse", user_agent=android)
        self.assertEqual(
            result["browser"],
            {"name": "Facebook", "version": "444.0.0.32.118"},
        )
        self.assertEqual(result["engine"]["name"], "Blink")
        instagram = (
            "Mozilla/5.0 (Linux; Android 14; SM-S918B Build/UP1A.231005.007) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 "
            "Chrome/119.0.6045.163 Mobile Safari/537.36 "
            "Instagram 309.0.0.29.110 Android"
        )
        result = self.tool.execute(mode="parse", user_agent=instagram)
        self.assertEqual(
            result["browser"],
            {"name": "Instagram", "version": "309.0.0.29.110"},
        )

    def test_case_insensitive_tokens(self) -> None:
        cases = [
            (
                "mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 "
                "(khtml, like gecko) chrome/120.0.0.0 safari/537.36",
                "Chrome", "Windows", "Blink",
            ),
            (
                "Mozilla/5.0 (Windows NT 10.0) Chrome/120.0.0.0 EDG/120.0.0.0",
                "Edge", "Windows", None,
            ),
            (
                "mozilla/5.0 (linux; android 13) chrome/120 mobile "
                "safari/537.36 edga/121.0.0.0",
                "Edge", "Android", None,
            ),
            (
                "mozilla/5.0 (macintosh; intel mac os x 10_15_7) "
                "applewebkit/605.1.15 (khtml, like gecko) version/17.1 "
                "safari/605.1.15",
                "Safari", "Mac OS X", "WebKit",
            ),
            (
                "mozilla/5.0 (windows nt 6.1; trident/7.0; rv:11.0) "
                "like gecko",
                "Internet Explorer", "Windows", "Trident",
            ),
            (
                "mozilla/5.0 (iphone; cpu iphone os 17_1 like mac os x) "
                "applewebkit/605.1.15 (khtml, like gecko) crios/119.0 "
                "mobile/15e148 safari/604.1",
                "Chrome", "iOS", "WebKit",
            ),
        ]
        for ua, browser, os_name, engine in cases:
            with self.subTest(ua=ua):
                result = self.tool.execute(mode="parse", user_agent=ua)
                self.assertEqual(result["browser"]["name"], browser)
                self.assertEqual(result["os"]["name"], os_name)
                if engine is not None:
                    self.assertEqual(result["engine"]["name"], engine)
        self.assertTrue(
            self.tool.execute(mode="short", user_agent="CURL/8.4.0")["is_bot"]
        )

    def test_bsd_and_kaios_os(self) -> None:
        cases = [
            (
                "Mozilla/5.0 (X11; FreeBSD amd64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                "FreeBSD",
                "desktop",
            ),
            (
                "Mozilla/5.0 (X11; NetBSD amd64; rv:128.0) Gecko/20100101 "
                "Firefox/128.0",
                "NetBSD",
                "desktop",
            ),
            (
                "Mozilla/5.0 (X11; OpenBSD amd64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "OpenBSD",
                "desktop",
            ),
            (
                "Mozilla/5.0 (Mobile; Nokia_8110_Virgin; rv:48.0) "
                "Gecko/48.0 Firefox/48.0 KAI/2.5",
                "KaiOS",
                "mobile",
            ),
        ]
        for ua, os_name, device_type in cases:
            with self.subTest(ua=ua):
                result = self.tool.execute(mode="parse", user_agent=ua)
                self.assertEqual(result["os"]["name"], os_name)
                self.assertEqual(result["device"]["type"], device_type)

    def test_windows_phone_without_version(self) -> None:
        ua = (
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows Phone; "
            "IEMobile/9.0)"
        )
        result = self.tool.execute(mode="parse", user_agent=ua)
        self.assertEqual(
            result["os"], {"name": "Windows Phone", "version": None}
        )
        self.assertEqual(result["device"]["type"], "mobile")

    def test_extended_bot_clients(self) -> None:
        cases = [
            ("facebookexternalhit/1.1", "facebookexternalhit", "1.1"),
            (
                "meta-externalagent/1.1 (+https://developers.facebook.com"
                "/docs/sharing/webmasters/crawler)",
                "meta-externalagent",
                "1.1",
            ),
            (
                "Mozilla/5.0 (Unknown; Linux x86_64) AppleWebKit/538.1 "
                "(KHTML, like Gecko) PhantomJS/2.1.1 Safari/538.1",
                "PhantomJS",
                "2.1.1",
            ),
            ("Scrapy/2.11.0 (+https://scrapy.org)", "Scrapy", "2.11.0"),
            ("python-httpx/0.27.0", "python-httpx", "0.27.0"),
            ("aiohttp/3.9.5", "aiohttp", "3.9.5"),
            ("Java/17.0.9", "Java", "17.0.9"),
            ("Java/1.8.0_311", "Java", "1.8.0_311"),
            ("libwww-perl/6.76", "libwww-perl", "6.76"),
            ("lwp-trivial/5.837 libwww-perl/6.76", "lwp-trivial", "5.837"),
            ("http.rb/5.1.1", "http.rb", "5.1.1"),
            ("undici/5.22.0", "undici", "5.22.0"),
            ("node-fetch/3.3.2", "node-fetch", "3.3.2"),
            ("HTTPie/3.2.2", "HTTPie", "3.2.2"),
            ("GuzzleHttp/7 (curl/7.87.0 PHP/8.2.4)", "GuzzleHttp", "7"),
            (
                "Mozilla/5.0 zgrab/0.x",
                "zgrab",
                "0.x",
            ),
            ("masscan/1.3.2", "masscan", "1.3.2"),
            (
                "Mozilla/5.0 (compatible; Claude-Web/2.0; "
                "claude-web@anthropic.com)",
                "Claude-Web",
                "2.0",
            ),
            (
                "Mozilla/5.0 (compatible; ChatGPT-User/1.0; "
                "+https://openai.com/bot)",
                "ChatGPT-User",
                "1.0",
            ),
            (
                "Mozilla/5.0 (compatible; YandexImages/3.0; "
                "+http://yandex.com/bots)",
                "YandexImages",
                "3.0",
            ),
        ]
        for ua, name, version in cases:
            with self.subTest(ua=ua):
                result = self.tool.execute(mode="parse", user_agent=ua)
                self.assertTrue(result["is_bot"])
                self.assertEqual(result["device"]["type"], "bot")
                self.assertEqual(result["browser"]["name"], name)
                self.assertEqual(result["browser"]["version"], version)

    def test_bot_names_without_version_token(self) -> None:
        cases = [
            (
                "Mozilla/5.0 (compatible; PetalBot; "
                "+https://webmaster.petalsearch.com/site/petalbot)",
                "PetalBot",
            ),
            (
                "Mozilla/5.0 (compatible; Bytespider; "
                "https://zhanzhang.toutiao.com/)",
                "Bytespider",
            ),
            ("TelegramBot (like TwitterBot)", "TelegramBot"),
            (
                "Sogou web spider/4.0"
                "(+http://www.sogou.com/docs/help/webmasters.htm#07)",
                "Sogou web spider",
            ),
            (
                "Slackbot-LinkExpanding 1.0 (+https://api.slack.com/robots)",
                "Slackbot-LinkExpanding",
            ),
            (
                "Mozilla/5.0 (compatible; MJ12bot/v1.4.8; "
                "http://mj12bot.com/)",
                "MJ12bot",
            ),
        ]
        for ua, name in cases:
            with self.subTest(ua=ua):
                result = self.tool.execute(mode="parse", user_agent=ua)
                self.assertTrue(result["is_bot"])
                self.assertEqual(result["browser"]["name"], name)

    def test_android_dual_sim_models(self) -> None:
        cases = [
            ("Android 13; SM-A536B/DS)", "SM-A536B", "Samsung"),
            ("Android 13; SM-A536B/DS Build/TP1A.220624.014)", "SM-A536B", "Samsung"),
            ("Android 12; SM-G975F/DS)", "SM-G975F", "Samsung"),
            ("Android 11; SM-A217F/DSN)", "SM-A217F", "Samsung"),
            ("Android 14; SM-A146P/DSN)", "SM-A146P", "Samsung"),
        ]
        for segment, model, vendor in cases:
            ua = (
                "Mozilla/5.0 (Linux; " + segment + ") AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
            )
            with self.subTest(segment=segment):
                result = self.tool.execute(mode="parse", user_agent=ua)
                self.assertEqual(result["device"]["model"], model)
                self.assertEqual(result["device"]["vendor"], vendor)

    def test_android_vendor_prefix_expansion(self) -> None:
        cases = [
            ("Android 12; SCG08)", "SCG08", "Samsung"),
            ("Android 11; SCV41)", "SCV41", "Samsung"),
            ("Android 13; RMX3261)", "RMX3261", "Realme"),
            ("Android 13; XQ-CT72)", "XQ-CT72", "Sony"),
            ("Android 11; SO-52D)", "SO-52D", "Sony"),
            ("Android 12; SOV41)", "SOV41", "Sony"),
            ("Android 12; HONOR 70)", "HONOR 70", "Huawei"),
            ("Android 9; KFMAWI)", "KFMAWI", "Amazon"),
        ]
        for segment, model, vendor in cases:
            ua = (
                "Mozilla/5.0 (Linux; " + segment + ") AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
            )
            with self.subTest(segment=segment):
                result = self.tool.execute(mode="parse", user_agent=ua)
                self.assertEqual(result["device"]["model"], model)
                self.assertEqual(result["device"]["vendor"], vendor)

    def test_android_locale_tokens_are_not_models(self) -> None:
        cases = [
            "Android 10; en-us; K)",
            "Android 13; zh-CN; SM-A536B)",
        ]
        for segment in cases:
            ua = (
                "Mozilla/5.0 (Linux; U; " + segment + ") "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 "
                "Mobile Safari/537.36"
            )
            with self.subTest(segment=segment):
                result = self.tool.execute(mode="parse", user_agent=ua)
                self.assertNotEqual(result["device"]["model"], "en-us")
                self.assertNotEqual(result["device"]["model"], "zh-CN")
        keep = (
            "Mozilla/5.0 (Linux; U; Android 4.4.2; en-us; SCH-I535 "
            "Build/KOT49H) AppleWebKit/534.30 (KHTML, like Gecko) "
            "Version/4.0 Mobile Safari/534.30"
        )
        result = self.tool.execute(mode="parse", user_agent=keep)
        self.assertEqual(result["device"]["model"], "SCH-I535")
        self.assertEqual(result["device"]["vendor"], "Samsung")

    def test_mixed_token_precedence_chain(self) -> None:
        cases = [
            (
                "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, "
                "like Gecko) Safari/537.36 Chrome/120.0.0.0 Edg/120.0.0.0",
                "Edge",
            ),
            (
                "Mozilla/5.0 (Windows NT 10.0) Safari/605 Chrome/120 "
                "SamsungBrowser/23",
                "Samsung Internet",
            ),
            (
                "Mozilla/5.0 (Windows NT 10.0) Chrome/120 Chromium/78",
                "Chromium",
            ),
            (
                "Mozilla/5.0 (Windows NT 10.0) Firefox/120 Chrome/120 "
                "Safari/537.36",
                "Firefox",
            ),
            (
                "Mozilla/5.0 (Windows NT 10.0) MSIE 9.0 Chrome/120",
                "Internet Explorer",
            ),
            (
                "Mozilla/5.0 (Windows NT 10.0) Version/17.0 Safari/605 "
                "CriOS/119",
                "Chrome",
            ),
            (
                "Mozilla/5.0 (Windows NT 10.0) Chrome/120 Edg/120 Edge/12",
                "Edge",
            ),
            (
                "Mozilla/5.0 (Linux; Android 13) Chrome/120 Mobile "
                "Safari/537.36 EdgA/121 YaBrowser/24.1",
                "Edge",
            ),
        ]
        for ua, expected in cases:
            with self.subTest(ua=ua):
                result = self.tool.execute(mode="parse", user_agent=ua)
                self.assertEqual(result["browser"]["name"], expected)


if __name__ == "__main__":
    unittest.main()
