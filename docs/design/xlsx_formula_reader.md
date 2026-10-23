# Formula-aware XLSX ingestion

Select `xlsx_formula_reader` explicitly through Knowledge configuration:

```yaml
readers:
  xlsx: xlsx_formula_reader
```

Install the existing optional Excel dependency `openpyxl` (tested 3.1.5).
The default XlsxReader is unchanged. This component loads formula and data-only
views of exactly the same workbook bytes and creates one Document per nonempty
worksheet. Chartsheets are not treated as tabular worksheets.

Formula cells retain their coordinate, formula text and stored cached value
in `formula_cells` metadata and the document text. Values are represented as
strings for JSON-compatible metadata, with the original cached cell type.
Zero is distinct from no observable value. `missing` means openpyxl returned
None, which may also represent an empty stored result; it is not an evaluation.
All observed cached values are `stored_unverified`: Excel may have saved stale
results. Nothing is recalculated, executed, repaired or written back.

Reserved provenance fields cannot be overridden by ext_info. Workbook SHA-256
and worksheet title determine stable IDs; changing workbook bytes changes IDs.
Metadata keeps the filename, sheet name, digest and formula annotations.
Raw formula text can itself contain sensitive references; protect the resulting
knowledge corpus and reports. No external links are fetched or followed.

Limits bound compressed bytes, declared aggregate ZIP size and worksheet cell
visits. Sparse sheets with huge declared dimensions are rejected. These are
resource guards, not a guarantee against every malformed Office document.
After the declared-size check, both read-only views reset their dimensions and
stream actual rows so an exporter reporting too small a range cannot hide later
formula cells. Empty row gaps consume at least one cell-budget unit per row.
This follows openpyxl's worksheet-dimension guidance:
https://openpyxl.readthedocs.io/en/stable/optimized.html#worksheet-dimensions
Only ordinary scalar formulas are supported; array/data-table formula objects
raise explicitly. This reader does not reconstruct merged tables, calculate
formulas, normalize accounting values or establish financial correctness.
Binary streams must be seekable; their position is restored and they stay open.
Internal workbooks are closed on success and error.

## 中文
按需启用的 Excel 读取器，把公式文本与文件中已有的计算结果分别保存。
结果可能过期，因此始终标记未核验；没有可读缓存值不会自动写成 0。
不会调用 Excel、执行公式或修改源文件。原有默认读取器不变。
真实 XLSX 测试包括缓存零值、普通值、缺失值、流位置、资源限制及
Knowledge 的显式 reader 路由，不代表真实财报准确性或完整应用启动验证。
