# test_xlsx_mock_compare.py
import unittest
from unittest.mock import MagicMock

class TestXLSXMock(unittest.TestCase):
    def setUp(self):
        # 创建两个 Mock sheet
        self.mock_sheet1 = MagicMock()
        self.mock_sheet2 = MagicMock()

    def test_fixed_mock(self):
        """修改前：固定返回值"""
        # 固定返回 Data1 / Data2
        self.mock_sheet1.cell.return_value = MagicMock(value='Data1')
        self.mock_sheet2.cell.return_value = MagicMock(value='Data2')

        # 读取两行两列
        sheet1_result = [
            [self.mock_sheet1.cell(1,1).value, self.mock_sheet1.cell(1,2).value],
            [self.mock_sheet1.cell(2,1).value, self.mock_sheet1.cell(2,2).value]
        ]
        sheet2_result = [
            [self.mock_sheet2.cell(1,1).value, self.mock_sheet2.cell(1,2).value],
            [self.mock_sheet2.cell(2,1).value, self.mock_sheet2.cell(2,2).value]
        ]

        print("\n[固定返回值] Sheet1 result:", sheet1_result)
        print("[固定返回值] Sheet2 result:", sheet2_result)

        # 验证所有单元格都返回固定值
        for row in sheet1_result:
            for cell in row:
                self.assertEqual(cell, 'Data1')
        for row in sheet2_result:
            for cell in row:
                self.assertEqual(cell, 'Data2')

    def test_dynamic_mock(self):
        """修改后：动态返回值（兼容 row/column 关键字参数）"""
        # 定义动态 cell 返回
        def mock_cell1(*args, **kwargs):
            row = kwargs.get('row', args[0] if len(args) > 0 else 1)
            col = kwargs.get('column', args[1] if len(args) > 1 else 1)
            return MagicMock(value=f'Sheet1 Cell {row},{col}')

        def mock_cell2(*args, **kwargs):
            row = kwargs.get('row', args[0] if len(args) > 0 else 1)
            col = kwargs.get('column', args[1] if len(args) > 1 else 1)
            return MagicMock(value=f'Sheet2 Cell {row},{col}')

        self.mock_sheet1.cell.side_effect = mock_cell1
        self.mock_sheet2.cell.side_effect = mock_cell2

        # 读取两行两列
        sheet1_result = [
            [self.mock_sheet1.cell(row=1,column=1).value, self.mock_sheet1.cell(row=1,column=2).value],
            [self.mock_sheet1.cell(row=2,column=1).value, self.mock_sheet1.cell(row=2,column=2).value]
        ]
        sheet2_result = [
            [self.mock_sheet2.cell(row=1,column=1).value, self.mock_sheet2.cell(row=1,column=2).value],
            [self.mock_sheet2.cell(row=2,column=1).value, self.mock_sheet2.cell(row=2,column=2).value]
        ]

        print("\n[动态返回值] Sheet1 result:", sheet1_result)
        print("[动态返回值] Sheet2 result:", sheet2_result)

        # 验证每个单元格值与行列匹配
        for r_idx, row in enumerate(sheet1_result, start=1):
            for c_idx, cell in enumerate(row, start=1):
                self.assertEqual(cell, f'Sheet1 Cell {r_idx},{c_idx}')
        for r_idx, row in enumerate(sheet2_result, start=1):
            for c_idx, cell in enumerate(row, start=1):
                self.assertEqual(cell, f'Sheet2 Cell {r_idx},{c_idx}')

if __name__ == '__main__':
    unittest.main()
