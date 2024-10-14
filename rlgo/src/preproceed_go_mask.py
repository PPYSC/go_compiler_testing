import json
import jsonlines
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch

from tqdm import tqdm

from go_tree_sitter.go_parser import GoParser

parser = GoParser()

def data_from_jsonl(path):
    with jsonlines.open(path, "r") as f:
        for line in f:
            yield line

def data_to_jsonl_append(path, data):
    with jsonlines.open(path, "a") as f:
        f.write(data)

def mask(code, mask):
    def find_ith_node(node, index, i):
        if index[0] == i:
            return node
        index[0] += 1
        for child in node.children:
            result = find_ith_node(child, index, i)
            if result is not None:
                return result
        return None
    
    tree = parser.parse(code)
    root_node = tree.root_node

    index = [0]
    target_node = find_ith_node(root_node, index, mask)
    if target_node is not None:
        start_byte = target_node.start_byte
        end_byte = target_node.end_byte
        masked_code = code[:start_byte] + "<mask>" + code[end_byte:]
    else:
        masked_code= code + "<mask>"
    return masked_code, target_node.text.decode('utf8', errors='replace')

def get_total_nodes(code):
    def count_nodes(node):
        count = 1
        for child in node.children:
            count += count_nodes(child)
        return count
    
    tree = parser.parse(code)
    root_node = tree.root_node
    total_nodes = count_nodes(root_node)
    return total_nodes


checkpoint1 = "Salesforce/codet5p-220m"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
tokenizer = AutoTokenizer.from_pretrained(checkpoint1)

corpus_path = "/home/shareduser/ysc/go_compiler_testing/CodeT5/CodeT5+/data/data_71421_no_web_import.jsonl"

output_path = "/home/shareduser/ysc/go_compiler_testing/CodeT5/CodeT5+/data/data_71421_no_web_import_train.jsonl"

corpus = data_from_jsonl(corpus_path)


for line in tqdm(corpus, desc="Processing lines", position=0):
    full_code = line["code"]
    total_nodes = get_total_nodes(full_code)
    for i in tqdm(range(total_nodes), desc="Explore i", leave=False, position=1):
        if i == 0:
            continue
        masked_code, target_code = mask(full_code, i)

        masked_code_encoding = tokenizer(masked_code, return_tensors="pt")
        target_code_encoding = tokenizer(target_code, return_tensors="pt")

        if len(masked_code_encoding.input_ids[0]) <= 512 and len(target_code_encoding.input_ids[0]) <= 256:
            data = {"input": masked_code, "output": target_code}
            data_to_jsonl_append(output_path, data)