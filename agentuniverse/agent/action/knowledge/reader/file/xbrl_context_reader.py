"""Read local XBRL instance facts without detaching their contexts."""

import hashlib
import json
import re
from copy import deepcopy
from pathlib import Path
from typing import ClassVar

from pydantic import StrictInt

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.store.document import Document

XI = "http://www.xbrl.org/2003/instance"
XD = "http://xbrl.org/2006/xbrldi"
LINK = "http://www.xbrl.org/2003/linkbase"
XSI = "http://www.w3.org/2001/XMLSchema-instance"
NS = {"i": XI, "d": XD}


def _qname(element, value):
    if not value or value != value.strip() or value.count(":") > 1:
        raise ValueError("Invalid QName")
    prefix, local = value.split(":") if ":" in value else (None, value)
    namespace = element.nsmap.get(prefix)
    if not namespace or not re.fullmatch(r"[^\W\d][\w.\-]*", local, re.UNICODE):
        raise ValueError("Unresolved or invalid QName")
    return "{" + namespace + "}" + local


def _one(element, path):
    values = element.findall(path, NS)
    if len(values) != 1:
        raise ValueError(f"Expected exactly one {path}")
    return values[0]


def _text(element):
    if len(element):
        raise ValueError("Expected simple text content")
    return element.text or ""


class XbrlContextReader(Reader):
    """Extract flat instance facts; taxonomy validation is explicitly not performed."""

    max_file_bytes: StrictInt = 20000000
    max_facts: StrictInt = 20000
    max_document_chars: StrictInt = 200000
    max_total_chars: StrictInt = 10000000
    _OPTIONS: ClassVar[dict] = {
        "max_file_bytes": 100000000,
        "max_facts": 100000,
        "max_document_chars": 2000000,
        "max_total_chars": 40000000,
    }

    def _settings(self):
        for key, maximum in self._OPTIONS.items():
            value = getattr(self, key)
            if type(value) is not int or not 1 <= value <= maximum:
                raise ValueError(f"Invalid {key}; expected integer in 1..{maximum}")

    def _initialize_by_component_configer(self, config):
        candidate = self.model_copy(deep=True)
        for key in self._OPTIONS:
            if key in config.configer.value:
                setattr(candidate, key, config.configer.value[key])
        candidate._settings()
        super()._initialize_by_component_configer(config)
        for key in self._OPTIONS:
            setattr(self, key, getattr(candidate, key))
        return self

    @staticmethod
    def _context(element, etree):
        entity = _one(element, "i:entity")
        identifier = _one(entity, "i:identifier")
        if not identifier.get("scheme") or not _text(identifier).strip():
            raise ValueError("Missing entity identifier/scheme")
        period = _one(element, "i:period")
        kinds = [child.tag for child in period]
        allowed = [[f"{{{XI}}}instant"], [f"{{{XI}}}startDate", f"{{{XI}}}endDate"], [f"{{{XI}}}forever"]]
        if kinds not in allowed:
            raise ValueError("Unsupported period structure")
        period_value = {etree.QName(child).localname: _text(child).strip() for child in period}
        if any(not value for key, value in period_value.items() if key != "forever"):
            raise ValueError("Empty period date")
        dimensions, other, seen = [], [], set()
        for location, container in [
            ("segment", entity.find("i:segment", NS)),
            ("scenario", element.find("i:scenario", NS)),
        ]:
            if container is None:
                continue
            for child in container:
                if child.tag in {f"{{{XD}}}explicitMember", f"{{{XD}}}typedMember"}:
                    dimension = _qname(child, child.get("dimension"))
                    if dimension in seen:
                        raise ValueError("Duplicate dimension in context")
                    seen.add(dimension)
                    item = {"dimension": dimension, "location": location}
                    if child.tag == f"{{{XD}}}explicitMember":
                        item.update(kind="explicit", member=_qname(child, _text(child).strip()))
                    else:
                        if len(child) != 1:
                            raise ValueError("Typed member must contain one element")
                        item.update(kind="typed", xml=etree.tostring(child[0], encoding="unicode", with_tail=False))
                    dimensions.append(item)
                else:
                    other.append(
                        {"location": location, "xml": etree.tostring(child, encoding="unicode", with_tail=False)}
                    )
        return {
            "id": element.get("id"),
            "entity": {"scheme": identifier.get("scheme"), "identifier": _text(identifier)},
            "period": period_value,
            "dimensions": dimensions,
            "other_context_content": other,
        }

    @staticmethod
    def _unit(element):
        def measures(parent):
            children = list(parent)
            if not children or any(child.tag != f"{{{XI}}}measure" for child in children):
                raise ValueError("Unsupported unit structure")
            return [_qname(child, _text(child).strip()) for child in children]

        children = list(element)
        if len(children) == 1 and children[0].tag == f"{{{XI}}}divide":
            divide = children[0]
            if len(divide) != 2:
                raise ValueError("Invalid divided unit")
            numerator = measures(_one(divide, "i:unitNumerator"))
            denominator = measures(_one(divide, "i:unitDenominator"))
        else:
            numerator, denominator = measures(element), []
        return {"id": element.get("id"), "numerator": numerator, "denominator": denominator}

    def load_instance(self, file, ext_info=None):
        """Return separate fact Documents and explicit unsupported-content report.

        No taxonomy/network loading, calculation, rounding or currency conversion.
        Values/periods remain lexical claims; this is not a financial validator.
        """
        self._settings()
        if ext_info is not None and (not isinstance(ext_info, dict) or "xbrl_evidence" in ext_info):
            raise ValueError("ext_info must be a dictionary without reserved xbrl_evidence")
        path = Path(file).resolve()
        if path.suffix.lower() not in {".xml", ".xbrl"}:
            raise ValueError("Expected local .xml or .xbrl instance; inline XBRL is unsupported")
        with path.open("rb") as stream:
            raw = stream.read(self.max_file_bytes + 1)
        if len(raw) > self.max_file_bytes:
            raise ValueError("max_file_bytes exceeded")
        try:
            from lxml import etree
        except ImportError as error:
            raise ImportError("XbrlContextReader requires agentUniverse[xbrl_ext]") from error
        parser = etree.XMLParser(
            resolve_entities=False,
            no_network=True,
            load_dtd=False,
            remove_comments=True,
            remove_pis=True,
            huge_tree=False,
            recover=False,
        )
        root = etree.fromstring(raw, parser)
        if root.getroottree().docinfo.doctype:
            raise ValueError("DTD is unsupported")
        if root.tag != f"{{{XI}}}xbrl":
            raise ValueError("Expected XBRL instance root; inline XBRL is unsupported")
        contexts, units, identifiers = {}, {}, set()
        for element in root.iter():
            identifier = element.get("id")
            if identifier:
                if identifier in identifiers:
                    raise ValueError("Duplicate XML id")
                identifiers.add(identifier)
        for tag, target, read in [
            ("context", contexts, lambda e: self._context(e, etree)),
            ("unit", units, self._unit),
        ]:
            for element in root.findall(f"i:{tag}", NS):
                if not element.get("id"):
                    raise ValueError(f"Missing {tag} id")
                target[element.get("id")] = read(element)
        digest = hashlib.sha256(raw).hexdigest()
        report = {
            "file_sha256": digest,
            "taxonomy_validation": "not_performed",
            "schema_references": [],
            "unsupported": [],
            "fact_count": 0,
        }
        documents, total = [], 0
        for index, element in enumerate(root):
            namespace = etree.QName(element).namespace
            if element.tag in {f"{{{XI}}}context", f"{{{XI}}}unit"}:
                continue
            locator = f"/*/*[{index + 1}]"
            if namespace == LINK:
                if element.tag == f"{{{LINK}}}schemaRef":
                    report["schema_references"].append(element.get("{http://www.w3.org/1999/xlink}href"))
                else:
                    report["unsupported"].append({"xpath": locator, "reason": "linkbase_content_not_extracted"})
                continue
            if not element.get("contextRef") or len(element):
                report["unsupported"].append({"xpath": locator, "reason": "tuple_or_complex_content"})
                continue
            context = contexts.get(element.get("contextRef"))
            if context is None:
                raise ValueError("Fact references missing context")
            unit_ref = element.get("unitRef")
            if unit_ref is not None and unit_ref not in units:
                raise ValueError("Fact references missing unit")
            nil = element.get(f"{{{XSI}}}nil", "false").strip()
            if nil not in {"true", "1", "false", "0"}:
                raise ValueError("Invalid xsi:nil")
            value = _text(element)
            if nil in {"true", "1"} and value.strip():
                raise ValueError("Nil fact contains text")
            decimals, precision = element.get("decimals"), element.get("precision")
            if decimals is not None and precision is not None:
                raise ValueError("Fact cannot specify both decimals and precision")
            for name, accuracy in [("decimals", decimals), ("precision", precision)]:
                if accuracy is not None and (
                    not unit_ref or not (accuracy == "INF" or re.fullmatch(r"[+-]?\d+", accuracy))
                ):
                    raise ValueError(f"Invalid {name} or missing unit")
            language = next(
                (
                    parent.get("{http://www.w3.org/XML/1998/namespace}lang")
                    for parent in [element, *element.iterancestors()]
                    if parent.get("{http://www.w3.org/XML/1998/namespace}lang") is not None
                ),
                None,
            )
            fact = {
                "concept": element.tag,
                "fact_id": element.get("id"),
                "context": deepcopy(context),
                "unit": deepcopy(units.get(unit_ref)),
                "nil": nil in {"true", "1"},
                "value": value,
                "decimals": decimals,
                "precision": precision,
                "language": language,
                "taxonomy_validation": "not_performed",
            }
            text = json.dumps(fact, ensure_ascii=False, sort_keys=True)
            total += len(text)
            if len(text) > self.max_document_chars or total > self.max_total_chars or len(documents) >= self.max_facts:
                raise ValueError("Fact extraction budget exceeded")
            metadata = deepcopy(ext_info) if ext_info else {}
            metadata["xbrl_evidence"] = {
                **deepcopy(fact),
                "file_path": str(path),
                "file_sha256": digest,
                "xpath": locator,
                "source_line": element.sourceline,
                "fact_index": len(documents),
            }
            documents.append(
                Document(id=hashlib.sha256((digest + locator).encode()).hexdigest(), text=text, metadata=metadata)
            )
        report["fact_count"] = len(documents)
        return documents, report

    def _load_data(self, file, ext_info=None):
        return self.load_instance(file, ext_info)[0]
