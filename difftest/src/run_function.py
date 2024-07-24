from test_case_generator import TestCaseGenerator

import torch
from transformers import RobertaTokenizer

from go_generate.go_generator import GoGenerator

MODEL_PATH = "/home/shareduser/ysc/go_compiler_testing/difftest/codet5-small-go_generation_v2"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

go_generator = GoGenerator(MODEL_PATH, DEVICE)

tokenizer = RobertaTokenizer.from_pretrained(MODEL_PATH)

SEED_PATH = "/home/shareduser/ysc/go_compiler_testing/difftest/src/data/data_go_testcase_token_size_filtered.jsonl"
TEST_UNIT_PATH = "/home/shareduser/ysc/go_compiler_testing/difftest/src/test_unit"

test_case_generator = TestCaseGenerator(SEED_PATH, TEST_UNIT_PATH, go_generator, tokenizer)

test_case_generator.generate_test_case_loop()
