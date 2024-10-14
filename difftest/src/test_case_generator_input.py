import itertools
import os
import random
import re
import subprocess

from tqdm import tqdm

from data_io.file_io import data_from_jsonl
from filter.internal_import_filter import InternalImportFilter
from filter.undefined_behavior_filter import UndefinedBehaviorFilter
from diff_test.cmd_runner import CmdRunner
from go_tree_sitter.go_parser import GoParser
from go_tree_sitter.go_tree_sitter_tool import GoTreeSitterTool
from diff_test.diff_test_runner import DiffTestRunner


class TestCaseGenerator:
    def __init__(self, seed_path, test_unit_path, go_generator, tokenizer):
        self.seed_path = seed_path
        self.test_unit_path = test_unit_path

        self.MAX_INPUT_TOKEN_LEN = 512

        self.parser = GoParser()
        self.go_generator = go_generator
        self.tokenizer = tokenizer

        self.seed_corpus = itertools.cycle(data_from_jsonl(self.seed_path))

        #self.cmdrunnerlist = [CmdRunner("go build -o exe0", "./exe0"), CmdRunner("go build -compiler=gccgo -o exe1", "./exe1")]
        self.cmdrunnerlist = [CmdRunner("/bigdata/qiuhan/go1.23rc2/bin/go build -o exe0", "./exe0 < sample_input"), CmdRunner("/bigdata/qiuhan/go1.22.5/bin/go build -o exe1", "./exe1 < sample_input")]

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

    def _test_case_do_filter(self, old_code, new_code):
        if old_code == new_code:
            return True
        node = self.parser.parse(new_code).root_node
        if GoTreeSitterTool.has_error(node):
            return True
        if UndefinedBehaviorFilter.do_filter(node):
            return True
        return False

    def generate_test_case(self, data):
        input_text = data["input"]
        output_text = self.go_generator.generate(input_text)
        test_case = {"input": input_text, "output": output_text}
        return test_case
    
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
    
    def _create_test_unit(self, code, path, i, sample_input):
        os.makedirs(path, exist_ok=True)
        
        file_path = os.path.join(path, 'main.go')
        with open(file_path, 'w') as f:
            f.write(code)
        
        file_path = os.path.join(path, 'sample_input')
        with open(file_path, 'w') as f:
            f.write(sample_input)
        
        subprocess.run(f"go mod init {i}", cwd=path, capture_output=True, shell=True, encoding="utf8")
    
    def _execute_test_unit(self, code, index, sample_input):
        dir_path = os.path.join(self.test_unit_path, str(index))
        self._create_test_unit(code, dir_path, index, sample_input)
        difftestrunner = DiffTestRunner(self.cmdrunnerlist, dir_path)
        check, rst = difftestrunner.run()

        rst_path = os.path.join(dir_path, 'rst.log')
        rst_string = "\n".join(str(item) for item in rst)
        with open(rst_path, 'w') as f:
            f.write(rst_string)

        if check == -1:
            hex_pattern = r'\b0x[0-9a-fA-F]+\b'
            match1 = re.search(hex_pattern, rst[0][1].stdout)
            match2 = re.search(hex_pattern, rst[1][1].stdout)
            if bool(match1) and bool(match2):
                os.rename(dir_path, os.path.join(self.test_unit_path, "hd_" + str(index)))
                check = 1
            else:
                os.rename(dir_path, os.path.join(self.test_unit_path, "d_" + str(index)))
        elif check == 0:
            os.rename(dir_path, os.path.join(self.test_unit_path, "u_" + str(index)))
        else:
            os.rename(dir_path, os.path.join(self.test_unit_path, "s_" + str(index)))

        return check

    def generate_test_case_loop(self):
        with tqdm() as pbar:
            index = 0
            d_count = 0
            while True:
                seed = next(self.seed_corpus)
                old_code = seed["code"]
                total_nodes = self._get_total_nodes(old_code)
                node_index = round((total_nodes - 1) * random.uniform(0, 1))
                masked_code = self._mask(old_code, node_index)
                new_code = masked_code.replace("<mask>", self._generate(masked_code))

                sample_input = seed["samples"][0]["input"]

                flag = self._test_case_do_filter(old_code, new_code)
                if not flag:
                    check = self._execute_test_unit(new_code, index, sample_input)
                    if check == -1:
                        d_count += 1
                    
                    # TODO: exploit 

                    index += 1
                    pbar.update(1)
                    pbar.set_postfix({"d_count": d_count})

                    if index > 2:
                        break
