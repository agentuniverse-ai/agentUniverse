#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: mime_type_tool.py

"""MIME type / file extension mapping tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency lookup layer agents
can call before touching files or uploading payloads: extension to
MIME type, MIME type back to extensions, category browsing and a
conservative text-format sniffer.

Lookups are answered by two layers, in order:

* Layer 1 — an embedded, curated table of roughly 195 extensions
  (``_TABLE_SPEC`` below) mapping each extension to a MIME type and a
  coarse category (``image`` / ``audio`` / ``video`` / ``text`` /
  ``binary`` / ``archive`` / ``code`` / ``font`` / ``model``). The
  table is frozen in this file, so every answer is deterministic and
  identical across machines and Python versions. Choices that remain
  genuinely debated are fixed and documented: ``.yaml`` / ``.yml``
  map to ``text/yaml`` (the long-standing practice; RFC 9512 later
  registered ``application/yaml`` in 2024); ``.py`` maps to
  ``text/x-python`` (the value used by the Python documentation);
  dual-suffix archives describe their *outer* container —
  ``.tar.gz`` and ``.tgz`` both map to ``application/gzip`` while a
  plain ``.tar`` maps to ``application/x-tar``; and the ambiguous
  ``.ts`` follows its IANA-registered media type ``video/mp2t`` (MPEG
  transport stream, also what the stdlib reports) rather than
  TypeScript, which keeps ``.tsx`` → ``application/typescript``.
* Layer 2 — a fallback to the standard library ``mimetypes`` module
  for extensions beyond the table. The result is reported with
  ``source: "stdlib"`` and its category is derived from the media
  type's maintype (``image/...`` → image, ..., everything else →
  ``binary``), because the stdlib has no category concept. The
  stdlib table follows the running interpreter, so layer 2 answers
  may differ between Python versions; layer 1 answers never do.

Four modes are supported:

* ``lookup`` — a filename (directories are stripped, POSIX and
  Windows separators both honored) or a bare extension (dot optional,
  case-insensitive) resolves to the MIME type, category, a ``known``
  flag and the ``source`` layer that answered. Unknown extensions
  return ``mime: None`` with ``known: False`` instead of raising.
  Filenames without an extension (including dotfiles such as
  ``.gitignore``, following :func:`os.path.splitext` semantics) also
  return ``known: False``.
* ``reverse`` — a MIME type resolves to the list of common
  extensions from the embedded table, ordered by popularity (the
  order extensions appear in the table, primary spelling first, e.g.
  ``image/jpeg`` → ``jpg`` then ``jpeg``). Parameters such as
  ``; charset=utf-8`` are ignored. Well-formed but unknown types
  return ``known: False`` with an empty list; this mode consults the
  embedded table only (documented limitation).
* ``category`` — lists every embedded-table extension of one of the
  nine categories together with its MIME type, sorted by extension.
* ``sniff`` — a best-effort *text* format guess from a short sample
  (the first ~1 KB) of file content given as a string. Signals, in
  priority order: JSON object/array shape (full ``json.loads`` parse
  when possible, structural shape when the sample is truncated), XML
  declaration, HTML markup tags, Markdown ATX headings, CSV with
  consistent comma-separated columns, and the Base64 alphabet. A
  UTF-8 BOM is reported as additional evidence whatever the verdict.
  The sniffer is deliberately honest: it only distinguishes textual
  formats — binary formats (images, archives, office documents)
  cannot be identified from text heuristics, and Base64 content can
  only be flagged, not decoded to its underlying type here.

Input validation is strict and happens before any computation:
malformed parameters (wrong types, unknown mode or category, a
filename/extension that is neither supplied nor uniquely supplied,
whitespace inside an extension, a MIME type without exactly one
``type/subtype`` pair, an empty or oversized sample) raise a
``ValueError``, mirroring the other common tools. An *unknown but
well-formed* extension or MIME type is not an error — it returns
``known: False`` so an agent can branch without catching exceptions.
"""

import json as json_module
import mimetypes
import re
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# Extension shape: alphanumeric segments joined by single dots
# (allows dual suffixes such as "tar.gz"); at most 24 characters.
_EXT_RE = re.compile(r"\A[a-z0-9]+(?:\.[a-z0-9]+)*\Z")
# RFC 6838-ish media type shape: non-empty type "/" non-empty subtype
# of restricted characters, no parameters, lowercase.
_MIME_RE = re.compile(r"\A[a-z0-9!#$&^_.+-]+/[a-z0-9!#$&^_.+-]+\Z")
# Standard (not urlsafe) Base64 alphabet with trailing padding only.
_BASE64_RE = re.compile(r"\A[A-Za-z0-9+/]+={0,2}\Z")
# ATX heading: one to six '#' followed by whitespace or end of line.
_ATX_RE = re.compile(r"\A#{1,6}(?:\s|\Z)")
# Whitespace collapsed out of a candidate Base64 sample.
_WHITESPACE_RE = re.compile(r"\s+")

# --------------------------------------------------------------------- #
# Layer 1 — the embedded, curated extension table.
#
# Each block is (category, ((extension, mime), ...)). Insertion order
# is meaningful: the first extension registered for a MIME type is
# the most popular spelling and leads the `reverse` result list.
# --------------------------------------------------------------------- #
_TABLE_SPEC: Tuple[Tuple[str, Tuple[Tuple[str, str], ...]], ...] = (
    (
        "text",
        (
            ("txt", "text/plain"),
            ("md", "text/markdown"),
            ("rst", "text/x-rst"),
            ("html", "text/html"),
            ("htm", "text/html"),
            ("css", "text/css"),
            ("csv", "text/csv"),
            ("tsv", "text/tab-separated-values"),
            ("xml", "application/xml"),
            ("json", "application/json"),
            ("jsonl", "application/x-ndjson"),
            ("ndjson", "application/x-ndjson"),
            # YAML: text/yaml per long-standing practice; RFC 9512
            # (2024) registered application/yaml — see the docstring.
            ("yaml", "text/yaml"),
            ("yml", "text/yaml"),
            ("toml", "application/toml"),
            ("ini", "text/plain"),
            ("cfg", "text/plain"),
            ("conf", "text/plain"),
            ("log", "text/plain"),
            ("rtf", "application/rtf"),
            ("ics", "text/calendar"),
            ("vcf", "text/vcard"),
            ("eml", "message/rfc822"),
            ("srt", "application/x-subrip"),
            ("vtt", "text/vtt"),
            ("tex", "application/x-tex"),
            ("gmi", "text/gemini"),
        ),
    ),
    (
        "code",
        (
            ("py", "text/x-python"),
            ("js", "text/javascript"),
            ("mjs", "text/javascript"),
            ("cjs", "text/javascript"),
            # NOTE: '.ts' alone is ambiguous (TypeScript vs MPEG
            # transport stream) and is registered as video/mp2t in
            # the video block below, following IANA and the stdlib;
            # '.tsx' carries the TypeScript mapping here.
            ("tsx", "application/typescript"),
            ("jsx", "text/javascript"),
            ("java", "text/x-java-source"),
            ("c", "text/x-c"),
            ("h", "text/x-c"),
            ("cpp", "text/x-c++"),
            ("cc", "text/x-c++"),
            ("cxx", "text/x-c++"),
            ("hpp", "text/x-c++"),
            ("hxx", "text/x-c++"),
            ("cs", "text/x-csharp"),
            ("go", "text/x-go"),
            ("rs", "text/rust"),
            ("rb", "text/x-ruby"),
            ("php", "application/x-httpd-php"),
            ("swift", "text/x-swift"),
            ("kt", "text/kotlin"),
            ("kts", "text/kotlin"),
            ("scala", "text/x-scala"),
            ("sh", "text/x-shellscript"),
            ("bash", "text/x-shellscript"),
            ("zsh", "text/x-shellscript"),
            ("fish", "text/x-shellscript"),
            ("ps1", "application/x-powershell"),
            ("pl", "text/x-perl"),
            ("pm", "text/x-perl"),
            ("lua", "text/x-lua"),
            ("r", "text/x-r"),
            ("jl", "text/x-julia"),
            ("sql", "application/sql"),
            ("dart", "text/x-dart"),
            ("groovy", "text/x-groovy"),
            ("scss", "text/x-scss"),
            ("sass", "text/x-sass"),
            ("less", "text/less"),
            ("ada", "text/x-ada"),
            ("f90", "text/x-fortran"),
            ("hs", "text/x-haskell"),
            ("clj", "text/x-clojure"),
            ("ex", "text/x-elixir"),
            ("exs", "text/x-elixir"),
            ("erl", "text/x-erlang"),
            ("fs", "text/x-fsharp"),
            ("vb", "text/x-vb"),
            ("asm", "text/x-asm"),
            ("bat", "application/x-bat"),
            ("coffee", "text/coffeescript"),
            ("elm", "text/x-elm"),
            ("nim", "text/x-nim"),
            ("cr", "text/x-crystal"),
            ("zig", "text/zig"),
            ("graphql", "application/graphql"),
            ("proto", "application/x-protobuf"),
            ("ipynb", "application/x-ipynb+json"),
        ),
    ),
    (
        "image",
        (
            ("png", "image/png"),
            ("jpg", "image/jpeg"),
            ("jpeg", "image/jpeg"),
            ("gif", "image/gif"),
            ("webp", "image/webp"),
            ("svg", "image/svg+xml"),
            ("bmp", "image/bmp"),
            ("tif", "image/tiff"),
            ("tiff", "image/tiff"),
            ("ico", "image/x-icon"),
            ("avif", "image/avif"),
            ("heic", "image/heic"),
            ("heif", "image/heif"),
            ("jp2", "image/jp2"),
            ("jxl", "image/jxl"),
            ("psd", "image/vnd.adobe.photoshop"),
            ("eps", "application/postscript"),
            ("xcf", "image/x-xcf"),
        ),
    ),
    (
        "audio",
        (
            ("mp3", "audio/mpeg"),
            ("wav", "audio/wav"),
            ("ogg", "audio/ogg"),
            ("oga", "audio/ogg"),
            ("flac", "audio/flac"),
            ("aac", "audio/aac"),
            ("m4a", "audio/mp4"),
            ("opus", "audio/opus"),
            ("wma", "audio/x-ms-wma"),
            ("aiff", "audio/aiff"),
            ("aif", "audio/aiff"),
            ("mid", "audio/midi"),
            ("midi", "audio/midi"),
            ("amr", "audio/amr"),
            ("au", "audio/basic"),
            ("mka", "audio/x-matroska"),
            ("weba", "audio/webm"),
        ),
    ),
    (
        "video",
        (
            ("mp4", "video/mp4"),
            ("mkv", "video/x-matroska"),
            ("webm", "video/webm"),
            ("mov", "video/quicktime"),
            ("avi", "video/x-msvideo"),
            ("wmv", "video/x-ms-wmv"),
            ("flv", "video/x-flv"),
            ("m4v", "video/x-m4v"),
            ("mpg", "video/mpeg"),
            ("mpeg", "video/mpeg"),
            ("ogv", "video/ogg"),
            ("3gp", "video/3gpp"),
            ("3g2", "video/3g2"),
            ("ts", "video/mp2t"),
            ("m2ts", "video/mp2t"),
            ("vob", "video/mpeg"),
        ),
    ),
    (
        "archive",
        (
            ("zip", "application/zip"),
            ("tar", "application/x-tar"),
            # Dual-suffix archives describe the outer compression
            # container; a plain .tar is application/x-tar.
            ("gz", "application/gzip"),
            ("tgz", "application/gzip"),
            ("tar.gz", "application/gzip"),
            ("bz2", "application/x-bzip2"),
            ("tar.bz2", "application/x-bzip2"),
            ("xz", "application/x-xz"),
            ("tar.xz", "application/x-xz"),
            ("zst", "application/zstd"),
            ("tar.zst", "application/zstd"),
            ("7z", "application/x-7z-compressed"),
            ("rar", "application/vnd.rar"),
            ("lz", "application/x-lzip"),
            ("lzma", "application/x-lzma"),
            ("cab", "application/vnd.ms-cab-compressed"),
            ("iso", "application/x-iso9660-image"),
            ("jar", "application/java-archive"),
            ("apk", "application/vnd.android.package-archive"),
            ("dmg", "application/x-apple-diskimage"),
            ("deb", "application/vnd.debian.binary-package"),
            ("rpm", "application/x-rpm"),
            ("msi", "application/x-msi"),
        ),
    ),
    (
        "binary",
        (
            ("pdf", "application/pdf"),
            ("doc", "application/msword"),
            (
                "docx",
                "application/vnd.openxmlformats-officedocument"
                ".wordprocessingml.document",
            ),
            ("xls", "application/vnd.ms-excel"),
            (
                "xlsx",
                "application/vnd.openxmlformats-officedocument"
                ".spreadsheetml.sheet",
            ),
            ("ppt", "application/vnd.ms-powerpoint"),
            (
                "pptx",
                "application/vnd.openxmlformats-officedocument"
                ".presentationml.presentation",
            ),
            ("odt", "application/vnd.oasis.opendocument.text"),
            ("ods", "application/vnd.oasis.opendocument.spreadsheet"),
            ("odp", "application/vnd.oasis.opendocument.presentation"),
            ("epub", "application/epub+zip"),
            ("bin", "application/octet-stream"),
            ("exe", "application/x-msdownload"),
            ("dll", "application/x-msdownload"),
            ("so", "application/x-sharedlib"),
            ("dylib", "application/octet-stream"),
            ("class", "application/java-vm"),
            ("wasm", "application/wasm"),
            ("o", "application/octet-stream"),
            ("img", "application/octet-stream"),
            ("dat", "application/octet-stream"),
            ("dump", "application/octet-stream"),
            ("pkg", "application/octet-stream"),
            ("lib", "application/octet-stream"),
        ),
    ),
    (
        "font",
        (
            ("ttf", "font/ttf"),
            ("otf", "font/otf"),
            ("woff", "font/woff"),
            ("woff2", "font/woff2"),
            ("eot", "application/vnd.ms-fontobject"),
            ("ttc", "font/collection"),
        ),
    ),
    (
        "model",
        (
            ("gltf", "model/gltf+json"),
            ("glb", "model/gltf-binary"),
            ("obj", "model/obj"),
            ("stl", "model/stl"),
            ("dae", "model/vnd.collada+xml"),
            ("usdz", "model/vnd.usdz+zip"),
            ("3mf", "model/3mf"),
            ("fbx", "application/octet-stream"),
        ),
    ),
)


def _build_maps() -> Tuple[
    Dict[str, Tuple[str, str]], Dict[str, List[str]], Dict[str, str]
]:
    """Build the extension, reverse and mime-category maps from the table."""
    extension_map: Dict[str, Tuple[str, str]] = {}
    for category, entries in _TABLE_SPEC:
        for ext, mime in entries:
            if ext in extension_map:
                raise ValueError(  # pragma: no cover - static table guard
                    f"duplicate extension {ext!r} in the MIME table"
                )
            extension_map[ext] = (mime, category)
    mime_extensions: Dict[str, List[str]] = {}
    mime_category: Dict[str, str] = {}
    for ext, (mime, category) in extension_map.items():
        # Insertion order of the table defines popularity ranking.
        mime_extensions.setdefault(mime, []).append(ext)
        mime_category.setdefault(mime, category)
    return extension_map, mime_extensions, mime_category


_EXTENSION_MAP, _MIME_EXTENSIONS, _MIME_CATEGORY = _build_maps()

_TABLE_SIZE = len(_EXTENSION_MAP)

# Layer 2 — stdlib fallback category derivation from the maintype.
_MAINTYPE_CATEGORY = {
    "image": "image",
    "audio": "audio",
    "video": "video",
    "text": "text",
    "font": "font",
    "model": "model",
}


class MimeTypeTool(Tool):
    """Extension ↔ MIME type mapping tool built purely on the stdlib.

    Attributes:
        max_filename_chars (int): Upper bound on a ``filename`` input.
        max_sample_chars (int): Upper bound on a sniff ``sample``
            input; only the first :data:`SNIFF_WINDOW` characters are
            analyzed.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "mime_type_tool"
    description: str = (
        "MIME type tool — pure Python stdlib, no network required. "
        "Map a filename or extension (dot-optional, case-insensitive) "
        "to a MIME type, category and known flag (mode='lookup', "
        "embedded ~195-entry table first, stdlib mimetypes fallback "
        "beyond it); map a MIME type back to its common extensions "
        "ordered by popularity (mode='reverse'); list every extension "
        "of a category image/audio/video/text/binary/archive/code/"
        "font/model with its MIME type (mode='category'); or sniff a "
        "short text sample for JSON, XML, HTML, Markdown, CSV or "
        "Base64 signatures (mode='sniff', textual formats only)."
    )

    MODES: ClassVar[tuple] = ("lookup", "reverse", "category", "sniff")
    CATEGORIES: ClassVar[tuple] = (
        "image",
        "audio",
        "video",
        "text",
        "binary",
        "archive",
        "code",
        "font",
        "model",
    )

    max_filename_chars: int = 4096
    max_sample_chars: int = 100_000
    SNIFF_WINDOW: ClassVar[int] = 1024

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        filename: Any = None,
        extension: Any = None,
        mime: Any = None,
        category: Any = None,
        sample: Any = None,
    ) -> Dict[str, Any]:
        """Run one MIME type operation.

        Args:
            mode (str): One of ``lookup`` / ``reverse`` / ``category`` /
                ``sniff``.
            filename (str): Lookup mode — a filename, optionally with
                directories (POSIX or Windows separators); the
                extension of the basename is resolved. Provide exactly
                one of ``filename`` / ``extension``.
            extension (str): Lookup mode — a bare extension, dot
                optional, case-insensitive; dual suffixes such as
                ``tar.gz`` are accepted.
            mime (str): Reverse mode — a MIME type such as
                ``image/jpeg``; parameters after ``;`` are ignored.
            category (str): Category mode — one of the nine
                categories listed in ``CATEGORIES``.
            sample (str): Sniff mode — the first part of the file
                content as a string (typically the first ~1 KB); only
                textual formats can be detected.

        Returns:
            Dict[str, Any]: The lookup / reverse / category / sniff
                result. Unknown but well-formed extensions and MIME
                types return ``known: False`` instead of raising.

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        if mode == "lookup":
            return self._run_lookup(filename, extension)
        if mode == "reverse":
            return self._run_reverse(mime)
        if mode == "category":
            return self._run_category(category)
        return self._run_sniff(sample)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"mime_type_tool: {message}")

    @classmethod
    def _validate_string(
        cls, value: Any, label: str, max_chars: int
    ) -> str:
        """Validate a plain non-empty string input."""
        if (
            value is None
            or isinstance(value, bool)
            or not isinstance(value, str)
        ):
            cls._invalid(f"{label} must be a non-empty string (got {value!r})")
        if not value:
            cls._invalid(f"{label} must be a non-empty string (got '')")
        if len(value) > max_chars:
            cls._invalid(
                f"{label} exceeds the {max_chars:,}-character limit "
                f"(got {len(value):,} characters)"
            )
        return value

    @classmethod
    def _normalize_extension(cls, ext_key: str) -> str:
        """Validate the shape of a lowercase, dot-free-lead extension key."""
        if not _EXT_RE.match(ext_key) or len(ext_key) > 24:
            cls._invalid(
                "extension must be 1-24 characters of alphanumeric "
                "segments joined by single dots, without whitespace or "
                f"path separators (got {ext_key!r})"
            )
        return ext_key

    # ------------------------------------------------------------------ #
    # lookup mode
    # ------------------------------------------------------------------ #

    def _run_lookup(
        self, filename: Any, extension: Any
    ) -> Dict[str, Any]:
        """Resolve a filename or bare extension to a MIME type."""
        if filename is not None and extension is not None:
            self._invalid(
                "provide either filename or extension, not both "
                f"(got filename={filename!r}, extension={extension!r})"
            )
        if filename is None and extension is None:
            self._invalid(
                "lookup requires either a filename or an extension "
                "(both are None)"
            )

        input_kind: str
        basename: Optional[str]
        ext_key: Optional[str]
        if filename is not None:
            clean = self._validate_string(
                filename, "filename", self.max_filename_chars
            )
            if "\x00" in clean:
                self._invalid("filename must not contain NUL characters")
            input_kind = "filename"
            basename = self._basename(clean)
            ext_key = self._extension_of(basename)
        else:
            if isinstance(extension, bool) or not isinstance(extension, str):
                self._invalid(
                    f"extension must be a non-empty string (got {extension!r})"
                )
            if not extension:
                self._invalid("extension must be a non-empty string (got '')")
            input_kind = "extension"
            basename = None
            ext_key = extension.strip().lower().lstrip(".")
            if "/" in ext_key or "\\" in ext_key:
                self._invalid(
                    "extension must not contain path separators "
                    f"(got {extension!r})"
                )
            self._normalize_extension(ext_key)

        return self._lookup_result(input_kind, basename, ext_key)

    @staticmethod
    def _basename(filename: str) -> str:
        """Return the final path segment (POSIX and Windows separators)."""
        cut = max(filename.rfind("/"), filename.rfind("\\"))
        return filename[cut + 1:] if cut >= 0 else filename

    @classmethod
    def _extension_of(cls, basename: str) -> Optional[str]:
        """Extract the (possibly dual) lowercase extension of a basename.

        Follows :func:`os.path.splitext` semantics: a leading dot does
        not start an extension, so dotfiles such as ``.gitignore``
        have no extension. Dual suffixes (``.tar.gz``) are returned
        whole when the table knows the compound form.
        """
        if not basename or basename.startswith("."):
            return None
        last = basename.rfind(".")
        if last <= 0:
            return None
        ext = basename[last + 1:].strip().lower()
        if not ext or not _EXT_RE.match(ext):
            return None
        dual = basename.rfind(".", 0, last)
        if dual > 0:
            compound = basename[dual + 1:].strip().lower()
            if compound in _EXTENSION_MAP:
                return compound
        return ext

    def _lookup_result(
        self,
        input_kind: str,
        basename: Optional[str],
        ext_key: Optional[str],
    ) -> Dict[str, Any]:
        """Answer a lookup from the table, then the stdlib fallback."""
        context: Dict[str, Any] = {
            "mode": "lookup",
            "input_kind": input_kind,
            "filename": basename,
        }
        if ext_key is None:
            return {
                **context,
                "extension": None,
                "mime": None,
                "category": None,
                "known": False,
                "source": None,
                "compound": False,
            }
        context["extension"] = "." + ext_key
        context["compound"] = "." in ext_key
        entry = _EXTENSION_MAP.get(ext_key)
        if entry is not None:
            mime, category = entry
            return {**context, "mime": mime, "category": category,
                    "known": True, "source": "table"}
        # Layer 2 — stdlib fallback for extensions beyond the table.
        stdlib_mime = mimetypes.types_map.get("." + ext_key)
        if stdlib_mime:
            return {
                **context,
                "mime": stdlib_mime,
                "category": self._stdlib_category(stdlib_mime),
                "known": True,
                "source": "stdlib",
            }
        return {
            **context,
            "mime": None,
            "category": None,
            "known": False,
            "source": None,
        }

    @staticmethod
    def _stdlib_category(mime: str) -> str:
        """Derive a category for a stdlib media type from its maintype."""
        return _MAINTYPE_CATEGORY.get(mime.split("/", 1)[0], "binary")

    # ------------------------------------------------------------------ #
    # reverse mode (embedded table only)
    # ------------------------------------------------------------------ #

    def _run_reverse(self, mime: Any) -> Dict[str, Any]:
        """Resolve a MIME type to its common extensions."""
        clean = self._validate_string(mime, "mime", 255)
        normalized = clean.strip().lower().split(";", 1)[0].strip()
        if not _MIME_RE.match(normalized):
            self._invalid(
                "mime must be a well-formed media type 'type/subtype' "
                f"such as 'image/jpeg' (got {clean[:64]!r})"
            )
        extensions = _MIME_EXTENSIONS.get(normalized)
        if extensions is None:
            return {
                "mode": "reverse",
                "mime": normalized,
                "extensions": [],
                "category": None,
                "known": False,
            }
        return {
            "mode": "reverse",
            "mime": normalized,
            "extensions": ["." + ext for ext in extensions],
            "category": _MIME_CATEGORY[normalized],
            "known": True,
        }

    # ------------------------------------------------------------------ #
    # category mode
    # ------------------------------------------------------------------ #

    def _run_category(self, category: Any) -> Dict[str, Any]:
        """List every extension of one category with its MIME type."""
        if category not in self.CATEGORIES:
            self._invalid(
                "category must be one of: "
                f"{', '.join(self.CATEGORIES)} (got {category!r})"
            )
        entries = [
            (ext, mime)
            for cat, block in _TABLE_SPEC
            if cat == category
            for ext, mime in block
        ]
        entries.sort(key=lambda item: item[0])
        return {
            "mode": "category",
            "category": category,
            "count": len(entries),
            "entries": [
                {"extension": "." + ext, "mime": mime} for ext, mime in entries
            ],
        }

    # ------------------------------------------------------------------ #
    # sniff mode (textual formats only)
    # ------------------------------------------------------------------ #

    def _run_sniff(self, sample: Any) -> Dict[str, Any]:
        """Best-effort textual format guess from a short content sample."""
        clean = self._validate_string(
            sample, "sample", self.max_sample_chars
        )
        analyzed = clean[: self.SNIFF_WINDOW]
        truncated = len(clean) > self.SNIFF_WINDOW
        evidence: List[str] = []

        has_bom = analyzed.startswith("\ufeff")
        body = analyzed[1:] if has_bom else analyzed
        if has_bom:
            evidence.append("UTF-8 BOM (U+FEFF) present at the start")

        mime, reason, is_base64 = self._sniff_body(body, truncated)
        if reason:
            evidence.insert(0, reason)
        return {
            "mode": "sniff",
            "mime": mime,
            "category": _MIME_CATEGORY.get(mime),
            "evidence": evidence,
            "analyzed_chars": len(analyzed),
            "truncated": truncated,
            "is_base64": is_base64,
        }

    @classmethod
    def _sniff_body(
        cls, body: str, truncated: bool
    ) -> Tuple[str, Optional[str], bool]:
        """Apply the sniff heuristics in priority order to the body."""
        stripped = body.strip()

        # 1. JSON object / array — full parse when possible, else shape.
        if stripped and stripped[0] in "{[":
            try:
                json_module.loads(stripped)
                kind = "object" if stripped[0] == "{" else "array"
                return (
                    "application/json",
                    f"sample parses as a JSON {kind}",
                    False,
                )
            except ValueError:
                ends_well = stripped[-1] in "}]"
                if (ends_well or truncated) and '"' in stripped and (
                    ":" in stripped or "," in stripped
                ):
                    return (
                        "application/json",
                        "JSON object/array shape (starts with '{' or "
                        "'[' and ends with '}' or ']' or is truncated)",
                        False,
                    )

        # 2. XML declaration.
        if body.lstrip().startswith("<?xml"):
            return "application/xml", "XML declaration '<?xml' at the start", False

        # 3. HTML markup.
        lowered = body.lower()
        tags = [
            tag
            for tag in ("<!doctype html", "<html", "<head", "<body")
            if tag in lowered
        ]
        if tags:
            return (
                "text/html",
                "HTML markup detected (tags: " + ", ".join(tags) + ")",
                False,
            )

        # 4. Markdown ATX heading.
        for line in body.splitlines():
            if _ATX_RE.match(line):
                return (
                    "text/markdown",
                    "Markdown ATX heading line ('# ...') found",
                    False,
                )

        # 5. CSV — at least two non-empty lines with the same number
        #    (>= 2) of comma-separated fields on every line.
        lines = [line for line in body.splitlines() if line.strip()]
        if len(lines) >= 2:
            widths = {line.count(",") + 1 for line in lines}
            if len(widths) == 1 and next(iter(widths)) >= 2:
                width = next(iter(widths))
                return (
                    "text/csv",
                    f"consistent comma-separated columns "
                    f"({len(lines)} non-empty lines each with {width} fields)",
                    False,
                )

        # 6. Base64 alphabet (standard, not urlsafe). A candidate must
        #    also contain at least one digit, uppercase letter, '+'/'/'
        #    or '=' — squashed lowercase prose (e.g. "wordword...")
        #    matches the bare alphabet but is not Base64 in practice.
        compact = _WHITESPACE_RE.sub("", body)
        if (
            len(compact) >= 16
            and _BASE64_RE.match(compact)
            and re.search(r"[A-Z0-9+/=]", compact)
            and (len(compact) % 4 == 0 or truncated)
            and len(compact) % 4 != 1
        ):
            return (
                "application/octet-stream",
                "sample consists solely of Base64 alphabet characters "
                "with consistent padding; the decoded payload is binary "
                "and needs separate inspection",
                True,
            )

        # 7. Give up honestly.
        return (
            "text/plain",
            "no structured text signature detected; defaulting to text/plain",
            False,
        )
