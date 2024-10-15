import itertools
import os
import random
import re
import subprocess

from tqdm import tqdm

from data_io.file_io import data_from_jsonl, data_to_jsonl_append
from filter.internal_import_filter import InternalImportFilter
from filter.undefined_behavior_filter import UndefinedBehaviorFilter
from diff_test.cmd_runner import CmdRunner
from go_tree_sitter.go_parser import GoParser
from go_tree_sitter.go_tree_sitter_tool import GoTreeSitterTool
from diff_test.diff_test_runner import DiffTestRunner


class TestDataGenerator:
    def __init__(self, seed_path, dst_path, go_generator, tokenizer):
        self.seed_path = seed_path
        self.dst_path = dst_path

        self.MAX_INPUT_TOKEN_LEN = 512

        self.parser = GoParser()
        self.go_generator = go_generator
        self.tokenizer = tokenizer

        self.seed_corpus = itertools.cycle(data_from_jsonl(self.seed_path))

    def _test_case_do_filter(self, old_code, new_code):
        def is_multithreaded_go_code(go_code: str) -> bool:
            patterns = [
                r'\bgo\s+\w+',
                r'\bsync\.',
                r'\bWaitGroup\b',
                r'\bmutex\b',
                r'\bsync\.Mutex\b',
            ]
            for pattern in patterns:
                if re.search(pattern, go_code):
                    return True
            return False
        
        def is_concurrent_code(code: str) -> bool:
            concurrent_pattern = re.compile(r'\bgo\s+\w+', re.MULTILINE)
            has_concurrent = bool(concurrent_pattern.search(code))
            sync_patterns = [
                re.compile(r'\bchan\b'),
                re.compile(r'\bsync\.Mutex\b'),
                re.compile(r'\bsync\.WaitGroup\b')
            ]
            has_sync_primitives = any(pattern.search(code) for pattern in sync_patterns)
            return has_concurrent and has_sync_primitives

        if old_code == new_code:
            return True
        if not is_concurrent_code(new_code):
            return True
        node = self.parser.parse(new_code).root_node
        if GoTreeSitterTool.has_error(node):
            return True
        if UndefinedBehaviorFilter.do_filter(node):
            return True
        return False

    def _generate(self, masked_code):
        return self.go_generator.generate(masked_code)
    
    def _mask(self, code, mask):
        def find_ith_node(node, index, i):
            if index[0] == i:
                return node
            index[0] += 1
            for child in node.children:
                result = find_ith_node(child, index, i)
                if result is not None:
                    return result
            return None
        
        tree = self.parser.parse(code)
        root_node = tree.root_node

        index = [0]
        target_node = find_ith_node(root_node, index, mask)
        if target_node is not None:
            start_byte = target_node.start_byte
            end_byte = target_node.end_byte
            masked_code = code[:start_byte] + "<mask>" + code[end_byte:]
        else:
            masked_code= code + "<mask>"
        return masked_code
    
    def _get_total_nodes(self, code):
        def count_nodes(node):
            count = 1
            for child in node.children:
                count += count_nodes(child)
            return count
        
        tree = self.parser.parse(code)
        root_node = tree.root_node
        total_nodes = count_nodes(root_node)
        return total_nodes

    def generate_test_data_loop(self):
        with tqdm() as pbar:
            index = 0
            while True:
                old_code = next(self.seed_corpus)["code"]
                total_nodes = self._get_total_nodes(old_code)
                node_index = round((total_nodes - 1) * random.uniform(0, 1))
                masked_code = self._mask(old_code, node_index)
                new_code = masked_code.replace("<mask>", self._generate(masked_code))

                flag = self._test_case_do_filter(old_code, new_code)
                if not flag:
                    data = {"code": new_code}
                    data_to_jsonl_append(self.dst_path, data)
                    index += 1
                    pbar.update(1)

                    if index > 3300:
                        break
