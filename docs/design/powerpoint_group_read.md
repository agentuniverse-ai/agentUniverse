# Reading grouped PowerPoint shapes / 读取分组幻灯片形状

`PowerPointTool.execute(mode="read", ...)` reads text and tables inside group
shapes, including nested groups. It visits shapes depth first in their saved
order. Texts and tables keep that order within their existing separate lists;
the public slide fields remain `slide_number`, `title`, `texts`, `tables`, and
`notes`. The slide title is returned separately and is not repeated in `texts`.

`max_shapes_per_slide` bounds the number of visited content shapes on each
slide. Every group container and every visited descendant consumes one slot,
including empty groups and shapes without readable text or tables. The title
is handled separately and does not consume a shape slot. Reaching the exact
limit is not truncation unless another content shape remains. The counter
resets on each slide. An iterative traversal keeps nested groups within this
budget without relying on Python's recursion limit.

Existing character, table-row, and table-column limits still apply to grouped
content. Speaker notes keep their existing handling and character budget.
`mode="info"` retains its existing top-level shape and table counts; these are
not recursive counts of group descendants. Reading extracts content rather
than reproducing a rendered slide's visual reading order.

`PowerPointTool.execute(mode="read", ...)` 现在也读取组合形状中的文字和表格，
包括嵌套组合。读取按文件中形状的顺序深度优先进行；文字与表格分别保持各自
列表中的顺序。每页的返回字段仍为 `slide_number`、`title`、`texts`、`tables`
和 `notes`。标题单独返回，不会再次出现在 `texts` 中。

`max_shapes_per_slide` 限制每页访问的内容形状数量。每个组合容器及访问到的
子形状各占一个名额，空组合、没有文字或表格的形状也计入。标题单独处理，
不占形状名额。恰好读完最后一个形状时不会因达到上限而标记截断；仍有其他
内容形状未读时才会标记。计数在每页重新开始。遍历采用显式迭代栈，避免递归
调用深度限制，并在形状预算处停止。

原有字符、表格行数和列数限制仍适用于组合内的内容。备注维持原有处理与字符
预算。`mode="info"` 继续统计顶层形状和表格，不递归统计组合内的形状。读取
功能提取文档内容，不保证与幻灯片实际渲染后的视觉阅读顺序一致。
