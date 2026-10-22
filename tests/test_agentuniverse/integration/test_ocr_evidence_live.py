"""Actual Tesseract recognition plus independent pixel geometry expectations."""

import hashlib
from pathlib import Path

import pytest
from PIL import Image, ImageDraw, ImageFont

from agentuniverse.agent.action.knowledge.reader.image.ocr_evidence_reader import OcrEvidenceReader


def sample(tmp_path, scale=1, orientation=1):
    image = Image.new("RGB", (600 * scale, 160 * scale), "white")
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 48 * scale)
    ImageDraw.Draw(image).text((40 * scale, 40 * scale), "ALPHA 123", font=font, fill="black")
    # Invert the EXIF transform when constructing a physically rotated source.
    inverse = {
        2: Image.Transpose.FLIP_LEFT_RIGHT,
        3: Image.Transpose.ROTATE_180,
        4: Image.Transpose.FLIP_TOP_BOTTOM,
        5: Image.Transpose.TRANSPOSE,
        6: Image.Transpose.ROTATE_90,
        7: Image.Transpose.TRANSVERSE,
        8: Image.Transpose.ROTATE_270,
    }
    if orientation in inverse:
        image = image.transpose(inverse[orientation])
    exif = Image.Exif()
    exif[274] = orientation
    path = tmp_path / f"sample-{scale}-{orientation}.png"
    image.save(path, exif=exif)
    return path


@pytest.mark.parametrize("orientation", range(1, 9))
def test_real_engine_orientation_and_original_ink_bounds(tmp_path, orientation):
    path = sample(tmp_path, orientation=orientation)
    before = path.read_bytes()
    doc = OcrEvidenceReader(crop=(20, 20, 550, 130)).load_data(path)[0]
    evidence = doc.metadata["ocr_evidence"]
    assert doc.text == "ALPHA 123"
    assert evidence["exif_orientation"] == orientation
    assert evidence["source_sha256"] == hashlib.sha256(before).hexdigest()
    with Image.open(path) as original:
        for word in evidence["words"]:
            # Each mapped box actually encloses dark pixels in the untransposed source.
            pixels = original.crop(word["bbox_original"]).convert("L")
            assert pixels.getextrema()[0] == 0
            assert pixels.point(lambda p: 255 if p < 128 else 0).getbbox() is not None
            assert 0 <= word["confidence"] <= 100
    alpha = evidence["words"][0]["bbox_display"]
    # Hand-specified word region, independent of OCR output and transform code.
    assert 38 <= alpha[0] <= 44 and 45 <= alpha[1] <= 55
    assert 190 <= alpha[2] <= 210 and 80 <= alpha[3] <= 90
    assert path.read_bytes() == before


@pytest.mark.parametrize("scale", [1, 2])
def test_resolution_and_low_confidence_retention(tmp_path, scale):
    doc = OcrEvidenceReader(low_confidence_threshold=100).load_data(sample(tmp_path, scale))[0]
    assert doc.text == "ALPHA 123"
    words = doc.metadata["ocr_evidence"]["words"]
    assert all(word["low_confidence"] for word in words)
    assert 38 * scale <= words[0]["bbox_display"][0] <= 44 * scale


def test_blank_bad_multipage_and_budgets(tmp_path):
    path = tmp_path / "blank.png"
    Image.new("RGB", (200, 100), "white").save(path)
    doc = OcrEvidenceReader().load_data(path)[0]
    assert doc.text == "" and doc.metadata["ocr_evidence"]["status"] == "empty"
    for config, message in [
        ({"max_bytes": 1}, "max_bytes"),
        ({"max_pixels": 1}, "max_pixels"),
        ({"crop": (0, 0, 300, 20)}, "crop"),
    ]:
        with pytest.raises(ValueError, match=message):
            OcrEvidenceReader(**config).load_data(path)
    path.write_bytes(b"not an image")
    with pytest.raises(Exception):
        OcrEvidenceReader().load_data(path)
    Image.new("RGB", (20, 20)).save(path, format="TIFF", save_all=True, append_images=[Image.new("RGB", (20, 20))])
    with pytest.raises(ValueError, match="single-frame"):
        OcrEvidenceReader().load_data(path)
    with pytest.raises(ValueError, match="max_words"):
        OcrEvidenceReader(max_words=1).load_data(sample(tmp_path))


def test_engine_failure_is_not_empty_result(tmp_path):
    import pytesseract

    with pytest.raises(pytesseract.TesseractError):
        OcrEvidenceReader(language="missing_test_language").load_data(sample(tmp_path))
    with pytest.raises(RuntimeError, match="timeout"):
        OcrEvidenceReader(timeout_seconds=0.000001).load_data(sample(tmp_path))


def test_yaml_knowledge_sqlite_preserves_evidence(tmp_path):
    import shutil
    from unittest.mock import patch

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

    path = sample(tmp_path)
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
        app.value = {"BASE_INFO": {"appname": "ocr-evidence-test"}}
        apps.app_configer = AppConfiger().load_by_configer(app)
        root = next(parent for parent in Path(__file__).parents if (parent / "pyproject.toml").is_file())
        copied = tmp_path / "reader.yaml"
        shutil.copyfile(
            root / "agentuniverse/agent/action/knowledge/reader/image/ocr_evidence_reader.yaml.example", copied
        )
        config = ComponentConfiger().load_by_configer(Configer(str(copied)).load())
        reader = OcrEvidenceReader().initialize_by_component_configer(config)
        expected = reader.load_data(path)[0]
        store = SQLiteStore(name="ocr_store", db_path=str(tmp_path / "knowledge.db"), keyword_extractor="ocr_keywords")
        store._new_client()
        components = [
            reader,
            store,
            BaseRouter(name="base_router"),
            JiebaKeywordExtractor(name="ocr_keywords", top_k=20),
        ]
        for manager, component in zip(managers, components):
            manager.register(component.get_instance_code(), component)
        knowledge = Knowledge(stores=["ocr_store"], readers={"png": "ocr_evidence_reader"})
        knowledge.insert_knowledge(source_path=str(path))
        with patch.object(trace_module, "ConversationMemoryModule"), patch.object(trace_module, "Monitor") as monitor:
            monitor.get_invocation_chain.return_value = []
            result = knowledge.query_knowledge(query_str="ALPHA", keywords={"ALPHA"})
        assert len(result) == 1
        assert result[0].metadata == expected.metadata
        assert result[0].id == expected.id
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


def test_transparency_metadata_and_configuration(tmp_path):
    from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
    from agentuniverse.base.config.configer import Configer

    path = tmp_path / "transparent.png"
    Image.new("RGBA", (200, 100), (0, 0, 0, 0)).save(path)
    ext = {"source": "fake", "ocr_evidence": "fake", "batch": "unit"}
    doc = OcrEvidenceReader().load_data(path, ext_info=ext)[0]
    assert doc.text == ""
    assert doc.metadata["source"] == str(path.resolve())
    assert doc.metadata["batch"] == "unit"
    assert ext["ocr_evidence"] == "fake"
    config = Configer()
    config.value = {"name": "ocr", "description": "", "ocr": {"unknown": True}}
    with pytest.raises(ValueError, match="Unknown"):
        OcrEvidenceReader().initialize_by_component_configer(ComponentConfiger().load_by_configer(config))
    config.value["ocr"] = {"crop": [0, 0, 10, 10], "low_confidence_threshold": 40}
    reader = OcrEvidenceReader().initialize_by_component_configer(ComponentConfiger().load_by_configer(config))
    assert reader.crop == (0, 0, 10, 10)
    assert reader.low_confidence_threshold == 40
