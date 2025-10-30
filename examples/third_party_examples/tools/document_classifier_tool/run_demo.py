#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
文档分类器演示启动脚本
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))

if __name__ == "__main__":
    from document_classifier_demo import main
    main()
