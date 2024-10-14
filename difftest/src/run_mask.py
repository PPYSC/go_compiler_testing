from test_case_generator_input import TestCaseGenerator


from go_mask_generator.node_mask_codet5p import NodeMaskCodet5p

go_generator = NodeMaskCodet5p()

tokenizer = go_generator.tokenizer

SEED_PATH = "/home/shareduser/ysc/go_compiler_testing/difftest/src/data/proceed_data.jsonl"
TEST_UNIT_PATH = "/home/shareduser/ysc/go_compiler_testing/difftest/src/test_unit"

test_case_generator = TestCaseGenerator(SEED_PATH, TEST_UNIT_PATH, go_generator, tokenizer)

test_case_generator.generate_test_case_loop()
