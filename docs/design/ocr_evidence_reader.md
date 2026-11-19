# OCR word evidence / OCR 词级证据

`OcrEvidenceReader` is an opt-in local, single-frame raster reader. It calls
Tesseract explicitly and returns one Document, with word text, confidence, line
IDs and boxes under `metadata.ocr_evidence`. Existing OCR readers and default
extension mappings are unchanged. Install `pytesseract==0.3.13`, `Pillow>=10.4`
and the Tesseract executable plus the requested language data separately.
No cloud account, GPU or automatic model download is used.

```python
from agentuniverse.agent.action.knowledge.reader.image.ocr_evidence_reader import OcrEvidenceReader
reader = OcrEvidenceReader(language="eng", crop=(20, 20, 550, 130))
doc = reader.load_data("scan.png")[0]
for word in doc.metadata["ocr_evidence"]["words"]:
    print(word["text"], word["confidence"], word["bbox_original"])
```

Copy `ocr_evidence_reader.yaml.example` to an application component directory.
Set Knowledge `readers: {png: ocr_evidence_reader}` explicitly; extension keys
are case-sensitive in the existing Knowledge loader. Use a metadata-preserving
Store (the integration test exercises SQLite). Configure crop inside YAML `ocr`
when invoking Knowledge, because Knowledge passes only the source path to Reader.

Geometry uses continuous pixel edges `[left, top, right, bottom]`, origin at the
top left. `bbox_display` refers to the full EXIF-normalized image, including crop
offset. `bbox_original` refers to stored pixels before EXIF. Orientations 1..8,
including mirrors, are inverted. There is no automatic deskew/OSD or resampling.
Cropping is applied after EXIF normalization. An untagged physically sideways
image will not be corrected automatically. Image bytes are never modified.

Confidence is Tesseract's 0..100 word score, **not a probability**. Low-confidence
words remain in text and metadata; the flag is informational. Blank pages return
an empty Document with `status: empty`. Missing engine/language, timeout, malformed
output, corrupt image, multipage input and budgets raise instead of returning
success. `max_words` limits accepted output after inference; it does not bound
Tesseract memory. Input bytes and decoded pixel budgets apply before inference;
the timeout limits the OCR subprocess, not every decoding or version-check step.
Metadata includes a source SHA-256, source filename/path and engine version; the
caller should control source paths and metadata disclosure. Supplied ext_info
cannot overwrite source or OCR evidence. Document ID hashes evidence, allowing
the same image with a different crop or recognition result to remain distinct.

English synthetic text at two resolutions and all eight EXIF orientations is
validated with a real CPU Tesseract process. Expected words and regions are fixed
in the fixture. This is geometry/provenance validation, not a multilingual or
real-world OCR accuracy benchmark. Custom traineddata is operator-managed; an
engine version alone does not identify custom language weights.

中文：显式选择 Tesseract，词级坐标、行标识及置信度随 Document 入库。坐标使用
左上原点、右下边界不包含的像素边缘；裁剪参数基于 EXIF 校正后的完整图片。
同时保留映射回原始像素的框。低置信词仅标记、不删除；空图与引擎失败严格区分。
不自动旋转无 EXIF 的横置文字、不纠偏、不接受多页图片。测试覆盖真实引擎、
人工固定文字与区域、不同分辨率、8 种方向及 Knowledge→SQLite，不承诺识别率提升。

References: [Tesseract TSV](https://tesseract-ocr.github.io/tessdoc/Command-Line-Usage.html#tsv-output),
[Pillow EXIF transpose](https://pillow.readthedocs.io/en/stable/reference/ImageOps.html#PIL.ImageOps.exif_transpose).

## Reproduce the focused validation

On Debian bookworm, install `tesseract-ocr=5.3.0-2`,
`tesseract-ocr-eng=1:4.1.0-2`, `fonts-dejavu-core=2.37-6`, the project's runtime
dependencies and `pytesseract==0.3.13`, `Pillow==10.4.0`, `pytest==7.4.4`.
The real-engine test deliberately fails if these prerequisites are missing.

```sh
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q --import-mode=importlib \
  tests/test_agentuniverse/integration/test_ocr_evidence_live.py \
  tests/test_agentuniverse/unit/agent/action/knowledge/reader/test_ocr_evidence_reader.py \
  tests/test_agentuniverse/unit/agent/action/knowledge/test_knowledge_rrf_integration.py \
  tests/test_agentuniverse/unit/agent/action/knowledge/test_knowledge_registration_errors.py \
  tests/test_agentuniverse/unit/agent/action/knowledge/test_knowledge_reader_lookup.py
```

Local Linux CPU runs on Python 3.10.19 and 3.12 each passed 43 tests, with no
skips. Transparent input is composited on white and recorded in evidence. The
integration fixture font path is Linux-specific; these results do not establish
Windows engine compatibility or full repository/hosted CI success.
