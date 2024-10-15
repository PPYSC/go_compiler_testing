from test_data_generator_multithreaded import TestDataGenerator

from go_mask_generator.node_mask_codet5p import NodeMaskCodet5p

go_generator = NodeMaskCodet5p()

tokenizer = go_generator.tokenizer

SEED_PATH = "/home/shareduser/ysc/go_compiler_testing/difftest/src/data/data_go_testcase_nocomment_token_size_filtered.jsonl"
#SEED_PATH = "/home/shareduser/ysc/go_compiler_testing/difftest/src/data/proceed_data_token_size_filtered.jsonl"
TEST_UNIT_PATH = "/home/shareduser/ysc/go_compiler_testing/difftest/src/data/data_go_testcase_nocomment_token_size_filtered_multithreaded.jsonl"
TEST_UNIT_PATH = "/home/shareduser/ysc/go_compiler_testing/difftest/src/data/data_go_testcase_nocomment_token_size_filtered_multithreaded_0gcb.jsonl"

test_case_generator = TestDataGenerator(SEED_PATH, TEST_UNIT_PATH, go_generator, tokenizer)

test_case_generator.generate_test_data_loop()
