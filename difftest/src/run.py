from test_case_generator import TestCaseGenerator

import torch
from transformers import RobertaTokenizer

from go_generate.go_generator import GoGenerator
from go_generate.test_case_maker import TestCaseMaker

MODEL_PATH = "/bigdata/qiuhan/codet5_fuzz/codet5-small-go_generation_v2"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

go_generator = GoGenerator(MODEL_PATH, DEVICE)

tokenizer = RobertaTokenizer.from_pretrained(MODEL_PATH)

SEED_PATH = "/bigdata/qiuhan/codet5_fuzz/src/data/seed_71421.jsonl"
TEST_UNIT_PATH = "/bigdata/qiuhan/codet5_fuzz/test_unit"

test_case_generator = TestCaseGenerator(SEED_PATH, TEST_UNIT_PATH, go_generator, tokenizer)

test_case_generator.make_test_case_loop()
