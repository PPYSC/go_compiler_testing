import os
import json

def find_and_write_go_files(path, output_file):
    with open(output_file, 'w') as jsonl_file:
        for root, _, files in os.walk(path):
            for file in files:
                if file.endswith('.go'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r') as go_file:
                            content = go_file.read()
                            if 'package main' in content:
                                jsonl_file.write(json.dumps({"code": content}) + '\n')
                                print(f"Processed {file_path}")
                    except IOError as e:
                        print(f"Error reading file {file_path}: {e}")

# 示例调用
folder_path = '/home/shareduser/ysc/go_compiler_testing/go/test'
output_file = 'data_go_testcase.jsonl'
find_and_write_go_files(folder_path, output_file)