import itertools
import random

from tqdm import tqdm

from data_io.file_io import data_from_jsonl, data_to_jsonl_append
from filter.internal_import_filter import InternalImportFilter
from filter.undefined_behavior_filter import UndefinedBehaviorFilter
from go_tree_sitter.go_parser import GoParser
from go_tree_sitter.go_tree_sitter_tool import GoTreeSitterTool
from go_generate.go_generator import GoGenerator

from cal_coverage import CalCoverage


class TestCaseGenerator:
    class TestCaseCov:
        def __init__(self, data, cov):
            self.data = data
            self.cov = cov

    def __init__(self, seed_path, test_unit_path, go_generator, tokenizer, test_case_cache_size=10000):
        self.seed_path = seed_path

        self.test_unit_path = test_unit_path

        self.MAX_INPUT_TOKEN_LEN = 512

        self.parser = GoParser()

        self.go_generator = go_generator

        self.tokenizer = tokenizer

        self.test_case_cnt = 0

        self.test_case_cache_list = []
        self.test_case_cache_size = test_case_cache_size
        for src_line in data_from_jsonl(self.seed_path):
            self.add_data_to_test_case_cache(src_line)

    def data_input_do_filter(self, data):
        flag = False
        count = {"has_error": 0, "undefined_behavior": 0}

        input_code = data["input"]
        token_len = len(self.tokenizer(input_code, return_tensors="pt").input_ids[0])

        if token_len > self.MAX_INPUT_TOKEN_LEN:
            flag = True
            return flag, count

        input_node = self.parser.parse(input_code)

        if GoTreeSitterTool.has_error(input_node):
            flag = True
            count["has_error"] += 1
        if UndefinedBehaviorFilter.do_filter(input_node):
            flag = True
            count["undefined_behavior"] += 1

        return flag, count

    def test_case_do_filter(self, test_case):
        flag = False
        count = {"has_error": 0, "undefined_behavior": 0}

        code = test_case["input"] + test_case["output"]
        node = self.parser.parse(code)

        if GoTreeSitterTool.has_error(node):
            flag = True
            count["has_error"] += 1
        if UndefinedBehaviorFilter.do_filter(node):
            flag = True
            count["undefined_behavior"] += 1

        return flag, count

    def generate_test_case(self, data):
        input_text = data["input"]
        output_text = self.go_generator.generate(input_text)
        test_case = {"input": input_text, "output": output_text}
        return test_case

    def make_test_case_loop(self):
        new_data_list = []
        with tqdm() as pbar:
            while True:
                if len(new_data_list) != 0:
                    curr_data = new_data_list.pop(0)
                    input_flag, input_count = self.data_input_do_filter(curr_data)
                    if not input_flag:
                        test_case = self.generate_test_case(curr_data)
                        test_case_flag, test_case_count = self.test_case_do_filter(test_case)
                        if not test_case_flag:
                            pbar.update(1)
                            ##
                            self.add_data_to_test_case_cache(test_case)
                            ##
                elif len(self.test_case_cache_list) != 0:
                    curr_data = self.get_top_data_from_test_case_cache()
                    input_flag, input_count = self.data_input_do_filter(curr_data)
                    if not input_flag:
                        test_case = self.generate_test_case(curr_data)
                        test_case_flag, test_case_count = self.test_case_do_filter(test_case)
                        if not test_case_flag:
                            pbar.update(1)
                            ##
                            self.add_data_to_test_case_cache(test_case)
                            ##
                            new_data_list += self.build_new_data(curr_data)
                else:
                    break
