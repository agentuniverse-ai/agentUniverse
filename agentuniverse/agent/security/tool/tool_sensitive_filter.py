from typing import List

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from agentuniverse.agent.action.tool.enum import ToolTypeEnum
from agentuniverse.agent.action.tool.tool import Tool, ToolInput

class SensitiveWordFilter(Tool):
    word_list: List[str] = []
    trie: dict = {}

    def __init__(self):
        super().__init__()
        self.tool_type = ToolTypeEnum.FUNC
        self.name = "sensitive_word_filter"
        self.description = "Filter or replace sensitive content from text"
        self.input_keys = ["text"]
        self.load_words("config/sensitive_words.txt")
        self.start_file_watcher()

    def load_words(self, path: str) -> List[str]:
        with open(path, 'r', encoding='utf-8') as f:
            self.word_list = [line.strip() for line in f if line.strip()]
            self.trie = self.build_trie(self.word_list)
            return self.word_list

    def start_file_watcher(self):
        """监听词库文件变化"""
        class FileHandler(FileSystemEventHandler):
            def on_modified(_, event):
                if event.src_path.endswith("sensitive_words.txt"):
                    self.load_words(event.src_path)

        observer = Observer()
        observer.schedule(FileHandler(), path="config/", recursive=False)
        observer.start()

    def build_trie(self, words: List[str]) -> dict:
        """构建Trie树优化敏感词匹配"""
        trie = {}
        for word in words:
            node = trie
            for char in word:
                node = node.setdefault(char, {})
            node['#'] = True  # 结束标记
        return trie

    def filter_text(self, text: str, replace_char: str = '*') -> str:
        """基于Trie树的敏感词过滤"""
        result = []
        i = 0
        while i < len(text):
            node = self.trie
            j = i
            while j < len(text) and text[j] in node:
                node = node[text[j]]
                j += 1
                if '#' in node:  # 匹配到完整敏感词
                    result.append(replace_char * (j - i))
                    i = j
                    break
            else:
                result.append(text[i])
                i += 1
        return ''.join(result)

    def execute(self, tool_input: ToolInput) -> str:
        self.input_check(tool_input.to_dict())
        return self.filter_text(tool_input.get_data("text"))
