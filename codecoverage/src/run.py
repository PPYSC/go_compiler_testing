import subprocess

import jsonlines
from tqdm import tqdm
from cal_coverage import CalCoverage, mkdir

cal_coverage = CalCoverage()

cal_cov_path = "/home/shareduser/ysc/go_compiler_testing/codecoverage/test_unit"

merged_path = cal_cov_path + "/merged"
profile_path = cal_cov_path + "/profile.txt"

name = "c_cal"

code_corpus_path = "/home/shareduser/ysc/go_compiler_testing/codecoverage/data/data_go_testcase_nocomment_token_size_filtered_multithreaded.jsonl"
#code_corpus_path = "/home/shareduser/ysc/go_compiler_testing/codecoverage/data/data_test.jsonl"


if mkdir(merged_path):
    with jsonlines.open(code_corpus_path, "r") as f:
        with tqdm() as pbar:
            for line in f:
                code = line["code"]
                rst_cov = cal_coverage.cal_coverage(cal_cov_path, name, code)
                pbar.update(1)
                pbar.set_postfix({"rst_cov": rst_cov})
    

    cmd = f"go tool covdata textfmt -i={merged_path} -o {profile_path}"
    subprocess.run(cmd, shell=True)

    total = 709107
    Sum=0
    with open(profile_path, 'r') as file:
        lines = file.readlines()[1:]
        for line in lines:
            values = line.split(' ')
            last_integer = int(values[-1])
            Sum += last_integer
    print(Sum/total)
else:
    print("merged dir is exist")


