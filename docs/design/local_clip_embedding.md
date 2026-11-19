# Local CLIP embeddings / 本地图文同空间向量

`LocalClipEmbedding` encodes original images and text into one L2-normalized
512-dimensional CLIP space on CPU. It does not OCR or caption the image. Explicit
helpers produce copied ImageDocuments (`embedding` and `image_embedding`) and
Queries (`embeddings`, text before image vectors); original objects are unchanged.
No Store's automatic embedding behavior is replaced. Use a vector backend that
accepts supplied vectors, or cosine similarity as in the real integration test.

Install `torch==2.6.0`, `transformers==4.49.0`, `huggingface-hub==0.36.0`,
`Pillow==10.4.0` and the framework runtime dependencies. Optional imports are lazy;
there is no new mandatory runtime dependency. CPU model weights are approximately
600 MB and inference uses additional memory. Model loading is cache-only by default.
Download the approved public snapshot explicitly before offline execution:

```python
from huggingface_hub import snapshot_download
snapshot_download('openai/clip-vit-base-patch32',
    revision='3d74acf9a28c67741b2f4f2ea7635f0aaf6f0268',
    allow_patterns=['*.json','*.txt','pytorch_model.bin','README.md'])
```

Alternatively set `allow_download=True` explicitly. Model and processor use the
same exact revision, never a floating branch; weights_only loading uses PyTorch
2.6+. The implementation uses CLIPModel/CLIPProcessor directly, with no remote
custom code. CPU/eval/inference_mode are fixed. Applications should install CPU
PyTorch wheels where supported and manage their own cache/storage limits.

```python
from PIL import Image
from agentuniverse.agent.action.knowledge.embedding.local_clip_embedding import LocalClipEmbedding
from agentuniverse.agent.action.knowledge.store.image_document import ImageDocument
from agentuniverse.agent.action.knowledge.store.query import Query
encoder = LocalClipEmbedding()
with Image.open('picture.png') as image:
    docs = encoder.embed_image_documents([ImageDocument(
        id='picture-1', origin_image=image, ocr_text=None, ocr_text_embedding=None)])
query = encoder.embed_query(Query(query_str='a green triangle'))
# Compare docs[0].embedding and query.embeddings[0] by cosine similarity.
```

ImageDocument strings are strict base64 image bytes, not paths/URLs. Direct
`get_image_embeddings` accepts Pillow images. EXIF display orientation is applied
to copies; transparency is composited on white. Processor resize/center crop follows
the fixed model, so small peripheral details may be lost. Multipage images are
rejected. The caller owns Pillow inputs and must not close/mutate them during async
inference. Long text beyond CLIP's token window raises instead of silent truncation.
`max_items`, `batch_size`, image byte/pixel budgets constrain inputs, not model RAM.

Calls are serialized per instance, including model initialization. Async methods
use worker threads: cancellation stops awaiting, not an already-running inference.
Create a new instance to change a loaded model/revision/dimension. Empty batches
return empty lists without model loading. Model/provenance metadata exposes the
revision, dimensions, normalization and CPU device; it is not a source-image digest.
`as_langchain` is not implemented; use the explicit public helpers above.

Copy local_clip_embedding.yaml.example into the application's component directory
for normal Embedding registration. Per-component settings live under `clip`.
Inference works offline once the specified snapshot is cached; no paid provider
or GPU service is used by these tests.

## Validation and limits

The real checkpoint was evaluated on three fixed synthetic images: red square,
blue circle and green triangle. Their matching text labels ranked first in all
three cases (cosines approximately 0.289, 0.341, 0.354). This tiny sanity fixture is
not a benchmark or evidence of improvement over another retriever. Tests also
compare vectors to a direct Transformers forward pass, check norms/dimensions,
batch/async equivalence, EXIF, immutable input objects, base64 failures, token and
pixel budgets, and ImageDocument→Query cosine retrieval without OCR.

Run `HF_HUB_OFFLINE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q
--import-mode=importlib tests/test_agentuniverse/integration/test_local_clip_live.py`
after downloading the fixed snapshot. Missing prerequisites fail rather than skip.
Set AU_CLIP_REPORT to a local JSON path to record the complete 3x3 cosine matrix.

中文：使用固定公开 CLIP revision 在本地 CPU 将原图和文字编码到同一单位向量空间，
不依赖 OCR。显式方法返回 ImageDocument/Query 副本；不改变现有 Store 自动嵌入行为。
默认只读缓存，联网下载需显式开启。批量、异步、EXIF、错误边界以真实模型验证。
三个合成图形标签测试仅证明接口可运行，不代表真实场景准确率或检索提升；模型对
细粒度计数、域外图片、语言偏差等存在限制，实际部署应另做领域评估。

Sources: [fixed model card](https://huggingface.co/openai/clip-vit-base-patch32/tree/3d74acf9a28c67741b2f4f2ea7635f0aaf6f0268),
[official CLIP MIT license](https://github.com/openai/CLIP/blob/main/LICENSE),
[model limitations](https://github.com/openai/CLIP/blob/main/model-card.md).
No weights are included in this contribution; other user-selected models require
their own license and suitability review.

Local Windows CPU verification on Python 3.10 and 3.12: each **21 passed**, no
skips (12 real-model/configuration cases and 9 existing Document regressions).
Ruff E4/E7/E9/F/I, formatting and git diff checks passed. This does not establish
hosted CI success, GPU behavior, arbitrary model compatibility or quality gains.
