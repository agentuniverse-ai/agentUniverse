# NetCDF坐标切片Reader

`NetcdfSliceReader` 从显式选择的本地数值变量读取带坐标数组块，保留维度、单位、缺值/缩放与时间日历。安装 `pip install "agentUniverse[netcdf_ext]"`。

```python
from agentuniverse.agent.action.knowledge.reader.file.netcdf_slice_reader import NetcdfSliceReader
reader = NetcdfSliceReader(variables=["temperature"], coordinate_ranges={"latitude": [10, 30]}, index_slices={"time": [0, 2]}, max_chunk_values=1000)
documents, report = reader.load_slice("climate.nc")
```

变量必填且不重复。坐标范围为解码后原单位中的数值闭区间，要求严格递增/递减；时间[30,59]指文件units/calendar中的数值，不接受日期字符串。索引[start,stop,可选step]非负、stop不含、step为正。同维度不能使用两种选择。未指定维度保留范围但受预算限制；空选区无文档。

复制netcdf_slice_reader.yaml.example至Reader包改为yaml，按文件修改变量/选择；Knowledge配置`readers: {nc: netcdf_slice_reader}`，按需加nc4/cdf。真实SQLite已验证insert/query；不改全局路由。load_data仅返Documents，load_slice另返投影报告。

正文JSON包含维度、坐标/属性和嵌套值，不丢维度展平。元数据netcdf_evidence另含shape、原索引块、路径/hash与解码标记。缺值/NaN为null，不是0；无穷为带符号字符串。xarray应用CF mask/scale，保留原FillValue/missing_value/scale_factor/add_offset/Unsigned；不区分源NaN与解码缺值。

cftime时间转ISO样式字符串，保留原units/calendar；360_day的2月30日不能当公历。缺calendar遵循CF/xarray默认。不换单位、不插值/汇总、不作科学有效性判断。仅复制选定描述/解码属性，不解释任意全局元数据、cell bounds、grid mapping或辅助变量。

先以netCDF4元数据检查坐标/值预算，再由xarray仅打开选中变量与维度坐标。坐标预算通过后可能加载索引；数据变量切片/分块后才读取值。hash分块读取全文件，不加载数组。逻辑块受限，但底层库可能解压更大存储块，不保证原生内存上限。

支持本地nc/nc4/cdf、根级NetCDF3/4实数变量、数值1维维度坐标和标量。远程URL、嵌套组、字符串/compound、无维度坐标、辅助/曲线坐标明确拒绝，无近邻回退。

默认/上限：文件512M/2G字节、坐标100000/1M、选中值100000/1M、块1000/10000值、文档1000/10000、单篇200000/2M字符、总文本10M/40M字符，M/G十进制。参数须正整数，失败不返部分结果，不是原生解析沙箱。ID由hash+变量+原索引块确定，同字节同切块异地不变；重打包/切块改变ID，不清理旧Store。返回前重验hash但不加文件锁；metadata深拷贝且保留键不能覆盖。

真实NetCDF3/4通过netCDF4独立对照xarray；记录真实后端读取，覆盖360_day、降序、缺值缩放、标量、步长、预算及YAML→Knowledge→SQLite。完整命令见[英文说明](../../../../en/In-Depth_Guides/Tutorials/Knowledge/NetCDF_Slice_Reader.md)。
