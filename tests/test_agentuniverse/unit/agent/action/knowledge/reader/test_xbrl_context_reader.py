"""Real XML instances compared with independent Arelle parsing."""

import hashlib
import json
import shutil
from pathlib import Path
from unittest.mock import patch

import pytest

from agentuniverse.agent.action.knowledge.reader.file.xbrl_context_reader import XbrlContextReader

INSTANCE = """<?xml version="1.0"?>
<x:xbrl xmlns:x="http://www.xbrl.org/2003/instance" xmlns:t="urn:example:taxonomy"
 xmlns:d="http://xbrl.org/2006/xbrldi" xmlns:iso="http://www.xbrl.org/2003/iso4217"
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:link="http://www.xbrl.org/2003/linkbase"
 xmlns:xl="http://www.w3.org/1999/xlink" xml:lang="en">
 <link:schemaRef xl:type="simple" xl:href="taxonomy.xsd"/>
 <x:context id="current"><x:entity><x:identifier scheme="urn:lei">COMPANY-A</x:identifier>
 <x:segment><d:explicitMember dimension="t:RegionAxis">t:Asia</d:explicitMember></x:segment></x:entity>
 <x:period><x:startDate>2025-01-01</x:startDate><x:endDate>2025-12-31</x:endDate></x:period></x:context>
 <x:context id="prior"><x:entity><x:identifier scheme="urn:lei">COMPANY-A</x:identifier></x:entity>
 <x:period><x:instant>2024-12-31</x:instant></x:period>
 <x:scenario><d:typedMember dimension="t:ProductAxis"><t:Product>hardware</t:Product></d:typedMember></x:scenario></x:context>
 <x:unit id="USD"><x:measure>iso:USD</x:measure></x:unit>
 <x:unit id="EUR"><x:measure>iso:EUR</x:measure></x:unit>
 <x:unit id="ratio"><x:divide><x:unitNumerator><x:measure>iso:USD</x:measure></x:unitNumerator>
 <x:unitDenominator><x:measure>x:shares</x:measure></x:unitDenominator></x:divide></x:unit>
 <t:Revenue id="f1" contextRef="current" unitRef="USD" decimals="-3">120000</t:Revenue>
 <t:Revenue id="f2" contextRef="prior" unitRef="EUR" decimals="INF">98000</t:Revenue>
 <t:Revenue id="f3" contextRef="prior" unitRef="USD" xsi:nil="true"/>
 <t:EPS contextRef="current" unitRef="ratio" precision="3">1.25</t:EPS>
 <t:Note contextRef="current" xml:lang="zh">收入说明</t:Note>
</x:xbrl>"""

SCHEMA = """<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:x="http://www.xbrl.org/2003/instance"
 targetNamespace="urn:example:taxonomy" xmlns:t="urn:example:taxonomy" elementFormDefault="qualified">
 <xs:import namespace="http://www.xbrl.org/2003/instance" schemaLocation="xbrl-instance.xsd"/>
 <xs:element name="Revenue" type="x:monetaryItemType" substitutionGroup="x:item" x:periodType="duration" nillable="true"/>
 <xs:element name="EPS" type="x:decimalItemType" substitutionGroup="x:item" x:periodType="duration"/>
 <xs:element name="Note" type="x:stringItemType" substitutionGroup="x:item" x:periodType="duration"/>
</xs:schema>"""
# Minimal local base declarations for Arelle's fact classification. This is an
# extraction oracle, not a taxonomy/schema/dimensional conformance assertion.
BASE_SCHEMA = """<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema" targetNamespace="http://www.xbrl.org/2003/instance"
 xmlns:x="http://www.xbrl.org/2003/instance" elementFormDefault="qualified">
 <xs:element name="item" abstract="true"/>
 <xs:complexType name="monetaryItemType"><xs:simpleContent><xs:extension base="xs:decimal"/></xs:simpleContent></xs:complexType>
 <xs:complexType name="decimalItemType"><xs:simpleContent><xs:extension base="xs:decimal"/></xs:simpleContent></xs:complexType>
 <xs:complexType name="stringItemType"><xs:simpleContent><xs:extension base="xs:string"/></xs:simpleContent></xs:complexType>
</xs:schema>"""


def fixture(tmp_path, xml=INSTANCE):
    path = tmp_path / "report.xbrl"
    path.write_text(xml, encoding="utf-8")
    (tmp_path / "taxonomy.xsd").write_text(SCHEMA)
    (tmp_path / "xbrl-instance.xsd").write_text(BASE_SCHEMA)
    return path


def test_facts_keep_context_units_nil_and_coordinates(tmp_path):
    path = fixture(tmp_path)
    before = path.read_bytes()
    docs, report = XbrlContextReader().load_instance(path)
    assert len(docs) == 5
    assert report["taxonomy_validation"] == "not_performed"
    assert report["schema_references"] == ["taxonomy.xsd"]
    facts = [json.loads(doc.text) for doc in docs]
    assert [f["value"] for f in facts] == ["120000", "98000", "", "1.25", "收入说明"]
    assert facts[0]["context"]["period"] == {"startDate": "2025-01-01", "endDate": "2025-12-31"}
    assert facts[1]["context"]["period"] == {"instant": "2024-12-31"}
    assert facts[0]["unit"]["numerator"] == ["{http://www.xbrl.org/2003/iso4217}USD"]
    assert facts[1]["unit"]["numerator"] == ["{http://www.xbrl.org/2003/iso4217}EUR"]
    assert facts[2]["nil"] is True
    assert facts[3]["unit"]["denominator"] == ["{http://www.xbrl.org/2003/instance}shares"]
    assert facts[4]["language"] == "zh"
    assert facts[0]["context"]["dimensions"][0]["member"] == "{urn:example:taxonomy}Asia"
    assert "hardware" in facts[1]["context"]["dimensions"][0]["xml"]
    assert len({d.id for d in docs}) == 5
    for doc in docs:
        info = doc.metadata["xbrl_evidence"]
        assert info["source_line"] > 0 and info["xpath"].startswith("/*/*[")
        assert info["file_sha256"] == hashlib.sha256(before).hexdigest()
    assert path.read_bytes() == before


def test_independent_arelle_offline_oracle(tmp_path):
    from arelle import Cntlr

    path = fixture(tmp_path)
    controller = Cntlr.Cntlr(logFileName="logToBuffer")
    controller.webCache.workOffline = True
    model = controller.modelManager.load(str(path))
    try:
        docs = XbrlContextReader().load_data(path)
        assert len(model.facts) == len(docs) == 5
        for doc, fact in zip(docs, model.facts):
            info = doc.metadata["xbrl_evidence"]
            assert info["concept"] == fact.qname.clarkNotation
            assert info["context"]["id"] == fact.contextID
            assert info["context"]["entity"]["identifier"] == fact.context.entityIdentifier[1]
            assert info["nil"] == fact.isNil
            assert info["value"] == fact.value
            assert info["decimals"] == fact.get("decimals")
            if fact.unitID:
                assert info["unit"]["numerator"] == [q.clarkNotation for q in fact.unit.measures[0]]
                assert info["unit"]["denominator"] == [q.clarkNotation for q in fact.unit.measures[1]]
        current = model.contexts["current"]
        assert current.startDatetime.year == 2025 and current.endDatetime.year == 2026
        assert current.entityIdentifier == ("urn:lei", "COMPANY-A")
        assert next(iter(current.qnameDims.values())).memberQname.clarkNotation == "{urn:example:taxonomy}Asia"
    finally:
        model.close()
        controller.close()


@pytest.mark.parametrize(
    "old,new,match",
    [
        ('contextRef="current"', 'contextRef="missing"', "missing context"),
        ('unitRef="USD"', 'unitRef="missing"', "missing unit"),
        ('id="f2"', 'id="f1"', "Duplicate"),
        ('decimals="-3"', 'decimals="-3" precision="4"', "both"),
        ('decimals="-3"', 'decimals="bad"', "decimals"),
        ('xsi:nil="true"/>', 'xsi:nil="true">5</t:Revenue>', "Nil"),
        ('xsi:nil="true"', 'xsi:nil="maybe"', "xsi:nil"),
        ("iso:USD</x:measure>", "unknown:USD</x:measure>", "QName"),
        ("<x:instant>2024-12-31</x:instant>", "<x:instant/>", "Empty period"),
    ],
)
def test_invalid_references_and_metadata_fail(tmp_path, old, new, match):
    with pytest.raises(ValueError, match=match):
        XbrlContextReader().load_data(fixture(tmp_path, INSTANCE.replace(old, new)))


def test_explicit_unsupported_tuple_and_inline(tmp_path):
    xml = INSTANCE.replace("</x:xbrl>", '<t:Tuple><t:Note contextRef="current">nested</t:Note></t:Tuple></x:xbrl>')
    docs, report = XbrlContextReader().load_instance(fixture(tmp_path, xml))
    assert len(docs) == 5 and report["unsupported"][0]["reason"] == "tuple_or_complex_content"
    with pytest.raises(ValueError, match="inline"):
        XbrlContextReader().load_data(fixture(tmp_path, '<html xmlns="http://www.w3.org/1999/xhtml"/>'))


@pytest.mark.parametrize(
    "settings",
    [
        {"max_file_bytes": 10},
        {"max_facts": 2},
        {"max_document_chars": 10},
        {"max_total_chars": 10},
        {"max_facts": True},
        {"max_facts": 0},
    ],
)
def test_budgets(tmp_path, settings):
    with pytest.raises(ValueError):
        XbrlContextReader(**settings).load_data(fixture(tmp_path))


def test_metadata_isolation_and_relocation(tmp_path):
    path = fixture(tmp_path)
    docs = XbrlContextReader().load_data(path, {"team": ["research"]})
    docs[0].metadata["team"].append("changed")
    assert docs[1].metadata["team"] == ["research"]
    copy = tmp_path / "copy.xml"
    copy.write_bytes(path.read_bytes())
    assert [d.id for d in docs] == [d.id for d in XbrlContextReader().load_data(copy)]
    with pytest.raises(ValueError, match="reserved"):
        XbrlContextReader().load_data(path, {"xbrl_evidence": {}})


def test_real_yaml_public_knowledge_sqlite_roundtrip(tmp_path):
    import agentuniverse.base.annotation.trace as trace_module
    from agentuniverse.agent.action.knowledge.doc_processor.doc_processor_manager import DocProcessorManager
    from agentuniverse.agent.action.knowledge.doc_processor.jieba_keyword_extractor import JiebaKeywordExtractor
    from agentuniverse.agent.action.knowledge.knowledge import Knowledge
    from agentuniverse.agent.action.knowledge.rag_router.base_router import BaseRouter
    from agentuniverse.agent.action.knowledge.rag_router.rag_router_manager import RagRouterManager
    from agentuniverse.agent.action.knowledge.reader.reader_manager import ReaderManager
    from agentuniverse.agent.action.knowledge.store.sqlite_store import SQLiteStore
    from agentuniverse.agent.action.knowledge.store.store_manager import StoreManager
    from agentuniverse.base.config.application_configer.app_configer import AppConfiger
    from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
    from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
    from agentuniverse.base.config.configer import Configer

    path = fixture(tmp_path)
    managers = [ReaderManager(), StoreManager(), RagRouterManager(), DocProcessorManager()]
    pools = [dict(manager._instance_obj_map) for manager in managers]
    apps = ApplicationConfigManager()
    try:
        previous = apps.app_configer
    except ValueError:
        previous = None
    knowledge, store = None, None
    try:
        app = Configer()
        app.value = {"BASE_INFO": {"appname": "xbrl-evidence-test"}}
        apps.app_configer = AppConfiger().load_by_configer(app)
        root = next(parent for parent in Path(__file__).parents if (parent / "pyproject.toml").is_file())
        copied = tmp_path / "reader.yaml"
        shutil.copyfile(
            root / "agentuniverse/agent/action/knowledge/reader/file/xbrl_context_reader.yaml.example", copied
        )
        config = ComponentConfiger().load_by_configer(Configer(str(copied)).load())
        reader = XbrlContextReader().initialize_by_component_configer(config)
        store = SQLiteStore(
            name="xbrl_store", db_path=str(tmp_path / "knowledge.db"), keyword_extractor="xbrl_keywords"
        )
        store._new_client()
        components = [
            reader,
            store,
            BaseRouter(name="base_router"),
            JiebaKeywordExtractor(name="xbrl_keywords", top_k=20),
        ]
        for manager, component in zip(managers, components):
            manager.register(component.get_instance_code(), component)
        knowledge = Knowledge(stores=["xbrl_store"], readers={"xbrl": "xbrl_context_reader"})
        knowledge.insert_knowledge(source_path=str(path))
        with patch.object(trace_module, "ConversationMemoryModule"), patch.object(trace_module, "Monitor") as monitor:
            monitor.get_invocation_chain.return_value = []
            result = knowledge.query_knowledge(query_str="Revenue")
        assert len(result) == 3
        assert result[0].metadata["xbrl_evidence"]["concept"] == "{urn:example:taxonomy}Revenue"
        assert result[0].metadata["xbrl_evidence"]["file_sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
    finally:
        if knowledge is not None:
            knowledge.insert_executor.shutdown(wait=True)
            knowledge.query_executor.shutdown(wait=True)
        if store is not None and store.conn is not None:
            store.conn.close()
        for manager, pool in zip(managers, pools):
            manager._instance_obj_map.clear()
            manager._instance_obj_map.update(pool)
        apps.app_configer = previous


def test_forever_other_context_and_unresolved_taxonomy_report(tmp_path):
    xml = INSTANCE.replace("<x:instant>2024-12-31</x:instant>", "<x:forever/>")
    xml = xml.replace("</x:scenario>", "<t:Classification>unaudited</t:Classification></x:scenario>")
    xml = xml.replace("taxonomy.xsd", "https://example.invalid/never-fetch.xsd")
    docs, report = XbrlContextReader().load_instance(fixture(tmp_path, xml))
    assert report["schema_references"] == ["https://example.invalid/never-fetch.xsd"]
    info = docs[1].metadata["xbrl_evidence"]
    assert info["context"]["period"] == {"forever": ""}
    assert "unaudited" in info["context"]["other_context_content"][0]["xml"]
    assert info["language"] == "en"


def test_dtd_and_malformed_xml_rejected(tmp_path):
    from lxml import etree

    with pytest.raises(ValueError, match="DTD"):
        XbrlContextReader().load_data(fixture(tmp_path, INSTANCE.replace('<?xml version="1.0"?>', "<!DOCTYPE xbrl>")))
    with pytest.raises(etree.XMLSyntaxError):
        XbrlContextReader().load_data(fixture(tmp_path, INSTANCE[:-10]))


def test_duplicate_dimensions_rejected(tmp_path):
    member = '<d:explicitMember dimension="t:RegionAxis">t:Asia</d:explicitMember>'
    with pytest.raises(ValueError, match="Duplicate dimension"):
        XbrlContextReader().load_data(fixture(tmp_path, INSTANCE.replace(member, member + member)))
