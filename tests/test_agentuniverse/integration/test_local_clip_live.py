"""CPU inference against the pinned public CLIP checkpoint (no mock model)."""

import asyncio
import base64
import io
import json
import os

import numpy as np
import pytest
from PIL import Image, ImageDraw

from agentuniverse.agent.action.knowledge.embedding.local_clip_embedding import LocalClipEmbedding
from agentuniverse.agent.action.knowledge.store.image_document import ImageDocument
from agentuniverse.agent.action.knowledge.store.query import Query


@pytest.fixture(scope="module")
def encoder():
    import torch

    torch.set_num_threads(2)
    return LocalClipEmbedding(batch_size=2)


def pictures():
    images = []
    for color, shape in [("red", "square"), ("blue", "circle"), ("green", "triangle")]:
        image = Image.new("RGB", (224, 224), "white")
        draw = ImageDraw.Draw(image)
        if shape == "square":
            draw.rectangle((40, 40, 184, 184), fill=color)
        elif shape == "circle":
            draw.ellipse((40, 40, 184, 184), fill=color)
        else:
            draw.polygon([(112, 30), (30, 190), (194, 190)], fill=color)
        images.append(image)
    return images


def test_real_vectors_reference_and_labels(encoder):
    import torch

    labels = ["a red square", "a blue circle", "a green triangle"]
    images = pictures()
    a = np.array(encoder.get_embeddings(labels))
    b = np.array(encoder.get_image_embeddings(images))
    assert a.shape == b.shape == (3, 512)
    np.testing.assert_allclose(np.linalg.norm(a, axis=1), 1, atol=1e-6)
    np.testing.assert_allclose(np.linalg.norm(b, axis=1), 1, atol=1e-6)
    with torch.inference_mode():
        inputs = encoder._processor(text=labels, images=images, padding=True, return_tensors="pt")
        direct = encoder._model(**inputs)
    np.testing.assert_allclose(a, direct.text_embeds.numpy(), rtol=1e-4, atol=1e-6)
    np.testing.assert_allclose(b, direct.image_embeds.numpy(), rtol=1e-4, atol=1e-6)
    scores = b @ a.T
    report = {
        "model": encoder.provenance(),
        "labels": labels,
        "cosine_scores": scores.tolist(),
        "predicted_label_indices": scores.argmax(axis=1).tolist(),
        "correct_of_three": int(sum(scores.argmax(axis=1) == np.arange(3))),
    }
    if os.environ.get("AU_CLIP_REPORT"):
        with open(os.environ["AU_CLIP_REPORT"], "w", encoding="utf-8") as out:
            json.dump(report, out, indent=2)
    assert next(encoder._model.parameters()).device.type == "cpu"
    assert not encoder._model.training


def test_async_and_batch_consistency(encoder):
    texts = ["a red square", "a blue circle", "a green triangle"]
    expected = encoder.get_embeddings(texts)

    async def run():
        return await asyncio.gather(encoder.async_get_embeddings(texts), encoder.async_get_image_embeddings(pictures()))

    text_vectors, image_vectors = asyncio.run(run())
    np.testing.assert_allclose(text_vectors, expected, atol=1e-6)
    np.testing.assert_allclose(image_vectors, encoder.get_image_embeddings(pictures()), atol=1e-6)
    individual = [encoder.get_embeddings([text])[0] for text in texts]
    np.testing.assert_allclose(individual, expected, atol=1e-5)


def test_exif_input_unchanged_and_document_query_integration(encoder):
    image = pictures()[2]
    rotated = image.transpose(Image.Transpose.ROTATE_90)
    rotated.getexif()[274] = 6
    before = rotated.tobytes()
    vectors = encoder.get_image_embeddings([image, rotated])
    np.testing.assert_allclose(vectors[0], vectors[1], atol=1e-6)
    assert rotated.getexif()[274] == 6 and rotated.tobytes() == before
    raw = io.BytesIO()
    image.save(raw, format="PNG")
    doc = ImageDocument(
        id="triangle",
        text="",
        origin_image=base64.b64encode(raw.getvalue()).decode(),
        ocr_text=None,
        ocr_text_embedding=None,
        metadata={"source": "synthetic"},
    )
    embedded = encoder.embed_image_documents([doc])[0]
    assert not doc.embedding and "clip_embedding" not in doc.metadata
    np.testing.assert_allclose(embedded.image_embedding, vectors[0], atol=1e-6)
    assert embedded.embedding == embedded.image_embedding
    query = Query(query_str="a green triangle", query_image_bundles=[image])
    filled = encoder.embed_query(query)
    assert not query.embeddings
    assert len(filled.embeddings) == 2
    assert filled.ext_info["clip_embedding"]["vector_modalities"] == ["text", "image"]
    # Simple cosine retrieval of original image vectors, not OCR text.
    docs = encoder.embed_image_documents(
        [
            ImageDocument(id=str(i), origin_image=img, ocr_text=None, ocr_text_embedding=None)
            for i, img in enumerate(pictures())
        ]
    )
    nearest = max(docs, key=lambda d: np.dot(d.embedding, filled.embeddings[1]))
    assert nearest.id == "2"


def test_empty_bad_image_limits_and_long_text(encoder):
    assert encoder.get_embeddings([]) == encoder.get_image_embeddings([]) == []
    with pytest.raises(ValueError):
        encoder.get_embeddings([" "])
    with pytest.raises(TypeError):
        encoder.get_image_embeddings(["https://example.com/image.png"])
    with pytest.raises(ValueError, match="token window"):
        encoder.get_embeddings(["word " * 100])
    bad = ImageDocument(origin_image="not base64!", ocr_text=None, ocr_text_embedding=None)
    with pytest.raises(ValueError):
        encoder.embed_image_documents([bad])
    with pytest.raises(ValueError, match="max_pixels"):
        LocalClipEmbedding(max_pixels=1).get_image_embeddings(pictures())
    with pytest.raises(ValueError, match="max_items"):
        LocalClipEmbedding(max_items=1).get_embeddings(["a", "b"])


def test_pin_dimensions_and_config_errors():
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        LocalClipEmbedding(revision="main")
    with pytest.raises(ValueError, match="projection_dim"):
        LocalClipEmbedding(embedding_dims=3).get_embeddings(["test"])


def test_yaml_registration_and_configuration(tmp_path):
    import shutil
    from pathlib import Path

    from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
    from agentuniverse.base.config.configer import Configer

    root = next(p for p in Path(__file__).parents if (p / "pyproject.toml").exists())
    path = tmp_path / "clip.yaml"
    shutil.copyfile(root / "agentuniverse/agent/action/knowledge/embedding/local_clip_embedding.yaml.example", path)
    config = ComponentConfiger().load_by_configer(Configer(str(path)).load())
    instance = LocalClipEmbedding().initialize_by_component_configer(config)
    assert instance.name == "local_clip_embedding"
    assert instance.allow_download is False
    assert len(instance.get_embeddings(["a red square"])[0]) == 512
    with pytest.raises(ValueError, match="reconfigure"):
        instance.initialize_by_component_configer(config)
    instance.revision = "0" * 40
    with pytest.raises(ValueError, match="new instance"):
        instance.get_embeddings(["test"])


@pytest.mark.parametrize(
    "options", [{"batch_size": 0}, {"max_items": True}, {"embedding_dims": 0}, {"revision": "main"}, {"max_pixels": -1}]
)
def test_invalid_options(options):
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        LocalClipEmbedding(**options)


def test_corrupt_image_and_transparency(encoder):
    from PIL import UnidentifiedImageError

    bad = ImageDocument(origin_image=base64.b64encode(b"not image").decode(), ocr_text=None, ocr_text_embedding=None)
    with pytest.raises(UnidentifiedImageError):
        encoder.embed_image_documents([bad])
    transparent = Image.new("RGBA", (224, 224), (0, 0, 0, 0))
    white = Image.new("RGB", (224, 224), "white")
    result = encoder.get_image_embeddings([transparent, white])
    np.testing.assert_allclose(result[0], result[1], atol=1e-6)
