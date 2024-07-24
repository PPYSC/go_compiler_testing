

from tqdm import tqdm
from data_io.file_io import data_from_jsonl, data_to_jsonl_append
from go_tree_sitter.go_parser import GoParser
from go_tree_sitter.go_tree_sitter_tool import GoTreeSitterTool

parser = GoParser()

def delete_all_comment(code):
        node = parser.parse(code).root_node

        comments = [elem.text.decode("utf8") for elem in GoTreeSitterTool.get_comment(node)]
        comments.sort(key=lambda x: len(x), reverse=True)

        for comment in comments:
            code = code.replace(comment, "")

        rst_code = ""
        for line in code.splitlines():
            if len(line) == 0:
                rst_code = rst_code + line + "\n"
            if len(line.replace("\t", "")) != 0:
                rst_code = rst_code + line + "\n"

        return rst_code.strip()


corpus_path = "/home/shareduser/ysc/go_compiler_testing/rlgo/src/data/data_go_testcase.jsonl"
output_path = "/home/shareduser/ysc/go_compiler_testing/rlgo/src/data/data_go_testcase_nocomment.jsonl"


corpus = data_from_jsonl(corpus_path)

for line in tqdm(corpus, desc="Processing lines"):
    new_line = {"code": delete_all_comment(line["code"])}
    data_to_jsonl_append(output_path, new_line)