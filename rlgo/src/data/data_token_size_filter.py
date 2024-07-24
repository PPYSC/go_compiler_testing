from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch
from data_io.file_io import data_from_jsonl, data_to_jsonl_append

from tqdm import tqdm


checkpoint1 = "Salesforce/codet5p-220m"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
tokenizer = AutoTokenizer.from_pretrained(checkpoint1)

corpus_path = "/home/shareduser/ysc/go_compiler_testing/rlgo/src/data/data_go_testcase_nocomment.jsonl"

output_path = "/home/shareduser/ysc/go_compiler_testing/rlgo/src/data/data_go_testcase_nocomment_token_size_filtered.jsonl"

corpus = data_from_jsonl(corpus_path)


for line in tqdm(corpus, desc="Processing lines"):
    encoding = tokenizer(line["code"], return_tensors="pt").to(device)
    if len(encoding.input_ids[0]) <= 512:
        data_to_jsonl_append(output_path, line)

