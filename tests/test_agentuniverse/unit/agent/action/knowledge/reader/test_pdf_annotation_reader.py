"""Real exported PDFs, with independent PyMuPDF annotation inspection."""

import hashlib
import io
import shutil
from pathlib import Path
from unittest.mock import patch

import pytest
from pypdf import PdfReader, PdfWriter
from pypdf.generic import ArrayObject, DictionaryObject, FloatObject, NameObject, NumberObject, TextStringObject
from reportlab.pdfgen.canvas import Canvas

from agentuniverse.agent.action.knowledge.reader.file.pdf_annotation_reader import PdfAnnotationReader


def annotation(subtype="/Text", contents="review evidence", rect=(80, 430, 180, 450), quads=None):
    obj = DictionaryObject(
        {
            NameObject("/Type"): NameObject("/Annot"),
            NameObject("/Subtype"): NameObject(subtype),
            NameObject("/Rect"): ArrayObject([FloatObject(v) for v in rect]),
            NameObject("/Contents"): TextStringObject(contents),
            NameObject("/T"): TextStringObject("Reviewer A"),
            NameObject("/CreationDate"): TextStringObject("D:20260101120000+08'00'"),
        }
    )
    if quads:
        obj[NameObject("/QuadPoints")] = ArrayObject([FloatObject(v) for v in quads])
    return obj


def fixture(tmp_path):
    stream = io.BytesIO()
    canvas = Canvas(stream, pagesize=(400, 600))
    for label in ["Review evidence - normal page", "Review evidence - rotated and cropped"]:
        canvas.drawString(60, 540, label)
        canvas.drawString(80, 435, "Anchored source text")
        canvas.showPage()
    canvas.save()
    writer = PdfWriter()
    writer.clone_document_from_reader(PdfReader(io.BytesIO(stream.getvalue())))
    comment = writer.add_annotation(0, annotation(rect=(20, 470, 40, 490)))
    highlight = annotation("/Highlight", "highlight review", quads=(80, 450, 180, 450, 80, 430, 180, 430))
    highlight[NameObject("/C")] = ArrayObject([FloatObject(1), FloatObject(1), FloatObject(0)])
    writer.add_annotation(0, highlight)
    reply = annotation(contents="reply evidence", rect=(20, 430, 40, 450))
    reply[NameObject("/IRT")] = comment.indirect_reference
    reply[NameObject("/RT")] = NameObject("/R")
    writer.add_annotation(0, reply)
    orphan = annotation(contents="orphan reply", rect=(20, 390, 40, 410))
    orphan[NameObject("/IRT")] = writer._add_object(annotation(contents="unlisted parent"))
    writer.add_annotation(0, orphan)
    writer.add_annotation(0, annotation("/Link", "not review evidence"))
    writer.add_annotation(1, annotation("/Underline", "", quads=(80, 450, 180, 450, 80, 430, 180, 430)))
    writer.pages[1].cropbox.lower_left = (50, 50)
    writer.pages[1].cropbox.upper_right = (350, 550)
    writer.pages[1].rotate(90)
    path = tmp_path / "review.pdf"
    writer.write(path)
    return path


def test_exported_pdf_coordinates_replies_and_read_only(tmp_path):
    path = fixture(tmp_path)
    original = path.read_bytes()
    docs, report = PdfAnnotationReader().load_annotations(path)
    assert len(docs) == 5 and report["annotation_count"] == 6
    assert report["omitted_annotations"][0]["subtype"] == "/Link"
    info = [doc.metadata["pdf_annotation"] for doc in docs]
    assert info[0]["contents"] == "review evidence" and info[0]["author"] == "Reviewer A"
    assert info[0]["creation_date_raw"] == "D:20260101120000+08'00'"
    assert info[2]["reply_status"] == "resolved" and info[2]["reply_to_document_id"] == docs[0].id
    assert info[3]["reply_status"] == "orphan_or_direct_reference"
    assert info[4]["page_number"] == 2 and info[4]["contents"] == ""
    assert info[4]["page_rotation"] == 90 and info[4]["crop_box"] == [50, 50, 350, 550]
    assert info[4]["quad_points"] == [80, 450, 180, 450, 80, 430, 180, 430]
    assert not any(i["anchor_text_extracted"] for i in info)
    assert path.read_bytes() == original
    assert report["file_sha256"] == hashlib.sha256(original).hexdigest()


def test_independent_pymupdf_inspection(tmp_path):
    import pymupdf

    path = fixture(tmp_path)
    docs = PdfAnnotationReader().load_data(path)
    with pymupdf.open(path) as pdf:
        page = pdf[0]
        annotations = list(page.annots())
        assert len(annotations) == 4
        assert [a.info["content"] for a in annotations] == [d.metadata["pdf_annotation"]["contents"] for d in docs[:4]]
        assert annotations[2].irt_xref == annotations[0].xref
        quads = docs[1].metadata["pdf_annotation"]["quad_points"]
        converted = [
            tuple(pymupdf.Point(*quads[i : i + 2]) * page.transformation_matrix) for i in range(0, len(quads), 2)
        ]
        assert annotations[1].vertices == converted
        cropped = pdf[1]
        assert cropped.rotation == 90
        underlined = next(cropped.annots())
        assert underlined.vertices == [(30, 100), (130, 100), (30, 120), (130, 120)]
        assert underlined.info["content"] == ""


@pytest.mark.parametrize(
    "settings",
    [
        {"max_file_bytes": 10},
        {"max_pages": 1},
        {"max_annotations": 2},
        {"max_document_chars": 10},
        {"max_total_chars": 10},
        {"max_pages": True},
        {"max_pages": 0},
    ],
)
def test_limits(tmp_path, settings):
    with pytest.raises(ValueError):
        PdfAnnotationReader(**settings).load_data(fixture(tmp_path))


def test_encrypted_and_empty_pdf(tmp_path):
    writer = PdfWriter()
    writer.add_blank_page(400, 600)
    empty = tmp_path / "empty.pdf"
    writer.write(empty)
    docs, report = PdfAnnotationReader().load_annotations(empty)
    assert docs == [] and report["annotation_count"] == 0
    writer.encrypt("password")
    encrypted = tmp_path / "encrypted.pdf"
    writer.write(encrypted)
    with pytest.raises(ValueError, match="Encrypted"):
        PdfAnnotationReader().load_data(encrypted)


@pytest.mark.parametrize(
    "key,value",
    [
        ("/Rect", ArrayObject([NumberObject(1)])),
        ("/QuadPoints", ArrayObject([NumberObject(1)])),
        ("/Contents", NumberObject(5)),
    ],
)
def test_invalid_annotation_fields(tmp_path, key, value):
    writer = PdfWriter()
    writer.add_blank_page(400, 600)
    obj = annotation()
    obj[NameObject(key)] = value
    writer.add_annotation(0, obj)
    path = tmp_path / "invalid.pdf"
    writer.write(path)
    with pytest.raises(ValueError):
        PdfAnnotationReader().load_data(path)


def test_metadata_isolation_and_relocation(tmp_path):
    path = fixture(tmp_path)
    docs = PdfAnnotationReader().load_data(path, {"team": ["review"]})
    docs[0].metadata["team"].append("changed")
    assert docs[1].metadata["team"] == ["review"]
    copy = tmp_path / "copy.pdf"
    copy.write_bytes(path.read_bytes())
    assert [d.id for d in docs] == [d.id for d in PdfAnnotationReader().load_data(copy)]
    with pytest.raises(ValueError, match="reserved"):
        PdfAnnotationReader().load_data(path, {"pdf_annotation": {}})


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
        app.value = {"BASE_INFO": {"appname": "pdf-evidence-test"}}
        apps.app_configer = AppConfiger().load_by_configer(app)
        root = next(parent for parent in Path(__file__).parents if (parent / "pyproject.toml").is_file())
        copied = tmp_path / "reader.yaml"
        shutil.copyfile(
            root / "agentuniverse/agent/action/knowledge/reader/file/pdf_annotation_reader.yaml.example", copied
        )
        config = ComponentConfiger().load_by_configer(Configer(str(copied)).load())
        reader = PdfAnnotationReader().initialize_by_component_configer(config)
        store = SQLiteStore(name="pdf_store", db_path=str(tmp_path / "knowledge.db"), keyword_extractor="pdf_keywords")
        store._new_client()
        components = [
            reader,
            store,
            BaseRouter(name="base_router"),
            JiebaKeywordExtractor(name="pdf_keywords", top_k=20),
        ]
        for manager, component in zip(managers, components):
            manager.register(component.get_instance_code(), component)
        knowledge = Knowledge(stores=["pdf_store"], readers={"pdf": "pdf_annotation_reader"})
        knowledge.insert_knowledge(source_path=str(path))
        with patch.object(trace_module, "ConversationMemoryModule"), patch.object(trace_module, "Monitor") as monitor:
            monitor.get_invocation_chain.return_value = []
            result = knowledge.query_knowledge(query_str="highlight")
        assert len(result) == 1
        assert result[0].metadata["pdf_annotation"]["contents"] == "highlight review"
        assert result[0].metadata["pdf_annotation"]["file_sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
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


def test_rich_text_action_presence_not_interpreted_and_reply_ambiguity(tmp_path):
    writer = PdfWriter()
    writer.add_blank_page(400, 600)
    obj = annotation(contents="plain review")
    obj[NameObject("/RC")] = TextStringObject("<b>rich alternate</b>")
    obj[NameObject("/A")] = DictionaryObject(
        {NameObject("/S"): NameObject("/URI"), NameObject("/URI"): TextStringObject("https://example.invalid/")}
    )
    parent = writer.add_annotation(0, obj)
    writer.pages[0]["/Annots"].append(parent.indirect_reference)
    reply = annotation(contents="ambiguous parent")
    reply[NameObject("/IRT")] = parent.indirect_reference
    writer.add_annotation(0, reply)
    path = tmp_path / "actions.pdf"
    writer.write(path)
    docs = PdfAnnotationReader().load_data(path)
    assert docs[0].metadata["pdf_annotation"]["has_rich_text"]
    assert docs[0].metadata["pdf_annotation"]["has_action"]
    assert "rich alternate" not in docs[0].text
    assert docs[2].metadata["pdf_annotation"]["reply_status"] == "ambiguous_target"


def test_user_unit_and_multiple_quads(tmp_path):
    writer = PdfWriter()
    writer.add_blank_page(400, 600)
    writer.pages[0][NameObject("/UserUnit")] = NumberObject(2)
    quads = [80, 450, 180, 450, 80, 430, 180, 430, 80, 410, 180, 410, 80, 390, 180, 390]
    writer.add_annotation(0, annotation("/Highlight", quads=quads))
    path = tmp_path / "units.pdf"
    writer.write(path)
    info = PdfAnnotationReader().load_data(path)[0].metadata["pdf_annotation"]
    assert info["user_unit"] == 2 and info["quad_points"] == quads

